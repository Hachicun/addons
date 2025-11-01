from odoo import api, fields, models


class TransactionWebhookBankMap(models.Model):
    _name = "transaction.webhook.bank.map"
    _description = "Transaction Webhook Bank Mapping"
    _rec_name = "external_account_identifier"

    external_account_identifier = fields.Char(
        string="External Account Identifier",
        required=True,
        help="Bank account number or sub account id coming from Casso (accountNumber or bank_sub_acc_id)",
        index=True,
    )
    journal_id = fields.Many2one(
        "account.journal",
        string="Bank Journal",
        domain=[("type", "=", "bank")],
        required=True,
    )
    company_id = fields.Many2one(
        "res.company",
        related="journal_id.company_id",
        store=True,
        readonly=True,
    )
    active = fields.Boolean(default=True)

    _sql_constraints = [
        (
            "uniq_ext_acc_company",
            "unique(external_account_identifier, company_id)",
            "Mapping for this account identifier already exists in this company.",
        )
    ]

