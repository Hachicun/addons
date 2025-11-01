# -*- coding: utf-8 -*-
{
    'name': 'Lục Khí Shop',
    'version': '1.0.0',
    'category': 'Website',
    'summary': 'E-commerce functionality for Lục Khí website',
    'description': """
E-commerce Module for Lục Khí Website
====================================
This module provides comprehensive e-commerce functionality with:
- Vietnamese product catalog
- Shopping cart and checkout
- Vietnamese payment gateway integration
- Order management and tracking
- Product recommendations based on Lục Khí
- Vietnamese tax compliance
- Mobile-responsive design
    """,
    'author': 'Lục Khí Team',
    'website': 'https://luc-khi.vn',
    'license': 'LGPL-3',
    'depends': [
        'website_sale',
        'luc_khi_website',
        'luc_khi_courses',
        'luc_khi_blog',
        'sale_management',
        'account',
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/product_views.xml',
        'views/order_views.xml',
        'views/luc_khi_product_category_views.xml',
        'views/luc_khi_product_views.xml',
        'views/luc_khi_order_views.xml',
        'views/templates.xml',
        'data/shop_data.xml',
    ],
    'demo': [],
    'installable': True,
    'auto_install': False,
    'application': False,
    'sequence': 100,
}