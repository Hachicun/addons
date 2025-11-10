# Copyright 2023 Domatix - Carlos Martínez
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import api, fields, models
from odoo.exceptions import ValidationError


class RenewSubscriptionWizard(models.TransientModel):
    _name = "renew.subscription.wizard"
    _description = "Renew Subscription Wizard"

    subscription_id = fields.Many2one(
        comodel_name="sale.subscription",
        string="Subscription",
        required=True,
        readonly=True,
    )
    renewal_periods = fields.Integer(
        default=1,
        string="Số chu kỳ gia hạn",
        required=True,
        help="Sẽ tạo ngay N SO draft + N Invoice draft với ngày giao hàng tương ứng",
    )

    @api.constrains("renewal_periods")
    def _check_renewal_periods(self):
        for record in self:
            if record.renewal_periods < 1:
                raise ValidationError("Số chu kỳ gia hạn phải lớn hơn 0")

    def action_renew(self):
        """Gia hạn subscription và tạo SO+Invoice cho từng chu kỳ"""
        self.ensure_one()
        subscription = self.subscription_id
        
        if self.renewal_periods < 1:
            raise ValidationError("Số chu kỳ gia hạn phải lớn hơn 0")
        
        # Tạo SO và Invoice cho từng chu kỳ
        orders_created, invoices_created = subscription._create_renewal_orders(
            self.renewal_periods
        )
        
        # Kéo dài date của subscription
        subscription._extend_subscription_date(self.renewal_periods)
        
        # Message thông báo
        orders_count = len(orders_created)
        invoices_count = len(invoices_created)
        message = (
            f"Đã gia hạn {self.renewal_periods} chu kỳ. "
            f"Tạo {orders_count} SO và {invoices_count} Invoice ở trạng thái draft. "
            f"Tổng số chu kỳ đã đặt: {subscription.total_periods_ordered}. "
            f"Đã giao: {subscription.total_periods_delivered}. "
            f"Còn lại: {subscription.remaining_periods}"
        )
        subscription.message_post(body=message)
        
        # Return action để xem các SO đã tạo
        if orders_created:
            return {
                "name": "Đơn hàng đã tạo",
                "view_type": "form",
                "view_mode": "list,form",
                "res_model": "sale.order",
                "type": "ir.actions.act_window",
                "domain": [("id", "in", [so.id for so in orders_created])],
                "context": self.env.context,
            }
        else:
            return {"type": "ir.actions.act_window_close"}

