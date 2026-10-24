import pytest


@pytest.fixture(autouse=True)
def clean_ai_keys_env(monkeypatch):
    """Ensure automated tests never leak host API keys or make paid/live network calls."""
    monkeypatch.delenv("NVIDIA_API_KEY", raising=False)
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
