import smtplib
import logging
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from ..config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


def send_email(to: str, subject: str, html_body: str):
    if not settings.smtp_host:
        logger.warning("SMTP not configured, skipping email to %s", to)
        return
    try:
        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"] = settings.smtp_from
        msg["To"] = to
        msg.attach(MIMEText(html_body, "html", "utf-8"))
        with smtplib.SMTP(settings.smtp_host, settings.smtp_port) as srv:
            if settings.smtp_tls:
                srv.starttls()
            if settings.smtp_user:
                srv.login(settings.smtp_user, settings.smtp_password)
            srv.sendmail(settings.smtp_from, [to], msg.as_string())
        logger.info("Email sent to %s: %s", to, subject)
    except Exception as exc:
        logger.error("Failed to send email to %s: %s", to, exc)


def send_tenant_ready(user_email: str, company_name: str, subdomain: str,
                       admin_email: str, admin_password: str, domain: str):
    url = f"https://{subdomain}.{domain}"
    html = f"""
<!DOCTYPE html>
<html dir="rtl" lang="ar">
<head><meta charset="utf-8"><style>
  body {{ font-family: Arial, sans-serif; background: #f4f6f8; margin: 0; padding: 20px; }}
  .card {{ background: white; max-width: 600px; margin: 0 auto; border-radius: 12px;
           padding: 40px; box-shadow: 0 2px 8px rgba(0,0,0,0.1); }}
  .header {{ background: linear-gradient(135deg,#4f46e5,#7c3aed); color:white;
             border-radius: 8px; padding: 24px; text-align: center; margin-bottom: 32px; }}
  .info-box {{ background: #f8fafc; border-right: 4px solid #4f46e5;
               padding: 16px; border-radius: 8px; margin: 16px 0; }}
  .btn {{ display: inline-block; background: #4f46e5; color: white;
          padding: 14px 32px; border-radius: 8px; text-decoration: none;
          font-weight: bold; margin: 24px auto; text-align: center; }}
  label {{ color: #6b7280; font-size: 12px; }}
  value {{ color: #111827; font-weight: bold; font-size: 14px; }}
</style></head>
<body>
<div class="card">
  <div class="header">
    <h1 style="margin:0;font-size:24px">🎉 حساب Odoo جاهز!</h1>
    <p style="margin:8px 0 0;opacity:0.9">تم إنشاء حسابك بنجاح</p>
  </div>
  <p>مرحباً <strong>{company_name}</strong>،</p>
  <p>تم إنشاء حساب Odoo الخاص بك وتثبيت جميع الموديولات. يمكنك البدء الآن!</p>
  <div class="info-box">
    <p><label>رابط الدخول</label><br>
       <value><a href="{url}">{url}</a></value></p>
    <p><label>البريد الإلكتروني (اسم المستخدم)</label><br>
       <value>{admin_email}</value></p>
    <p><label>كلمة المرور</label><br>
       <value>{admin_password}</value></p>
  </div>
  <p style="color:#ef4444;font-size:13px">
    ⚠️ يرجى تغيير كلمة المرور فور الدخول الأول من: الإعدادات ← تغيير كلمة المرور
  </p>
  <div style="text-align:center">
    <a href="{url}/web#action=login" class="btn">دخول إلى Odoo ←</a>
  </div>
  <hr style="border:none;border-top:1px solid #e5e7eb;margin:24px 0">
  <p style="color:#9ca3af;font-size:12px;text-align:center">
    للدعم الفني: support@{domain}
  </p>
</div>
</body></html>
"""
    send_email(user_email, f"✅ حساب Odoo جاهز - {company_name}", html)


def send_tenant_suspended(user_email: str, company_name: str, domain: str):
    html = f"""
<!DOCTYPE html>
<html dir="rtl" lang="ar">
<head><meta charset="utf-8"></head>
<body style="font-family:Arial;background:#f4f6f8;padding:20px">
<div style="background:white;max-width:600px;margin:0 auto;border-radius:12px;padding:40px">
  <div style="background:#ef4444;color:white;border-radius:8px;padding:20px;text-align:center;margin-bottom:24px">
    <h2 style="margin:0">⚠️ تم تعليق حسابك</h2>
  </div>
  <p>عزيزي <strong>{company_name}</strong>،</p>
  <p>تم تعليق حساب Odoo الخاص بك بسبب انتهاء صلاحية الاشتراك أو مشكلة في الدفع.</p>
  <p>لإعادة التفعيل، يرجى تسوية الدفعة المستحقة من لوحة التحكم.</p>
  <div style="text-align:center;margin:24px 0">
    <a href="https://admin.{domain}/tenants"
       style="background:#4f46e5;color:white;padding:14px 32px;border-radius:8px;text-decoration:none;font-weight:bold">
      تسوية الدفع ←
    </a>
  </div>
</div>
</body></html>
"""
    send_email(user_email, f"⚠️ تم تعليق حساب {company_name}", html)
