import os
from odoo import api, SUPERUSER_ID


def post_init_hook(cr, registry):
    company_name = os.environ.get("TENANT_COMPANY_NAME", "My Company")
    company_email = os.environ.get("TENANT_COMPANY_EMAIL", "")
    company_phone = os.environ.get("TENANT_COMPANY_PHONE", "")

    with api.Environment.manage():
        env = api.Environment(cr, SUPERUSER_ID, {})
        company = env["res.company"].browse(1)
        vals = {"name": company_name}
        if company_email:
            vals["email"] = company_email
        if company_phone:
            vals["phone"] = company_phone
        company.write(vals)

        # تحديث بيانات المستخدم المدير أيضاً
        if company_email:
            admin_user = env["res.users"].browse(SUPERUSER_ID)
            admin_user.write({"login": company_email, "email": company_email})
