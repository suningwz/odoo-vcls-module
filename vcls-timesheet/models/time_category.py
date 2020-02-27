from odoo import models, fields, tools, api, _
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
            raise UserError(_("Please use the existing category '{}'").format(existing.name))
        else:
            return super(TimeCategory, self).create(vals)
    
    @api.model
    def merge(self,name_to_merge=False):
        if name_to_merge:
            #we get all the records having
            tcs = self.search([('name','=ilike',name_to_merge)]).sorted(key=lambda t: t.id)
            if tcs:
                _logger.info("Merging {} tc as {}".format(len(tcs),name_to_merge))
                to_keep = tcs[0]
                to_replace = tcs-to_keep
                for tc in to_replace:
                    #we look in products
                    pt = self.env['product.template'].with_context(active_test=False).search([('time_category_ids','in',tc.id)])
                    if pt:
                        _logger.info("Found product template to update {}".format(len(pt)))
                        pt.write({'time_category_ids': [(3, tc.id, 0)]})
                        pt.write({'time_category_ids': [(4, to_keep.id, 0)]})


