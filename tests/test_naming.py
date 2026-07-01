import pytest
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'control-panel'))

from app.services.naming import build_slug, validate_slug, build_subdomain, db_identifier, random_password


def test_build_slug_basic():
    assert build_slug("My Company") == "my-company"


def test_build_slug_special_chars():
    result = build_slug("Acme Corp! 2024")
    assert all(c.isalnum() or c == '-' for c in result)


def test_validate_slug_valid():
    validate_slug("my-company")
    validate_slug("acme123")


def test_validate_slug_invalid_short():
    with pytest.raises(ValueError):
        validate_slug("ab")


def test_validate_slug_invalid_chars():
    with pytest.raises(ValueError):
        validate_slug("my_company!")


def test_build_subdomain():
    assert build_subdomain("my-company") == "my-company"


def test_db_identifier_default():
    result = db_identifier("my-company")
    assert result.startswith("db_")
    assert "-" not in result


def test_db_identifier_prefix():
    result = db_identifier("my-company", prefix="u_")
    assert result.startswith("u_")


def test_random_password_length():
    p = random_password(32)
    assert len(p) == 32


def test_random_password_uniqueness():
    assert random_password() != random_password()
