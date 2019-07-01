from odoo import models, fields, tools, api
from odoo.exceptions import UserError, ValidationError

from datetime import date, datetime
from dateutil.relativedelta import relativedelta

class ProductTemplate(models.Model):

    _inherit = 'product.template'

    #################
    # CUSTOM FIELDS #
    #################

    grouping_info = fields.Char(
        store = True,
        compute = '_compute_grouping_info',
    )

    ###################
    # COMPUTE METHODS #
    ###################

    @api.depends('deliverable_id','seniority_level_id')
    def _compute_grouping_info(self):
        for prod in self:
            if prod.deliverable_id:
                prod.grouping_info = prod.deliverable_id.name
            elif prod.seniority_level_id:
                prod.grouping_info = prod.seniority_level_id.name
            else:
                prod.grouping_info = False

    @api.model
    def _match_forecast_employee(self):
        rates = self.search([('seniority_level_id','!=',False)])
        for rate in rates:
            emp = self.env['hr.employee'].with_context(active_test=False).search([('name','=',rate.name)])
            if emp:
                #we ensure a contract to exists for these employee
                if not emp.contract_id:
                    contract = self.env['hr.contract'].create({
                        'name':emp.name,
                        'employee_id':emp.id,
                        'resource_calendar_id':self.env.ref('__import__.WT_FRC100').id,
                        'active':False,
                        'type_id':self.env.ref('vcls-hr.contract_permanent').id,
                        'date_start': datetime.now() + relativedelta(years=5),
                    })
                    emp.contract_id = contract

                rate.write({
                    'forecast_employee_id':emp.id,
                    }) 
