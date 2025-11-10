from odoo import fields, models


class MrpProduction(models.Model):
    _inherit = "mrp.production"

    formula = fields.Text(
        string="Formula",
        help="Formula or instructions for manufacturing this product",
    )

