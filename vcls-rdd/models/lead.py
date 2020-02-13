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
        In the context of a migration, we don't request a new internal_ref but we try to extract in from the name of the opportunity.
        """
        if self.env.user.context_data_integration:
            for lead in self:
                lead_vals = {**vals} #we make a copy of the vals to avoid iterative updates

                if lead_vals.get('type',lead.type) == 'opportunity' and lead_vals.get('name',False): #if opportunity we try to rename
                    client = self.env['res.partner'].browse(lead_vals.get('partner_id',self.partner_id.id))
                    if not client.altname:
                        raise ValidationError("Please document an ALTNAME in the {} client sheet to automate refence calculation.".format(client.name))
                    else:
                        raw_name = lead_vals['name']
                        if client.altname.lower() in raw_name.lower(): 
                            index = raw_name.lower().split(client.altname.lower())[1][1:4]

                            try:
                                new_ref = "{}-{:03}".format(client.altname.upper(), int(index))
                                new_name = raw_name.split(index)[1].lstrip()
                                lead_vals.update({
                                    'internal_ref': new_ref,
                                    #'name':raw_name.split(index)[1].lstrip(),
                                    'name':"{} | {}".format(new_ref,new_name) if new_name else new_ref,
                                    })
                                _logger.info("OPP MIGRATION: found {} in {} with index {} new ref {}".format(client.altname,raw_name,index,new_ref))

                                if int(index) > client.core_process_index: #we force the next index
                                    client.write({
                                        'core_process_index': int(index),
                                        'altname': client.altname.upper(),
                                        })
                            except:
                                _logger.info("OPP MIGRATION: Bad format for opp {}".format(lead_vals['name']))
                                lead_vals.update({
                                    'internal_ref': False,
                                    'name':"({}) {}".format(index,raw_name.lower().split(index.lower())[1].lstrip()) if index else raw_name,
                                    })
                                

                #_logger.info("OPP MIGRATION: New vals {}".format(lead_vals))
                if not super(Leads, lead).write(lead_vals):
                    return False
            return True
        

        else:
            return super(Leads, self).write(vals)