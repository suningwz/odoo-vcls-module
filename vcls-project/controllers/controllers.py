# -*- coding: utf-8 -*-
from odoo import http

# class Vcls-project(http.Controller):
#     @http.route('/vcls-project/vcls-project/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/vcls-project/vcls-project/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('vcls-project.listing', {
#             'root': '/vcls-project/vcls-project',
#             'objects': http.request.env['vcls-project.vcls-project'].search([]),
#         })

#     @http.route('/vcls-project/vcls-project/objects/<model("vcls-project.vcls-project"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('vcls-project.object', {
#             'object': obj
#         })