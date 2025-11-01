import json
import logging
import hashlib
import hmac

from odoo import http
from odoo.http import request

_logger = logging.getLogger(__name__)


class Track123Controller(http.Controller):

    def _verify_webhook_signature(self, webhook_data):
        """Verify Track123 webhook signature for security"""
        try:
            verify_info = webhook_data.get('verify', {})
            received_signature = verify_info.get('signature')
            timestamp = verify_info.get('timestamp')
            
            if not received_signature or not timestamp:
                _logger.error("Missing signature or timestamp in webhook data")
                return False
            
            # Get API key from system parameters
            api_key = request.env['ir.config_parameter'].sudo().get_param('track123.api_key')
            if not api_key:
                _logger.error("Track123 API key not configured")
                return False
            
            # Generate expected signature
            # According to Track123 docs: SHA256 with API key and timestamp
            expected_signature = hashlib.sha256((api_key + timestamp).encode('utf-8')).hexdigest()
            
            # Compare signatures
            if received_signature != expected_signature:
                _logger.error(f"Webhook signature verification failed. Expected: {expected_signature}, Received: {received_signature}")
                return False
            
            return True
            
        except Exception as e:
            _logger.error(f"Error verifying webhook signature: {e}")
            return False

    @http.route('/delivery_custom/track123/webhook', type='json', auth='public', methods=['POST'], csrf=False)
    def track123_webhook(self, **kwargs):
        """Handle Track123 webhook notifications"""
        try:
            # Get webhook data from request
            webhook_data = request.jsonrequest
            
            if not webhook_data:
                _logger.error("Empty webhook data received")
                return {'status': 'error', 'message': 'Empty data'}
            
            # Verify webhook signature
            if not self._verify_webhook_signature(webhook_data):
                _logger.error("Webhook signature verification failed")
                return {'status': 'error', 'message': 'Invalid signature'}
            
            # Process the webhook data
            stock_picking = request.env['stock.picking']
            success = stock_picking.process_track123_webhook(webhook_data)
            
            if success:
                _logger.info("Track123 webhook processed successfully")
                return {'status': 'success', 'message': 'Webhook processed'}
            else:
                _logger.warning("Track123 webhook processing failed")
                return {'status': 'error', 'message': 'Processing failed'}
                
        except Exception as e:
            _logger.error(f"Error processing Track123 webhook: {e}")
            return {'status': 'error', 'message': str(e)}