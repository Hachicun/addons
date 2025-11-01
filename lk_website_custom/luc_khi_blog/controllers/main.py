# -*- coding: utf-8 -*-
from odoo import http, _
from odoo.http import request
from odoo.addons.website.controllers.main import Website
from odoo.exceptions import ValidationError


class LucKhiBlogController(Website):
    
    def _get_blog_posts(self, category_id=None, limit=12, offset=0):
        """Get blog posts with optional category filtering"""
        domain = [('website_published', '=', True)]
        
        if category_id:
            domain.append(('luc_khi_category_id', '=', int(category_id)))
        
        posts = request.env['blog.post'].search(
            domain,
            limit=limit,
            offset=offset,
            order='is_featured DESC, post_date DESC'
        )
        
        return posts
    
    def _get_blog_categories(self):
        """Get all published blog categories"""
        return request.env['luc_khi.blog.category'].search([
            ('active', '=', True),
            ('website_published', '=', True)
        ], order='sequence, name')
    
    @http.route([
        '/blog',
        '/blog/page/<int:page>',
        '/blog/category/<model("luc_khi.blog.category"):category>',
        '/blog/category/<model("luc_khi.blog.category"):category>/page/<int:page>'
    ], type='http', auth='public', website=True)
    def blog_listing(self, category=None, page=1, **kwargs):
        """Blog listing page with category filtering and pagination"""
        posts_per_page = 12
        offset = (page - 1) * posts_per_page
        
        # Get posts
        category_id = category.id if category else None
        posts = self._get_blog_posts(category_id, posts_per_page + 1, offset)
        
        # Check if there are more posts
        has_more = len(posts) > posts_per_page
        if has_more:
            posts = posts[:-1]
        
        # Get categories for sidebar
        categories = self._get_blog_categories()
        
        # Get featured posts for sidebar
        featured_posts = request.env['blog.post'].search([
            ('is_featured', '=', True),
            ('website_published', '=', True)
        ], limit=3, order='post_date DESC')
        
        values = {
            'posts': posts,
            'category': category,
            'categories': categories,
            'featured_posts': featured_posts,
            'current_page': page,
            'has_more': has_more,
            'pager': {
                'page_count': (len(posts) + posts_per_page - 1) // posts_per_page,
                'current': page,
            }
        }
        
        return request.render('luc_khi_blog.blog_listing', values)
    
    @http.route([
        '/blog/<model("blog.blog"):blog>/<int:post_id>',
        '/blog/<model("blog.blog"):blog>/<string:slug>'
    ], type='http', auth='public', website=True)
    def blog_post_detail(self, blog, post_id=None, slug=None, **kwargs):
        """Blog post detail page"""
        # Find the post
        if post_id:
            post = request.env['blog.post'].search([
                ('id', '=', post_id),
                ('blog_id', '=', blog.id),
                ('website_published', '=', True)
            ])
        elif slug:
            post = request.env['blog.post'].search([
                ('vietnamese_slug', '=', slug),
                ('blog_id', '=', blog.id),
                ('website_published', '=', True)
            ])
        else:
            raise ValidationError(_("Post not found"))
        
        if not post:
            raise ValidationError(_("Post not found"))
        
        post.ensure_one()
        
        # Increment view count
        post.increment_view_count()
        
        # Get related posts
        related_posts = post.get_related_posts(limit=4)
        
        # Get categories for navigation
        categories = self._get_blog_categories()
        
        values = {
            'post': post,
            'blog': blog,
            'related_posts': related_posts,
            'categories': categories,
            'main_object': post,
        }
        
        return request.render('luc_khi_blog.blog_post_detail', values)
    
    @http.route('/blog/search', type='http', auth='public', website=True)
    def blog_search(self, search='', **kwargs):
        """Blog search functionality"""
        if not search:
            return request.redirect('/blog')
        
        posts = request.env['blog.post'].search([
            ('website_published', '=', True),
            '|', '|',
            ('name', 'ilike', search),
            ('content', 'ilike', search),
            ('meta_keywords', 'ilike', search)
        ], order='post_date DESC')
        
        categories = self._get_blog_categories()
        
        values = {
            'posts': posts,
            'search_query': search,
            'categories': categories,
            'search_count': len(posts),
        }
        
        return request.render('luc_khi_blog.blog_search', values)
    
    @http.route('/blog/category/<model("luc_khi.blog.category"):category>', 
                type='http', auth='public', website=True)
    def blog_category(self, category, **kwargs):
        """Blog category page (redirects to listing with category filter)"""
        return request.redirect(f'/blog/category/{category.id}')
    
    @http.route('/blog/feed', type='http', auth='public', website=True)
    def blog_rss_feed(self, **kwargs):
        """RSS feed for blog posts"""
        posts = request.env['blog.post'].search([
            ('website_published', '=', True)
        ], limit=20, order='post_date DESC')
        
        values = {
            'posts': posts,
            'base_url': request.httprequest.url_root,
        }
        
        return request.render('luc_khi_blog.blog_rss', values, headers={
            'Content-Type': 'application/rss+xml'
        })
    
    @http.route('/blog/like/<int:post_id>', type='json', auth='public', website=True)
    def blog_like_post(self, post_id, **kwargs):
        """Like/unlike blog post via AJAX"""
        post = request.env['blog.post'].browse(post_id)
        if not post.exists():
            return {'error': _('Post not found')}
        
        # Simple like functionality (in production, you'd track user likes)
        post.like_count += 1
        
        return {
            'success': True,
            'like_count': post.like_count
        }