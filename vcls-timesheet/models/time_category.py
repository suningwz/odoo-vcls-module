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

        time_categories_ids = super(TimeCategory, self)._search(args, offset, limit, order, count=count, access_rights_uid=access_rights_uid)
        _logger.info("{} | {}".format(task_id,time_categories_ids))

        #if we are in the context of a custom task filtered search, we look at the list of authorized categories in the related task
        if task_id:
            time_categories_ids.filter(lambda r: r.id in task_id.time_categories_ids)
            
        return time_categories_ids