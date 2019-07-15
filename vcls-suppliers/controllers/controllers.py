# -*- coding: utf-8 -*-
from odoo import http

class Suppliers(http.Controller):
    
    @http.route('/supplier/<int:id>/', auth='public', website=True)
    def render(self, id):
        user = http.request.env['res.users'].search([('id','=',id)])
        tasks = http.request.env['project.task'].search([('user_id','=',id)])
        return http.request.render('vcls-suppliers.portal', {
            'user': user,
            'tasks': tasks
        })
        
'''
    @http.route('/vcls-suppliers/vcls-suppliers/objects/', auth='public')
    def list(self, **kw):
        return http.request.render('vcls-suppliers.listing', {
            'root': '/vcls-suppliers/vcls-suppliers',
            'objects': http.request.env['vcls-suppliers.vcls-suppliers'].search([]),
        })
    
    @http.route('/vcls-suppliers/vcls-suppliers/objects/<model("vcls-suppliers.vcls-suppliers"):obj>/', auth='public')
    def object(self, obj, **kw):
        return http.request.render('vcls-suppliers.object', {
            'object': obj
        })
'''