# -*- coding: utf-8 -*-

#Odoo Imports
from odoo import api, fields, models

class Benefit(models.Model):
    
    _name = 'hr.benefit'
    _description = 'Benefits'
    _order = 'date desc'
    
    #################
    # Custom Fields #
    #################
    
    employee_id = fields.Many2one(
        'hr.employee',
        required = True,
        )
    
    date = fields.Date(
        string='Date from',
        required=True)
    
    currency_id = fields.Many2one(
        related = 'employee_id.company_id.currency_id',
        string="Currency",
        readonly=True,)
    
    car_info = fields.Char(
        string='Company car',
        compute='_get_car_info',
        )
    
    car_allowance = fields.Monetary(
        string='Car allowance',)
    
    transport_allowance = fields.Monetary(
        string='Transport allowance',)
    
    mobility_type = fields.Selection(
        selection = [
            ('bike','Bike'),
            ('public_yearly','Public (Yearly)'),
            ('public_monthly','Public (Monthly)'),
            ('parking','Parking'),
        ]
    )
    
    lunch_allowance = fields.Monetary(
        string='Lunch allowance',)
    
    phone = fields.Boolean()
    
    #################################
    # Automated Calculation Methods #
    #################################
    
    @api.multi
    def _get_car_info(self):
        wt = self.env['fleet.vehicle']
        for rec in self:
            cars = wt.search([('driver_id','=',rec.employee_id.user_id.partner_id.id),('active','=',True)])
            if len(cars)>0: #if a car has been found
                car = wt.browse(cars[0].id)
                rec.car_info = car.info
            else:
                rec.car_info = 'no car'