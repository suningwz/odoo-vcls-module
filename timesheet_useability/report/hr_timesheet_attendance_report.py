# Copyright 2019 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models, tools


class TimesheetAttendance(models.Model):
    _inherit = 'hr.timesheet.attendance.report'

    employee_id = fields.Many2one('hr.employee')

    @api.model_cr
    def init(self):
        """Copy of the original view to add 'employee_id' field"""
        tools.drop_view_if_exists(self.env.cr, self._table)
        self._cr.execute(
            """CREATE OR REPLACE VIEW %s AS (
            SELECT
                max(id) AS id,
                t.user_id,
                t.date,
                coalesce(sum(t.attendance), 0) AS total_attendance,
                coalesce(sum(t.timesheet), 0) AS total_timesheet,
                coalesce(sum(t.attendance), 0) -
                    coalesce(sum(t.timesheet), 0) as total_difference,
                employee_id
            FROM (
                SELECT
                    -hr_attendance.id AS id,
                    resource_resource.user_id AS user_id,
                    hr_attendance.worked_hours AS attendance,
                    NULL AS timesheet,
                    date_trunc('day', hr_attendance.check_in) AS date,
                    hr_employee.id AS employee_id
                FROM hr_attendance
                LEFT JOIN hr_employee
                    ON hr_employee.id = hr_attendance.employee_id
                LEFT JOIN resource_resource
                    ON resource_resource.id = hr_employee.resource_id
                UNION ALL
                    SELECT
                        ts.id AS id,
                        ts.user_id AS user_id,
                        NULL AS attendance,
                        ts.unit_amount AS timesheet,
                        date_trunc('day', ts.date) AS date,
                        ts.employee_id
                    FROM account_analytic_line AS ts
                    WHERE ts.project_id IS NOT NULL
            ) AS t
            GROUP BY t.user_id, t.date, t.employee_id
            ORDER BY t.date
        )
        """
            % self._table
        )
