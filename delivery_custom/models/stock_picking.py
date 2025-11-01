import json
import logging
import requests
import hashlib
import hmac
from datetime import datetime

from odoo import api, fields, models, _
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


class StockPicking(models.Model):
    _inherit = "stock.picking"

    # Track123 delivery status
    carrier_status = fields.Selection(
        selection=[
            ("INIT", "New shipments added that are pending to track"),
            ("NO_RECORD", "This shipment has no tracking information available yet"),
            ("INFO_RECEIVED", "The carrier has received a request from the shipper and is preparing to pick up the package"),
            ("IN_TRANSIT", "The shipment is in transit"),
            ("WAITING_DELIVERY", "The shipment is out for delivery or has arrived at the collection point for pick up"),
            ("DELIVERY_FAILED", "Carrier attempted to deliver but failed due to address issues, unavailability of the recipient, etc."),
            ("ABNORMAL", "Parcels are damaged, returned, customs detained, and other abnormal situations"),
            ("DELIVERED", "Parcel delivered successfully"),
            ("EXPIRED", "Parcel has no tracking information for 30 days since added"),
        ],
        string="Carrier Status",
        default="INIT",
        help="Track123 delivery status for logistics partners.",
        tracking=True,
    )

    # Track123 subdelivery status
    subdelivery_status = fields.Selection(
        selection=[
            # In Transit Sub-status
            ("IN_TRANSIT_01", "Parcel is on it's way"),
            ("IN_TRANSIT_02", "Parcels have arrived at the sorting center"),
            ("IN_TRANSIT_03", "Parcel customs clearance completed"),
            ("IN_TRANSIT_04", "Dispatching, the package has been encapsulated and will be sent to the airport soon"),
            ("IN_TRANSIT_05", "The package has been handed over to the airline and is being sent to the destination country"),
            ("IN_TRANSIT_06", "Landed, the package has arrived in the destination country"),
            ("IN_TRANSIT_07", "The parcel has arrived at the local post office or courier outlet and delivery will be arranged soon"),
            ("IN_TRANSIT_08", "The package is on the plane and the plane has departed"),
            # Waiting Delivery Sub-status
            ("WAITING_DELIVERY_01", "The parcel is out for delivery"),
            ("WAITING_DELIVERY_02", "The parcel has arrived at the collection point for receipts to pick up"),
            ("WAITING_DELIVERY_03", "The recipient requests a delayed delivery or the courier leaves a note after a failed delivery waiting for a second delivery"),
            # Delivered Sub-status
            ("DELIVERED_01", "Parcel delivered successfully"),
            ("DELIVERED_02", "Successful pick-up by the recipient at the collection point"),
            ("DELIVERED_03", "Parcel delivered and signed by the customer"),
            ("DELIVERED_04", "Parcel delivered to property owners, doormen, family members, or neighbors"),
            # Delivery Failed Sub-status
            ("DELIVERY_FAILED_01", "Delivery failed due to address related issues"),
            ("DELIVERY_FAILED_02", "Delivery failed due to the recipient was not at home"),
            ("DELIVERY_FAILED_03", "Delivery failed due to the recipient can not being reached"),
            ("DELIVERY_FAILED_04", "Delivery failed due to other reasons"),
            # Abnormal sub-status
            ("ABNORMAL_01", "Parcel unclaimed"),
            ("ABNORMAL_02", "Parcels detained by customs"),
            ("ABNORMAL_03", "The package is damaged, lost, or discarded"),
            ("ABNORMAL_04", "The order is canceled"),
            ("ABNORMAL_05", "The recipient refuses to accept the parcel"),
            ("ABNORMAL_06", "The return package has been successfully received by the sender"),
            ("ABNORMAL_07", "The package is on its way to the sender"),
            ("ABNORMAL_08", "Other exceptions"),
            # Info Received Sub-status
            ("INFO_RECEIVED_01", "The carrier has received a request from the shipper and is preparing to pick up the package"),
        ],
        string="Subdelivery Status",
        help="Track123 subdelivery status for detailed tracking information.",
        tracking=True,
    )

    # Track123 event information
    eventTime = fields.Datetime(string="Latest Event Time", help="Latest tracking event timestamp from Track123")
    eventDetail = fields.Text(string="Latest Event Detail", help="Latest tracking event description from Track123")

    # Recipient overrideable fields (default from partner_id)
    recipient_name = fields.Char(string="Recipient Name")
    recipient_state_id = fields.Many2one("res.country.state", string="State")
    recipient_city = fields.Char(string="City")
    recipient_street = fields.Char(string="Street")
    recipient_street2 = fields.Char(string="Street2")
    recipient_country_id = fields.Many2one("res.country", string="Country")

    # Carrier partner and tracking
    carrier_partner_id = fields.Many2one(
        "res.partner",
        string="Carrier",
        help="Logistics provider as a partner record.",
    )
    tracking_code = fields.Char(string="Tracking Code")
    tracking_link = fields.Char(string="Tracking Link")
    shipping_fee = fields.Monetary(string="Shipping Fee")
    currency_id = fields.Many2one(
        related="company_id.currency_id", store=True, readonly=True
    )

    # Link to vendor bills
    vendor_bill_count = fields.Integer(string="Vendor Bills", compute="_compute_vendor_bill_count")
    vendor_bill_ids = fields.One2many(
        "account.move", "picking_id", string="Vendor Bills",
        help="Vendor bills linked to this delivery.")

    def _compute_vendor_bill_count(self):
        Move = self.env['account.move'].sudo()
        for picking in self:
            picking.vendor_bill_count = Move.search_count([
                ('move_type', '=', 'in_invoice'),
                '|', ('picking_id', '=', picking.id), ('invoice_origin', '=', picking.name),
            ])

    def _prefill_recipient_from_partner(self, partner):
        return {
            'recipient_name': partner.name or False,
            'recipient_state_id': partner.state_id.id if partner.state_id else False,
            'recipient_city': partner.city or False,
            'recipient_street': partner.street or False,
            'recipient_street2': partner.street2 or False,
            'recipient_country_id': partner.country_id.id if partner.country_id else False,
        }

    @api.onchange("partner_id")
    def _onchange_partner_id_fill_recipient(self):
        for picking in self:
            partner = picking.partner_id
            if partner:
                vals = self._prefill_recipient_from_partner(partner)
                for k, v in vals.items():
                    setattr(picking, k, v)

    @api.model_create_multi
    def create(self, vals_list):
        records = super().create(vals_list)
        for rec, vals in zip(records, vals_list):
            # If recipient fields not provided, initialize from partner
            recipient_keys = {
                'recipient_name', 'recipient_state_id', 'recipient_city',
                'recipient_street', 'recipient_street2', 'recipient_country_id'
            }
            if rec.partner_id and not any(key in vals for key in recipient_keys):
                rec.write(self._prefill_recipient_from_partner(rec.partner_id))
        return records

    def write(self, vals):
        res = super().write(vals)
        # If partner changed and no explicit recipient overrides provided, refresh recipient from partner
        if 'partner_id' in vals:
            recipient_keys = {
                'recipient_name', 'recipient_state_id', 'recipient_city',
                'recipient_street', 'recipient_street2', 'recipient_country_id'
            }
            if not any(key in vals for key in recipient_keys):
                for rec in self:
                    if rec.partner_id:
                        rec.write(self._prefill_recipient_from_partner(rec.partner_id))
        return res

    @api.onchange("carrier_partner_id", "tracking_code")
    def _onchange_tracking_link(self):
        for picking in self:
            base = (picking.carrier_partner_id and picking.carrier_partner_id.website) or ""
            code = picking.tracking_code or ""
            picking.tracking_link = f"{base}{code}" if base or code else False

    def action_create_vendor_bill(self):
        self.ensure_one()
        picking = self
        if picking.vendor_bill_count:
            # Prevent duplicate creation; guide user to open existing bills
            raise UserError(_("This delivery is already linked to at least one vendor bill."))
        if not self.env['ir.module.module'].sudo().search([('name', '=', 'account'), ('state', '=', 'installed')], limit=1):
            raise UserError(_("The Accounting app is not installed."))

        vendor = picking.carrier_partner_id
        if not vendor:
            raise UserError(_("Please set a Carrier to use as Vendor for the bill."))

        company = picking.company_id
        journal = self.env['account.journal'].search([
            ('type', '=', 'purchase'),
            ('company_id', '=', company.id),
        ], limit=1)

        # Find delivery product by common names
        Product = self.env['product.product']
        product = Product.search([
            ('name', 'in', ['Delivery services', 'Dịch vụ vận chuyển']),
            ('purchase_ok', '=', True)
        ], limit=1)
        if not product:
            # Create a simple service product for delivery services
            product = Product.create({
                'name': 'Delivery services',
                'purchase_ok': True,
                'sale_ok': False,
                'detailed_type': 'service',
            })

        # Determine expense account
        expense_account = False
        if product:
            expense_account = product.property_account_expense_id or product.categ_id.property_account_expense_categ_id
        if not expense_account:
            expense_account = self.env['account.account'].search([
                ('company_id', '=', company.id),
                ('internal_group', '=', 'expense')
            ], limit=1)
        if not expense_account and not product:
            raise UserError(_("No expense account found to create vendor bill line. Please configure an expense account or a delivery product."))

        price = picking.shipping_fee or 0.0
        line_vals = {
            'name': _('Delivery service charge for %s', picking.name),
            'quantity': 1.0,
            'price_unit': price,
        }
        if product:
            line_vals['product_id'] = product.id
        if expense_account:
            line_vals['account_id'] = expense_account.id

        move_vals = {
            'move_type': 'in_invoice',
            'partner_id': vendor.id,
            'invoice_origin': picking.name,
            'picking_id': picking.id,
            'invoice_line_ids': [(0, 0, line_vals)],
            'company_id': company.id,
        }
        if journal:
            move_vals['journal_id'] = journal.id

        move = self.env['account.move'].create(move_vals)

        action = self.env.ref('account.action_move_in_invoice_type').read()[0]
        action.update({
            'views': [(self.env.ref('account.view_move_form').id, 'form')],
            'res_id': move.id,
            'domain': [('id', '=', move.id)],
            'context': {'default_move_type': 'in_invoice'},
            'target': 'current',
        })
        return action

    def action_open_vendor_bills(self):
        self.ensure_one()
        Move = self.env['account.move']
        domain = [('move_type', '=', 'in_invoice'), '|', ('picking_id', '=', self.id), ('invoice_origin', '=', self.name)]
        bills = Move.search(domain, limit=2)
        action = self.env.ref('account.action_move_in_invoice_type').read()[0]
        if len(bills) == 1:
            form = self.env.ref('account.view_move_form')
            action.update({
                'views': [(form.id, 'form')],
                'res_id': bills.id,
                'domain': [('id', '=', bills.id)],
                'context': {'default_move_type': 'in_invoice'},
                'target': 'current',
            })
        else:
            action.update({
                'domain': domain,
                'context': {'default_move_type': 'in_invoice', 'search_default_draft': 1},
            })
        return action

    def _get_track123_api_key(self):
        """Get Track123 API key from system parameters"""
        api_key = self.env['ir.config_parameter'].sudo().get_param('track123.api_key')
        if not api_key:
            raise UserError(_("Track123 API key is not configured. Please set it in Settings > Technical > System Parameters with key 'track123.api_key'"))
        return api_key

    def _call_track123_api(self, endpoint, data):
        """Make API call to Track123"""
        api_key = self._get_track123_api_key()
        url = f"https://api.track123.com/gateway/open-api/tk/v2.1/{endpoint}"
        
        headers = {
            'Content-Type': 'application/json',
            'Track123-Api-Secret': api_key
        }
        
        try:
            _logger.info(f"Track123 API request to {url}: {data}")
            response = requests.post(url, json=data, headers=headers, timeout=30)
            response.raise_for_status()
            result = response.json()
            _logger.info(f"Track123 API response: {result}")
            return result
        except requests.exceptions.RequestException as e:
            _logger.error(f"Track123 API call failed: {e}")
            if hasattr(e, 'response') and e.response is not None:
                try:
                    error_detail = e.response.json()
                    _logger.error(f"Track123 API error response: {error_detail}")
                except:
                    _logger.error(f"Track123 API error response text: {e.response.text}")
            raise UserError(_("Failed to connect to Track123 API: %s") % str(e))

    def action_track123_register(self):
        """Register tracking with Track123 and immediately get tracking info"""
        self.ensure_one()
        
        if not self.tracking_code:
            raise UserError(_("Tracking code is required to register with Track123"))
        
        # Register tracking - must be array directly, not wrapped in object
        # Note: courierCode empty string or omitted = auto-detect carrier
        register_data = [
            {
                "trackNo": self.tracking_code,
                "courierCode": ""  # Empty string = auto-detect carrier
            }
        ]
        
        try:
            result = self._call_track123_api('track/import', register_data)
            _logger.info(f"Track123 registration result: {result}")
            
            # Check registration result
            # Track123 success code is '00000', not '0'
            if result.get('code') == '00000':
                # Success - check if tracking was accepted
                accepted = result.get('data', {}).get('accepted', [])
                rejected = result.get('data', {}).get('rejected', [])
                
                if accepted:
                    _logger.info(f"Tracking {self.tracking_code} registered successfully")
                    message = _('Tracking registered successfully with Track123')
                    get_tracking = True
                elif rejected:
                    error_msg = rejected[0].get('error', {}).get('msg', 'Unknown error')
                    _logger.warning(f"Tracking {self.tracking_code} rejected: {error_msg}")
                    
                    # Check if tracking already exists - common error messages
                    already_exists_keywords = [
                        'already', 'imported', 'exists', 'duplicate',
                        'đã được', 'tồn tại'  # Vietnamese keywords
                    ]
                    is_already_exists = any(keyword in error_msg.lower() for keyword in already_exists_keywords)
                    
                    if is_already_exists:
                        _logger.info(f"Tracking {self.tracking_code} already exists, fetching tracking info instead")
                        message = _('Tracking already registered. Fetching latest tracking info...')
                        get_tracking = True
                    else:
                        # Other rejection error - still try to get tracking but show error
                        message = _('Tracking registration issue: %s. Attempting to fetch info...') % error_msg
                        get_tracking = True
                else:
                    message = _('Tracking registered with Track123')
                    get_tracking = True
                
                # Try to get tracking info
                if get_tracking:
                    try:
                        self.action_track123_get_tracking()
                    except Exception as get_error:
                        _logger.warning(f"Could not get tracking info: {get_error}")
                        # If registration was successful, this is OK (data may not be available yet)
                        if not accepted and rejected:
                            # If registration failed and get also failed, re-raise the error
                            raise
                
                return {
                    'type': 'ir.actions.client',
                    'tag': 'display_notification',
                    'params': {
                        'title': _('Success'),
                        'message': message,
                        'type': 'success',
                    }
                }
            else:
                error_msg = result.get('msg', 'Unknown error')
                raise UserError(_('Track123 API returned error: %s') % error_msg)
            
        except UserError:
            raise
        except Exception as e:
            _logger.error(f"Track123 registration failed: {e}", exc_info=True)
            raise UserError(_("Failed to register tracking with Track123: %s") % str(e))

    def action_track123_get_tracking(self):
        """Get tracking information from Track123"""
        self.ensure_one()
        
        if not self.tracking_code:
            raise UserError(_("Tracking code is required to get tracking information"))
        
        query_data = {
            "trackNoInfos": [
                {
                    "trackNo": self.tracking_code
                }
            ]
        }
        
        try:
            result = self._call_track123_api('track/query', query_data)
            _logger.info(f"Track123 query result for {self.tracking_code}: {result}")
            
            # Check response code
            # Track123 success code is '00000', not '0'
            if result.get('code') == '00000':
                # Success - check if we have tracking data
                # Note: query response format is different from import
                # {'accepted': {'content': [...], 'totalElements': '1'}, 'rejected': []}
                accepted = result.get('data', {}).get('accepted')
                
                if accepted and isinstance(accepted, dict):
                    # Query response: accepted is object with 'content' array
                    content = accepted.get('content', [])
                    if content and len(content) > 0:
                        tracking_data = content[0]
                        self._update_tracking_from_api(tracking_data)
                        _logger.info(f"Updated tracking data for {self.tracking_code}")
                    else:
                        _logger.warning(f"No tracking content found for {self.tracking_code}")
                        raise UserError(_("No tracking data available yet. Please try again later."))
                elif accepted and isinstance(accepted, list) and len(accepted) > 0:
                    # Import response: accepted is array directly (fallback)
                    tracking_data = accepted[0]
                    self._update_tracking_from_api(tracking_data)
                    _logger.info(f"Updated tracking data for {self.tracking_code}")
                else:
                    # Check rejected
                    rejected = result.get('data', {}).get('rejected', [])
                    if rejected:
                        error_msg = rejected[0].get('error', {}).get('msg', 'Unknown error')
                        _logger.warning(f"Tracking query rejected for {self.tracking_code}: {error_msg}")
                        raise UserError(_("Track123 cannot find tracking: %s") % error_msg)
                    else:
                        _logger.warning(f"No tracking data found for {self.tracking_code}")
                        raise UserError(_("No tracking data available yet. Please try again later."))
            else:
                error_msg = result.get('msg', 'Unknown error')
                raise UserError(_('Track123 API returned error: %s') % error_msg)
                
        except UserError:
            raise
        except Exception as e:
            _logger.error(f"Failed to get tracking from Track123: {e}", exc_info=True)
            raise UserError(_("Failed to get tracking information from Track123: %s") % str(e))

    def _update_tracking_from_api(self, tracking_data):
        """Update picking fields from Track123 API response"""
        # Get status from root level
        transit_status = tracking_data.get('transitStatus')
        transit_sub_status = tracking_data.get('transitSubStatus')
        
        values = {}
        
        # Update carrier status if available
        if transit_status:
            values['carrier_status'] = transit_status
        
        # Update subdelivery status if available
        if transit_sub_status:
            values['subdelivery_status'] = transit_sub_status
        
        # Get latest tracking details
        local_logistics = tracking_data.get('localLogisticsInfo', {})
        tracking_details = local_logistics.get('trackingDetails', [])
        
        if tracking_details:
            latest_detail = tracking_details[0]  # First item is the latest
            
            # Parse UTC time and convert to Vietnam timezone (UTC+7)
            event_time_utc = latest_detail.get('eventTimeZeroUTC')
            if event_time_utc:
                parsed_time = self._parse_track123_utc_datetime(event_time_utc)
                if parsed_time:
                    values['eventTime'] = parsed_time
            
            # Update event detail
            event_detail = latest_detail.get('eventDetail')
            if event_detail:
                values['eventDetail'] = event_detail
        
        if values:
            self.write(values)
            _logger.info(f"Updated tracking fields: {list(values.keys())}")

    def _parse_track123_utc_datetime(self, datetime_str):
        """Parse Track123 UTC datetime (eventTimeZeroUTC) and convert to Vietnam timezone
        
        Track123 eventTimeZeroUTC format: "2025-10-29T04:44:41Z" (ISO 8601 UTC)
        Convert to Vietnam timezone (Asia/Ho_Chi_Minh, UTC+7)
        Return naive datetime for Odoo (Odoo stores datetime in UTC internally)
        """
        if not datetime_str:
            return False
        
        try:
            # Parse ISO 8601 UTC format: "2025-10-29T04:44:41Z"
            # Remove 'Z' and parse
            if datetime_str.endswith('Z'):
                datetime_str = datetime_str[:-1]
            
            # Parse as datetime
            from datetime import datetime as dt_class
            utc_dt = dt_class.strptime(datetime_str, '%Y-%m-%dT%H:%M:%S')
            
            # Odoo stores all datetime fields in UTC internally
            # So we return the UTC datetime as-is (naive)
            # Odoo will handle timezone conversion for display
            return utc_dt
            
        except ValueError as e:
            _logger.warning(f"Failed to parse UTC datetime '{datetime_str}': {e}")
            return False

    def process_track123_webhook(self, webhook_data):
        """Process webhook data from Track123"""
        try:
            tracking_info = webhook_data.get('data', {})
            track_no = tracking_info.get('trackNo')
            
            if not track_no:
                _logger.error("Webhook data missing trackNo")
                return False
            
            # Find the picking with this tracking code
            picking = self.search([('tracking_code', '=', track_no)], limit=1)
            if not picking:
                _logger.warning(f"No picking found for tracking code: {track_no}")
                return False
            
            # Update picking with webhook data
            picking._update_tracking_from_api(tracking_info)
            
            _logger.info(f"Updated picking {picking.id} from webhook for tracking {track_no}")
            return True
            
        except Exception as e:
            _logger.error(f"Error processing Track123 webhook: {e}")
            return False
