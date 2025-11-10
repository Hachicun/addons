{
    "name": "Delivery Custom",
    "version": "18.0.1.15.0",
    "summary": "Extend stock pickings with shipping workflow and fields",
    "category": "Inventory/Delivery",
    "author": "Your Company",
    "website": "https://example.com",
    "license": "LGPL-3",
    "depends": ["stock", "contacts", "account", "web"],
    "data": [
        "security/ir.model.access.csv",
        "views/stock_picking_views.xml",
        "views/stock_picking_tree_views.xml",
        "views/account_move_views.xml",
    ],
    "installable": True,
    "application": False,
}
