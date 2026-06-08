from app.core.config import Settings


def test_groq_transcription_config_has_safe_defaults():
    settings = Settings()

    assert settings.groq_api_key is None
    assert settings.groq_base_url == "https://api.groq.com/openai/v1"
    assert settings.groq_transcription_model == "whisper-large-v3-turbo"


def test_openai_api_key_defaults_to_none():
    settings = Settings()

    assert settings.openai_api_key is None
