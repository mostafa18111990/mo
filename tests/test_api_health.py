import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'control-panel'))

from unittest.mock import patch, MagicMock
import pytest

mock_settings = MagicMock()
mock_settings.secret_key = 'testsecret123456789012345678901234567890123456789012345678901234'
mock_settings.algorithm = 'HS256'
mock_settings.access_token_expire_minutes = 60
mock_settings.cp_database_url = 'postgresql+psycopg://user:pass@localhost/db'
mock_settings.admin_domain = 'admin.example.com'
mock_settings.celery_broker_url = 'redis://localhost/1'
mock_settings.celery_result_backend = 'redis://localhost/2'

with patch('app.config.get_settings', return_value=mock_settings), \
     patch('app.database.create_engine'), \
     patch('app.database.SessionLocal'), \
     patch('app.worker.Celery'):
    from fastapi.testclient import TestClient
    from app.main import app

client = TestClient(app)


def test_health_endpoint():
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
