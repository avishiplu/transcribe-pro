from app.core.config import settings


def test_database_url_is_configured():
    assert settings.database_url
    assert settings.database_url.startswith("postgresql+asyncpg://")
