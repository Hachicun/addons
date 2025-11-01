# -*- coding: utf-8 -*-
{
    'name': 'Lục Khí CRM',
    'version': '1.0.0',
    'category': 'Website',
    'summary': 'CRM functionality for Lục Khí website with Vietnamese contact forms',
    'description': """
Lục Khí CRM Module
===================
This module provides comprehensive CRM functionality with:
- Vietnamese contact forms with validation
- Lead management with Lục Khí element analysis
- Automated lead scoring based on user interests
- Email notifications in Vietnamese
- Integration with website forms
- Vietnamese address and contact field support
- Lead nurturing workflows
    """,
    'author': 'Lục Khí Team',
    'website': 'https://luc-khi.vn',
    'license': 'LGPL-3',
    'depends': [
        'website_crm',
        'crm',
        'luc_khi_website',
        'mail',
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/luc_khi_crm_lead_views.xml',
        'views/luc_khi_contact_form_views.xml',
        'views/crm_templates.xml',
        'data/crm_data.xml',
    ],
    'assets': {
        'web.assets_frontend': [
            'luc_khi_crm/static/src/js/contact_form.js',
            'luc_khi_crm/static/src/css/contact_form.css',
        ],
    },
    'demo': [],
    'installable': True,
    'auto_install': False,
    'application': False,
    'sequence': 110,
}