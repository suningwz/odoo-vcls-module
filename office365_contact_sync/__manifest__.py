# -*- coding: utf-8 -*-
# Odoo Proprietary License v1.0
#
# This software and associated files (the "Software") may only be used (executed, modified,
# executed after modifications) if you have purchased a valid license from the authors, typically
# via Odoo Apps, or if you have received a written agreement from the authors of the Software (see
# the COPYRIGHT file).
#
# You may develop Odoo modules that use the Software as a library (typically by depending on it,
# importing it and using its resources), but without copying any source code or material from the
# Software. You may distribute those modules under the license of your choice, provided that this
# license is compatible with the terms of the Odoo Proprietary License (For example: LGPL, MIT, or
# proprietary licenses similar to this one).
#
# It is forbidden to publish, distribute, sublicense, or sell copies of the Software or modified
# copies of the Software.
#
# The above copyright notice and this permission notice must be included in all copies or
# substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING
# BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
# NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM,
# DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
{
    'name': 'Office 365 Contact Sync',
    'version': '12.0.1.0',
    'author': 'Somko',
    'category': 'Productivity',
    'description': """Handles the synchronisation of Outlook and Odoo contacts.""",
    'summary': """Sync Outlook and Odoo contacts""",
    'website': 'https://www.somko.be',
    'images': ['static/description/cover.png',],
    'license': "OPL-1",
    'depends': ['base', 'office365_framework'],
    'data': [
        'views/res_users.xml',
        'views/res_partner_filter.xml',
        'views/res_partner_view.xml',

        'views/res_config_settings.xml',

        'security/ir.model.access.csv',

        'data/res_partner_filter.xml',
    ],
    'qweb': [],
    'demo': [],
    'test': [],
    "auto_install": False,
    'application': False,
    "installable": True,
    "price": 499,
    "currency": "EUR",
}