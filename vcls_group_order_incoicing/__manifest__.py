# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    'name': 'Sale quote group invoicing',
    'description': "make group invoice for sale order by different granularity",
    'version': '12.0.1.0.0',
    'author': 'Vcls',
    'license': 'AGPL-3',
    'category': 'Others',
    'depends': [
        'sale_timesheet',
        'vcls-project',
        'agreement_sale'
    ],
    'data': [
        'wizard/sale_make_invoice_advance_views.xml',
    ],
    'installable': True,
}