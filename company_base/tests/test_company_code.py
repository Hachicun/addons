from odoo.tests import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestCompanyCode(TransactionCase):
    def test_company_code_field_available(self):
        company = self.env.ref("base.main_company")
        company.company_code = "HQ"
        self.assertEqual(company.company_code, "HQ")
