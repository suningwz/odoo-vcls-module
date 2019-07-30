# Copyright 2019 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, fields, api


class CalculatePriceWizard(models.TransientModel):
    _name = 'sale.order.line.prize.wizard'
    _description = 'sale.order.line.prize.wizard'

    so_line_id = fields.Many2one(
        string='So line',
        comodel_name='sale.order.line',
    )

    wizard_line_ids = fields.One2many(
        string='Profiles',
        comodel_name='sale.order.line.prize.wizard.line',
        inverse_name='wizard_id'
    )

    old_price = fields.Monetary(
        'Current Price',
        related='so_line_id.price_subtotal',
        readonly=True,
    )

    currency_id = fields.Many2one(
        'res.currency',
        string='Currency',
        related='so_line_id.currency_id',
        readonly=True
    )
    new_price = fields.Monetary(
        'New Price',
    )

    @api.model
    def default_get(self, fields):
        """Function gets default values."""
        uom_hour = self.env.ref('uom.product_uom_hour')
        res = super().default_get(fields)
        so_line = self.env['sale.order.line'].browse(
            self.env.context['active_id']
        )
        res['so_line_id'] = so_line.id
        task = so_line.task_id
        task_ids = task.ids + task.child_ids.ids
        forecasts = self.env['project.forecast'].search(
            [('task_id', 'in', task_ids)]
        )
        rate_lines = so_line.order_id.get_rate_tasks()
        rates = {}
        res['wizard_line_ids'] = []
        line_model = self.env['sale.order.line.prize.wizard.line']
        suggested_price = 0.0
        for rate_line in rate_lines:
            rates[rate_line.product_id.seniority_level_id.id] = rate_line
        for forecast in forecasts:
            current_rate = rates.get(
                forecast.employee_id.seniority_level_id.id
            )
            if not current_rate:
                continue
            unit_price = current_rate.price_unit
            amount = uom_hour._compute_price(
                unit_price * forecast.resource_hours,
                current_rate.product_uom  # target unit
            )
            suggested_price += amount
            line = line_model.create({
                'name': current_rate.name,
                'price': amount,
                'currency_id': current_rate.currency_id.id,
                'time': forecast.resource_hours,
                'wizard_id': self.id
            })
            res['wizard_line_ids'].append(line.id)
        res['new_price'] = suggested_price
        return res

    @api.multi
    def update_line(self):
        self.so_line_id.write({
            'price_unit': self.new_price,
            'amount': 1.0,
        })
        return {'type': 'ir.actions.act_window_close'}


class CalculatePriceWizardLine(models.TransientModel):
    _name = 'sale.order.line.prize.wizard.line'
    _description = 'sale.order.line.prize.wizard.line'

    name = fields.Char("Name")

    price = fields.Monetary("Price")

    currency_id = fields.Many2one(
        'res.currency',
        string='Currency'
    )

    time = fields.Float("Time (h)")

    wizard_id = fields.Many2one(
        string='Wizard',
        comodel_name='sale.order.line.prize.wizard'
    )
