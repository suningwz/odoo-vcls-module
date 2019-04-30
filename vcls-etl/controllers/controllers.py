# -*- coding: utf-8 -*-
from odoo import http

# class Vcls-etl(http.Controller):
#     @http.route('/vcls-etl/vcls-etl/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/vcls-etl/vcls-etl/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('vcls-etl.listing', {
#             'root': '/vcls-etl/vcls-etl',
#             'objects': http.request.env['vcls-etl.vcls-etl'].search([]),
#         })

#     @http.route('/vcls-etl/vcls-etl/objects/<model("vcls-etl.vcls-etl"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('vcls-etl.object', {
#             'object': obj
#         })