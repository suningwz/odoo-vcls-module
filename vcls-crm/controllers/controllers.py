# -*- coding: utf-8 -*-
from odoo import http

# class Vcls-crm(http.Controller):
#     @http.route('/vcls-crm/vcls-crm/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/vcls-crm/vcls-crm/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('vcls-crm.listing', {
#             'root': '/vcls-crm/vcls-crm',
#             'objects': http.request.env['vcls-crm.vcls-crm'].search([]),
#         })

#     @http.route('/vcls-crm/vcls-crm/objects/<model("vcls-crm.vcls-crm"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('vcls-crm.object', {
#             'object': obj
#         })