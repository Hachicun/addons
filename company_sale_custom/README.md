# Company Sale Custom

Summary: Lightweight customization of Sales Orders for Odoo 18 CE. Adds payment progress information from invoices, Delivery/Manufacturing/Invoices/Related Invoices tabs, guarded invoice creation, a per‑order Manufacturing Formula, and convenient list/search tweaks.

## Features

- Sale Order field `payment_status` (stored, computed):
  - Values: `paid`, `not_paid`, `no_invoice`.
  - Computation: from related customer invoices/credit notes (`account.move` with `move_type` in `('out_invoice','out_refund')`). If all are `payment_state='paid'` → `paid`; none → `no_invoice`; otherwise `not_paid`.
- Sale Order field `delivery_status_display` (computed, non‑stored):
  - Human‑friendly aggregation of related outgoing pickings states. This complements core `sale_stock.delivery_status` and is labeled "Delivery Progress" to avoid label conflicts.
- Delivery / Manufacturing / Invoices / Related Invoices tabs (form)
  - Delivery: shows related outgoing deliveries with carrier status, fee, tracking (requires `delivery_custom`). Hidden if none.
  - Manufacturing: shows linked MOs (origin = SO number) with quick open button; hidden if none.
  - Invoices: shows invoices linked to this Sales Order; hidden if none.
  - Related Invoices: shows customer invoices of the Contact's Related Contacts (from `contact_custom`). Sorted by payment status (Not Paid first), then most recent. Limited to 5 for performance; includes "View Related Invoices" to open the full list.
- Guarded Create Invoice button
  - Replace default “Create Invoice” with a guarded method. If the SO already has invoices, it raises a warning to avoid duplicates.
- Formula (per Sales Order)
  - Text area shown under Order Lines when SO contains products to manufacture (by product routes or custom boolean) or the SO already has MOs.
  - Propagates to MO on creation (via `origin`), and also editable on MO form.
- Views and search
  - List (tree): badges for `state`, `payment_status`, and a `delivery_status_display` column.
  - Search: groups of filters for Payment Status and Delivery Status; tag filtering via top‑bar field `tag_ids`.

## Module Scope and Design

- Non‑intrusive: extends models and views via `_inherit` and xpath only. No core patching.
- Dependencies: `sale_management`, `sale_stock`, `account` (to read invoices and payment states).
  - Also integrates with `contact_custom` to surface Related Contacts' invoices on the Sales Order form.
- Upgrade‑safe: stored field for searchability; no data migrations beyond computed values.

## Installation

1) Ensure module is on addons path (docker compose in this repo already mounts `./addons`).
2) Install dependencies if not already installed: `sale_management`, `sale_stock`, `account`, `contact_custom`.
3) Install module:

```bash
docker compose run --rm web \
  odoo -c /etc/odoo/odoo.conf -d <DB> -i company_sale_custom --stop-after-init
```

## Usage

