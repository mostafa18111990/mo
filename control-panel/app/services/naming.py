import re
import secrets
import string
from slugify import slugify


def build_slug(raw: str) -> str:
    return slugify(raw, max_length=63, word_boundary=True)


def validate_slug(slug: str):
    if not re.match(r'^[a-z0-9][a-z0-9\-]{1,61}[a-z0-9]$', slug):
        raise ValueError(
            "Slug must be 3-63 chars, lowercase alphanumeric and hyphens, "
            "start and end with alphanumeric."
        )


def build_subdomain(slug: str) -> str:
    return slug


def db_identifier(slug: str, prefix: str = "db_") -> str:
    safe = re.sub(r'[^a-z0-9]', '_', slug)[:50]
    return f"{prefix}{safe}"


def random_password(length: int = 32) -> str:
    alphabet = string.ascii_letters + string.digits
    return ''.join(secrets.choice(alphabet) for _ in range(length))
