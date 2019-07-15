from odoo import models, fields, tools, api
from odoo.exceptions import UserError, ValidationError
import datetime

class CrmLead(models.Model):
    _inherit='crm.lead'

    task_id = fields.Many2one("project.task", string="Task", track_visibility="onchange")

    @api.onchange('stage_id')
    def _onchange_stage_id(self):
        stage_won = self.env['crm.stage'].search([('name','=','Won')])
        stage_lost = self.env['crm.stage'].search([('name','=','Lost')])
        task_id = self.env['project.task'].search([('name','=',self.name)])
        if task_id:
            if self.stage_id == stage_won:
                task_id.write({'stage_id':self.env['project.task.type'].search([('name','=','Completed')], limit=1).id})

            if self.stage_id == stage_lost:
                task_id.write({'stage_id': self.env['project.task.type'].search([('name','=','Cancelled')], limit=1).id})
    
    def task_timesheet(self):
        return {
            'name': 'Timesheet',
            'view_type': 'form',
            'view_mode': 'tree,kanban,form',
            'target': 'current',
            'res_model': 'account.analytic.line',
            'type': 'ir.actions.act_window',
            'context': {'search_default_task_id': self.task_id.id,},
        } 