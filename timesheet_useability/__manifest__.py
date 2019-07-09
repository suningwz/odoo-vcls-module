# Copyright 2019 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)
{
    "name": "Timesheet Useability",
    "summary": "Changes in UI for better useability",
    "version": "12.0.1.0.0",
    "category": "Timesheet",
    "website": "https://github.com/camptocamp/odoo-enterprise-addons",
    "author": "Camptocamp",
    "license": "AGPL-3",
    "depends": [
        "sale_timesheet",
        "hr_timesheet_attendance",
    ],
    "data": [
        "views/account_analytic_line.xml",
        "views/hr_timesheet_attendance.xml",
    ],
    "installable": True,
    "auto-install": True,
}
