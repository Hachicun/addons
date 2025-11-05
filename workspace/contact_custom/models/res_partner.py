from datetime import date as py_date, datetime as py_datetime

from odoo import api, fields, models
from odoo.tools.safe_eval import safe_eval


class ResPartner(models.Model):
    _inherit = "res.partner"

    relation_ids = fields.One2many(
        "res.partner.relation",
        "partner_id",
        string="Related Contacts",
    )
    # Symmetric relations: manage one list, auto-mirror handled in model logic

    related_by_ids = fields.Many2many(
        "res.partner",
        compute="_compute_related_by_ids",
        string="Related By",
        help="Compatibility alias for deprecated field; mirrors related contacts.",
    )

    recent_sale_order_ids = fields.Many2many(
        "sale.order",
        compute="_compute_recent_sale_orders",
        string="Recent Sales Orders",
        readonly=True,
    )
    sale_order_total_count = fields.Integer(
        compute="_compute_recent_sale_orders",
        string="Sales Orders Count",
        readonly=True,
    )

    recent_invoice_ids = fields.Many2many(
        "account.move",
        compute="_compute_recent_invoices",
        string="Recent Invoices",
        readonly=True,
    )
    invoice_total_count = fields.Integer(
        compute="_compute_recent_invoices",
        string="Invoices Count",
        readonly=True,
    )

    recent_delivery_ids = fields.Many2many(
        "stock.picking",
        compute="_compute_recent_deliveries",
        string="Recent Deliveries",
        readonly=True,
    )
    delivery_total_count = fields.Integer(
        compute="_compute_recent_deliveries",
        string="Deliveries Count",
        readonly=True,
    )

    recent_purchase_ids = fields.Many2many(
        "purchase.order",
        compute="_compute_recent_purchases",
        string="Recent Purchase Orders",
        readonly=True,
    )
    purchase_total_count = fields.Integer(
        compute="_compute_recent_purchases",
        string="Purchase Orders Count",
        readonly=True,
    )

    related_invoice_ids = fields.Many2many(
        "account.move",
        compute="_compute_related_invoices",
        string="Related Contacts' Invoices",
        readonly=True,
    )
    related_invoice_total_count = fields.Integer(
        compute="_compute_related_invoices",
        string="Related Invoices Count",
        readonly=True,
    )

    PAYMENT_STATE_ORDER = {
        "not_paid": 0,
        "partial": 1,
        "in_payment": 2,
        "paid": 3,
        "reversed": 4,
        "cancel": 5,
    }

    @classmethod
    def _payment_state_rank(cls, state):
        return cls.PAYMENT_STATE_ORDER.get(state or "", len(cls.PAYMENT_STATE_ORDER))

    @classmethod
    def _invoice_sort_key(cls, invoice):
        payment_rank = cls._payment_state_rank(invoice.payment_state)
        date_value = invoice.invoice_date or getattr(invoice, "date", False) or invoice.create_date or invoice.write_date
        if isinstance(date_value, str):
            date_value = fields.Date.to_date(date_value)
        elif isinstance(date_value, py_datetime):
            date_value = date_value.date()
        if not isinstance(date_value, py_date):
            today = fields.Date.context_today(invoice)
            date_value = today if isinstance(today, py_date) else fields.Date.to_date(today)
        ordinal = date_value.toordinal() if isinstance(date_value, py_date) else 0
        return payment_rank, -ordinal, -invoice.id

    @api.depends("relation_ids.related_partner_id")
    def _compute_related_by_ids(self):
        for partner in self:
            partner.related_by_ids = partner.relation_ids.mapped("related_partner_id")

    def _compute_recent_sale_orders(self):
        SaleOrder = self.env["sale.order"]
        counts = {}
        if self.ids:
            data = SaleOrder.read_group(
                [("partner_id", "in", self.ids)],
                ["partner_id"],
                ["partner_id"],
            )
            counts = {item["partner_id"][0]: item["partner_id_count"] for item in data if item.get("partner_id")}
        for partner in self:
            if partner.id:
                orders = SaleOrder.search(
                    [("partner_id", "=", partner.id)],
                    order="date_order desc, id desc",
                    limit=5,
                )
            else:
                orders = SaleOrder.browse()
            partner.recent_sale_order_ids = orders
            partner.sale_order_total_count = counts.get(partner.id, 0)

    def _compute_recent_invoices(self):
        Invoice = self.env["account.move"]
        domain = [
            ("partner_id", "in", self.ids),
            ("move_type", "in", ["out_invoice", "out_refund", "out_receipt"]),
        ]
        counts = {}
        if self.ids:
            data = Invoice.read_group(domain, ["partner_id"], ["partner_id"])
            counts = {item["partner_id"][0]: item["partner_id_count"] for item in data if item.get("partner_id")}
        for partner in self:
            invoices = Invoice.search(
                [
                    ("partner_id", "=", partner.id),
                    ("move_type", "in", ["out_invoice", "out_refund", "out_receipt"]),
                ],
                order="invoice_date desc, id desc",
                limit=20,
            ) if partner.id else Invoice.browse()
            if invoices:
                invoices = invoices.sorted(key=self._invoice_sort_key)[:5]
            partner.recent_invoice_ids = invoices
            partner.invoice_total_count = counts.get(partner.id, 0)

    def _compute_recent_deliveries(self):
        Picking = self.env["stock.picking"]
        counts = {}
        if self.ids:
            data = Picking.read_group(
                [("partner_id", "in", self.ids)],
                ["partner_id"],
                ["partner_id"],
            )
            counts = {item["partner_id"][0]: item["partner_id_count"] for item in data if item.get("partner_id")}
        for partner in self:
            pickings = Picking.search(
                [("partner_id", "=", partner.id)],
                order="scheduled_date desc, id desc",
                limit=5,
            ) if partner.id else Picking.browse()
            partner.recent_delivery_ids = pickings
            partner.delivery_total_count = counts.get(partner.id, 0)

    def _compute_recent_purchases(self):
        Purchase = self.env["purchase.order"]
        counts = {}
        if self.ids:
            data = Purchase.read_group(
                [("partner_id", "in", self.ids)],
                ["partner_id"],
                ["partner_id"],
            )
            counts = {item["partner_id"][0]: item["partner_id_count"] for item in data if item.get("partner_id")}
        for partner in self:
            purchases = Purchase.search(
                [("partner_id", "=", partner.id)],
                order="date_order desc, id desc",
                limit=5,
            ) if partner.id else Purchase.browse()
            partner.recent_purchase_ids = purchases
            partner.purchase_total_count = counts.get(partner.id, 0)

    def _compute_related_invoices(self):
        Invoice = self.env["account.move"]
        relation_map = {}
        aggregated_partner_ids = set()
        for partner in self:
            related_partners = partner.relation_ids.mapped("related_partner_id")
            relation_map[partner.id] = related_partners
            aggregated_partner_ids.update(related_partners.ids)

        count_map = {}
        if aggregated_partner_ids:
            data = Invoice.read_group(
                [
                    ("partner_id", "in", list(aggregated_partner_ids)),
                    ("move_type", "in", ["out_invoice", "out_refund", "out_receipt"]),
                ],
                ["partner_id"],
                ["partner_id"],
            )
            count_map = {item["partner_id"][0]: item["partner_id_count"] for item in data if item.get("partner_id")}

        for partner in self:
            related_partners = relation_map.get(partner.id, self.env["res.partner"])
            related_ids = related_partners.ids
            if related_ids:
                invoices = Invoice.search(
                    [
                        ("partner_id", "in", related_ids),
                        ("move_type", "in", ["out_invoice", "out_refund", "out_receipt"]),
                    ],
                    order="invoice_date desc, id desc",
                    limit=50,
                )
                invoices = invoices.sorted(key=self._invoice_sort_key)[:5]
            else:
                invoices = Invoice.browse()
            partner.related_invoice_ids = invoices
            partner.related_invoice_total_count = sum(count_map.get(pid, 0) for pid in related_ids)

    def action_view_sale_orders(self):
        self.ensure_one()
        action = self.env.ref("sale.action_orders").read()[0]
        action["domain"] = [("partner_id", "=", self.id)]
        ctx = action.get("context", {})
        if isinstance(ctx, str):
            ctx = safe_eval(ctx) or {}
        ctx.update(search_default_partner_id=self.id, default_partner_id=self.id)
        action["context"] = ctx
        return action

    def action_view_invoices(self):
        self.ensure_one()
        action = self.env.ref("account.action_move_out_invoice_type").read()[0]
        action["domain"] = [("partner_id", "=", self.id), ("move_type", "in", ["out_invoice", "out_refund", "out_receipt"])]
        ctx = action.get("context", {})
        if isinstance(ctx, str):
            ctx = safe_eval(ctx) or {}
        ctx.update(search_default_partner_id=self.id, default_partner_id=self.id)
        action["context"] = ctx
        return action

    def action_view_deliveries(self):
        self.ensure_one()
        action = self.env.ref("stock.action_picking_tree_all").read()[0]
        action["domain"] = [("partner_id", "=", self.id)]
        ctx = action.get("context", {})
        if isinstance(ctx, str):
            ctx = safe_eval(ctx) or {}
        ctx.update(search_default_partner_id=self.id, default_partner_id=self.id)
        action["context"] = ctx
        return action

    def action_view_purchases(self):
        self.ensure_one()
        action = self.env.ref("purchase.purchase_rfq").read()[0]
        action["domain"] = [("partner_id", "=", self.id)]
        ctx = action.get("context", {})
        if isinstance(ctx, str):
            ctx = safe_eval(ctx) or {}
        ctx.update(search_default_partner_id=self.id, default_partner_id=self.id)
        action["context"] = ctx
        return action

    def action_view_related_invoices(self):
        self.ensure_one()
        related_partners = self.relation_ids.mapped("related_partner_id")
        if not related_partners:
            return False
        action = self.env.ref("account.action_move_out_invoice_type").read()[0]
        action["domain"] = [
            ("partner_id", "in", related_partners.ids),
            ("move_type", "in", ["out_invoice", "out_refund", "out_receipt"]),
        ]
        ctx = action.get("context", {})
        if isinstance(ctx, str):
            ctx = safe_eval(ctx) or {}
        ctx.update(search_default_partner_id=self.id)
        action["context"] = ctx
        return action
