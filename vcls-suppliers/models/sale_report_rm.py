# -*- coding: utf-8 -*-

from odoo import tools
from odoo import api, fields, models
AVAILABLE_PRIORITIES = [
    ('0', 'Low'),
    ('1', 'Medium'),
    ('2', 'High'),
    ('3', 'Very High'),
]


class SaleReportRM(models.Model):
    _name = 'sale.report.rm'
    _description = "Ongoing sales for Resource Management"
    _auto = False

    name = fields.Char('Name', readonly=True)

    # Opportunity
    opportunity_id = fields.Many2one('crm.lead', readonly=True)
    amount_customer_currency = fields.Float(
        string='Customer amount', readonly=True)
    priority = fields.Selection(AVAILABLE_PRIORITIES, string='Priority', readonly=True)
    expected_start_date = fields.Date(
        string="Expected Project Start Date", readonly=True)
    stage_id = fields.Many2one('crm.stage', string='Stage', readonly=True)
    probability = fields.Float('Probability', group_operator="avg", readonly=True)
    partner_id = fields.Many2one('res.partner', string='Customer', readonly=True)
    app_country_group_id = fields.Many2one('res.country.group', string="Application Geographic Area", readonly=True)
    user_id = fields.Many2one('res.users', string='Salesperson', readonly=True)
    technical_adv_id = fields.Many2one('hr.employee', string='PIC', readonly=True)
    
    # Program
    program_id = fields.Many2one('project.program', 'Program', readonly=True)
    product_name = fields.Char(string="Product Name", help='The client product name', readonly=True)
    program_stage_id = fields.Selection([
        ('pre', 'Preclinical'),
        ('exploratory', 'Exploratory Clinical'),
        ('confirmatory', 'Confirmatory Clinical'),
        ('post', 'Post Marketing')],
        'Program Stage',
        readonly=True)
    leader_id = fields.Many2one(comodel_name='res.users', string='Program Leader', readonly=True)
    
    # QUOTATION FIELDS
    order_id = fields.Many2one('sale.order', 'Quotations', readonly=True)
    order_expected_start_date = fields.Date(readonly=True)
    order_expected_end_date = fields.Date(readonly=True)
    scope_of_work = fields.Html(string="Scope of Work", readonly=True)
    deliverables = fields.Char('Deliverables', readonly=True)
    state = fields.Selection([
        ('draft', 'Quotation'),
        ('sent', 'Quotation Sent'),
        ('sale', 'Sales Order'),
        ('done', 'Locked'),
        ('cancel', 'Cancelled'),
    ], string='Status', readonly=True)
    
    # Core_team_id
    core_team_id = fields.Many2one(
        'core.team',
        string='Core team'
    )
    lead_consultant = fields.Many2one(
        'hr.employee',
        string='Lead Consultant', readonly=True
    )
    lead_backup = fields.Many2one('hr.employee', string='Lead Consultant Backup', readonly=True)
    consultant_ids = fields.Many2many(
        comodel_name='hr.employee',
        string='Consultants',
        readonly=True,
        compute='_get_core_team_data',
        search=lambda self, operator, value: [('core_team_id.consultant_ids', operator, value)],
        store=False,
    )
    ta_ids = fields.Many2many(
        comodel_name='hr.employee',
        string='Ta', readonly=True,
        compute='_get_core_team_data',
        search=lambda self, operator, value: [('core_team_id.ta_ids', operator, value)],
        store=False,
    )

    @api.one
    @api.depends('core_team_id')
    def _get_core_team_data(self):
        self.consultant_ids = self.core_team_id.consultant_ids.ids
        self.ta_ids = self.core_team_id.ta_ids.ids

    def _select(self):
        select_str = """
        (select row_number() OVER () as id,
        crm.id as opportunity_id,
        crm.probability as probability,
        crm.amount_customer_currency as amount_customer_currency,
        crm.priority as priority,
        crm.expected_start_date as expected_start_date,
        crm.stage_id as stage_id,
        crm.partner_id as partner_id,
        crm.app_country_group_id as app_country_group_id,
        crm.user_id as user_id,
        crm.technical_adv_id as technical_adv_id,
        program.id as program_id,
        program.product_name as product_name,
        program.stage_id as program_stage_id,
        program.leader_id as leader_id,
        o.id as order_id,
        o.expected_start_date as order_expected_start_date,
        o.expected_end_date as order_expected_end_date,
        o.scope_of_work as scope_of_work,
        o.state as state,
        o.name as name,
        team.lead_consultant as lead_consultant,
        team.id as core_team_id,
        team.lead_backup as lead_backup,
        (SELECT string_agg(DISTINCT(deli.name), ', ') 
            from sale_order_line sol 
            left join product_product product
            on sol.product_id = product.id
            left join product_template product_tpl
            on product_tpl.id = product.product_tmpl_id
            left join product_deliverable deli
            on product_tpl.deliverable_id = deli.id
            where o.id = sol.order_id
        ) as deliverables
         """
        return select_str
    
    def _from(self):
        from_str = """
         sale_order as o
        left join crm_lead as crm on crm.id = o.opportunity_id
        left join project_program as program on program.id = o.program_id
        left join core_team as team on team.id = o.core_team_id """
        return from_str
    
    def _group_by(self):
        group_by_str = """
        WHERE o.state != 'sale'
        GROUP BY crm.id,
        crm.probability,
        crm.amount_customer_currency,
        crm.priority,
        crm.expected_start_date,
        crm.stage_id,
        crm.partner_id,
        crm.app_country_group_id,
        crm.user_id,
        crm.technical_adv_id,
        program.id,
        program.product_name,
        program.stage_id,
        program.leader_id,
        o.id,
        o.expected_start_date,
        o.expected_end_date,
        o.scope_of_work,
        o.state,
        o.name,
        team.id
        """
        return group_by_str

    @api.model_cr
    def init(self):
        self = self.sudo()
        tools.drop_view_if_exists(self.env.cr, self._table)
        self.env.cr.execute("""CREATE or REPLACE VIEW sale_report_rm as (
                    %s
                    FROM ( %s )
                    %s
                    ))""" % (self._select(), self._from(), self._group_by()))
