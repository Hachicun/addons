# -*- coding: utf-8 -*-
{
    'name': 'Lục Khí Website',
    'version': '18.0.1.0.0',
    'category': 'Website',
    'summary': 'Core website functionality for Lục Khí platform',
    'description': """
Lục Khí Website Module
======================

This module provides the core website functionality for Lục Khí platform including:
- Homepage with banner and featured content
- About page with team information
- Contact page with CRM integration
- Vietnamese language support
- SEO optimization
    """,
    'author': 'Lục Khí Team',
    'website': 'https://luckhi.vn',
    'license': 'LGPL-3',
    'depends': [
        'website',
        'website_crm',
        'base',
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/luc_khi_website_page_views.xml',
        'views/luc_khi_team_member_views.xml',
        'views/menus.xml',
        'views/templates.xml',
        'data/website_data.xml',
    ],
    'demo': [
    ],
    'installable': True,
    'auto_install': False,
    'application': False,
    'sequence': 100,
    'images': ['static/description/banner.png'],
}