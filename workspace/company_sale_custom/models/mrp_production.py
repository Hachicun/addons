from odoo import models


class MrpProduction(models.Model):
    _inherit = "mrp.production"

    def action_open_form(self):
        self.ensure_one()
        action = self.env.ref('mrp.action_mrp_production_form').read()[0]
        form = self.env.ref('mrp.mrp_production_form_view')
        action.update({
            'views': [(form.id, 'form')],
            'res_id': self.id,
            'domain': [('id', '=', self.id)],
            'target': 'current',
        })
        return action

