{
    "name": "Transaction Webhook",
    "summary": "Receive bank transactions from Casso webhook and create bank statement lines",
    "version": "18.0.1.0.0",
    "category": "Accounting/Banking",
    "author": "Your Company",
    "website": "",
    "license": "AGPL-3",
    "depends": [
        "account",
        "account_statement_base",
        "account_reconcile_oca",
    ],
    "data": [
        "security/ir.model.access.csv",
        "views/casso_bank_map_views.xml",
    ],
    "installable": True,
    "application": False,
}
