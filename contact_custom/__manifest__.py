{
    "name": "Contact Custom - Related Contacts",
    "version": "18.0.1.1.6",
    "summary": "Add related contacts tab with relationship type",
    "category": "Contacts",
    "author": "Your Company",
    "depends": ["base", "contacts", "sale_management", "account", "stock", "purchase"],
    "data": [
        "security/ir.model.access.csv",
        "views/res_partner_views.xml",
        "views/res_partner_relation_views.xml",
    ],
    "installable": True,
    "application": False,
}
