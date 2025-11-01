# Delivery Custom with Track123 Integration

Summary: Extends Delivery Orders (stock.picking) with shipping workflow, recipient override fields, carrier/tracking info, vendor bill creation, Track123 integration, and a Bills tab. Designed for Odoo 18 CE.

## Features

### Track123 Integration
- **Carrier Status**: Updated to match Track123's 9 standard delivery statuses (INIT, NO_RECORD, INFO_RECEIVED, IN_TRANSIT, WAITING_DELIVERY, DELIVERY_FAILED, ABNORMAL, DELIVERED, EXPIRED)
- **Subdelivery Status**: Detailed sub-status options for precise tracking (30+ sub-statuses across all main statuses)
- **Event Tracking**: Latest event time and detail information from Track123
- **API Integration**: Register and query tracking information with Track123 API
- **Webhook Support**: Real-time updates from Track123 with signature verification
- **Track123 Button**: One-click tracking registration and immediate status fetch

### Original Features
- Carrier Status (`carrier_status`): Track123 standard statuses with badges on list/form
- Shipping Details tab (first tab):
  - Recipient fields (editable, stored): name, street, street2, city, state, country.
    - Prefilled from `partner_id` when creating or changing Delivery Address.
    - Persist after edits (no silent overrides).
  - Carrier partner (`carrier_partner_id`) and Shipping Fee (`shipping_fee`).
  - Tracking Code and Tracking Link (url): link auto‑composed as `carrier website + tracking code` on change.
- Vendor Bills integration:
  - Create Delivery Bill button (header): visible only when no linked bills yet.
  - Auto‑create or re‑use product "Delivery services" (service, purchase_ok) if missing.
  - Bill line: Qty=1, Unit Price=`shipping_fee`, product set if available; expense account resolved from product/category or a fallback expense account.
  - Links: `account.move.picking_id = this picking` and `invoice_origin = picking.name`.
  - Bills tab (after Shipping Details): visible only when bills exist; lists linked vendor bills.
  - Smart button "Delivery" on the vendor bill (top-right, beside Payments/Purchases) opens the linked Delivery; hidden when not linked.
- List enhancements:
  - Adds `carrier_status` badge column after core `state` in the picking list.

## Behavior details

- Recipient persistence:
  - On create: if recipient fields not provided, they are initialized from `partner_id`.
  - On write: changing `partner_id` will refresh recipient from the new partner only if you did not pass explicit recipient overrides in the same write.
  - On form onchange of `partner_id`: recipient fields are refreshed to match the newly selected Delivery Address.
- Create Delivery Bill safety:
  - If linked bills already exist, the action is blocked with a warning and the button is hidden; use Bills tab instead.

## Installation

Dependencies: `stock`, `contacts`, `account`, `web`.

```
docker compose run --rm web \
  odoo -c /etc/odoo/odoo.conf -d <DB> -i delivery_custom --stop-after-init
```

## Configuration

### Track123 API Setup
1. Go to **Settings > Technical > System Parameters**
2. Create or update parameter with key: `track123.api_key`
3. Enter your Track123 API key as the value

### Webhook Configuration
1. In your Track123 account, set webhook URL to:
   ```
   https://your-odoo-domain.com/delivery_custom/track123/webhook
   ```
2. Select tracking update events
3. Save webhook configuration

## Usage

1) Open a Delivery Order.
2) Fill/adjust Shipping Details (Recipient, Carrier, Fee, Tracking).
3) Click “Create Delivery Bill” to draft a bill from shipping cost. Once created, the Bills tab appears and the create button hides.
4) Manage the bill normally (post/pay). Use the “Delivery” smart button on the bill or Bills tab back on the delivery.

## Technical Notes

- Models (`stock.picking`):
  - `carrier_status` (Selection) – displayed as badge.
  - `recipient_*` fields (Char / Many2one): stored, editable.
  - `carrier_partner_id` (Many2one), `tracking_code` (Char), `tracking_link` (Char, url), `shipping_fee` (Monetary).
  - `vendor_bill_ids` (O2M to `account.move`), `vendor_bill_count` (compute).
  - Actions: `action_create_vendor_bill()`, `action_open_vendor_bills()`.
- Models (`account.move`):
  - `picking_id` (M2O to `stock.picking`), action `action_open_picking()`.
- Views:
  - Form picking: header button, Shipping Details tab, Bills tab.
  - Tree picking: add `carrier_status` next to `state`.
  - Form move (vendor bill): smart button “Delivery” beside Payments/Purchases; hidden when no related Delivery.

## Known limitations

- The auto tracking link is a simple concatenation of `carrier_partner_id.website + tracking_code`. For carriers with structured tracking URLs, add a dedicated base URL field on `res.partner` or a small mapping model.
- If your accounting setup lacks an expense account and no delivery product exists, the module will ask for configuration instead of guessing.
