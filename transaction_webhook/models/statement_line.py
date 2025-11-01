from odoo import fields, models


class AccountBankStatementLine(models.Model):
    _inherit = "account.bank.statement.line"

    x_tw_source = fields.Selection(
        selection=[("casso", "Casso")],
        string="Webhook Source",
        help="Source of the webhook transaction",
        copy=False,
    )
    x_tw_tid = fields.Char(
        string="Webhook TID",
        index=True,
        copy=False,
        help="Unique transaction id from webhook provider (reference|tid)",
    )
    x_tw_account_identifier = fields.Char(
        string="Webhook Account Identifier",
        index=True,
        copy=False,
        help="Account number or sub account id used to route to journal",
    )
    x_tw_bank_abbreviation = fields.Char(string="Bank Abbreviation", copy=False)
    x_tw_bank_name = fields.Char(string="Bank Name", copy=False)
    x_tw_counter_account = fields.Char(string="Counter Account", copy=False)
    x_tw_virtual_account = fields.Char(string="Virtual Account", copy=False)
    x_tw_account_number = fields.Char(string="Account Number", copy=False)
    x_tw_bank_sub_acc_id = fields.Char(string="Bank Sub Account ID", copy=False)
    x_tw_casso_id = fields.Char(string="Casso Transaction ID", index=True, copy=False,
                                 help="Unique Casso transaction id (Webhook V2 'id')")

    _sql_constraints = [
        (
            "uniq_tw_casso_id",
            "unique(x_tw_casso_id)",
            "A bank statement line with this Casso ID already exists.",
        )
    ]
