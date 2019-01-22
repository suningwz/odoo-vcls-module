# -*- coding: utf-8 -*-
from odoo import http

# class Vcls-theme(http.Controller):
#     @http.route('/vcls-theme/vcls-theme/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/vcls-theme/vcls-theme/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('vcls-theme.listing', {
#             'root': '/vcls-theme/vcls-theme',
#             'objects': http.request.env['vcls-theme.vcls-theme'].search([]),
#         })

#     @http.route('/vcls-theme/vcls-theme/objects/<model("vcls-theme.vcls-theme"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('vcls-theme.object', {
#             'object': obj
#         })