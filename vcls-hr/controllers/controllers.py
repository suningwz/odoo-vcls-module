# -*- coding: utf-8 -*-
from odoo import http

# class Vcls-hr(http.Controller):
#     @http.route('/vcls-hr/vcls-hr/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/vcls-hr/vcls-hr/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('vcls-hr.listing', {
#             'root': '/vcls-hr/vcls-hr',
#             'objects': http.request.env['vcls-hr.vcls-hr'].search([]),
#         })

#     @http.route('/vcls-hr/vcls-hr/objects/<model("vcls-hr.vcls-hr"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('vcls-hr.object', {
#             'object': obj
#         })