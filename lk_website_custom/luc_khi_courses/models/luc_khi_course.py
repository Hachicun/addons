# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
import re


class LucKhiCourse(models.Model):
    _name = 'luc_khi.course'
    _description = 'Lục Khí Course'
    _order = 'sequence, name'
    
    # Basic Information
    name = fields.Char('Course Name', required=True, translate=True)
    description = fields.Html('Description', translate=True)
    short_description = fields.Text('Short Description', translate=True)
    
    # Course Structure
    level = fields.Selection([
        ('basic', 'Cơ Bản'),
        ('intermediate_1', 'Trung Cấp 1'),
        ('intermediate_2', 'Trung Cấp 2'), 
        ('intermediate_3', 'Trung Cấp 3'),
        ('advanced', 'Nâng Cao'),
    ], required=True, default='basic')
    
    sequence = fields.Integer('Sequence', default=10)
    
    # Media and Content
    image = fields.Image('Course Image')
    video_url = fields.Char('Introduction Video URL')
    slide_channel_id = fields.Many2one(
        'slide.channel', 
        string='Slide Channel',
        help='Connected slide channel for course content'
    )
    
    # Pricing and Sales
    price = fields.Monetary('Price', currency_field='currency_id')
    currency_id = fields.Many2one('res.currency', default=lambda self: self.env.company.currency_id)
    
    # Access Control
    is_published = fields.Boolean('Published', default=False)
    featured = fields.Boolean('Featured Course', default=False)
    access_mode = fields.Selection([
        ('public', 'Public'),
        ('registered', 'Registered Users'),
        ('purchased', 'Purchased Only'),
    ], default='purchased')
    
    # Metadata
    duration_hours = fields.Float('Duration (Hours)')
    difficulty_level = fields.Integer('Difficulty Level (1-10)')
    prerequisites = fields.Text('Prerequisites', translate=True)
    learning_objectives = fields.Html('Learning Objectives', translate=True)
    
    # SEO and Marketing
    seo_title = fields.Char('SEO Title', translate=True)
    seo_description = fields.Text('SEO Description', translate=True)
    seo_keywords = fields.Char('SEO Keywords', translate=True)
    slug = fields.Char('URL Slug', compute='_compute_slug', store=True)
    
    # Relations
    category_id = fields.Many2one('luc_khi.course.category', string='Category')
    instructor_ids = fields.Many2many('res.partner', string='Instructors')
    tag_ids = fields.Many2many('luc_khi.course.tag', string='Tags')
    
    # Statistics
    student_count = fields.Integer('Number of Students', compute='_compute_student_count')
    rating = fields.Float('Average Rating', compute='_compute_rating')
    
    _sql_constraints = [
        ('slug_unique', 'unique(slug)', 'URL slug must be unique!'),
    ]
    
    @api.depends('name')
    def _compute_slug(self):
        for course in self:
            if course.name:
                course.slug = self._generate_slug(course.name)
    
    def _generate_slug(self, text):
        # Vietnamese-friendly slug generation
        text = text.lower()
        # Vietnamese character normalization
        replacements = {
            'á': 'a', 'à': 'a', 'ả': 'a', 'ã': 'a', 'ạ': 'a',
            'ă': 'a', 'ắ': 'a', 'ằ': 'a', 'ẳ': 'a', 'ẵ': 'a', 'ặ': 'a',
            'â': 'a', 'ấ': 'a', 'ầ': 'a', 'ẩ': 'a', 'ẫ': 'a', 'ậ': 'a',
            'đ': 'd',
            'é': 'e', 'è': 'e', 'ẻ': 'e', 'ẽ': 'e', 'ẹ': 'e',
            'ê': 'e', 'ế': 'e', 'ề': 'e', 'ể': 'e', 'ễ': 'e', 'ệ': 'e',
            'í': 'i', 'ì': 'i', 'ỉ': 'i', 'ĩ': 'i', 'ị': 'i',
            'ó': 'o', 'ò': 'o', 'ỏ': 'o', 'õ': 'o', 'ọ': 'o',
            'ô': 'o', 'ố': 'o', 'ồ': 'o', 'ổ': 'o', 'ỗ': 'o', 'ộ': 'o',
            'ơ': 'o', 'ớ': 'o', 'ờ': 'o', 'ở': 'o', 'ỡ': 'o', 'ợ': 'o',
            'ú': 'u', 'ù': 'u', 'ủ': 'u', 'ũ': 'u', 'ụ': 'u',
            'ư': 'u', 'ứ': 'u', 'ừ': 'u', 'ử': 'u', 'ữ': 'u', 'ự': 'u',
            'ý': 'y', 'ỳ': 'y', 'ỷ': 'y', 'ỹ': 'y', 'ỵ': 'y',
        }
        for viet_char, latin_char in replacements.items():
            text = text.replace(viet_char, latin_char)
        text = re.sub(r'[^a-z0-9]+', '-', text)
        return text.strip('-')
    
    def _compute_student_count(self):
        for course in self:
            # Count students who have access to this course
            if course.slide_channel_id:
                course.student_count = course.slide_channel_id.partner_count
            else:
                course.student_count = 0
    
    def _compute_rating(self):
        for course in self:
            # Compute average rating from slide channel
            if course.slide_channel_id:
                ratings = course.slide_channel_id.rating_ids
                if ratings:
                    course.rating = sum(rating.rating for rating in ratings) / len(ratings)
                else:
                    course.rating = 0.0
            else:
                course.rating = 0.0
    
    def action_view_website(self):
        """View course on website"""
        self.ensure_one()
        return {
            'type': 'ir.actions.act_url',
            'url': f'/course/{self.slug}',
            'target': 'new',
        }
    
    def action_create_slide_channel(self):
        """Create slide channel for this course"""
        self.ensure_one()
        if not self.slide_channel_id:
            channel = self.env['slide.channel'].create({
                'name': self.name,
                'description': self.description,
                'channel_type': 'training',
                'is_published': self.is_published,
                'visibility': 'public' if self.access_mode == 'public' else 'members',
            })
            self.slide_channel_id = channel.id
            return {
                'type': 'ir.actions.act_window',
                'name': 'Slide Channel',
                'res_model': 'slide.channel',
                'res_id': channel.id,
                'view_mode': 'form',
            }
        else:
            return {
                'type': 'ir.actions.act_window',
                'name': 'Slide Channel',
                'res_model': 'slide.channel',
                'res_id': self.slide_channel_id.id,
                'view_mode': 'form',
            }
    
    def action_enroll_student(self):
        """Enroll current user in course"""
        self.ensure_one()
        if self.slide_channel_id and self.env.user.partner_id:
            self.slide_channel_id._action_add_member(self.env.user.partner_id)
    
    def toggle_published(self):
        """Toggle the published status of courses"""
        for record in self:
            record.is_published = not record.is_published

    def toggle_featured(self):
        """Toggle the featured status of courses"""
        for record in self:
            record.featured = not record.featured

    def check_access_rights(self, user=None):
        """Check if user has access to this course"""
        if not user:
            user = self.env.user

        # Public access
        if self.access_mode == 'public':
            return True

        # Registered users
        if self.access_mode == 'registered' and not user.has_group('base.group_public'):
            return True

        # Purchased only - check if user has access through slide channel
        if self.access_mode == 'purchased' and self.slide_channel_id:
            return self.slide_channel_id._check_access(user.partner_id)

        return False