"""Predefined sector configurations with their Odoo modules."""

SECTORS = {
    "retail": {
        "name_ar": "التجزئة",
        "name_en": "Retail",
        "description_ar": "نقاط البيع، المخزون، المحاسبة، الموظفون",
        "modules": [
            "account",
            "stock",
            "point_of_sale",
            "sale_management",
            "purchase",
            "hr",
            "hr_holidays",
            "hr_attendance",
            "contacts",
            "crm",
            "fleet",
            "l10n_sa",
            "base_accounting_kit",
        ],
        "icon": "🛍️",
    },
    "services": {
        "name_ar": "الخدمات",
        "name_en": "Services",
        "description_ar": "شركات الخدمات والاستشارات والمقاولات",
        "modules": [
            "account",
            "sale_management",
            "purchase",
            "hr",
            "hr_holidays",
            "hr_attendance",
            "contacts",
            "crm",
            "project",
            "l10n_sa",
            "base_accounting_kit",
        ],
        "icon": "🤝",
    },
    "manufacturing": {
        "name_ar": "التصنيع",
        "name_en": "Manufacturing",
        "description_ar": "قطاع التصنيع والإنتاج والتوزيع",
        "modules": [
            "account",
            "stock",
            "mrp",
            "purchase",
            "sale_management",
            "hr",
            "hr_holidays",
            "hr_attendance",
            "contacts",
            "fleet",
            "l10n_sa",
            "base_accounting_kit",
        ],
        "icon": "🏭",
    },
    "restaurant": {
        "name_ar": "المطاعم والضيافة",
        "name_en": "Restaurant & Hospitality",
        "description_ar": "مطاعم، كافيهات، فنادق، ضيافة",
        "modules": [
            "account",
            "stock",
            "point_of_sale",
            "purchase",
            "hr",
            "hr_holidays",
            "hr_attendance",
            "contacts",
            "l10n_sa",
            "base_accounting_kit",
        ],
        "icon": "🍽️",
    },
    "realestate": {
        "name_ar": "العقارات",
        "name_en": "Real Estate",
        "description_ar": "شركات العقارات والإيجارات والتطوير",
        "modules": [
            "account",
            "sale_management",
            "purchase",
            "hr",
            "hr_holidays",
            "contacts",
            "crm",
            "project",
            "fleet",
            "l10n_sa",
            "base_accounting_kit",
        ],
        "icon": "🏢",
    },
    "healthcare": {
        "name_ar": "الصحة والطب",
        "name_en": "Healthcare",
        "description_ar": "مستشفيات، عيادات، صيدليات",
        "modules": [
            "account",
            "stock",
            "purchase",
            "hr",
            "hr_holidays",
            "hr_attendance",
            "contacts",
            "l10n_sa",
            "base_accounting_kit",
        ],
        "icon": "🏥",
    },
    "education": {
        "name_ar": "التعليم",
        "name_en": "Education",
        "description_ar": "مدارس، جامعات، مراكز تدريب",
        "modules": [
            "account",
            "hr",
            "hr_holidays",
            "hr_attendance",
            "contacts",
            "sale_management",
            "l10n_sa",
            "base_accounting_kit",
        ],
        "icon": "🎓",
    },
    "custom": {
        "name_ar": "مخصص",
        "name_en": "Custom",
        "description_ar": "ابدأ بالموديولات الأساسية وأضف ما تحتاج",
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
