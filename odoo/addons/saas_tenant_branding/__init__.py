import os
from odoo import api, SUPERUSER_ID


def post_init_hook(cr, registry):
    company_name = os.environ.get("TENANT_COMPANY_NAME", "My Company")
    with api.Environment.manage():
        env = api.Environment(cr, SUPERUSER_ID, {})
        company = env["res.company"].browse(1)
        company.write({"name": company_name})
