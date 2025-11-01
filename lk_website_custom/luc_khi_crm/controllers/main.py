# -*- coding: utf-8 -*-
from odoo import http, _, fields
from odoo.http import request
from odoo.addons.website.controllers.main import Website
from odoo.addons.website_crm.controllers.main import WebsiteCrm
from odoo.exceptions import ValidationError
import json


class LucKhiCrmController(WebsiteCrm):

    @http.route('/contactus', type='http', auth='public', website=True, methods=['GET'])
    def contactus(self, **kwargs):
        """Override contact page to add Lục Khí elements"""
        response = super(LucKhiCrmController, self).contactus(**kwargs)

        # Add Lục Khí elements for interest selection
        if hasattr(response, 'qcontext'):
            response.qcontext['luc_khi_elements'] = request.env['luc_khi.element'].search([])
            response.qcontext['courses'] = request.env['luc_khi.course'].search([
                ('website_published', '=', True)
            ], limit=10)
            response.qcontext['products'] = request.env['product.template'].search([
                ('website_published', '=', True),
                ('sale_ok', '=', True)
            ], limit=10)

        return response

    @http.route('/website_form/<string:model_name>', type='http', auth='public', methods=['POST'], website=True)
    def website_form(self, model_name, **kwargs):
        """Override website form to handle Lục Khí contact forms"""
        if model_name == 'luc_khi.contact.form':
            return self._handle_luc_khi_contact_form(**kwargs)

        return super(LucKhiCrmController, self).website_form(model_name, **kwargs)

    def _handle_luc_khi_contact_form(self, **kwargs):
        """Handle Lục Khí contact form submission"""
        try:
            # Extract form data
            form_data = {
                'name': kwargs.get('name', '').strip(),
                'email': kwargs.get('email', '').strip(),
                'phone': kwargs.get('phone', '').strip(),
                'preferred_contact_method': kwargs.get('preferred_contact_method', 'phone'),
                'preferred_contact_time': kwargs.get('preferred_contact_time', 'anytime'),
                'contact_reason': kwargs.get('contact_reason', 'general_inquiry'),
                'subject': kwargs.get('subject', '').strip(),
                'message': kwargs.get('message', '').strip(),
                'source': 'website_contact_form',
                'ip_address': request.httprequest.remote_addr,
                'user_agent': request.httprequest.headers.get('User-Agent', ''),
            }

            # Handle many2many fields
            interested_elements = kwargs.get('interested_elements')
            if interested_elements and isinstance(interested_elements, str) and interested_elements.strip():
                element_ids = [int(x) for x in interested_elements.split(',') if x.strip().isdigit()]
                form_data['interested_elements'] = [(6, 0, element_ids)]

            interested_courses = kwargs.get('interested_courses')
            if interested_courses and isinstance(interested_courses, str) and interested_courses.strip():
                course_ids = [int(x) for x in interested_courses.split(',') if x.strip().isdigit()]
                form_data['interested_courses'] = [(6, 0, course_ids)]

            interested_products = kwargs.get('interested_products')
            if interested_products and isinstance(interested_products, str) and interested_products.strip():
                product_ids = [int(x) for x in interested_products.split(',') if x.strip().isdigit()]
                form_data['interested_products'] = [(6, 0, product_ids)]

            # Validate required fields
            required_fields = ['name', 'email', 'phone', 'subject', 'message']
            missing_fields = [field for field in required_fields if not form_data.get(field)]

            if missing_fields:
                return json.dumps({
                    'success': False,
                    'error': f'Vui lòng điền đầy đủ thông tin: {", ".join(missing_fields)}'
                })

            # Create contact form record
            contact_form = request.env['luc_khi.contact.form'].sudo().create(form_data)

            # Send auto-reply email
            contact_form.action_send_auto_reply()

            # Check if should auto-convert to lead based on contact reason
            auto_convert_reasons = ['consultation', 'course_inquiry', 'product_inquiry']
            if form_data['contact_reason'] in auto_convert_reasons:
                try:
                    contact_form.action_convert_to_lead()
                except Exception as e:
                    # Log but don't fail the form submission
                    request.env['ir.logging'].sudo().create({
                        'name': 'Lục Khí CRM Auto-convert',
                        'type': 'server',
                        'level': 'WARNING',
                        'message': f'Auto-convert failed for contact form {contact_form.id}: {str(e)}',
                        'path': 'luc_khi_crm.controllers.main',
                        'func': '_handle_luc_khi_contact_form',
                        'line': '80'
                    })

            return json.dumps({
                'success': True,
                'message': 'Cảm ơn bạn đã liên hệ! Chúng tôi sẽ phản hồi trong vòng 24 giờ.',
                'form_id': contact_form.id
            })

        except ValidationError as e:
            return json.dumps({
                'success': False,
                'error': str(e)
            })
        except Exception as e:
            # Log the error
            request.env['ir.logging'].sudo().create({
                'name': 'Lục Khí CRM Form Error',
                'type': 'server',
                'level': 'ERROR',
                'message': f'Contact form submission failed: {str(e)}',
                'path': 'luc_khi_crm.controllers.main',
                'func': '_handle_luc_khi_contact_form',
                'line': '95'
            })

            return json.dumps({
                'success': False,
                'error': 'Có lỗi xảy ra. Vui lòng thử lại sau.'
            })

    @http.route('/luc-khi/consultation', type='http', auth='public', website=True, methods=['GET'])
    def luc_khi_consultation_form(self, **kwargs):
        """Dedicated Lục Khí consultation booking page"""
        values = {
            'elements': request.env['luc_khi.element'].search([]),
            'consultants': request.env['luc_khi.team.member'].search([
                ('is_consultant', '=', True),
                ('website_published', '=', True)
            ]),
            'available_times': [
                {'value': 'morning', 'label': 'Buổi sáng (8h-12h)'},
                {'value': 'afternoon', 'label': 'Buổi chiều (12h-18h)'},
                {'value': 'evening', 'label': 'Buổi tối (18h-22h)'},
            ]
        }

        return request.render('luc_khi_crm.consultation_form', values)

    @http.route('/luc-khi/consultation/book', type='http', auth='public', website=True, methods=['POST'])
    def book_consultation(self, **kwargs):
        """Handle consultation booking"""
        try:
            booking_data = {
                'name': kwargs.get('name', '').strip(),
                'email': kwargs.get('email', '').strip(),
                'phone': kwargs.get('phone', '').strip(),
                'contact_reason': 'consultation',
                'subject': f'Đăng ký tư vấn Lục Khí - {kwargs.get("name", "")}',
                'message': kwargs.get('consultation_goals', ''),
                'preferred_contact_method': kwargs.get('preferred_method', 'phone'),
                'preferred_contact_time': kwargs.get('preferred_time', 'anytime'),
                'source': 'consultation_booking',
            }

            # Add interested elements
            interested_elements = kwargs.get('interested_elements')
            if interested_elements and isinstance(interested_elements, str) and interested_elements.strip():
                element_ids = [int(x) for x in interested_elements.split(',') if x.strip().isdigit()]
                booking_data['interested_elements'] = [(6, 0, element_ids)]

            # Add preferred consultant
            consultant_id = kwargs.get('consultant_id')
            if consultant_id and isinstance(consultant_id, str) and consultant_id.isdigit():
                booking_data['assigned_to'] = int(consultant_id)

            # Create contact form
            contact_form = request.env['luc_khi.contact.form'].sudo().create(booking_data)

            # Auto-convert to lead
            contact_form.action_convert_to_lead()

            # Send confirmation
            contact_form.action_send_auto_reply()

            return json.dumps({
                'success': True,
                'message': 'Đăng ký tư vấn thành công! Chúng tôi sẽ liên hệ với bạn trong vòng 24 giờ.',
                'booking_id': contact_form.id
            })

        except Exception as e:
            return json.dumps({
                'success': False,
                'error': 'Có lỗi xảy ra khi đăng ký. Vui lòng thử lại.'
            })

    @http.route('/api/luc-khi/contact/stats', type='json', auth='user', website=True)
    def get_contact_stats(self, **kwargs):
        """API endpoint for contact form statistics"""
        user = request.env.user

        # Check permissions
        if not user.has_group('sales_team.group_sale_manager'):
            return {'error': 'Không có quyền truy cập'}

        # Get stats
        stats = {
            'total_forms': request.env['luc_khi.contact.form'].search_count([]),
            'pending_forms': request.env['luc_khi.contact.form'].search_count([('state', '=', 'draft')]),
            'converted_leads': request.env['luc_khi.contact.form'].search_count([('state', '=', 'converted')]),
            'response_rate': 0,  # Calculate based on your business logic
        }

        # Calculate response rate
        total_responded = request.env['luc_khi.contact.form'].search_count([
            ('state', 'in', ['responded', 'closed', 'converted'])
        ])
        if stats['total_forms'] > 0:
            stats['response_rate'] = (total_responded / stats['total_forms']) * 100

        return stats

    @http.route('/api/luc-khi/elements/popular', type='json', auth='public', website=True)
    def get_popular_elements(self, **kwargs):
        """Get popular Lục Khí elements from recent contacts"""
        # Get elements from recent contact forms (last 30 days)
        recent_forms = request.env['luc_khi.contact.form'].search([
            ('create_date', '>=', fields.Datetime.now() - '30 days')
        ])

        element_counts = {}
        for form in recent_forms:
            for element in form.interested_elements:
                element_counts[element.id] = element_counts.get(element.id, 0) + 1

        # Sort by popularity
        popular_elements = sorted(
            element_counts.items(),
            key=lambda x: x[1],
            reverse=True
        )[:5]  # Top 5

        # Get element details
        elements = []
        for element_id, count in popular_elements:
            element = request.env['luc_khi.element'].browse(element_id)
            if element.exists():
                elements.append({
                    'id': element.id,
                    'name': element.name,
                    'code': element.code,
                    'count': count
                })

        return {'popular_elements': elements}