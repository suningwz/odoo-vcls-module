# -*- coding: utf-8 -*-

#Python Imports
from datetime import datetime, time
from dateutil.relativedelta import relativedelta
#Odoo Imports
from odoo import api, fields, models


class BankHoliday(models.Model):
    
    _name = 'hr.bank.holiday'
    _description = 'Bank Holiday'
    _sql_constraints = [
                     ('bank_per_company_unique', 
                      'unique(name,company_id)',
                      'This Bank holiday name already exists for this company.')
                    ]
      
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
        rec=super().create(vals)
        
        #Search the working times that are linked to the company
        wts = rec.env['resource.calendar'].search([('company_id','=',rec.company_id.id)])
        
        #loop results to create related global leaves
        for wt in wts:
            date_from = datetime.combine(rec.date, time(0, 0, 0))
            wt.env['resource.calendar.leaves'].create(
                {
                    'name':rec.name,
                    'company_id':rec.company_id.id,
                    'calendar_id':wt.id,
                    'date_from':date_from,
                    'date_to':date_from + relativedelta(days=1),
                }
            )

        return rec
    
    #Delete related global leaves if the bank holiday is deleted
    @api.multi
    def unlink(self):
        for rec in self:
            rec.env['resource.calendar.leaves'].search([('company_id.id','=',rec.company_id.id),('name','=',rec.name),('resource_id','=',False)]).unlink()
            #ajouter unicité du name par compny
            
        return super().unlink()
            
            
