# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from datetime import datetime, timedelta


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    # Vietnamese specific fields
    customer_tax_code = fields.Char('Tax Code', help='Vietnamese tax identification code')
    customer_address_vietnam = fields.Text('Vietnamese Address Format', compute='_compute_vietnam_address', store=True)
    
    # Lục Khí analysis
    luc_khi_analysis = fields.Text('Lục Khí Analysis', help='Analysis of customer Lục Khí profile based on purchases')
    luc_khi_recommendations = fields.Html('Lục Khí Recommendations', help='Product recommendations based on Lục Khí analysis')
    
    # Vietnamese compliance
    invoice_vat = fields.Boolean('VAT Invoice Required', default=True)
    electronic_invoice = fields.Boolean('Electronic Invoice', default=True)
    
    # Delivery information
    delivery_province = fields.Many2one('res.country.state', 'Province/City')
    delivery_district = fields.Char('District')
    delivery_ward = fields.Char('Ward')
    
    @api.depends('partner_id', 'partner_shipping_id')
    def _compute_vietnam_address(self):
        for order in self:
            if order.partner_shipping_id:
                address_parts = []
                if order.partner_shipping_id.street:
                    address_parts.append(order.partner_shipping_id.street)
                if order.delivery_ward:
                    address_parts.append(f'Phường/Xã {order.delivery_ward}')
                if order.delivery_district:
                    address_parts.append(f'Quận/Huyện {order.delivery_district}')
                if order.delivery_province:
                    address_parts.append(order.delivery_province.name)
                if order.partner_shipping_id.country_id:
                    address_parts.append(order.partner_shipping_id.country_id.name)
                
                order.customer_address_vietnam = ', '.join(address_parts)
            else:
                order.customer_address_vietnam = ''
    
    def action_confirm(self):
        """Override to add Lục Khí analysis"""
        result = super(SaleOrder, self).action_confirm()
        self._analyze_luc_khi_profile()
        return result
    
    def _analyze_luc_khi_profile(self):
        """Analyze customer Lục Khí profile based on order items"""
        if not self.order_line:
            return
        
        element_counts = {}
        for line in self.order_line:
            if line.product_id.luc_khi_element:
                element = line.product_id.luc_khi_element
                element_counts[element] = element_counts.get(element, 0) + 1
        
        if element_counts:
            # Find dominant element
            dominant_element = max(element_counts, key=element_counts.get)
            
            # Generate analysis
            analysis = self._generate_luc_khi_analysis(dominant_element, element_counts)
            self.luc_khi_analysis = analysis
            
            # Generate recommendations
            recommendations = self._generate_luc_khi_recommendations(dominant_element)
            self.luc_khi_recommendations = recommendations
    
    def _generate_luc_khi_analysis(self, dominant_element, element_counts):
        """Generate Lục Khí analysis text"""
        element_names = {
            'kim': 'Kim (Kim loại)',
            'moc': 'Mộc (Cây cối)',
            'thuy': 'Thủy (Nước)',
            'hoa': 'Hỏa (Lửa)',
            'tho': 'Thổ (Đất)',
            'phong': 'Phong (Gió)',
        }
        
        analysis = f"Phân tích hồ sơ Lục Khí của khách hàng:\n\n"
        analysis += f"Yếu tố chủ đạo: {element_names.get(dominant_element, dominant_element)}\n\n"
        analysis += "Phân bổ các yếu tố:\n"
        
        for element, count in element_counts.items():
            percentage = (count / sum(element_counts.values())) * 100
            analysis += f"- {element_names.get(element, element)}: {count} sản phẩm ({percentage:.1f}%)\n"
        
        return analysis
    
    def _generate_luc_khi_recommendations(self, dominant_element):
        """Generate product recommendations based on dominant element"""
        recommendations = "<h4>Gợi ý sản phẩm dựa trên yếu tố Lục Khí của bạn</h4>"
        
        element_recommendations = {
            'kim': {
                'title': 'Yếu tố Kim - Cần sự cân bằng với Mộc và Thủy',
                'products': ['Sản phẩm gỗ mộc', 'Đồ trang trí nước', 'Vật dụng kim loại tinh xảo'],
                'advice': 'Người có yếu tố Kim mạnh nên bổ sung các yếu tố Mộc để tăng sự sáng tạo và Thủy để tăng sự linh hoạt.'
            },
            'moc': {
                'title': 'Yếu tố Mộc - Cần sự hỗ trợ từ Thổ và Hỏa',
                'products': ['Đồ gốm sứ', 'Sản phẩm ánh sáng', 'Vật liệu tự nhiên'],
                'advice': 'Người có yếu tố Mộc mạnh nên bổ sung Thổ để tạo nền tảng vững chắc và Hỏa để tăng năng lượng.'
            },
            'thuy': {
                'title': 'Yếu tố Thủy - Cần sự cân bằng với Kim và Mộc',
                'products': ['Đồ kim loại', 'Sản phẩm gỗ', 'Vật dụng trang trí'],
                'advice': 'Người có yếu tố Thủy mạnh nên bổ sung Kim để tăng sự quyết đoán và Mộc để phát triển.'
            },
            'hoa': {
                'title': 'Yếu tố Hỏa - Cần sự hỗ trợ từ Thổ và Kim',
                'products': ['Đồ gốm', 'Sản phẩm kim loại', 'Vật liệu cách nhiệt'],
                'advice': 'Người có yếu tố Hỏa mạnh nên bổ sung Thổ để ổn định và Kim để tăng sự tập trung.'
            },
            'tho': {
                'title': 'Yếu tố Thổ - Cần sự cân bằng với Kim và Mộc',
                'products': ['Đồ kim loại', 'Sản phẩm gỗ', 'Vật liệu tự nhiên'],
                'advice': 'Người có yếu tố Thổ mạnh nên bổ sung Kim để tăng sự linh hoạt và Mộc để phát triển.'
            },
            'phong': {
                'title': 'Yếu tố Phong - Cần sự hỗ trợ từ tất cả các yếu tố',
                'products': ['Sản phẩm đa dạng', 'Bộ sưu tập', 'Vật dụng trang trí'],
                'advice': 'Người có yếu tố Phong mạnh nên cân bằng tất cả các yếu tố khác để tạo sự hài hòa.'
            },
        }
        
        rec = element_recommendations.get(dominant_element, {})
        if rec:
            recommendations += f"<p><strong>{rec.get('title', '')}</strong></p>"
            recommendations += f"<p>{rec.get('advice', '')}</p>"
            recommendations += "<h5>Sản phẩm gợi ý:</h5><ul>"
            
            for product in rec.get('products', []):
                recommendations += f"<li>{product}</li>"
            
            recommendations += "</ul>"
        
        return recommendations


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    # Lục Khí specific fields
    luc_khi_element = fields.Selection(
        related='product_id.luc_khi_element',
        string='Lục Khí Element',
        readonly=True
    )
    
    luc_khi_benefit = fields.Text('Lục Khí Benefit', help='Specific benefit of this product for customer Lục Khí profile')
    
    @api.onchange('product_id')
    def _onchange_product_id_luc_khi(self):
        """Update Lục Khí information when product changes"""
        if self.product_id:
            # Auto-generate benefit based on product Lục Khí element
            benefits = {
                'kim': 'Tăng cường sự quyết đoán, tổ chức và khả năng lãnh đạo',
                'moc': 'Thúc đẩy sự sáng tạo, phát triển và linh hoạt',
                'thuy': 'Cải thiện sự thông minh, thích nghi và giao tiếp',
                'hoa': 'Tăng năng lượng, đam mê và khả năng truyền cảm hứng',
                'tho': 'Tạo sự ổn định, vững chãi và nền tảng',
                'phong': 'Thúc đẩy sự tự do, thay đổi và kết nối',
            }
            
            if self.product_id.luc_khi_element:
                self.luc_khi_benefit = benefits.get(self.product_id.luc_khi_element, '')


class AccountMove(models.Model):
    _inherit = 'account.move'

    # Vietnamese invoice fields
    invoice_type_vietnam = fields.Selection([
        ('vat', 'Hóa đơn GTGT'),
        ('retail', 'Hóa đơn bán lẻ'),
        ('export', 'Hóa đơn xuất khẩu'),
    ], string='Invoice Type Vietnam', default='vat')
    
    electronic_invoice_code = fields.Char('Electronic Invoice Code')
    electronic_invoice_date = fields.Datetime('Electronic Invoice Date')
    
    def action_post(self):
        """Override to handle electronic invoice generation"""
        result = super(AccountMove, self).action_post()
        
        if self.move_type in ['out_invoice', 'out_refund'] and self.electronic_invoice:
            self._generate_electronic_invoice()
        
        return result
    
    def _generate_electronic_invoice(self):
        """Generate electronic invoice for Vietnamese compliance"""
        # This would integrate with Vietnamese electronic invoice system
        self.electronic_invoice_code = f"INV-{self.id}-{datetime.now().strftime('%Y%m%d%H%M%S')}"
        self.electronic_invoice_date = datetime.now()