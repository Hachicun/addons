from odoo import api, fields, models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    delivery_status_display = fields.Char(
        string="Delivery Progress",
        compute="_compute_delivery_status_display",
        help="Summary of related delivery orders status mapped to business-friendly labels.",
    )

    @api.depends("picking_ids.state")
    def _compute_delivery_status_display(self):
        label_map = {
            "draft": "Draft",
            "waiting": "Waiting Another Operation",
            "confirmed": "Waiting",
            "assigned": "Ready",
            "done": "Done",
            "cancel": "Cancelled",
        }
        order_preference = ["draft", "waiting", "confirmed", "assigned", "done", "cancel"]
        order_index = {state: idx for idx, state in enumerate(order_preference)}

        for order in self:
            pickings = order.picking_ids.filtered(lambda picking: picking.picking_type_code == "outgoing")
            if not pickings:
                order.delivery_status_display = "No Delivery"
                continue

            states = sorted(
                {picking.state for picking in pickings if picking.state in label_map},
                key=lambda state: order_index[state],
            )

            order.delivery_status_display = ", ".join(label_map[state] for state in states) if states else "No Delivery"

    # Payment status computed from related customer invoices
    payment_status = fields.Selection(
        selection=[
            ("no_invoice", "No Invoice"),
            ("not_paid", "Not Paid"),
            ("paid", "Paid"),
        ],
        string="Payment Status",
        compute="_compute_payment_status",
        help=(
            "Shows whether all related customer invoices for this sales order "
            "are fully paid. If there are no invoices, shows 'No Invoice'."
        ),
        store=True,
    )

    @api.depends(
        "order_line.invoice_lines.move_id.payment_state",
        "order_line.invoice_lines.move_id.move_type",
    )
    def _compute_payment_status(self):
        for order in self:
            # Collect related account.move invoices from sale lines
            moves = order.order_line.mapped("invoice_lines").mapped("move_id")
            # Keep only customer invoices/credit notes
            moves = moves.filtered(lambda m: m.move_type in ("out_invoice", "out_refund"))

            if not moves:
                order.payment_status = "no_invoice"
                continue

            # Consider fully paid only if every related move is paid
            all_paid = all(m.payment_state == "paid" for m in moves)
            order.payment_status = "paid" if all_paid else "not_paid"

    # Related contacts' invoices on the sale order's partner
    recent_related_invoice_ids = fields.Many2many(
        "account.move",
        compute="_compute_recent_related_invoices",
        string="Related Contacts' Invoices",
        readonly=True,
    )
    related_invoice_total_count = fields.Integer(
        compute="_compute_recent_related_invoices",
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
    def _invoice_sort_key(cls, inv):
        # Payment status first (unpaid to the top), then by invoice_date desc, then id desc
        rank = cls._payment_state_rank(getattr(inv, "payment_state", None))
        date_val = inv.invoice_date or inv.create_date or inv.write_date
        # None last, so use 0 when missing
        ts = fields.Datetime.to_datetime(date_val).timestamp() if date_val else 0
        return rank, -ts, -inv.id

    def _compute_recent_related_invoices(self):
        Move = self.env["account.move"]
        for order in self:
            partner = order.partner_id
            if not partner:
                order.recent_related_invoice_ids = Move.browse()
                order.related_invoice_total_count = 0
                continue
            related_partners = partner.relation_ids.mapped("related_partner_id")
            if not related_partners:
                order.recent_related_invoice_ids = Move.browse()
                order.related_invoice_total_count = 0
                continue
            domain = [
                ("partner_id", "in", related_partners.ids),
                ("move_type", "in", ["out_invoice", "out_refund", "out_receipt"]),
            ]
            moves = Move.search(domain, order="invoice_date desc, id desc", limit=50)
            # Sort by payment status then date
            moves = moves.sorted(key=self._invoice_sort_key)[:5]
            order.recent_related_invoice_ids = moves
            # Count all (no limit) cheaply by read_group
            data = Move.read_group(domain, ["partner_id"], ["partner_id"])
            order.related_invoice_total_count = sum(d.get("partner_id_count", 0) for d in data)

    def action_view_related_invoices(self):
        self.ensure_one()
        partner = self.partner_id
        related_partners = partner.relation_ids.mapped("related_partner_id") if partner else self.env["res.partner"]
        if not related_partners:
            return False
        action = self.env.ref("account.action_move_out_invoice_type").read()[0]
        action["domain"] = [
            ("partner_id", "in", related_partners.ids),
            ("move_type", "in", ["out_invoice", "out_refund", "out_receipt"]),
        ]
        # Ensure context is a dict
        ctx = action.get("context", {})
        if isinstance(ctx, str):
            from odoo.tools.safe_eval import safe_eval
            ctx = safe_eval(ctx) or {}
        ctx.update(search_default_partner_id=self.partner_id.id)
        action["context"] = ctx
        return action

    # Manufacturing linkage
    mo_ids = fields.Many2many(
        "mrp.production",
        string="Manufacturing Orders",
        compute="_compute_mo_ids",
        store=False,
    )
    mo_count = fields.Integer(string="MO Count", compute="_compute_mo_ids")

    def _compute_mo_ids(self):
        Production = self.env["mrp.production"]
        for order in self:
            mos = Production.search([("origin", "=", order.name)]) if order.name else Production.browse()
            order.mo_ids = mos
            order.mo_count = len(mos)

    def action_view_sale_advance_payment_inv_guarded(self):
        """Open the standard Create Invoice wizard, but warn if invoices already exist.

        If any invoice is already linked to this sale order, prevent creating another one and
        show a clear warning to the user.
        """
        self.ensure_one()
        if self.invoice_ids:
            # Block creation and warn the user to be careful
            from odoo.exceptions import UserError
            from odoo import _
            raise UserError(_("This Sales Order already has linked invoices. Please be careful."))

        action = self.env.ref('sale.action_view_sale_advance_payment_inv').read()[0]
        # Ensure correct active context for the wizard
        ctx = dict(self.env.context)
        ctx.update(active_model='sale.order', active_id=self.id, active_ids=self.ids)
        action['context'] = ctx
        return action
