from datetime import datetime

from odoo import _, api, fields, models
from odoo.exceptions import UserError


class TransactionWebhookService(models.AbstractModel):
    _name = "transaction.webhook.service"
    _description = "Transaction Webhook Service"

    # Public API used by controller
    def process_casso_payload(self, tx: dict):
        """Process a single Casso Webhook V2 transaction payload and return (line, created).

        - Supports Webhook V2 fields: id, reference, description, amount, transactionDateTime,
          accountNumber, bankName, bankAbbreviation, counterAccountNumber, virtualAccountNumber, ...
        - Idempotent: if line exists (by Casso id) return it with created=False
        """
        self = self.sudo()
        tx = dict(tx or {})

        # V2 Casso transaction id (integer or string)
        casso_id = tx.get("id")
        if casso_id is None:
            raise UserError(_("Missing Casso transaction id (data.id)"))
        casso_id = str(casso_id)

        description = tx.get("description") or ""
        amount = tx.get("amount")
        if amount is None:
            raise UserError(_("Missing amount"))

        # Date/time
        when = tx.get("transactionDateTime")
        date = self._normalize_date(when)

        # Account identifier
        account_number = tx.get("accountNumber")
        bank_sub_acc_id = tx.get("bank_sub_acc_id")
        account_identifier = account_number or bank_sub_acc_id
        if not account_identifier:
            raise UserError(_("Missing account identifier (accountNumber)"))
        account_identifier = str(account_identifier).strip()

        bank_abbrev = tx.get("bankAbbreviation")
        bank_name = tx.get("bankName")
        counter_account = tx.get("counterAccountNumber") or tx.get("corresponsiveAccount") or tx.get("corresponsiveAccountNumber")
        virtual_account = tx.get("virtualAccountNumber") or tx.get("virtualAccount") or ""
        reference = tx.get("reference") or ""

        # Resolve journal (by mapping first, then fallback to journal bank account)
        journal = self._resolve_journal(account_identifier)
        if not journal:
            # Fallback to configured default journal id
            default_journal_id = (
                self.env["ir.config_parameter"]
                .sudo()
                .get_param("transaction_webhook.default_journal_id")
            )
            if default_journal_id:
                journal = self.env["account.journal"].browse(int(default_journal_id))
                if journal and journal.type != "bank":
                    raise UserError(
                        _("Configured default journal must be of type 'bank'.")
                    )
            if not journal:
                raise UserError(
                    _(
                        "Cannot resolve bank journal. Set system parameter 'transaction_webhook.default_journal_id' to a Bank journal ID."
                    )
                )

        # Idempotency: find existing line by Casso id
        existing = self.env["account.bank.statement.line"].search(
            [("x_tw_casso_id", "=", casso_id)], limit=1
        )
        if existing:
            return existing, False

        # Create bank statement line (attach to journal; statement assignment handled by Odoo)
        vals = {
            "journal_id": journal.id,
            "date": date,
            "payment_ref": description or reference or casso_id,
            "amount": float(amount),
            # Webhook metadata
            "x_tw_source": "casso",
            "x_tw_tid": reference or False,
            "x_tw_casso_id": casso_id,
            "x_tw_account_identifier": account_identifier,
            "x_tw_bank_abbreviation": bank_abbrev,
            "x_tw_bank_name": bank_name,
            "x_tw_counter_account": counter_account,
            "x_tw_virtual_account": virtual_account,
            "x_tw_account_number": account_number,
            "x_tw_bank_sub_acc_id": bank_sub_acc_id,
        }
        line = self.env["account.bank.statement.line"].create(vals)
        return line, True

    # Helpers
    def _resolve_journal(self, account_identifier: str):
        Map = self.env["transaction.webhook.bank.map"]
        # Try company of env first, then any
        mapping = Map.search(
            [
                ("external_account_identifier", "=", account_identifier),
                ("active", "=", True),
                ("company_id", "=", self.env.company.id),
            ],
            limit=1,
        )
        if not mapping:
            mapping = Map.search(
                [
                    ("external_account_identifier", "=", account_identifier),
                    ("active", "=", True),
                ],
                limit=1,
            )
        if mapping:
            return mapping.journal_id

        # Fallback: find bank journal with matching bank account number
        Journal = self.env["account.journal"]
        journal = Journal.search(
            [
                ("type", "=", "bank"),
                ("bank_account_id.acc_number", "=", account_identifier),
            ],
            limit=1,
        )
        return journal

    @api.model
    def _normalize_date(self, dt_str):
        """Return a date string (YYYY-MM-DD) from various datetime formats.
        Default fallback to today if missing or unparsable.
        """
        if not dt_str:
            return fields.Date.context_today(self)
        # Try common formats: "YYYY-MM-DD HH:MM:SS" or ISO
        try:
            # Replace T separator if present
            s = str(dt_str).replace("T", " ").strip()
            # Trim timezone if present (keep local naive)
            if "+" in s:
                s = s.split("+")[0].strip()
            if "Z" in s:
                s = s.replace("Z", "").strip()
            dt = datetime.strptime(s, "%Y-%m-%d %H:%M:%S")
            return dt.date()
        except Exception:
            try:
                # Try ISO format
                dt = fields.Datetime.to_datetime(dt_str)
                return dt.date()
            except Exception:
                return fields.Date.context_today(self)
