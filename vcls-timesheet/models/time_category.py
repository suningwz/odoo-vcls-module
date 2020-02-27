from odoo import models, fields, tools, api
from odoo.exceptions import UserError, ValidationError

import logging
_logger = logging.getLogger(__name__)


class TimeCategory(models.Model):
    _name = 'project.time_category'

    _description = 'Time Category'

    name = fields.Char(required=True)
    active = fields.Boolean(default="True")

    @api.model
    def _search(self, args, offset=0, limit=None, order=None, count=False, access_rights_uid=None):

        task_id = self._context.get('task_id')

        time_category_ids = super(TimeCategory, self)._search(args, offset, limit, order, count=count, access_rights_uid=access_rights_uid)

        #if we are in the context of a custom task filtered search, we look at the list of authorized categories in the related task
        if self._context.get('task_filter'):
            if task_id:
                task = self.env['project.task'].browse(task_id)
                return task.time_category_ids.mapped('id')
            else:
                return []
            
        return time_category_ids

    @api.model
    def create(self,vals):
        #we search for exisiting entries
        existing = self.search([('name','=ilike',vals['name'])],limit=1)
        if existing:
            raise UserError(_("Please use the existing category '{}'").format(exisiting.name))
        else:
            return super(TimeCategory, self).create(vals)

    
    """@api.model
    def replace(self):"""