- Sales > Orders list: see `Payment Status` badge and `Delivery Progress` column.
- Sales > Order form: `Payment Status` badge and `Delivery Progress` above order lines.
  - Invoices tab: invoices linked to this SO.
  - Related Invoices tab: invoices of Related Contacts of the customer (from Contacts app's Related Contacts). Use the "View Related Invoices" link for the full list.
  - Invoices tab: invoices linked to this SO.
  - Related Invoices tab: invoices of Related Contacts of the customer (from Contacts app's Related Contacts). Use the "View Related Invoices" link for the full list.
- Filters:
  - Payment Status (group): Paid / Not Paid / No Invoice
  - Delivery Status (group): Fully / Partial / Started / Not Delivered
  - Tags: use the `Tags` field on the search bar (many2many; search panel is not used as it only supports many2one/selection categories).

## Technical Notes

### Models

- `sale.order` (inherit):
  - `payment_status` (Selection, store=True, compute):
    - depends: `order_line.invoice_lines.move_id.payment_state`, `order_line.invoice_lines.move_id.move_type`.
    - logic: collects `order_line.invoice_lines.move_id` filtered by `move_type in ('out_invoice','out_refund')`, then evaluates `payment_state`.
  - `delivery_status_display` (Char, compute):
    - depends: `picking_ids.state`.
    - maps picking states to user‑friendly labels; only outgoing pickings are considered.
  - `mo_ids` (Many2many, compute) and `mo_count` (Integer):
    - linked manufacturing orders via `mrp.production.origin == sale.order.name`.
  - `formula` (Text):
    - Visible when the order contains products that need manufacturing (by product/template/category routes containing “Manufacture” or a custom boolean `manufacture`) or when `mo_count > 0`.
    - Propagated to `mrp.production.formula` on MO creation.
  - `recent_related_invoice_ids` (Many2many, compute) and `related_invoice_total_count` (Integer):
    - linked invoices from Related Contacts of `partner_id` with move_type in customer docs.
    - sorted by payment priority (Not Paid first), then recent first; limited to 5 for performance.
  - `action_view_related_invoices` (object): opens a filtered list of customer invoices for all Related Contacts of the Sales Order's customer.

### Views

- Tree view (inherit `sale.sale_order_tree`): adds `state` badge, `payment_status` badge, and `delivery_status_display` column.
- Form view (inherit `sale.view_order_form`):
  - shows `payment_status` badge and `delivery_status_display` above lines.
  - inserts tabs: Delivery (hidden if none), Invoices (hidden if none), Related Invoices (hidden if none), Manufacturing (hidden if none).
  - adds `formula` field under Order Lines (hidden unless manufacturing applies).
  - guards the Create Invoice button.
- Search view (inherit `sale.view_sales_order_filter`): groups for Payment/Delivery filters and a tag field.

## Common Pitfalls and Decisions

- Payment vs Invoice Status: `sale.order.invoice_status` (To invoice/Invoiced) is not used; payment is derived from `account.move.payment_state`.
- Label Conflict: core `sale_stock` defines a `delivery_status` field labeled "Delivery Status". To avoid warnings, this module labels its computed text field as "Delivery Progress".
- Search Panel & Tags: Odoo searchpanel categories support only many2one/selection; therefore, tag filtering stays on the top bar.

## Testing Quick Checks

- Create a quotation, confirm it, create invoice(s):
  - Before payments: list shows `Payment Status = Not Paid`.
  - Register full payment on all invoices: list shows `Payment Status = Paid`.
  - No invoice created: `Payment Status = No Invoice`.
- Deliveries: confirm delivery picks and validate to see `Delivery Progress` change and core `delivery_status` filters work.

## Upgrade Notes

- Forward compatible with Odoo 18 minor updates:
  - Stored selection `payment_status` avoids recomputation for basic searches; it will recompute when invoices change.
  - No data files with hardcoded IDs; all view inheritance uses xml_ids.
- When upgrading across Odoo major versions, verify:
  - `account.move.payment_state` values and semantics.
  - `sale.order` <-> invoice relation through `invoice_lines` is unchanged.
  - Search view xml_ids in `sale` remain the same (e.g., `sale.view_sales_order_filter`).

## Code Pointers

- Manifest: `addons/company_sale_custom/__manifest__.py`
- Models:
  - `addons/company_sale_custom/models/sale_order.py`
  - `addons/company_sale_custom/models/sale_mrp_formula.py`
  - `addons/company_sale_custom/models/mrp_production.py`
- Views: `addons/company_sale_custom/views/sale_order_views.xml`

## Known limitations

- Manufacturing detection prefers explicit custom boolean `manufacture` when present; otherwise falls back to route names containing “Manufacture”. If your flag is named differently, adjust `_compute_show_formula` accordingly.
- If you need to force Formula visibility per order regardless of product routes, consider adding a simple boolean flag and include it in the compute expression.

## Roadmap (suggested)

- Add group by Tags in search (context `{'group_by': 'tag_ids'}`) for quick reporting.
- Optional statusbar badges on the form header for payment/delivery.
- Unit tests via `odoo.tests.common.TransactionCase` for payment status transitions.
