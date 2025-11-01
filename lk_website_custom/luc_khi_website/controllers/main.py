# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import request
from odoo.addons.website.controllers.main import Website


class LucKhiWebsite(Website):
    
    @http.route('/', type='http', auth='public', website=True, sitemap=True)
    def index(self, **kwargs):
        """Homepage controller"""
        # Get featured content
        featured_courses = request.env['luc_khi.course'].search([
            ('is_published', '=', True),
            ('featured', '=', True)
        ], limit=3) if request.env['ir.module.module'].search([('name', '=', 'luc_khi_courses'), ('state', '=', 'installed')]) else []
        
        latest_posts = request.env['blog.post'].search([
            ('website_published', '=', True)
        ], order='post_date desc', limit=3) if request.env['ir.module.module'].search([('name', '=', 'luc_khi_blog'), ('state', '=', 'installed')]) else []
        
        featured_products = request.env['product.template'].search([
            ('website_published', '=', True),
            ('sale_ok', '=', True)
        ], limit=3) if request.env['ir.module.module'].search([('name', '=', 'luc_khi_shop'), ('state', '=', 'installed')]) else []
        
        return request.render('luc_khi_website.homepage', {
            'featured_courses': featured_courses,
            'latest_posts': latest_posts,
            'featured_products': featured_products,
        })
    
    @http.route('/about', type='http', auth='public', website=True, sitemap=True)
    def about(self, **kwargs):
        """About page controller"""
        team_members = request.env['luc_khi.team.member'].search([
            ('is_published', '=', True)
        ], order='sequence, name')
        
        return request.render('luc_khi_website.about', {
            'team_members': team_members,
        })
    
    @http.route('/contact', type='http', auth='public', website=True, sitemap=True, methods=['GET', 'POST'])
    def contact(self, **kwargs):
        """Contact page controller"""
        if request.httprequest.method == 'POST':
            # Process contact form submission
            contact_name = request.params.get('name')
            contact_email = request.params.get('email')
            contact_phone = request.params.get('phone')
            contact_message = request.params.get('message')
            
            if contact_name and contact_email and contact_message:
                # Create CRM lead if CRM module is installed
                if request.env['ir.module.module'].search([('name', '=', 'luc_khi_crm'), ('state', '=', 'installed')]):
                    request.env['crm.lead'].create({
                        'name': f'Contact Form: {contact_name}',
                        'contact_name': contact_name,
                        'email_from': contact_email,
                        'phone': contact_phone,
                        'description': contact_message,
                        'lead_type': 'general_info',
                        'source_page': '/contact',
                    })
                
                return request.render('website.contactus_thanks')
        
        return request.render('luc_khi_website.contact', {})
    
    @http.route('/page/<string:page_key>', type='http', auth='public', website=True, sitemap=True)
    def custom_page(self, page_key, **kwargs):
        """Custom page controller"""
        page = request.env['luc_khi.website.page'].search([
            ('page_key', '=', page_key),
            ('is_published', '=', True)
        ])
        
        if not page:
            return request.not_found()
        
        return request.render('luc_khi_website.custom_page', {
            'page': page,
        })
    
    @http.route('/team/<int:member_id>', type='http', auth='public', website=True, sitemap=True)
    def team_member(self, member_id, **kwargs):
        """Team member profile controller"""
        member = request.env['luc_khi.team.member'].search([
            ('id', '=', member_id),
            ('is_published', '=', True)
        ])
        
        if not member:
            return request.not_found()
        
        return request.render('luc_khi_website.team_member', {
            'member': member,
        })