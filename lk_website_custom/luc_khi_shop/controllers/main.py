# -*- coding: utf-8 -*-
from odoo import http, _
from odoo.http import request
from odoo.addons.website.controllers.main import Website
from odoo.addons.website_sale.controllers.main import WebsiteSale
from odoo.exceptions import ValidationError


class LucKhiShopController(Website):
    
    def _get_products(self, category_id=None, element=None, limit=20, offset=0, search=''):
        """Get products with optional filtering"""
        domain = [('sale_ok', '=', True), ('website_published', '=', True)]

        if category_id:
            domain.append(('luc_khi_category_id', '=', category_id))

        if element:
            domain.append(('luc_khi_element_ids.code', '=', element.upper()))

        if search:
            # Add OR conditions for search
            search_domain = [
                '|', '|', '|',
                ('name', 'ilike', search),
                ('description_sale', 'ilike', search),
                ('website_description', 'ilike', search),
                ('luc_khi_benefits', 'ilike', search)
            ]
            domain.extend(search_domain)

        products = request.env['product.template'].search(
            domain,
            limit=limit,
            offset=offset,
            order='website_sequence ASC, sales_count DESC, name'
        )

        return products
    
    def _get_categories(self):
        """Get all published product categories"""
        return request.env['luc_khi.product.category'].search([
            ('website_published', '=', True)
        ], order='sequence, name')
    
    def _get_featured_products(self, limit=8):
        """Get featured products"""
        return request.env['product.template'].search([
            ('sale_ok', '=', True),
            ('website_published', '=', True),
            ('is_featured', '=', True)
        ], limit=limit, order='sales_count DESC')
    
    @http.route([
        '/shop',
        '/shop/page/<int:page>',
        '/shop/category/<model("luc_khi.product.category"):category>',
        '/shop/category/<model("luc_khi.product.category"):category>/page/<int:page>',
        '/shop/element/<string:element>',
        '/shop/element/<string:element>/page/<int:page>',
        '/shop/search',
        '/shop/search/page/<int:page>'
    ], type='http', auth='public', website=True)
    def shop_listing(self, category=None, element=None, page=1, search='', **kwargs):
        """Shop listing page with filtering and pagination"""
        products_per_page = 20
        offset = (page - 1) * products_per_page
        
        # Get products
        category_id = category.id if category else None
        products = self._get_products(category_id, element, products_per_page + 1, offset, search)
        
        # Check if there are more products
        has_more = len(products) > products_per_page
        if has_more:
            products = products[:-1]
        
        # Get categories and featured products
        categories = self._get_categories()
        featured_products = self._get_featured_products()
        
        # Get Lục Khí elements for filtering
        elements = [
            ('kim', 'Kim - Kim loại'),
            ('moc', 'Mộc - Cây cối'),
            ('thuy', 'Thủy - Nước'),
            ('hoa', 'Hỏa - Lửa'),
            ('tho', 'Thổ - Đất'),
            ('phong', 'Phong - Gió'),
        ]
        
        values = {
            'products': products,
            'category': category,
            'element': element,
            'categories': categories,
            'featured_products': featured_products,
            'elements': elements,
            'search_query': search,
            'current_page': page,
            'has_more': has_more,
            'pager': {
                'page_count': (len(products) + products_per_page - 1) // products_per_page,
                'current': page,
            }
        }
        
        return request.render('luc_khi_shop.shop_listing', values)
    
    @http.route([
        '/shop/product/<model("product.template"):product>',
        '/shop/product/<string:slug>'
    ], type='http', auth='public', website=True)
    def product_detail(self, product=None, slug=None, **kwargs):
        """Product detail page"""
        # Find the product
        if product:
            # Product passed directly
            pass
        elif slug:
            # Find product by slug
            product = request.env['product.template'].search([
                ('vietnamese_slug', '=', slug),
                ('sale_ok', '=', True),
                ('website_published', '=', True)
            ])
        else:
            raise ValidationError(_("Product not found"))
        
        if not product:
            raise ValidationError(_("Product not found"))
        
        product.ensure_one()
        
        # Increment view count
        product.increment_view_count()
        
        # Get recommended products
        recommended_products = product.get_recommended_products(limit=4)
        
        # Get related products
        related_products = product.related_product_ids.filtered(
            lambda p: p.sale_ok and p.website_published
        )[:4]
        
        # Get categories for navigation
        categories = self._get_categories()
        
        values = {
            'product': product,
            'recommended_products': recommended_products,
            'related_products': related_products,
            'categories': categories,
            'main_object': product,
        }
        
        return request.render('luc_khi_shop.product_detail', values)
    
    @http.route('/shop/luc_khi-analysis', type='json', auth='public', website=True)
    def luc_khi_analysis(self, product_ids, **kwargs):
        """Analyze Lục Khí profile based on selected products"""
        if not product_ids:
            return {'error': _('No products selected')}
        
        products = request.env['product.template'].browse(product_ids)
        element_counts = {}
        
        for product in products:
            for element in product.luc_khi_element_ids:
                element_code = element.code.lower()
                element_counts[element_code] = element_counts.get(element_code, 0) + 1
        
        if not element_counts:
            return {'error': _('No Lục Khí elements found in selected products')}
        
        # Find dominant element
        dominant_element = max(element_counts.items(), key=lambda x: x[1])[0]
        
        # Generate analysis
        analysis = self._generate_luc_khi_analysis(dominant_element, element_counts)
        
        return {
            'success': True,
            'dominant_element': dominant_element,
            'element_counts': element_counts,
            'analysis': analysis,
        }
    
    def _generate_luc_khi_analysis(self, dominant_element, element_counts):
        """Generate Lục Khí analysis for customer"""
        element_names = {
            'kim': 'Kim (Kim loại)',
            'moc': 'Mộc (Cây cối)',
            'thuy': 'Thủy (Nước)',
            'hoa': 'Hỏa (Lửa)',
            'tho': 'Thổ (Đất)',
            'phong': 'Phong (Gió)',
        }
        
        element_descriptions = {
            'kim': 'Bạn có xu hướng mạnh mẽ, quyết đoán và có khả năng tổ chức tốt.',
            'moc': 'Bạn là người sáng tạo, linh hoạt và luôn hướng đến sự phát triển.',
            'thuy': 'Bạn thông minh, có khả năng thích nghi tốt và giao tiếp khéo léo.',
            'hoa': 'Bạn đầy năng lượng, đam mê và có khả năng truyền cảm hứng cho người khác.',
            'tho': 'Bạn là người ổn định, đáng tin cậy và tạo được nền tảng vững chắc.',
            'phong': 'Bạn yêu tự do, thích thay đổi và có khả năng kết nối tốt.',
        }
        
        analysis = {
            'dominant_element': element_names.get(dominant_element, dominant_element),
            'description': element_descriptions.get(dominant_element, ''),
            'element_breakdown': []
        }
        
        total = sum(element_counts.values())
        for element, count in element_counts.items():
            percentage = (count / total) * 100
            analysis['element_breakdown'].append({
                'element': element_names.get(element, element),
                'count': count,
                'percentage': round(percentage, 1)
            })
        
        return analysis


