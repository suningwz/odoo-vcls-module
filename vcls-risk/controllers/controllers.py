# -*- coding: utf-8 -*-
from odoo import http

# class Vcls-risk(http.Controller):
#     @http.route('/vcls-risk/vcls-risk/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/vcls-risk/vcls-risk/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('vcls-risk.listing', {
#             'root': '/vcls-risk/vcls-risk',
#             'objects': http.request.env['vcls-risk.vcls-risk'].search([]),
#         })

#     @http.route('/vcls-risk/vcls-risk/objects/<model("vcls-risk.vcls-risk"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('vcls-risk.object', {
#             'object': obj
#         })