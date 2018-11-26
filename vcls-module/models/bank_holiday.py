# -*- coding: utf-8 -*-

#Python Imports
from datetime import datetime, time
from dateutil.relativedelta import relativedelta
#Odoo Imports
from odoo import api, fields, models


class BankHoliday(models.Model):
    
    _name = 'hr.bank.holiday'
    _description = 'Bank Holiday'
      
    #################
    # Custom Fields #
    #################
    
    name = fields.Char(
        required=True,)
    
    company_id = fields.Many2one(
        'res.company',
        string='Company',
        required=True,)
    
    date = fields.Date(
        required=True,)
    
    comment = fields.Char()
    
    ################
    # CRUD Methods #
    ################
    
    #Create the related global leaves, in each active working time of the related company
    @api.model
    def create(self,vals):
        rec=super(BankHoliday,self).create(vals)
        
        #Search the working times that are linked to the company
        wts = rec.env['resource.calendar'].search([('company_id','=',rec.company_id.id)])
        
        #loop results to create related global leaves
        for wt in wts:
            wt.env['resource.calendar.leaves'].create(
                {
                    'name':rec.name,
                    'company_id':rec.company_id.id,
                    'calendar_id':wt.id,
                    'date_from':rec.date,
                    'date_to':rec.date + relativedelta(days=1),
                }
            )

        return rec
    
    #Delete related global leaves if the bank holiday is deleted
    @api.multi
    def unlink(self):
        for rec in self:
            rec.env['resource.calendar.leaves'].search([('company_id.id','=',rec.company_id.id),('name','=',rec.name),('resource_id','=',False)]).unlink()
        return models.Model.unlink(self)
            
            
