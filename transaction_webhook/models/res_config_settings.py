from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    casso_webhook_token = fields.Char(
        string="Casso Webhook Token",
        config_parameter="transaction_webhook.casso_webhook_token",
        help="Shared secret token to validate webhook requests",
    )
    casso_statement_grouping = fields.Selection(
        [
            ("by_day", "Group statement lines by day"),
            ("single_open", "Single open statement"),
        ],
        string="Statement Grouping",
        default="by_day",
        config_parameter="transaction_webhook.statement_grouping",
        help="Currently informational; lines are attached to journal and can be grouped by Odoo views.",
    )

