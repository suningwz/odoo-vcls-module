from odoo import models, fields, tools, api
from odoo.exceptions import UserError, ValidationError

import logging
_logger = logging.getLogger(__name__)


class TimeCategory(models.Model):
    _name = 'project.time_category'

    _description = 'Time Category'

    name = fields.Char()
    active = fields.Boolean(default="True")

    @api.model
    def _search(self, args, offset=0, limit=None, order=None, count=False, access_rights_uid=None):

        task_id = self._context.get('task_id')

        time_category_ids = super(TimeCategory, self)._search(args, offset, limit, order, count=count, access_rights_uid=access_rights_uid)

        #if we are in the context of a custom task filtered search, we look at the list of authorized categories in the related task
        if task_id:
            task = self.env['project.task'].browse(task_id)
            #_logger.info("task {} | all tc {} | found {} with tc {}".format(task_id,time_category_ids,task.id,task.time_category_ids))
            return task.time_category_ids
            
        return time_category_ids