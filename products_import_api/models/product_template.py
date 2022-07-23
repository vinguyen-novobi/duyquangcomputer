from odoo import fields, models

class ProductTemplate(models.Model):
    _inherit = 'product.template'

    purchase_ok = fields.Boolean('Can be Purchased', default=False)