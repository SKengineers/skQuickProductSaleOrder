from odoo import api, fields, models, SUPERUSER_ID, _
from odoo.exceptions import AccessError, UserError, ValidationError


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    def action_open_wizard_quick_product(self):
        return self.env.ref('sk_quick_product_sale_order.wizard_action_quick_product').read()[0]