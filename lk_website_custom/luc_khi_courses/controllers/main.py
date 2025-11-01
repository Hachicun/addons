# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import request
from odoo.exceptions import AccessError, ValidationError


class LucKhiCourses(http.Controller):
    
    @http.route('/courses', type='http', auth='public', website=True, sitemap=True)
    def courses(self, category=None, level=None, search='', **kwargs):
        """Courses listing page"""
        domain = [('is_published', '=', True)]
        
        # Filter by category
        if category:
            cat_domain = request.env['luc_khi.course.category'].search([('slug', '=', category)])
            if cat_domain:
                domain.append(('category_id', '=', cat_domain.id))
        
        # Filter by level
        if level:
            domain.append(('level', '=', level))
        
        # Search filter
        if search:
            domain.append(('name', 'ilike', search))
        
        courses = request.env['luc_khi.course'].search(domain, order='sequence, name')
        categories = request.env['luc_khi.course.category'].search([('is_published', '=', True)])
        
        return request.render('luc_khi_courses.courses', {
            'courses': courses,
            'categories': categories,
            'current_category': category,
            'current_level': level,
            'search': search,
            'level_options': [
                ('basic', 'Cơ Bản'),
                ('intermediate_1', 'Trung Cấp 1'),
                ('intermediate_2', 'Trung Cấp 2'),
                ('intermediate_3', 'Trung Cấp 3'),
                ('advanced', 'Nâng Cao'),
            ]
        })
    
    @http.route('/course/<string:slug>', type='http', auth='public', website=True, sitemap=True)
    def course_detail(self, slug, **kwargs):
        """Course detail page"""
        course = request.env['luc_khi.course'].search([
            ('slug', '=', slug),
            ('is_published', '=', True)
        ])
        
        if not course:
            return request.not_found()
        
        # Check access rights
        has_access = course.check_access_rights()
        is_enrolled = False
        
        if course.slide_channel_id and request.env.user.partner_id:
            is_enrolled = course.slide_channel_id._check_access(request.env.user.partner_id)
        
        # Get related courses
        related_courses = request.env['luc_khi.course'].search([
            ('category_id', '=', course.category_id.id),
            ('id', '!=', course.id),
            ('is_published', '=', True)
        ], limit=3)
        
        return request.render('luc_khi_courses.course_detail', {
            'course': course,
            'has_access': has_access,
            'is_enrolled': is_enrolled,
            'related_courses': related_courses,
        })
    
    @http.route('/my-courses', type='http', auth='user', website=True, sitemap=True)
    def my_courses(self, **kwargs):
        """Student's enrolled courses"""
        if not request.env.user.partner_id:
            return request.redirect('/web/login')
        
        # Get courses where user has access through slide channels
        slide_channels = request.env['slide.channel'].search([
            ('partner_ids', 'in', [request.env.user.partner_id.id])
        ])
        
        courses = request.env['luc_khi.course'].search([
            ('slide_channel_id', 'in', slide_channels.ids),
            ('is_published', '=', True)
        ])
        
        return request.render('luc_khi_courses.my_courses', {
            'courses': courses,
            'slide_channels': slide_channels,
        })
    
    @http.route('/course/<string:slug>/enroll', type='http', auth='user', website=True, methods=['POST'])
    def enroll_course(self, slug, **kwargs):
        """Enroll in a course"""
        course = request.env['luc_khi.course'].search([
            ('slug', '=', slug),
            ('is_published', '=', True)
        ])
        
        if not course:
            return request.not_found()
        
        try:
            course.action_enroll_student()
            return request.redirect(f'/course/{slug}')
        except Exception as e:
            return request.render('website.http_error', {
                'error_message': str(e)
            })
    
    @http.route('/courses/category/<string:slug>', type='http', auth='public', website=True, sitemap=True)
    def category_courses(self, slug, **kwargs):
        """Courses by category"""
        category = request.env['luc_khi.course.category'].search([
            ('slug', '=', slug),
            ('is_published', '=', True)
        ])
        
        if not category:
            return request.not_found()
        
        courses = request.env['luc_khi.course'].search([
            ('category_id', '=', category.id),
            ('is_published', '=', True)
        ], order='sequence, name')
        
        return request.render('luc_khi_courses.category_courses', {
            'category': category,
            'courses': courses,
        })
    
    @http.route('/api/courses', type='json', auth='public', methods=['GET'])
    def api_courses(self, category=None, level=None, limit=20, offset=0):
        """API endpoint for courses"""
        domain = [('is_published', '=', True)]
        
        if category:
            domain.append(('category_id.slug', '=', category))
        if level:
            domain.append(('level', '=', level))
        
        courses = request.env['luc_khi.course'].search(
            domain, 
            limit=limit, 
            offset=offset,
            order='sequence, name'
        )
        
        result = []
        for course in courses:
            result.append({
                'id': course.id,
                'name': course.name,
                'slug': course.slug,
                'description': course.short_description,
                'level': course.level,
                'price': course.price,
                'image': course.image_1024,
                'category': course.category_id.name if course.category_id else None,
                'student_count': course.student_count,
                'rating': course.rating,
            })
        
        return {
            'courses': result,
            'total': len(result),
        }