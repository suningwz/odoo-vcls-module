from odoo import tools
from odoo import api, fields, models


class TimesheetForecastReport(models.Model):

    _name = "timesheet.report"
    _description = "Timesheet Reports"
    _auto=False

    # NEEDED FIELDS

    name = fields.Char(string = 'External Comment', readonly = True)
    project_id = fields.Many2one('project.project', string = 'Project', readonly = True)
    task_id = fields.Many2one('project.task', string = 'Task', readonly = True)
    unit_amount = fields.Float('Duration (Hour(s))', readonly = True)
    date = fields.Date('Date', readonly = True)
    employee_id = fields.Many2one('hr.employee', readonly = True)

    # END OF NEEDED FIELDS

    # SQL REQUEST
    @api.model_cr
    def init(self):
        tools.drop_view_if_exists(self.env.cr, self._table)
        self.env.cr.execute("""
            CREATE or REPLACE VIEW %s as (
                (
                    SELECT
                        A.name AS name,
                        A.project_id AS project_id,
                        A.task_id AS task_id,
                        A.unit_amount AS unit_amount,
                        A.date AS date,
                        A.employee_id AS employee_id,
                        A.id AS id
                    FROM account_analytic_line A
                )
            )
        """ % (self._table,))