class LucKhiShopCheckout(WebsiteSale):

    @http.route('/shop/cart/update', type='json', auth='public', website=True)
    def cart_update(self, product_id, add_qty=1, set_qty=0, **kw):
        """Update cart with Lục Khí analysis"""
        result = super(LucKhiShopCheckout, self).cart_update(product_id, add_qty, set_qty, **kw)

        # Update Lục Khí analysis after cart change
        order = request.website.sale_get_order()
        if order:
            order._analyze_luc_khi_profile()

        return result

    @http.route('/shop/cart/update_json', type='json', auth='public', website=True)
    def cart_update_json(self, product_id, line_id=None, add_qty=None, set_qty=None, display=True):
        """Update cart via JSON with Lục Khí analysis"""
        result = super(LucKhiShopCheckout, self).cart_update_json(product_id, line_id, add_qty, set_qty, display)

        # Update Lục Khí analysis after cart change
        order = request.website.sale_get_order()
        if order:
            order._analyze_luc_khi_profile()

        return result

    @http.route(['/shop/cart'], type='http', auth='public', website=True)
    def cart(self, **post):
        """Override cart page to add Lục Khí analysis"""
        response = super(LucKhiShopCheckout, self).cart(**post)

        if hasattr(response, 'qcontext') and response.qcontext.get('website_sale_order'):
            order = response.qcontext['website_sale_order']
            if order:
                # Add Lục Khí analysis to cart
                order._analyze_luc_khi_profile()

        return response
    
    @http.route(['/shop/checkout'], type='http', auth='public', website=True)
    def checkout(self, **post):
        """Override checkout to add Vietnamese address fields and Lục Khí analysis"""
        response = super(LucKhiShopCheckout, self).checkout(**post)

        # Add Vietnamese provinces/states
        if hasattr(response, 'qcontext'):
            response.qcontext['vietnam_states'] = request.env['res.country.state'].search([
                ('country_id.code', '=', 'VN')
            ], order='name')

            # Add Lục Khí analysis if order exists
            if response.qcontext.get('website_sale_order'):
                order = response.qcontext['website_sale_order']
                if order:
                    order._analyze_luc_khi_profile()
                    response.qcontext['luc_khi_analysis'] = order.luc_khi_profile_analysis

        return response

    @http.route('/shop/add_to_cart', type='json', auth='public', website=True)
    def add_to_cart(self, product_id, qty=1, **kw):
        """Add product to cart via AJAX"""
        try:
            product = request.env['product.product'].browse(int(product_id))
            if not product.exists() or not product.website_published:
                return {'success': False, 'error': 'Product not found'}

            # Add to cart
            order = request.website.sale_get_order(force_create=True)
            order_line = order._cart_update(
                product_id=int(product_id),
                add_qty=float(qty),
                set_qty=0
            )

            # Update Lục Khí analysis
            order._analyze_luc_khi_profile()

            return {
                'success': True,
                'cart_quantity': order.cart_quantity,
                'line_id': order_line.get('line_id'),
                'luc_khi_analysis': order.luc_khi_profile_analysis
            }

        except Exception as e:
            return {'success': False, 'error': str(e)}

    @http.route(['/shop/confirm_order'], type='http', auth='public', website=True)
    def confirm_order(self, **post):
        """Override order confirmation to handle Vietnamese compliance"""
        response = super(LucKhiShopCheckout, self).confirm_order(**post)
        
        # Add Vietnamese specific processing
        if hasattr(response, 'qcontext') and response.qcontext.get('order'):
            order = response.qcontext['order']
            
            # Set Vietnamese defaults
            if not order.invoice_vat:
                order.invoice_vat = True
            if not order.electronic_invoice:
                order.electronic_invoice = True
        
        return response
    
    @http.route(['/shop/payment'], type='http', auth='public', website=True)
    def payment(self, **post):
        """Override payment to add Vietnamese payment methods"""
        response = super(LucKhiShopCheckout, self).payment(**post)
        
        # Add Vietnamese payment gateway information
        if hasattr(response, 'qcontext'):
            response.qcontext['show_vietnamese_payment'] = True
            response.qcontext['vietnamese_payment_methods'] = [
                {
                    'code': 'vnpay',
                    'name': 'VNPay',
                    'description': 'Thanh toán qua VNPay',
                    'icon': '/luc_khi_shop/static/img/vnpay.png'
                },
                {
                    'code': 'momo',
                    'name': 'MoMo',
                    'description': 'Thanh toán qua MoMo ví',
                    'icon': '/luc_khi_shop/static/img/momo.png'
                },
                {
                    'code': 'cod',
                    'name': 'COD',
                    'description': 'Thanh toán khi nhận hàng (COD)',
                    'icon': '/luc_khi_shop/static/img/cod.png'
                }
            ]
        
        return response