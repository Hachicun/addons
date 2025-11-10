from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class ResPartnerRelation(models.Model):
    _name = "res.partner.relation"
    _description = "Partner Relationship"
    _rec_name = "related_partner_id"

    partner_id = fields.Many2one(
        "res.partner",
        string="Contact",
        required=True,
        ondelete="cascade",
        index=True,
    )
    related_partner_id = fields.Many2one(
        "res.partner",
        string="Related Contact",
        required=True,
        ondelete="cascade",
        index=True,
        domain="[('id','!=',partner_id)]",
    )
    relation_type = fields.Selection(
        selection=[("friend", "Friend"), ("family", "Family")],
        string="Relationship",
        required=True,
        default="friend",
    )

    _sql_constraints = [
        (
            "partner_related_unique",
            "unique(partner_id, related_partner_id)",
            "This related contact already exists for this contact.",
        ),
    ]

    @api.constrains("partner_id", "related_partner_id")
    def _check_not_self(self):
        for rec in self:
            if rec.partner_id and rec.related_partner_id and rec.partner_id.id == rec.related_partner_id.id:
                raise ValidationError(_("A contact cannot be related to itself."))

    # --- Symmetric behavior: auto-mirror create/write/unlink ---
    def _mirror_domain(self):
        self.ensure_one()
        return [
            ("partner_id", "=", self.related_partner_id.id),
            ("related_partner_id", "=", self.partner_id.id),
        ]

    @api.model_create_multi
    def create(self, vals_list):
        records = super().create(vals_list)
        if not self.env.context.get("_skip_mirror"):
            for rec in records:
                mirror_vals = {
                    "partner_id": rec.related_partner_id.id,
                    "related_partner_id": rec.partner_id.id,
                    "relation_type": rec.relation_type,
                }
                existing = self.search(rec._mirror_domain(), limit=1)
                if not existing:
                    self.with_context(_skip_mirror=True).create(mirror_vals)
        return records

    def write(self, vals):
        res = super().write(vals)
        if any(k in vals for k in ["partner_id", "related_partner_id", "relation_type"]) and not self.env.context.get("_skip_mirror"):
            for rec in self:
                mirror = self.search(rec._mirror_domain(), limit=1)
                if mirror:
                    mvals = {}
                    if "relation_type" in vals:
                        mvals["relation_type"] = rec.relation_type
                    # If endpoints changed, realign mirror to point back to this
                    if "partner_id" in vals or "related_partner_id" in vals:
                        mvals.update({
                            "partner_id": rec.related_partner_id.id,
                            "related_partner_id": rec.partner_id.id,
                        })
                    if mvals:
                        mirror.with_context(_skip_mirror=True).write(mvals)
                else:
                    # Recreate mirror if it was missing
                    self.with_context(_skip_mirror=True).create({
                        "partner_id": rec.related_partner_id.id,
                        "related_partner_id": rec.partner_id.id,
                        "relation_type": rec.relation_type,
                    })
        return res

    def unlink(self):
        mirrors = self.env["res.partner.relation"]
        for rec in self:
            mirror = self.search(rec._mirror_domain(), limit=1)
            mirrors |= mirror
        res = super().unlink()
        if mirrors:
            mirrors.with_context(_skip_mirror=True).unlink()
        return res

    def action_open_related_partner(self):
        self.ensure_one()
        if not self.related_partner_id:
            return False
        return {
            "type": "ir.actions.act_window",
            "res_model": "res.partner",
            "res_id": self.related_partner_id.id,
            "view_mode": "form",
            "target": "current",
        }
