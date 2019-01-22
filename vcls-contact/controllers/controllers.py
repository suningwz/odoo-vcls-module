# -*- coding: utf-8 -*-
from odoo import http

# class Vcls-contact(http.Controller):
#     @http.route('/vcls-contact/vcls-contact/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/vcls-contact/vcls-contact/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('vcls-contact.listing', {
#             'root': '/vcls-contact/vcls-contact',
#             'objects': http.request.env['vcls-contact.vcls-contact'].search([]),
#         })

#     @http.route('/vcls-contact/vcls-contact/objects/<model("vcls-contact.vcls-contact"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('vcls-contact.object', {
#             'object': obj
#         })