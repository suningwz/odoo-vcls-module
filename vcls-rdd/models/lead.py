# -*- coding: utf-8 -*-
# (C) 2019 Smile (<http://www.smile.fr>)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).

from odoo import fields, models, api
from odoo.exceptions import UserError, ValidationError
from odoo import exceptions
import re
import logging
_logger = logging.getLogger(__name__)


class Leads(models.Model):
    _inherit = 'crm.lead'

    @api.model
    def clear_migrated_ref(self):
        #we get the opps and clean
        keys = self.env['etl.sync.keys'].search([('externalObjName','=','Opportunity'),('odooId','!=',False)])
        opp_ids = [int(i) for i in keys.mapped('odooId')]
        opps = self.env['crm.lead'].browse(opp_ids)
        opps.with_context(clear_ref=True).write({'internal_ref':False})

        #get the non-cleaned opps
        manual_opps = self.search([('internal_ref','!=',False)])
        client_ids = manual_opps.mapped('partner_id.id')
        clients = self.env['res.partner'].browse(client_ids).write({'core_process_index':0})

        for opp in manual_opps:
            index = int(opp.internal_ref.split('-')[1])
            if index > opp.partner_id.core_process_index:
                opp.partner_id.core_process_index=index
                _logger.info("CLient Index Update {}-{}".format(opp.partner_id.altname,index))

    def write(self, vals):
        """
        In the context of a migration, we don't request a new internal_ref but we try to extract it from the name of the opportunity.
        """
        if self.env.user.context_data_integration:
            for lead in self:
                lead_vals = {**vals} #we make a copy of the vals to avoid iterative updates
                bad_output = True
                #if lead_vals.get('type',lead.type) == 'opportunity' and lead_vals.get('name',False):
                if lead_vals.get('type',lead.type) == 'opportunity' and lead_vals.get('name',False) and not lead_vals.get('internal_ref',lead.internal_ref): #if opportunity we try to rename
                    client = self.env['res.partner'].browse(lead_vals.get('partner_id',self.partner_id.id))
                    if not client.altname:
                        raise ValidationError("Please document an ALTNAME in the {} client sheet to automate refence calculation.".format(client.name))
                    else:
                        raw_name = lead_vals['name']

                        if client.altname.lower() in raw_name.lower(): 
                            index = raw_name.lower().split(client.altname.lower())[1][1:4]
                            try:
                                new_ref = "{}-{:03}".format(client.altname.upper(), int(index))
                                raw_name = raw_name.split(index)[1].lstrip()
                                bad_output = False
                                _logger.info("OPP MIGRATION: found {} in {} with index {} new ref {}".format(client.altname,raw_name,index,new_ref))
                            except:
                                pass
                        
                        else: #we try to find a 3digit number
                            indexes = re.findall(r"\D(\d{3})\D",raw_name)
                            for index in indexes:
                                if int(index)<100:
                                    bad_output = False
                                    break

                    if bad_output:
                        _logger.info("OPP MIGRATION: Bad format for opp with altname {}".format(lead_vals['name']))
                        lead_vals.update({
                            'internal_ref': False,
                            'name': raw_name,
                            })
                    else:
                        new_ref = "{}-{:03}".format(client.altname.upper(), int(index))
                        lead_vals.update({
                            'internal_ref': new_ref,
                            'name':"{} | {}".format(new_ref,raw_name) if raw_name else new_ref,
                            })

                        if int(index) > client.core_process_index: #we force the next index
                            client.write({
                                'core_process_index': int(index),
                                'altname': client.altname.upper(),
                                })
                                

                #_logger.info("OPP MIGRATION: New vals {}".format(lead_vals))
                lead_vals['planned_revenue']=lead.get_revenue_in_company_currency()
                if not super(Leads, lead).write(lead_vals):
                    return False
            return True
        

        else:
            return super(Leads, self).write(vals)