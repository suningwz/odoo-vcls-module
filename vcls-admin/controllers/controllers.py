# -*- coding: utf-8 -*-
from odoo import http

# class Vcls-admin(http.Controller):
#     @http.route('/vcls-admin/vcls-admin/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/vcls-admin/vcls-admin/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('vcls-admin.listing', {
#             'root': '/vcls-admin/vcls-admin',
#             'objects': http.request.env['vcls-admin.vcls-admin'].search([]),
#         })

#     @http.route('/vcls-admin/vcls-admin/objects/<model("vcls-admin.vcls-admin"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('vcls-admin.object', {
#             'object': obj
#         })