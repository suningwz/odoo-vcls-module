# -*- coding: utf-8 -*-
from odoo import http

# class Vcls-suppliers(http.Controller):
#     @http.route('/vcls-suppliers/vcls-suppliers/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/vcls-suppliers/vcls-suppliers/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('vcls-suppliers.listing', {
#             'root': '/vcls-suppliers/vcls-suppliers',
#             'objects': http.request.env['vcls-suppliers.vcls-suppliers'].search([]),
#         })

#     @http.route('/vcls-suppliers/vcls-suppliers/objects/<model("vcls-suppliers.vcls-suppliers"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('vcls-suppliers.object', {
#             'object': obj
#         })