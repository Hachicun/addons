# -*- coding: utf-8 -*-
from odoo import models, fields, api


class LucKhiCourseCategory(models.Model):
    _name = 'luc_khi.course.category'
    _description = 'Course Category'
    _order = 'name'
    
    name = fields.Char('Category Name', required=True, translate=True)
    description = fields.Text('Description', translate=True)
    parent_id = fields.Many2one('luc_khi.course.category', string='Parent Category')
    child_ids = fields.One2many('luc_khi.course.category', 'parent_id', string='Child Categories')
    course_ids = fields.One2many('luc_khi.course', 'category_id', string='Courses')
    sequence = fields.Integer('Sequence', default=10)
    is_published = fields.Boolean('Published', default=True)
    
    # SEO fields
    seo_title = fields.Char('SEO Title', translate=True)
    seo_description = fields.Text('SEO Description', translate=True)
    slug = fields.Char('URL Slug', compute='_compute_slug', store=True)
    
    _sql_constraints = [
        ('slug_unique', 'unique(slug)', 'URL slug must be unique!'),
    ]
    
    @api.depends('name')
    def _compute_slug(self):
        for category in self:
            if category.name:
                category.slug = self._generate_slug(category.name)
    
    def _generate_slug(self, text):
        # Vietnamese-friendly slug generation
        import re
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
    
    def action_view_website(self):
        """View category on website"""
        self.ensure_one()
        return {
            'type': 'ir.actions.act_url',
            'url': f'/courses/category/{self.slug}',
            'target': 'new',
        }
    
    @api.depends('name')
    def name_get(self):
        result = []
        for category in self:
            if category.parent_id:
                name = f"{category.parent_id.name} / {category.name}"
            else:
                name = category.name
            result.append((category.id, name))
        return result