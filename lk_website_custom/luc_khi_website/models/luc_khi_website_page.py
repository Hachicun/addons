# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
import re


class LucKhiWebsitePage(models.Model):
    _name = 'luc_khi.website.page'
    _description = 'Lục Khí Website Page'
    _order = 'sequence, name'
    
    name = fields.Char('Page Name', required=True, translate=True)
    title = fields.Char('Page Title', required=True, translate=True)
    content = fields.Html('Page Content', translate=True)
    
    # Ordering
    sequence = fields.Integer('Sequence', default=10)
    
    # Page identification
    page_key = fields.Char('Page Key', required=True, help='Unique identifier for page')
    is_published = fields.Boolean('Published', default=True)
    
    # SEO
    seo_title = fields.Char('SEO Title', translate=True)
    seo_description = fields.Text('SEO Description', translate=True)
    seo_keywords = fields.Char('SEO Keywords', translate=True)
    
    # Layout and display
    show_in_menu = fields.Boolean('Show in Menu', default=False)
    menu_sequence = fields.Integer('Menu Sequence', default=10)
    parent_menu_id = fields.Many2one('website.menu', string='Parent Menu')
    
    # Template
    view_id = fields.Many2one('ir.ui.view', string='Template')
    
    # Slug (computed from name for potential website usage)
    slug = fields.Char('Slug', compute='_compute_slug', store=True, index=True)
    
    _sql_constraints = [
        ('page_key_unique', 'unique(page_key)', 'Page key must be unique!'),
    ]
    
    @api.depends('name')
    def _compute_slug(self):
        for page in self:
            if page.name:
                page.slug = self._generate_slug(page.name)
    
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
    
    def action_view_website(self):
        """View the page on website"""
        self.ensure_one()
        return {
            'type': 'ir.actions.act_url',
            'url': f'/page/{self.page_key}',
            'target': 'new',
        }
