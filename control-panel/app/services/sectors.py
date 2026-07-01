"""Predefined sector configurations with their Odoo modules."""

SECTORS = {
    "retail": {
        "name_ar": "التجزئة",
        "name_en": "Retail",
        "description_ar": "قطاع التجزئة - نقاط البيع والمخزون والمحاسبة",
        "modules": [
            "account",           # المحاسبة والفواتير
            "stock",             # إدارة المخزون
            "point_of_sale",     # نقاط البيع
            "sale_management",   # المبيعات
            "purchase",          # المشتريات
            "hr",                # الموظفون
            "hr_holidays",       # الإجازات
            "hr_attendance",     # الحضور والانصراف
            "contacts",          # جهات الاتصال
            "crm",               # علاقات العملاء (CRM)
            "fleet",             # إدارة الأسطول
            "l10n_sa",           # الضريبة السعودية (VAT)
            "base_accounting_kit",  # كيت المحاسبة الكامل للكومينتى
        ],
        "icon": "🛍️",
    },
    "services": {
        "name_ar": "الخدمات",
        "name_en": "Services",
        "description_ar": "شركات الخدمات والاستشارات",
        "modules": [
            "account",
            "sale_management",
            "hr",
            "hr_holidays",
            "hr_attendance",
            "contacts",
            "crm",
            "project",
            "timesheet_grid",
            "l10n_sa",
            "base_accounting_kit",
        ],
        "icon": "🤝",
    },
    "manufacturing": {
        "name_ar": "التصنيع",
        "name_en": "Manufacturing",
        "description_ar": "قطاع التصنيع والإنتاج",
        "modules": [
            "account",
            "stock",
            "mrp",
            "purchase",
            "sale_management",
            "hr",
            "hr_holidays",
            "contacts",
            "l10n_sa",
            "base_accounting_kit",
        ],
        "icon": "🏭",
    },
    "custom": {
        "name_ar": "مخصص",
        "name_en": "Custom",
        "description_ar": "اختر موديولاتك بنفسك",
        "modules": ["account", "base_accounting_kit"],
        "icon": "⚙️",
    },
}


def get_sector(code: str) -> dict:
    return SECTORS.get(code, SECTORS["custom"])


def get_sector_modules(code: str) -> list[str]:
    return get_sector(code)["modules"]


def list_sectors() -> list[dict]:
    return [
        {"code": code, **info}
        for code, info in SECTORS.items()
    ]
