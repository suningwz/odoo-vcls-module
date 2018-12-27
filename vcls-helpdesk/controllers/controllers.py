# -*- coding: utf-8 -*-
from odoo import http

# class Vcls-helpdesk(http.Controller):
#     @http.route('/vcls-helpdesk/vcls-helpdesk/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/vcls-helpdesk/vcls-helpdesk/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('vcls-helpdesk.listing', {
#             'root': '/vcls-helpdesk/vcls-helpdesk',
#             'objects': http.request.env['vcls-helpdesk.vcls-helpdesk'].search([]),
#         })

#     @http.route('/vcls-helpdesk/vcls-helpdesk/objects/<model("vcls-helpdesk.vcls-helpdesk"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('vcls-helpdesk.object', {
#             'object': obj
#         })