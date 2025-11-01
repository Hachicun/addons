# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
import re


class LucKhiBlogCategory(models.Model):
    _name = 'luc_khi.blog.category'
    _description = 'Lục Khí Blog Category'
    _order = 'sequence, name'

    name = fields.Char('Category Name', required=True, translate=True)
    description = fields.Text('Description', translate=True)
    sequence = fields.Integer('Sequence', default=10)
    active = fields.Boolean('Active', default=True)
    
    # SEO fields
    meta_title = fields.Char('Meta Title', translate=True)
    meta_description = fields.Text('Meta Description', translate=True)
    meta_keywords = fields.Char('Meta Keywords', translate=True)
    
    # Relations
    post_ids = fields.One2many('blog.post', 'luc_khi_category_id', string='Blog Posts')
    post_count = fields.Integer('Post Count', compute='_compute_post_count')
    
    # Website fields
    website_published = fields.Boolean('Published on Website', default=True)
    color = fields.Char('Color', help='Category color for website display')
    
    @api.depends('post_ids')
    def _compute_post_count(self):
        for category in self:
            category.post_count = len(category.post_ids.filtered('website_published'))
    
    @api.model
    def create(self, vals):
        if 'meta_title' not in vals or not vals['meta_title']:
            vals['meta_title'] = vals.get('name', '')
        return super(LucKhiBlogCategory, self).create(vals)
    
    def write(self, vals):
        if 'name' in vals and ('meta_title' not in vals or not vals['meta_title']):
            vals['meta_title'] = vals['name']
        return super(LucKhiBlogCategory, self).write(vals)
    
    @api.model
    def get_vietnamese_slug(self, text):
        """Generate Vietnamese-friendly URL slug"""
        if not text:
            return ''
        
        # Vietnamese character mapping
        vietnamese_map = {
            'à': 'a', 'á': 'a', 'ạ': 'a', 'ả': 'a', 'ã': 'a',
            'ă': 'a', 'ằ': 'a', 'ắ': 'a', 'ặ': 'a', 'ẳ': 'a', 'ẵ': 'a',
            'â': 'a', 'ầ': 'a', 'ấ': 'a', 'ậ': 'a', 'ẩ': 'a', 'ẫ': 'a',
            'è': 'e', 'é': 'e', 'ẹ': 'e', 'ẻ': 'e', 'ẽ': 'e',
            'ê': 'e', 'ề': 'e', 'ế': 'e', 'ệ': 'e', 'ể': 'e', 'ễ': 'e',
            'ì': 'i', 'í': 'i', 'ị': 'i', 'ỉ': 'i', 'ĩ': 'i',
            'ò': 'o', 'ó': 'o', 'ọ': 'o', 'ỏ': 'o', 'õ': 'o',
            'ô': 'o', 'ồ': 'o', 'ố': 'o', 'ộ': 'o', 'ổ': 'o', 'ỗ': 'o',
            'ơ': 'o', 'ờ': 'o', 'ớ': 'o', 'ợ': 'o', 'ở': 'o', 'ỡ': 'o',
            'ù': 'u', 'ú': 'u', 'ụ': 'u', 'ủ': 'u', 'ũ': 'u',
            'ư': 'u', 'ừ': 'u', 'ứ': 'u', 'ự': 'u', 'ử': 'u', 'ữ': 'u',
            'ỳ': 'y', 'ý': 'y', 'ỵ': 'y', 'ỷ': 'y', 'ỹ': 'y',
            'đ': 'd',
            'À': 'a', 'Á': 'a', 'Ạ': 'a', 'Ả': 'a', 'Ã': 'a',
            'Ă': 'a', 'Ằ': 'a', 'Ắ': 'a', 'Ặ': 'a', 'Ẳ': 'a', 'Ẵ': 'a',
            'Â': 'a', 'Ầ': 'a', 'Ấ': 'a', 'Ậ': 'a', 'Ẩ': 'a', 'Ẫ': 'a',
            'È': 'e', 'É': 'e', 'Ẹ': 'e', 'Ẻ': 'e', 'Ẽ': 'e',
            'Ê': 'e', 'Ề': 'e', 'Ế': 'e', 'Ệ': 'e', 'Ể': 'e', 'Ễ': 'e',
            'Ì': 'i', 'Í': 'i', 'Ị': 'i', 'Ỉ': 'i', 'Ĩ': 'i',
            'Ò': 'o', 'Ó': 'o', 'Ọ': 'o', 'Ỏ': 'o', 'Õ': 'o',
            'Ô': 'o', 'Ồ': 'o', 'Ố': 'o', 'Ộ': 'o', 'Ổ': 'o', 'Ỗ': 'o',
            'Ơ': 'o', 'Ờ': 'o', 'Ớ': 'o', 'Ợ': 'o', 'Ở': 'o', 'Ỡ': 'o',
            'Ù': 'u', 'Ú': 'u', 'Ụ': 'u', 'Ủ': 'u', 'Ũ': 'u',
            'Ư': 'u', 'Ừ': 'u', 'Ứ': 'u', 'Ự': 'u', 'Ử': 'u', 'Ữ': 'u',
            'Ỳ': 'y', 'Ý': 'y', 'Ỵ': 'y', 'Ỷ': 'y', 'Ỹ': 'y',
            'Đ': 'd',
        }
        
        # Convert Vietnamese characters
        converted_text = ''.join(vietnamese_map.get(c, '') if c else '' for c in text)
        
        # Convert to lowercase and replace non-alphanumeric with hyphens
        converted_text = re.sub(r'[^a-z0-9]+', '-', converted_text.lower())
        
        # Remove leading/trailing hyphens and multiple hyphens
        converted_text = re.sub(r'^-+|-+$', '', converted_text)
        converted_text = re.sub(r'-+', '-', converted_text)
        
        return converted_text

    def action_view_posts(self):
        """View blog posts in this category"""
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': f'Posts in {self.name}',
            'res_model': 'blog.post',
            'view_mode': 'tree,form',
            'domain': [('luc_khi_category_id', '=', self.id)],
            'context': {'default_luc_khi_category_id': self.id},
        }