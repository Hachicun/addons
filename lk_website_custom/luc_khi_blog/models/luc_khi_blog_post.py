# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
import re


class BlogPost(models.Model):
    _inherit = 'blog.post'

    # Lục Khí specific fields
    luc_khi_category_id = fields.Many2one(
        'luc_khi.blog.category', 
        string='Lục Khí Category',
        help='Lục Khí specific blog categorization'
    )
    
    # Enhanced SEO fields
    meta_title = fields.Char('Meta Title', translate=True)
    meta_description = fields.Text('Meta Description', translate=True)
    meta_keywords = fields.Char('Meta Keywords', translate=True)
    
    # Course linking
    related_course_ids = fields.Many2many(
        'luc_khi.course',
        'blog_post_course_rel',
        'blog_post_id',
        'course_id',
        string='Related Courses'
    )
    
    # Enhanced content fields
    summary = fields.Text('Summary', translate=True, help='Short summary for blog listing')
    featured_image = fields.Binary('Featured Image', attachment=True)
    reading_time = fields.Integer('Reading Time (minutes)', compute='_compute_reading_time', store=True)
    
    # Website enhancements
    is_featured = fields.Boolean('Featured Post', default=False)
    view_count = fields.Integer('View Count', default=0)
    like_count = fields.Integer('Like Count', default=0)
    
    # Vietnamese URL slug
    vietnamese_slug = fields.Char('Vietnamese Slug', compute='_compute_vietnamese_slug', store=True)
    
    @api.depends('content')
    def _compute_reading_time(self):
        """Calculate estimated reading time based on content length"""
        for post in self:
            if post.content:
                # Average reading speed: 200 words per minute
                word_count = len(re.findall(r'\w+', post.content))
                post.reading_time = max(1, round(word_count / 200))
            else:
                post.reading_time = 1
    
    @api.depends('name')
    def _compute_vietnamese_slug(self):
        """Generate Vietnamese-friendly URL slug"""
        for post in self:
            if post.name:
                post.vietnamese_slug = self._get_vietnamese_slug(post.name)
            else:
                post.vietnamese_slug = ''
    
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
        
        # Auto-generate summary from content if not provided
        if not vals.get('summary') and vals.get('content'):
            # Extract first 150 characters as summary
            content = vals['content'][:150] + '...' if len(vals['content']) > 150 else vals['content']
            vals['summary'] = content
        
        return super(BlogPost, self).create(vals)
    
    def write(self, vals):
        # Auto-update meta title if name changes and meta_title is empty
        if 'name' in vals and ('meta_title' not in vals or not vals['meta_title']):
            vals['meta_title'] = vals['name']
        
        return super(BlogPost, self).write(vals)
    
    def action_view_website(self):
        """Open blog post on website"""
        self.ensure_one()
        return {
            'type': 'ir.actions.act_url',
            'url': f'/blog/{self.blog_id.id}/{self.vietnamese_slug or self.id}',
            'target': 'new',
        }
    
    def increment_view_count(self):
        """Increment view count for analytics"""
        self.view_count += 1
    
    def get_related_posts(self, limit=5):
        """Get related blog posts based on category"""
        if not self.luc_khi_category_id:
            return self.browse()
        
        return self.search([
            ('luc_khi_category_id', '=', self.luc_khi_category_id.id),
            ('id', '!=', self.id),
            ('website_published', '=', True),
        ], limit=limit)