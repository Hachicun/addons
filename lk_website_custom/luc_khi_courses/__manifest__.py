# -*- coding: utf-8 -*-
{
    'name': 'Lục Khí Courses',
    'version': '18.0.1.0.0',
    'category': 'Website/E-learning',
    'summary': 'E-learning platform for Lục Khí courses',
    'description': """
Lục Khí Courses Module
=====================

This module provides comprehensive e-learning functionality for Lục Khí platform including:
- Course management with Vietnamese content support
- Course categories and tagging system
- Integration with website_slides for video content
- Course access control and enrollment
- Vietnamese-friendly URL slugs
- SEO optimization for courses
- Student progress tracking
    """,
    'author': 'Lục Khí Team',
    'website': 'https://luckhi.vn',
    'license': 'LGPL-3',
    'depends': [
        'website',
        'website_slides',
        'luc_khi_website',
        'sale',
        'auth_signup',
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/luc_khi_course_views.xml',
        'views/luc_khi_course_category_views.xml',
        'views/luc_khi_course_tag_views.xml',
        'views/templates.xml',
        'data/course_data.xml',
    ],
    'demo': [
    ],
    'installable': True,
    'auto_install': False,
    'application': False,
    'sequence': 110,
    'images': ['static/description/banner.png'],
}