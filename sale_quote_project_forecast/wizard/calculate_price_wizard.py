from odoo import models, fields, api


class CalculatePriceWizard(models.TransientModel):
    _name = 'sale.order.line.prize.wizard'

    so_line_id = fields.Many2one(
        string='so_line',
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
    )

    currency_id = fields.Many2one(
        'res.currency',
        related='so_line_id.currency_id'
    )
    new_price = fields.Monetary(
        'New Price',
    )

    @api.model
    def default_get(self, fields):
        """Function gets default values."""
        res = super(CalculatePriceWizard, self).default_get(fields)
        so_line = self.env['sale.order.line'].browse(
            self.env.context['active_id']
        )
        res['so_line_id'] = so_line.id
        task = so_line.task_id
        task_ids = task.ids + task.child_ids.ids
        forecasts = self.env['project.forecast'].search(
            [('task_id', 'in', task_ids)]
        )
        rate_products = so_line.order_id.get_rate_tasks()
        rates = {}
        res['wizard_line_ids'] = []
        line_model = self.env['sale.order.line.prize.wizard.line']
        suggested_price = 0.0
        for rate_product in rate_products:
            rates[rate_product.product_id.seniority_level_id.id] = rate_product
        for forecast in forecasts:
            current_rate = rates[forecast.employee_id.seniority_level_id.id]
            per_hour = current_rate.price_unit
            amount = per_hour * forecast.resource_hours
            suggested_price += amount
            res['wizard_line_ids'].append(line_model.create({
                'name': current_rate.name,
                'price': amount,
                'currency_id': current_rate.currency_id.id,
                'time': forecast.resource_hours,
                'wizard_id': self.id
            }).id)
        res['new_price'] = suggested_price
        return res

    @api.multi
    def update_line(self):
        self.so_line_id.price_unit = self.new_price
        self.so_line_id.amount = 1.0
        return {'type': 'ir.actions.act_window_close'}


class CalculatePriceWizardLine(models.TransientModel):
    _name = 'sale.order.line.prize.wizard.line'

    name = fields.Char("Name")

    price = fields.Monetary("Price")

    currency_id = fields.Many2one(
        'res.currency'
    )

    time = fields.Float("Time (h)")

    wizard_id = fields.Many2one(
        string='Wizard',
        comodel_name='sale.order.line.prize.wizard'
    )
