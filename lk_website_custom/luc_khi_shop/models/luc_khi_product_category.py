# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
import re


class LucKhiProductCategory(models.Model):
    _name = 'luc_khi.product.category'
    _description = 'Lục Khí Product Category'
    _order = 'sequence, name'
    _parent_name = 'parent_id'
    _parent_store = True
    _rec_name = 'complete_name'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char('Category Name', required=True, translate=True, tracking=True)
    complete_name = fields.Char('Complete Name', compute='_compute_complete_name', recursive=True, store=True)
    parent_id = fields.Many2one('luc_khi.product.category', 'Parent Category', ondelete='cascade')
    parent_path = fields.Char('Parent Path', index=True, unaccent=False)
    child_ids = fields.One2many('luc_khi.product.category', 'parent_id', 'Child Categories')
    
    # Lục Khí specific fields
    luc_khi_element = fields.Selection([
        ('kim', 'Kim - Metal'),
        ('moc', 'Mộc - Wood'),
        ('thuy', 'Thủy - Water'),
        ('hoa', 'Hỏa - Fire'),
        ('tho', 'Thổ - Earth'),
        ('phong', 'Phong - Wind'),
    ], string='Lục Khí Element', help='Primary Lục Khí element for this category')
    
    # SEO fields
    meta_title = fields.Char('Meta Title', translate=True)
    meta_description = fields.Text('Meta Description', translate=True)
    meta_keywords = fields.Char('Meta Keywords', translate=True)
    
    # Website fields
    sequence = fields.Integer('Sequence', default=10)
    description = fields.Html('Description', translate=True, sanitize_attributes=False)
    image = fields.Binary('Image', attachment=True)
    
    # Product relations
    product_count = fields.Integer('Product Count', compute='_compute_product_count')
    website_published = fields.Boolean('Published on Website', default=True)
    
    # Vietnamese URL slug
    vietnamese_slug = fields.Char('Vietnamese Slug', compute='_compute_vietnamese_slug', store=True)
    
    @api.depends('name', 'parent_id.complete_name')
    def _compute_complete_name(self):
        for category in self:
            if category.parent_id:
                category.complete_name = '%s / %s' % (category.parent_id.complete_name, category.name)
            else:
                category.complete_name = category.name
    
    @api.depends('product_tmpl_ids')
    def _compute_product_count(self):
        for category in self:
            category.product_count = len(category.product_tmpl_ids)
    
    @api.depends('name')
    def _compute_vietnamese_slug(self):
        for category in self:
            if category.name:
                category.vietnamese_slug = self._get_vietnamese_slug(category.name)
            else:
                category.vietnamese_slug = ''
    
    @api.model
    def _get_vietnamese_slug(self, text):
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
    
    @api.model
    def create(self, vals):
        if 'meta_title' not in vals or not vals['meta_title']:
            vals['meta_title'] = vals.get('name', '')
        return super(LucKhiProductCategory, self).create(vals)
    
    def write(self, vals):
        if 'name' in vals and ('meta_title' not in vals or not vals['meta_title']):
            vals['meta_title'] = vals['name']
        return super(LucKhiProductCategory, self).write(vals)
    
    def action_view_products(self):
        """View products in this category"""
        self.ensure_one()
        action = self.env.ref('luc_khi_shop.action_luc_khi_product').read()[0]
        action['domain'] = [('luc_khi_category_id', '=', self.id)]
        action['context'] = {'default_luc_khi_category_id': self.id}
        return action
    
    def get_element_color(self):
        """Get color associated with Lục Khí element"""
        colors = {
            'kim': '#C0C0C0',      # Silver
            'moc': '#228B22',      # Forest Green
            'thuy': '#4682B4',     # Steel Blue
            'hoa': '#FF4500',      # Orange Red
            'tho': '#8B4513',      # Saddle Brown
            'phong': '#87CEEB',     # Sky Blue
        }
        return colors.get(self.luc_khi_element, '#6c757d')