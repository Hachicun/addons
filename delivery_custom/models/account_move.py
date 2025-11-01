import re

from odoo import api, fields, models, _


class AccountMove(models.Model):
    _inherit = "account.move"

    picking_id = fields.Many2one("stock.picking", string="Related Picking", index=True)
    has_related_picking = fields.Boolean(
        string="Has Related Picking",
        compute="_compute_has_related_picking",
    )

    @api.depends("picking_id", "invoice_origin")
    def _compute_has_related_picking(self):
        StockPicking = self.env["stock.picking"].sudo()

        # Pre-fetch pickings linked to any of the current moves via the explicit Many2one
        linked_move_ids = {move.id for move in self if move.picking_id}

        # Fetch pickings connected through the reverse relation (vendor_bill_ids)
        pickings_for_moves = StockPicking.search([("vendor_bill_ids", "in", self.ids)])
        for picking in pickings_for_moves:
            linked_move_ids.update(picking.vendor_bill_ids.ids)

        # Prepare lookup by name using invoice_origin tokens as a fallback
        name_tokens = set()
        move_tokens = {}
        for move in self:
            if move.invoice_origin:
                parts = re.split(r"[,\n\r]+", move.invoice_origin)
                parts = [part.strip() for part in parts if part and part.strip()]
                move_tokens[move.id] = parts
                name_tokens.update(parts)
        pickings_by_name = {}
        if name_tokens:
            for picking in StockPicking.search([("name", "in", list(name_tokens))]):
                pickings_by_name[picking.name] = picking.id

        for move in self:
            has_link = move.id in linked_move_ids
            if not has_link:
                for token in move_tokens.get(move.id, []):
                    if token in pickings_by_name:
                        has_link = True
                        break
            move.has_related_picking = has_link

    def action_open_picking(self):
        self.ensure_one()
        picking = self.picking_id
        if not picking and self.invoice_origin:
            tokens = [self.invoice_origin.strip()]
            if "," in self.invoice_origin or "\n" in self.invoice_origin:
                tokens = [part.strip() for part in re.split(r"[,\n\r]+", self.invoice_origin) if part and part.strip()]
            domain = [('name', 'in', tokens)] if tokens else [('name', '=', self.invoice_origin)]
            picking = self.env['stock.picking'].search(domain, limit=1)
        if not picking:
            # fallback to list view filtered on origin
            action = self.env.ref('stock.action_picking_tree_all').read()[0]
            if self.invoice_origin:
                tokens = [self.invoice_origin.strip()]
                if "," in self.invoice_origin or "\n" in self.invoice_origin:
                    tokens = [part.strip() for part in re.split(r"[,\n\r]+", self.invoice_origin) if part and part.strip()]
                action.update({'domain': [('name', 'in', tokens)]})
            else:
                action.update({'domain': [('id', '=', 0)]})
            return action

        action = self.env.ref('stock.action_picking_tree_all').read()[0]
        form = self.env.ref('stock.view_picking_form')
        action.update({
            'views': [(form.id, 'form')],
            'res_id': picking.id,
            'domain': [('id', '=', picking.id)],
            'target': 'current',
        })
        return action
