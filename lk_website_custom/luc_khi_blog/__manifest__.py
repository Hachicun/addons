# -*- coding: utf-8 -*-
{
    'name': 'Lục Khí Blog',
    'version': '1.0.0',
    'category': 'Website',
    'summary': 'Enhanced blog functionality for Lục Khí website',
    'description': """
Enhanced Blog Module for Lục Khí Website
========================================
This module provides enhanced blog functionality with:
- Vietnamese blog categories
- SEO optimization
- Blog-course cross-linking
- Enhanced templates
- Vietnamese language support
    """,
    'author': 'Lục Khí Team',
    'website': 'https://luc-khi.vn',
    'license': 'LGPL-3',
    'depends': [
        'website_blog',
        'luc_khi_website',
        'luc_khi_courses',
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/luc_khi_blog_category_views.xml',
        'views/luc_khi_blog_post_views.xml',
        'views/templates.xml',
        'data/blog_data.xml',
    ],
    'demo': [],
    'installable': True,
    'auto_install': False,
    'application': False,
    'sequence': 100,
}