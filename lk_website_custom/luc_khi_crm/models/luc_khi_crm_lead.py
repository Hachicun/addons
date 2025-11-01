# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
import re


class LucKhiCrmLead(models.Model):
    _inherit = 'crm.lead'

    # Vietnamese Contact Fields
    full_name_vietnamese = fields.Char(
        string='Họ và tên (Tiếng Việt)',
        help='Họ và tên đầy đủ theo tiếng Việt'
    )

    phone_mobile = fields.Char(
        string='Số điện thoại di động',
        help='Số điện thoại di động chính'
    )

    phone_home = fields.Char(
        string='Số điện thoại nhà',
        help='Số điện thoại cố định'
    )

    # Vietnamese Address Fields
    address_street_vietnamese = fields.Char(
        string='Địa chỉ đường phố',
        help='Số nhà, tên đường, khu vực'
    )

    address_ward = fields.Char(
        string='Phường/Xã',
        help='Tên phường hoặc xã'
    )

    address_district = fields.Char(
        string='Quận/Huyện',
        help='Tên quận hoặc huyện'
    )

    address_city = fields.Char(
        string='Tỉnh/Thành phố',
        help='Tên tỉnh hoặc thành phố'
    )

    # Lục Khí Profile Analysis
    luc_khi_profile_analysis = fields.Text(
        string='Phân tích hồ sơ Lục Khí',
        help='Phân tích ngũ hành và năng lượng của khách hàng'
    )

    luc_khi_dominant_element = fields.Many2one(
        'luc_khi.element',
        string='Ngũ hành chủ đạo',
        help='Ngũ hành chiếm ưu thế trong hồ sơ khách hàng'
    )

    luc_khi_element_scores = fields.Json(
        string='Điểm số ngũ hành',
        help='Điểm số của từng ngũ hành (JSON format)'
    )

    luc_khi_energy_level = fields.Selection([
        ('low', 'Thấp'),
        ('medium', 'Trung bình'),
        ('high', 'Cao'),
        ('very_high', 'Rất cao')
    ], string='Mức năng lượng', default='medium')

    # Interest Tracking
    interested_courses = fields.Many2many(
        'luc_khi.course',
        string='Khóa học quan tâm',
        help='Các khóa học mà khách hàng quan tâm'
    )

    interested_products = fields.Many2many(
        'product.template',
        string='Sản phẩm quan tâm',
        help='Các sản phẩm mà khách hàng quan tâm'
    )

    interested_blog_categories = fields.Many2many(
        'luc_khi.blog.category',
        string='Chủ đề blog quan tâm',
        help='Các chủ đề blog mà khách hàng quan tâm'
    )

    # Lead Scoring
    luc_khi_lead_score = fields.Integer(
        string='Điểm đánh giá Lục Khí',
        compute='_compute_luc_khi_lead_score',
        store=True,
        help='Điểm đánh giá dựa trên phân tích Lục Khí'
    )

    # Contact Preferences
    preferred_contact_method = fields.Selection([
        ('phone', 'Điện thoại'),
        ('email', 'Email'),
        ('zalo', 'Zalo'),
        ('facebook', 'Facebook'),
        ('in_person', 'Gặp trực tiếp')
    ], string='Phương thức liên lạc ưa thích', default='phone')

    preferred_contact_time = fields.Selection([
        ('morning', 'Buổi sáng (8h-12h)'),
        ('afternoon', 'Buổi chiều (12h-18h)'),
        ('evening', 'Buổi tối (18h-22h)'),
        ('anytime', 'Bất kỳ lúc nào')
    ], string='Thời gian liên lạc ưa thích', default='anytime')

    # Vietnamese Business Fields
    company_tax_code = fields.Char(
        string='Mã số thuế công ty',
        help='Mã số thuế của công ty (nếu có)'
    )

    personal_tax_code = fields.Char(
        string='Mã số thuế cá nhân',
        help='Mã số thuế cá nhân (nếu có)'
    )

    # Follow-up and Notes
    last_contact_date = fields.Datetime(
        string='Lần liên lạc cuối',
        help='Thời gian liên lạc gần nhất'
    )

    next_followup_date = fields.Datetime(
        string='Lần theo dõi tiếp theo',
        help='Thời gian cần theo dõi tiếp theo'
    )

    followup_notes = fields.Text(
        string='Ghi chú theo dõi',
        help='Ghi chú về các lần theo dõi'
    )

    # Validation methods
    @api.constrains('phone_mobile', 'phone_home')
    def _check_phone_numbers(self):
        """Validate Vietnamese phone numbers"""
        vietnamese_phone_pattern = re.compile(r'^(0|\+84)[3|5|7|8|9][0-9]{8}$')

        for lead in self:
            if lead.phone_mobile and not vietnamese_phone_pattern.match(lead.phone_mobile.replace(' ', '')):
                raise ValidationError(_('Số điện thoại di động không hợp lệ. Vui lòng nhập số điện thoại Việt Nam hợp lệ.'))

            if lead.phone_home and not vietnamese_phone_pattern.match(lead.phone_home.replace(' ', '')):
                raise ValidationError(_('Số điện thoại nhà không hợp lệ. Vui lòng nhập số điện thoại Việt Nam hợp lệ.'))

    @api.constrains('company_tax_code', 'personal_tax_code')
    def _check_tax_codes(self):
        """Validate Vietnamese tax codes"""
        tax_code_pattern = re.compile(r'^\d{10}(-\d{3})?$')

        for lead in self:
            if lead.company_tax_code and not tax_code_pattern.match(lead.company_tax_code):
                raise ValidationError(_('Mã số thuế công ty không hợp lệ.'))

            if lead.personal_tax_code and not tax_code_pattern.match(lead.personal_tax_code):
                raise ValidationError(_('Mã số thuế cá nhân không hợp lệ.'))

    @api.depends('luc_khi_dominant_element', 'luc_khi_energy_level', 'interested_courses', 'interested_products')
    def _compute_luc_khi_lead_score(self):
        """Compute lead score based on Lục Khí analysis"""
        for lead in self:
            score = 0

            # Base score from dominant element
            if lead.luc_khi_dominant_element:
                score += 20

            # Energy level bonus
            energy_bonus = {'low': 5, 'medium': 10, 'high': 15, 'very_high': 20}
            score += energy_bonus.get(lead.luc_khi_energy_level, 0)

            # Interest bonuses
            score += len(lead.interested_courses) * 5
            score += len(lead.interested_products) * 3
            score += len(lead.interested_blog_categories) * 2

            # Cap at 100
            lead.luc_khi_lead_score = min(score, 100)

    @api.model
    def create(self, vals):
        """Override create to add Lục Khí analysis"""
        lead = super(LucKhiCrmLead, self).create(vals)

        # Auto-analyze Lục Khí profile if interests are provided
        if any(key in vals for key in ['interested_courses', 'interested_products', 'interested_blog_categories']):
            lead._analyze_luc_khi_profile()

        return lead

    def write(self, vals):
        """Override write to update Lục Khí analysis"""
        result = super(LucKhiCrmLead, self).write(vals)

        # Re-analyze if interests changed
        if any(key in vals for key in ['interested_courses', 'interested_products', 'interested_blog_categories']):
            self._analyze_luc_khi_profile()

        return result

    def _analyze_luc_khi_profile(self):
        """Analyze Lục Khí profile based on interests"""
        self.ensure_one()

        element_scores = {'KIM': 0, 'MOC': 0, 'THUY': 0, 'HOA': 0, 'THO': 0, 'PHONG': 0}

        # Analyze course interests
        for course in self.interested_courses:
            for element in course.luc_khi_element_ids:
                element_scores[element.code] += 2

        # Analyze product interests
        for product in self.interested_products:
            for element in product.luc_khi_element_ids:
                element_scores[element.code] += 1

        # Analyze blog category interests
        for category in self.interested_blog_categories:
            for element in category.luc_khi_element_ids:
                element_scores[element.code] += 1

        # Find dominant element
        if element_scores:
            dominant_code = max(element_scores.items(), key=lambda x: x[1])[0]
            dominant_element = self.env['luc_khi.element'].search([('code', '=', dominant_code)], limit=1)

            # Generate analysis text
            analysis = self._generate_profile_analysis(dominant_element, element_scores)

            # Update fields
            self.write({
                'luc_khi_dominant_element': dominant_element.id,
                'luc_khi_element_scores': element_scores,
                'luc_khi_profile_analysis': analysis,
                'luc_khi_energy_level': self._calculate_energy_level(element_scores)
            })

    def _generate_profile_analysis(self, dominant_element, element_scores):
        """Generate human-readable profile analysis"""
        if not dominant_element:
            return "Chưa có đủ thông tin để phân tích hồ sơ Lục Khí."

        element_names = {
            'KIM': 'Kim (Kim loại)',
            'MOC': 'Mộc (Cây cối)',
            'THUY': 'Thủy (Nước)',
            'HOA': 'Hỏa (Lửa)',
            'THO': 'Thổ (Đất)',
            'PHONG': 'Phong (Gió)'
        }

        analysis = f"""
        Phân tích hồ sơ Lục Khí:

        • Ngũ hành chủ đạo: {dominant_element.name}
        • Mô tả: {dominant_element.vietnamese_description}

        Chi tiết điểm số ngũ hành:
        """

        for code, score in element_scores.items():
            element_name = element_names.get(code, code)
            analysis += f"• {element_name}: {score} điểm\n"

        analysis += f"\nKhuyến nghị: {dominant_element.recommended_for}"

        return analysis.strip()

    def _calculate_energy_level(self, element_scores):
        """Calculate energy level based on element scores"""
        total_score = sum(element_scores.values())
        max_possible = len(element_scores) * 3  # Assuming max 3 points per interest type

        if total_score >= max_possible * 0.8:
            return 'very_high'
        elif total_score >= max_possible * 0.6:
            return 'high'
        elif total_score >= max_possible * 0.4:
            return 'medium'
        else:
            return 'low'

    def action_schedule_followup(self):
        """Schedule next follow-up"""
        return {
            'type': 'ir.actions.act_window',
            'name': 'Lên lịch theo dõi',
            'res_model': 'calendar.event',
            'view_mode': 'form',
            'context': {
                'default_name': f'Theo dõi lead: {self.name}',
                'default_partner_ids': [(6, 0, self.partner_id.ids if self.partner_id else [])],
                'default_res_id': self.id,
                'default_res_model': 'crm.lead',
            }
        }

    def action_send_luc_khi_recommendation(self):
        """Send personalized Lục Khí recommendations via email"""
        self.ensure_one()

        if not self.luc_khi_dominant_element:
            raise ValidationError(_("Cần phân tích hồ sơ Lục Khí trước khi gửi khuyến nghị."))

        template = self.env.ref('luc_khi_crm.email_template_luc_khi_recommendation')
        if template:
            template.send_mail(self.id, force_send=True)

        # Log the activity
        self.message_post(
            body="Đã gửi email khuyến nghị Lục Khí cá nhân hóa",
            message_type='notification'
        )