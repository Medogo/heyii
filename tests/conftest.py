"""Configuration globale des tests pytest."""
import pytest
from fastapi.testclient import TestClient

from src.api.main import app


@pytest.fixture
def client():
    """Fixture pour le client de test FastAPI."""
    return TestClient(app)


@pytest.fixture
def mock_settings():
    """Fixture pour les settings mockés."""
    from src.core.config import Settings
    return Settings(
        database_url="sqlite+aiosqlite:///:memory:",
        redis_url="redis://localhost:6379/1",
        deepgram_api_key="test_key",
        openai_api_key="test_key",
        elevenlabs_api_key="test_key",
        elevenlabs_voice_id="test_voice",
        telnyx_api_key="test_key",
        telnyx_phone_number="+1234567890",
        telnyx_connection_id="test_connection",
        erp_api_url="http://test.erp.com",
        erp_api_key="test_key",
        secret_key="test_secret_key_change_in_production",
    )
