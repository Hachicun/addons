from odoo import fields, models


class ResCompany(models.Model):
    _inherit = "res.company"

    company_code = fields.Char(
        string="Internal Company Code",
        help="Short code used for integrations and reporting.",
    )
