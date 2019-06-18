# -*- coding: utf-8 -*-
from odoo import http

# class Vcls-timesheet(http.Controller):
#     @http.route('/vcls-timesheet/vcls-timesheet/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/vcls-timesheet/vcls-timesheet/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('vcls-timesheet.listing', {
#             'root': '/vcls-timesheet/vcls-timesheet',
#             'objects': http.request.env['vcls-timesheet.vcls-timesheet'].search([]),
#         })

#     @http.route('/vcls-timesheet/vcls-timesheet/objects/<model("vcls-timesheet.vcls-timesheet"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('vcls-timesheet.object', {
#             'object': obj
#         })