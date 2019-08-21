from odoo import models, fields, tools, api
from odoo.exceptions import UserError, ValidationError
import datetime

class SaleOrder(models.Model):
    _inherit='sale.order'
    @api.multi
    def action_view_forecast(self):
        self.ensure_one()
        project_ids = self.project_ids
        return {
            'type': 'ir.actions.act_window',
            'name': "Forecast",
            'res_model': 'project.forecast',
            'search_view_id': self.env.ref('project_timesheet_forecast.project_timesheet_forecast_report_view_search').id,
            'view_mode': 'graph,pivot',
            'context': {
                'project_id': project_ids.id,
                'default_project_id': project_ids.id, 
                'search_default_project_id': [project_ids.id],
                'grid_anchor': (datetime.date.today()).strftime('%Y-%m-%d'),
            }
        }
    @api.model
    def create(self, vals):
        result = super(SaleOrder, self).create(vals)
        result.first_quotation()
        return result

    def first_quotation(self):
        if self.opportunity_id:
            if self.opportunity_id.sale_number == 1 : 
                pre_project = self.env.ref('vcls-timesheet.default_project').id
                stage_id = self.env['project.task.type'].sudo().search([('name','=','0% Progress')], limit=1).id
                self.opportunity_id.task_id = self.env['project.task'].sudo().create({
                                                                                    'name':self.opportunity_id.name,
                                                                                    'project_id':pre_project, 
                                                                                    'stage_id':stage_id, 
                                                                                    'active':True}).id
    
    #We override the OCA to inject the stage domain
    @api.multi
    @api.depends('timesheet_limit_date')
    def _compute_timesheet_ids(self):
        # this method copy of base method, it injects date in domain
        for order in self:
            if order.analytic_account_id:
                domain = [
                    ('so_line', 'in', order.order_line.ids),
                    ('amount', '<=', 0.0),
                    ('project_id', '!=', False),
                    #XXX OCA override
                    ('stage_id', 'in', ['invoiceable','invoiced']),
                ]
                if order.timesheet_limit_date:
                    domain.append(
                        ('date', '<=', order.timesheet_limit_date)
                    )
                order.timesheet_ids = self.env[
                    'account.analytic.line'].search(domain)
            else:
                order.timesheet_ids = []
            order.timesheet_count = len(order.timesheet_ids)


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    name = fields.Char(
        store = True
    )

    

