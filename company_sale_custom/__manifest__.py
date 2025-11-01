{
    "name": "Company Sale Custom",
    "summary": "Customize sale order list view for company specific needs.",
    "version": "18.0.1.1.0",
    "category": "Sales/Sales",
    "author": "Your Company",
    "maintainers": [],
    "website": "https://example.com",
    "license": "LGPL-3",
    "depends": [
        "sale_management",
        "sale_stock",
        "account",          # needed to read invoice payment_state
        "delivery_custom",  # show extra delivery info on the Delivery tab
        "mrp",              # manufacturing tab
        "contact_custom",   # related contacts and related invoices on partner
    ],
    "data": [
        "views/sale_order_views.xml",
    ],
    "installable": True,
    "application": False,
    "auto_install": False,
}
