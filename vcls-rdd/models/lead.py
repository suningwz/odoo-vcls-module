# -*- coding: utf-8 -*-
# (C) 2019 Smile (<http://www.smile.fr>)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).

from odoo import fields, models, api
from odoo.exceptions import UserError, ValidationError
from odoo import exceptions

import logging
_logger = logging.getLogger(__name__)


class Leads(models.Model):
    _inherit = 'crm.lead'

    def write(self, vals):
        """
        In the context of a migration, we don't request a new internal_ref but we set it based on the name of the opportunity.
        """
        if (vals.get('type',False) == 'opportunity' or self.type == 'opportunity') and self.env.user.context_data_integration:
            #we get the related client
            client = self.env['res.partner'].browse(vals.get('partner_id',self.partner_id.id))
            raw_name = vals.get('name',False)
            _logger.info("OPP MIGRATION WRITE {}:".format(vals))

            #if no ALTNAME, then we raise an error, else, we try to find in in the name of the opp
            if not client.altname:
                raise ValidationError("Please document an ALTNAME in the {} client sheet to automate refence calculation.".format(client.name))
            elif not raw_name:
                _logger.info("OPP MIGRATION: corrupted opp {}.".format(vals))
            else:
                try:
                    if client.altname.lower() in raw_name.lower(): 
                        index = raw_name.lower().split(client.altname.lower())[1][1:4]
                        _logger.info("OPP MIGRATION: found {} in {} with index {}".format(client.altname,raw_name,index))

                        if int(index) > client.core_process_index: #we force the next index
                            client.write({'core_process_index': int(index)})

                        vals['name'] = raw_name.split(index)[1].lstrip()
                        vals['internal_ref'] = "{}-{}".format(client.altname.upper(), index)

                except:
                    _logger.info("OPP MIGRATION: Bad format for opp {}".format(vals['name']))

            
        return super(Leads, self).write(vals)