# -*- coding: utf-8 -*-
from odoo import http

# class Vcls-expenses(http.Controller):
#     @http.route('/vcls-expenses/vcls-expenses/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/vcls-expenses/vcls-expenses/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('vcls-expenses.listing', {
#             'root': '/vcls-expenses/vcls-expenses',
#             'objects': http.request.env['vcls-expenses.vcls-expenses'].search([]),
#         })

#     @http.route('/vcls-expenses/vcls-expenses/objects/<model("vcls-expenses.vcls-expenses"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('vcls-expenses.object', {
#             'object': obj
#         })