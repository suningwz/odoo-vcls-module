# -*- coding: utf-8 -*-
from odoo import http

# class Vcls-interfaces(http.Controller):
#     @http.route('/vcls-interfaces/vcls-interfaces/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/vcls-interfaces/vcls-interfaces/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('vcls-interfaces.listing', {
#             'root': '/vcls-interfaces/vcls-interfaces',
#             'objects': http.request.env['vcls-interfaces.vcls-interfaces'].search([]),
#         })

#     @http.route('/vcls-interfaces/vcls-interfaces/objects/<model("vcls-interfaces.vcls-interfaces"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('vcls-interfaces.object', {
#             'object': obj
#         })