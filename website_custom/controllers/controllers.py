from odoo import http
from odoo.http import request


class WebsiteCustom(http.Controller):
    @http.route("/landing", type="http", auth="public", website=True, sitemap=True)
    def landing(self, **kw):
        values = {
            "title": "Welcome",
            "subtitle": "My coded page on Odoo",
        }
        return request.render("website_custom.landing_page", values)

