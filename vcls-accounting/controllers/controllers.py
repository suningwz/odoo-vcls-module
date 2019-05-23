# -*- coding: utf-8 -*-
from odoo import http

# class Vcls-accounting(http.Controller):
#     @http.route('/vcls-accounting/vcls-accounting/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/vcls-accounting/vcls-accounting/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('vcls-accounting.listing', {
#             'root': '/vcls-accounting/vcls-accounting',
#             'objects': http.request.env['vcls-accounting.vcls-accounting'].search([]),
#         })

#     @http.route('/vcls-accounting/vcls-accounting/objects/<model("vcls-accounting.vcls-accounting"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('vcls-accounting.object', {
#             'object': obj
#         })