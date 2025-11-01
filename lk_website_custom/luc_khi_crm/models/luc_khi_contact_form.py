# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
import re


class LucKhiContactForm(models.Model):
    _name = 'luc_khi.contact.form'
    _description = 'Lục Khí Contact Form'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    # Basic Contact Information
    name = fields.Char(
        string='Họ và tên',
        required=True,
        help='Họ và tên đầy đủ của người liên hệ'
    )

    email = fields.Char(
        string='Email',
        required=True,
        help='Địa chỉ email để liên hệ'
    )

    phone = fields.Char(
        string='Số điện thoại',
        required=True,
        help='Số điện thoại di động hoặc cố định'
    )

    # Contact Preferences
    preferred_contact_method = fields.Selection([
        ('phone', 'Điện thoại'),
        ('email', 'Email'),
        ('zalo', 'Zalo'),
        ('facebook', 'Facebook')
    ], string='Phương thức liên lạc ưa thích', default='phone')

    preferred_contact_time = fields.Selection([
        ('morning', 'Buổi sáng (8h-12h)'),
        ('afternoon', 'Buổi chiều (12h-18h)'),
        ('evening', 'Buổi tối (18h-22h)'),
        ('anytime', 'Bất kỳ lúc nào')
    ], string='Thời gian liên lạc ưa thích', default='anytime')

    # Contact Reason and Details
    contact_reason = fields.Selection([
        ('general_inquiry', 'Thắc mắc chung'),
        ('course_inquiry', 'Hỏi về khóa học'),
        ('product_inquiry', 'Hỏi về sản phẩm'),
        ('consultation', 'Đăng ký tư vấn'),
        ('partnership', 'Hợp tác kinh doanh'),
        ('support', 'Hỗ trợ kỹ thuật'),
        ('complaint', 'Khiếu nại'),
        ('other', 'Khác')
    ], string='Lý do liên hệ', required=True, default='general_inquiry')

    subject = fields.Char(
        string='Tiêu đề',
        required=True,
        help='Tiêu đề ngắn gọn về nội dung liên hệ'
    )

    message = fields.Text(
        string='Nội dung tin nhắn',
        required=True,
        help='Chi tiết nội dung cần liên hệ'
    )

    # Lục Khí Specific Interests
    interested_elements = fields.Many2many(
        'luc_khi.element',
        string='Ngũ hành quan tâm',
        help='Các ngũ hành mà người liên hệ quan tâm'
    )

    interested_courses = fields.Many2many(
        'luc_khi.course',
        string='Khóa học quan tâm',
        help='Các khóa học mà người liên hệ muốn biết thêm'
    )

    interested_products = fields.Many2many(
        'product.template',
        string='Sản phẩm quan tâm',
        help='Các sản phẩm mà người liên hệ muốn biết thêm'
    )

    # Status and Processing
    state = fields.Selection([
        ('draft', 'Chưa xử lý'),
        ('in_progress', 'Đang xử lý'),
        ('responded', 'Đã phản hồi'),
        ('closed', 'Đã đóng'),
        ('converted', 'Đã chuyển thành lead')
    ], string='Trạng thái', default='draft', tracking=True)

    priority = fields.Selection([
        ('low', 'Thấp'),
        ('medium', 'Trung bình'),
        ('high', 'Cao'),
        ('urgent', 'Khẩn cấp')
    ], string='Mức độ ưu tiên', default='medium')

    # Processing Information
    assigned_to = fields.Many2one(
        'res.users',
        string='Phụ trách',
        help='Người phụ trách xử lý liên hệ này'
    )

    response_date = fields.Datetime(
        string='Thời gian phản hồi',
        help='Thời gian phản hồi đầu tiên'
    )

    resolution_date = fields.Datetime(
        string='Thời gian giải quyết',
        help='Thời gian giải quyết hoàn toàn'
    )

    # Related Records
    lead_id = fields.Many2one(
        'crm.lead',
        string='Lead liên quan',
        help='Lead được tạo từ form liên hệ này'
    )

    partner_id = fields.Many2one(
        'res.partner',
        string='Đối tác',
        help='Đối tác liên quan (nếu có)'
    )

    # Additional Information
    source = fields.Char(
        string='Nguồn',
        help='Nguồn gốc của form liên hệ (website, landing page, etc.)'
    )

    ip_address = fields.Char(
        string='Địa chỉ IP',
        help='Địa chỉ IP của người gửi form'
    )

    user_agent = fields.Text(
        string='User Agent',
        help='Thông tin trình duyệt của người gửi'
    )

    # Validation constraints
    @api.constrains('email')
    def _check_email(self):
        """Validate email format"""
        email_pattern = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')

        for form in self:
            if form.email and not email_pattern.match(form.email):
                raise ValidationError(_('Địa chỉ email không hợp lệ.'))

    @api.constrains('phone')
    def _check_phone(self):
        """Validate Vietnamese phone number"""
        vietnamese_phone_pattern = re.compile(r'^(0|\+84)[3|5|7|8|9][0-9]{8}$')

        for form in self:
            if form.phone and not vietnamese_phone_pattern.match(form.phone.replace(' ', '')):
                raise ValidationError(_('Số điện thoại không hợp lệ. Vui lòng nhập số điện thoại Việt Nam hợp lệ.'))

    @api.model
    def create(self, vals):
        """Override create to set default values and auto-assign"""
        if 'source' not in vals:
            vals['source'] = 'website'

        # Auto-assign based on contact reason
        if 'assigned_to' not in vals and vals.get('contact_reason'):
            vals['assigned_to'] = self._auto_assign_user(vals['contact_reason'])

        return super(LucKhiContactForm, self).create(vals)

    def _auto_assign_user(self, contact_reason):
        """Auto-assign user based on contact reason"""
        # This could be enhanced with more sophisticated assignment logic
        user_mapping = {
            'course_inquiry': 'sales_team.group_sale_salesman',  # Sales team
            'product_inquiry': 'sales_team.group_sale_salesman',  # Sales team
            'consultation': 'sales_team.group_sale_manager',     # Sales manager
            'partnership': 'base.group_system',                  # Admin
            'support': 'base.group_user',                        # Support team
            'complaint': 'base.group_system',                    # Admin
        }

        group_xml_id = user_mapping.get(contact_reason)
        if group_xml_id:
            group = self.env.ref(group_xml_id, raise_if_not_found=False)
            if group:
                users = self.env['res.users'].search([
                    ('groups_id', 'in', group.id),
                    ('active', '=', True)
                ], limit=1)
                if users:
                    return users.id

        return False

    def action_assign_to_me(self):
        """Assign the form to current user"""
        self.ensure_one()
        self.write({
            'assigned_to': self.env.user.id,
            'state': 'in_progress'
        })

    def action_mark_responded(self):
        """Mark as responded"""
        self.ensure_one()
        self.write({
            'state': 'responded',
            'response_date': fields.Datetime.now()
        })

    def action_close(self):
        """Close the contact form"""
        self.ensure_one()
        self.write({
            'state': 'closed',
            'resolution_date': fields.Datetime.now()
        })

    def action_convert_to_lead(self):
        """Convert contact form to CRM lead"""
        self.ensure_one()

        if self.lead_id:
            raise ValidationError(_('Form này đã được chuyển thành lead.'))

        # Create lead from contact form
        lead_vals = {
            'name': self.subject,
            'contact_name': self.name,
            'email_from': self.email,
            'phone': self.phone,
            'description': self.message,
            'type': 'lead',
            'source_id': self.env.ref('utm.utm_source_website', raise_if_not_found=False).id,
            'medium_id': self.env.ref('utm.utm_medium_website', raise_if_not_found=False).id,
            # Lục Khí specific fields
            'full_name_vietnamese': self.name,
            'phone_mobile': self.phone,
            'preferred_contact_method': self.preferred_contact_method,
            'preferred_contact_time': self.preferred_contact_time,
            'interested_courses': [(6, 0, self.interested_courses.ids)],
            'interested_products': [(6, 0, self.interested_products.ids)],
        }

        lead = self.env['crm.lead'].create(lead_vals)

        # Update form
        self.write({
            'lead_id': lead.id,
            'state': 'converted'
        })

        # Log the conversion
        self.message_post(
            body=f"Đã chuyển thành lead: <a href='/web#id={lead.id}&model=crm.lead'>{lead.name}</a>",
            message_type='notification'
        )

        return {
            'type': 'ir.actions.act_window',
            'name': 'Lead mới',
            'res_model': 'crm.lead',
            'res_id': lead.id,
            'view_mode': 'form',
            'target': 'current'
        }

    def action_send_auto_reply(self):
        """Send automatic reply email"""
        self.ensure_one()

        template = self.env.ref('luc_khi_crm.email_template_contact_auto_reply')
        if template:
            template.send_mail(self.id, force_send=True)

            self.message_post(
                body="Đã gửi email tự động phản hồi",
                message_type='notification'
            )

    @api.model
    def _cron_process_pending_forms(self):
        """Cron job to process pending contact forms"""
        pending_forms = self.search([
            ('state', '=', 'draft'),
            ('create_date', '<', fields.Datetime.now() - '1 day')
        ])

        for form in pending_forms:
            # Auto-assign if not assigned
            if not form.assigned_to:
                form.assigned_to = form._auto_assign_user(form.contact_reason)

            # Send auto-reply if configured
            form.action_send_auto_reply()

    def _get_form_url(self):
        """Get the URL for this contact form"""
        self.ensure_one()
        return f'/contact/form/{self.id}'