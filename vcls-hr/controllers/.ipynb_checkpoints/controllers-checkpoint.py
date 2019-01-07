# -*- coding: utf-8 -*-
from odoo import http

# class Vcls-module(http.Controller):
#     @http.route('/vcls-module/vcls-module/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/vcls-module/vcls-module/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('vcls-module.listing', {
#             'root': '/vcls-module/vcls-module',
#             'objects': http.request.env['vcls-module.vcls-module'].search([]),
#         })

#     @http.route('/vcls-module/vcls-module/objects/<model("vcls-module.vcls-module"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('vcls-module.object', {
#             'object': obj
#         })