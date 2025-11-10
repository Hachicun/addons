# Contact Custom — Related Contacts for Odoo 18

Summary: Adds a simple, upgrade‑safe way to relate contacts to each other (friends/family) and surfaces related business info on the contact form. Designed to be symmetric (A↔B) with minimal database footprint and Odoo‑native UI.

## Feature Highlights

- Related Contacts tab on `res.partner` form.
  - Manage a single list of relations (no duplicate reverse list shown).
  - Create/select the related contact and set a relationship type (Friend/Family).
  - Clicking the row’s Open button or the contact name opens the related contact form.
- Symmetric relations: creating/updating/removing a relation automatically mirrors the reverse record.
- Optional business tabs on contact (if dependencies installed):
  - Sales, Invoices, Related Invoices, Delivery, Purchase — each shows up to 5 recent records and a link to view all. Tabs auto‑hide when empty, except Related Contacts which always shows.
- Integrates with Sales (company_sale_custom): the Sales Order form displays a Related Invoices tab for the customer’s related contacts.

## Models

- `res.partner.relation` — lightweight relation line:
  - `partner_id` (Many2one → res.partner): the base contact.
  - `related_partner_id` (Many2one → res.partner): the related contact.
  - `relation_type` (Selection): Friend / Family.
  - SQL constraints: unique per (partner_id, related_partner_id); self‑relation prevented.
  - Symmetry logic: overrides `create` (batch‑safe), `write`, `unlink` to auto‑manage reverse rows.

- `res.partner` (inherit):
  - `relation_ids` (One2many → res.partner.relation.partner_id): manage relations on the contact.
  - Backward‑compatibility compute `related_by_ids` to avoid legacy view crashes (not shown in UI).
  - If you installed `sale_management`/`account`/`stock`/`purchase`, extra compute fields expose five most recent records and counters for conditional tabs:
    - `recent_sale_order_ids`, `sale_order_total_count`
    - `recent_invoice_ids`, `invoice_total_count` (customer docs only)
    - `related_invoice_ids`, `related_invoice_total_count` (from related contacts)
    - `recent_delivery_ids`, `delivery_total_count`
    - `recent_purchase_ids`, `purchase_total_count`

## Views

- Partner form (inherit `base.view_partner_form`): inserts tabs in this order: Sales, Invoices, Related Invoices, Delivery, Purchase, Related Contacts. Hides other default pages for a focused UI. Lists are compact, limited to 5, with buttons to open full actions.
- Relation list uses `<list>` with an Open button per line.

## Dependencies

- Minimal: `base`, `contacts`.
- Optional for business tabs: `sale_management`, `account`, `stock`, `purchase`.

## Installation

1) Ensure `addons/` is bind‑mounted to `/mnt/extra-addons` (docker compose in this repo already does).
2) Install dependencies per your use case (see above).
3) Install/upgrade:

```bash
docker compose run --rm web \
  odoo -c /etc/odoo/odoo.conf -d <DB> -i contact_custom --stop-after-init
# or upgrade
docker compose run --rm web \
  odoo -c /etc/odoo/odoo.conf -d <DB> -u contact_custom --stop-after-init
```

## Usage Tips

- Open a contact, go to Related Contacts tab, add lines and set type.
- The mirror record is created/updated automatically; the other party sees the link too.
- Invoices/Related Invoices prioritize unpaid first, then most recent, to focus attention.

## Extending

- Add more `relation_type` values by extending the selection in `res.partner.relation`.
- To keep only one physical record per pair (instead of mirrored rows), replace the mirroring with a Many2many through a custom relation table and store the type on the through model; update compute domains accordingly.
- For performance with very large datasets, consider adding SQL indexes on (`partner_id`), (`related_partner_id`), and composite filters you query often.

## Upgrade Notes

- Odoo 18 removes `attrs` in favor of inline expressions; this addon uses `invisible="expr == value"` consistently.
- If your DB previously used a different relation module, remove or deactivate leftover views and models to avoid field-validation errors.

