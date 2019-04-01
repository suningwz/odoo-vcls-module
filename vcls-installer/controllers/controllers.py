# -*- coding: utf-8 -*-
from odoo import http

# class Vcls-installer(http.Controller):
#     @http.route('/vcls-installer/vcls-installer/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/vcls-installer/vcls-installer/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('vcls-installer.listing', {
#             'root': '/vcls-installer/vcls-installer',
#             'objects': http.request.env['vcls-installer.vcls-installer'].search([]),
#         })

#     @http.route('/vcls-installer/vcls-installer/objects/<model("vcls-installer.vcls-installer"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('vcls-installer.object', {
#             'object': obj
#         })