# -*- coding: utf-8 -*-
import hashlib
import hmac
import json
import requests
import urllib.parse
from datetime import datetime
from odoo import http, _
from odoo.http import request
from odoo.addons.website_sale.controllers.main import WebsiteSale


class LucKhiPaymentController(WebsiteSale):

    @http.route('/shop/payment/vnpay/create', type='http', auth='public', website=True, methods=['POST'])
    def vnpay_create_payment(self, **post):
        """Create VNPay payment URL"""
        order = request.website.sale_get_order()
        if not order:
            return request.redirect('/shop/cart')

        # VNPay configuration (should be in system parameters)
        vnp_TmnCode = request.env['ir.config_parameter'].sudo().get_param('luc_khi_shop.vnpay_tmn_code', '')
        vnp_HashSecret = request.env['ir.config_parameter'].sudo().get_param('luc_khi_shop.vnpay_hash_secret', '')
        vnp_Url = request.env['ir.config_parameter'].sudo().get_param('luc_khi_shop.vnpay_url', 'https://sandbox.vnpayment.vn/paymentv2/vpcpay.html')
        vnp_ReturnUrl = request.httprequest.host_url + 'shop/payment/vnpay/return'

        if not all([vnp_TmnCode, vnp_HashSecret, vnp_Url]):
            request.session['error_message'] = _('VNPay chưa được cấu hình')
            return request.redirect('/shop/payment')

        # Create payment parameters
        vnp_Params = {
            'vnp_Version': '2.1.0',
            'vnp_Command': 'pay',
            'vnp_TmnCode': vnp_TmnCode,
            'vnp_Amount': int(order.amount_total * 100),  # Amount in smallest currency unit
            'vnp_CurrCode': 'VND',
            'vnp_TxnRef': str(order.id),
            'vnp_OrderInfo': f'Thanh toan don hang {order.name}',
            'vnp_OrderType': 'billpayment',
            'vnp_Locale': 'vn',
            'vnp_ReturnUrl': vnp_ReturnUrl,
            'vnp_IpAddr': request.httprequest.remote_addr,
            'vnp_CreateDate': datetime.now().strftime('%Y%m%d%H%M%S'),
        }

        # Sort parameters
        vnp_Params = dict(sorted(vnp_Params.items()))

        # Create hash
        hash_data = '&'.join([f'{key}={value}' for key, value in vnp_Params.items()])
        vnp_SecureHash = hmac.new(
            vnp_HashSecret.encode('utf-8'),
            hash_data.encode('utf-8'),
            hashlib.sha512
        ).hexdigest()

        vnp_Params['vnp_SecureHash'] = vnp_SecureHash

        # Create payment URL
        payment_url = vnp_Url + '?' + urllib.parse.urlencode(vnp_Params)

        return request.redirect(payment_url)

    @http.route('/shop/payment/vnpay/return', type='http', auth='public', website=True)
    def vnpay_return(self, **get):
        """Handle VNPay return"""
        vnp_HashSecret = request.env['ir.config_parameter'].sudo().get_param('luc_khi_shop.vnpay_hash_secret', '')

        # Verify signature
        vnp_SecureHash = get.pop('vnp_SecureHash', '')
        sorted_params = dict(sorted(get.items()))
        hash_data = '&'.join([f'{key}={value}' for key, value in sorted_params.items()])

        calculated_hash = hmac.new(
            vnp_HashSecret.encode('utf-8'),
            hash_data.encode('utf-8'),
            hashlib.sha512
        ).hexdigest()

        if vnp_SecureHash != calculated_hash:
            request.session['error_message'] = _('Chữ ký không hợp lệ')
            return request.redirect('/shop/payment')

        # Process payment result
        order_id = get.get('vnp_TxnRef')
        response_code = get.get('vnp_ResponseCode')

        order = request.env['sale.order'].sudo().browse(int(order_id))
        if not order.exists():
            request.session['error_message'] = _('Đơn hàng không tồn tại')
            return request.redirect('/shop')

        if response_code == '00':  # Success
            # Confirm order and create payment
            order.action_confirm()

            # Create payment record
            payment_method = request.env['account.payment.method'].search([
                ('code', '=', 'vnpay')
            ], limit=1)

            if payment_method:
                payment_vals = {
                    'payment_type': 'inbound',
                    'partner_type': 'customer',
                    'partner_id': order.partner_id.id,
                    'amount': order.amount_total,
                    'currency_id': order.currency_id.id,
                    'payment_date': datetime.now().date(),
                    'communication': f'VNPay - {order.name}',
                    'payment_method_id': payment_method.id,
                    'journal_id': payment_method.journal_id.id,
                }
                payment = request.env['account.payment'].sudo().create(payment_vals)
                payment.action_post()

                # Mark as paid
                order.invoice_ids.write({'payment_state': 'paid'})

            request.session['success_message'] = _('Thanh toán thành công!')
            return request.redirect('/shop/confirmation')

        else:
            request.session['error_message'] = _('Thanh toán thất bại')
            return request.redirect('/shop/payment')

    @http.route('/shop/payment/momo/create', type='http', auth='public', website=True, methods=['POST'])
    def momo_create_payment(self, **post):
        """Create MoMo payment"""
        order = request.website.sale_get_order()
        if not order:
            return request.redirect('/shop/cart')

        # MoMo configuration
        momo_endpoint = request.env['ir.config_parameter'].sudo().get_param('luc_khi_shop.momo_endpoint', '')
        momo_partner_code = request.env['ir.config_parameter'].sudo().get_param('luc_khi_shop.momo_partner_code', '')
        momo_access_key = request.env['ir.config_parameter'].sudo().get_param('luc_khi_shop.momo_access_key', '')
        momo_secret_key = request.env['ir.config_parameter'].sudo().get_param('luc_khi_shop.momo_secret_key', '')
        momo_return_url = request.httprequest.host_url + 'shop/payment/momo/return'

        if not all([momo_endpoint, momo_partner_code, momo_access_key, momo_secret_key]):
            request.session['error_message'] = _('MoMo chưa được cấu hình')
            return request.redirect('/shop/payment')

        # Create MoMo request
        request_id = str(order.id) + str(int(datetime.now().timestamp()))
        order_info = f'Thanh toan don hang {order.name}'
        amount = str(int(order.amount_total))
        order_id = str(order.id)
        request_type = 'captureWallet'

        # Create raw signature
        raw_signature = f"accessKey={momo_access_key}&amount={amount}&extraData=&ipnUrl={momo_return_url}&orderId={order_id}&orderInfo={order_info}&partnerCode={momo_partner_code}&redirectUrl={momo_return_url}&requestId={request_id}&requestType={request_type}"

        signature = hmac.new(
            momo_secret_key.encode('utf-8'),
            raw_signature.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()

        # Create request data
        data = {
            'partnerCode': momo_partner_code,
            'accessKey': momo_access_key,
            'requestId': request_id,
            'amount': amount,
            'orderId': order_id,
            'orderInfo': order_info,
            'redirectUrl': momo_return_url,
            'ipnUrl': momo_return_url,
            'extraData': '',
            'requestType': request_type,
            'signature': signature,
            'lang': 'vi'
        }

        try:
            response = requests.post(momo_endpoint, json=data, timeout=30)
            response_data = response.json()

            if response_data.get('resultCode') == 0:
                pay_url = response_data.get('payUrl')
                return request.redirect(pay_url)
            else:
                request.session['error_message'] = response_data.get('message', _('Lỗi thanh toán MoMo'))
                return request.redirect('/shop/payment')

        except Exception as e:
            request.session['error_message'] = _('Lỗi kết nối MoMo')
            return request.redirect('/shop/payment')

    @http.route('/shop/payment/momo/return', type='http', auth='public', website=True)
    def momo_return(self, **get):
        """Handle MoMo return"""
        result_code = get.get('resultCode')
        order_id = get.get('orderId')

        order = request.env['sale.order'].sudo().browse(int(order_id))
        if not order.exists():
            request.session['error_message'] = _('Đơn hàng không tồn tại')
            return request.redirect('/shop')

        if result_code == '0':  # Success
            # Confirm order and create payment
            order.action_confirm()

            # Create payment record
            payment_method = request.env['account.payment.method'].search([
                ('code', '=', 'momo')
            ], limit=1)

            if payment_method:
                payment_vals = {
                    'payment_type': 'inbound',
                    'partner_type': 'customer',
                    'partner_id': order.partner_id.id,
                    'amount': order.amount_total,
                    'currency_id': order.currency_id.id,
                    'payment_date': datetime.now().date(),
                    'communication': f'MoMo - {order.name}',
                    'payment_method_id': payment_method.id,
                    'journal_id': payment_method.journal_id.id,
                }
                payment = request.env['account.payment'].sudo().create(payment_vals)
                payment.action_post()

                # Mark as paid
                order.invoice_ids.write({'payment_state': 'paid'})

            request.session['success_message'] = _('Thanh toán thành công!')
            return request.redirect('/shop/confirmation')

        else:
            request.session['error_message'] = _('Thanh toán thất bại')
            return request.redirect('/shop/payment')

    @http.route('/shop/payment/cod/confirm', type='http', auth='public', website=True, methods=['POST'])
    def cod_confirm(self, **post):
        """Handle Cash on Delivery confirmation"""
        order = request.website.sale_get_order()
        if not order:
            return request.redirect('/shop/cart')

        # Set payment method to COD
        order.write({
            'payment_term_id': request.env.ref('account.account_payment_term_immediate').id,
            'note': 'Thanh toán khi nhận hàng (COD)'
        })

        # Confirm order
        order.action_confirm()

        request.session['success_message'] = _('Đơn hàng đã được xác nhận. Bạn sẽ thanh toán khi nhận hàng!')
        return request.redirect('/shop/confirmation')