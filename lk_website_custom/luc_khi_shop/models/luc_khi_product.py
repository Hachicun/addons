# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
import re


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    # Lục Khí specific fields
    luc_khi_category_id = fields.Many2one(
        'luc_khi.product.category',
        string='Lục Khí Category',
        help='Lục Khí specific product categorization'
    )
    
    luc_khi_element = fields.Selection([
        ('kim', 'Kim - Metal'),
        ('moc', 'Mộc - Wood'),
        ('thuy', 'Thủy - Water'),
        ('hoa', 'Hỏa - Fire'),
        ('tho', 'Thổ - Earth'),
        ('phong', 'Phong - Wind'),
    ], string='Primary Lục Khí Element', help='Primary Lục Khí element for this product')
    
    luc_khi_secondary_elements = fields.Selection([
        ('kim', 'Kim - Metal'),
        ('moc', 'Mộc - Wood'),
        ('thuy', 'Thủy - Water'),
        ('hoa', 'Hỏa - Fire'),
        ('tho', 'Thổ - Earth'),
        ('phong', 'Phong - Wind'),
    ], string='Secondary Lục Khí Element', help='Secondary Lục Khí element for this product')
    
    # Enhanced SEO fields
    meta_title = fields.Char('Meta Title', translate=True)
    meta_description = fields.Text('Meta Description', translate=True)
    meta_keywords = fields.Char('Meta Keywords', translate=True)
    
    # Enhanced product fields
    short_description = fields.Text('Short Description', translate=True, help='Brief description for product listings')
    featured_image = fields.Binary('Featured Image', attachment=True, help='Main product image for listings')
    is_featured = fields.Boolean('Featured Product', default=False, help='Show in featured products section')
    is_recommended = fields.Boolean('Recommended Product', default=False, help='Show in recommendations')
    
    # Vietnamese URL slug
    vietnamese_slug = fields.Char('Vietnamese Slug', compute='_compute_vietnamese_slug', store=True)
    
    # Product relations
    related_product_ids = fields.Many2many(
        'product.template',
        'product_product_rel',
        'product_id',
        'related_product_id',
        string='Related Products',
        help='Products frequently bought together'
    )
    
    compatible_elements = fields.Selection([
        ('kim', 'Kim - Metal'),
        ('moc', 'Mộc - Wood'),
        ('thuy', 'Thủy - Water'),
        ('hoa', 'Hỏa - Fire'),
        ('tho', 'Thổ - Earth'),
        ('phong', 'Phong - Wind'),
        ('all', 'Tất cả - All'),
    ], string='Compatible With', help='Lục Khí elements this product is compatible with')
    
    # Usage and benefits
    luc_khi_benefits = fields.Html('Lục Khí Benefits', translate=True, sanitize_attributes=False)
    usage_instructions = fields.Html('Usage Instructions', translate=True, sanitize_attributes=False)
    
    # Vietnamese compliance
    vietnam_origin = fields.Boolean('Made in Vietnam', default=False)
    quality_certification = fields.Char('Quality Certification', help='Vietnamese quality certification')
    
    # Analytics
    view_count = fields.Integer('View Count', default=0)
    sales_count = fields.Integer('Sales Count', default=0)
    
    @api.depends('name')
    def _compute_vietnamese_slug(self):
        """Generate Vietnamese-friendly URL slug"""
        for product in self:
            if product.name:
                product.vietnamese_slug = self._get_vietnamese_slug(product.name)
            else:
                product.vietnamese_slug = ''
    
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
        # Auto-generate meta title if not provided
        if 'meta_title' not in vals or not vals['meta_title']:
            vals['meta_title'] = vals.get('name', '')
        
        # Auto-generate short description from description if not provided
        if not vals.get('short_description') and vals.get('description'):
            # Extract first 150 characters as short description
            description = vals['description'][:150] + '...' if len(vals['description']) > 150 else vals['description']
            vals['short_description'] = description
        
        return super(ProductTemplate, self).create(vals)
    
    def write(self, vals):
        # Auto-update meta title if name changes and meta_title is empty
        if 'name' in vals and ('meta_title' not in vals or not vals['meta_title']):
            vals['meta_title'] = vals['name']
        
        return super(ProductTemplate, self).write(vals)
    
    def increment_view_count(self):
        """Increment view count for analytics"""
        self.view_count += 1
    
    def get_recommended_products(self, limit=4):
        """Get recommended products based on Lục Khí compatibility"""
        if not self.luc_khi_element:
            return self.browse()
        
        # Get products with compatible elements
        domain = [
            ('id', '!=', self.id),
            ('website_published', '=', True),
            '|', '|',
            ('luc_khi_element', '=', self.luc_khi_element),
            ('compatible_elements', '=', self.luc_khi_element),
            ('compatible_elements', '=', 'all'),
        ]
        
        return self.search(domain, limit=limit)
    
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
    
    def action_view_website(self):
        """Open product on website"""
        self.ensure_one()
        return {
            'type': 'ir.actions.act_url',
            'url': f'/shop/product/{self.vietnamese_slug or self.id}',
            'target': 'new',
        }


class ProductProduct(models.Model):
    _inherit = 'product.product'

    # Inherit Lục Khí fields from template
    luc_khi_category_id = fields.Many2one(
        related='product_tmpl_id.luc_khi_category_id',
        string='Lục Khí Category',
        readonly=False
    )
    
    luc_khi_element = fields.Selection(
        related='product_tmpl_id.luc_khi_element',
        string='Primary Lục Khí Element',
        readonly=False
    )
    
    vietnamese_slug = fields.Char(
        related='product_tmpl_id.vietnamese_slug',
        string='Vietnamese Slug',
        readonly=False
    )