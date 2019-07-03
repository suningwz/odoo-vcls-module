# -*- coding: utf-8 -*-
from odoo import http

# class Vcls-invoicing(http.Controller):
#     @http.route('/vcls-invoicing/vcls-invoicing/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/vcls-invoicing/vcls-invoicing/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('vcls-invoicing.listing', {
#             'root': '/vcls-invoicing/vcls-invoicing',
#             'objects': http.request.env['vcls-invoicing.vcls-invoicing'].search([]),
#         })

#     @http.route('/vcls-invoicing/vcls-invoicing/objects/<model("vcls-invoicing.vcls-invoicing"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('vcls-invoicing.object', {
#             'object': obj
#         })