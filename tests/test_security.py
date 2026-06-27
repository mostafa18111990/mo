import pytest
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'control-panel'))

from unittest.mock import patch, MagicMock

with patch('app.config.Settings', autospec=True) as mock_settings_cls:
    mock_settings = MagicMock()
    mock_settings.secret_key = 'testsecret123456789012345678901234567890123456789012345678901234'
    mock_settings.algorithm = 'HS256'
    mock_settings.access_token_expire_minutes = 60
    mock_settings.cp_database_url = 'postgresql+psycopg://user:pass@localhost/db'
    mock_settings_cls.return_value = mock_settings

    with patch('app.config.get_settings', return_value=mock_settings):
        from app.core.security import hash_password, verify_password, create_access_token, decode_token


def test_password_roundtrip():
    hashed = hash_password("mysecretpassword")
    assert verify_password("mysecretpassword", hashed)
    assert not verify_password("wrongpassword", hashed)


def test_password_different_hashes():
    h1 = hash_password("password")
    h2 = hash_password("password")
    assert h1 != h2


def test_jwt_encode_decode():
    with patch('app.core.security.settings', new=MagicMock(
        secret_key='testsecret123456789012345678901234567890123456789012345678901234',
        algorithm='HS256',
        access_token_expire_minutes=60,
    )):
        token = create_access_token(42)
        assert isinstance(token, str)
        subject = decode_token(token)
        assert subject == "42"
