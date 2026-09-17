import importlib

import pytest


def test_cors_origins_support_multiple_configured_origins(monkeypatch):
    monkeypatch.setenv("AURA_CORS_ORIGINS", "https://app.example.com, https://staging.example.com")

    from app import main

    importlib.reload(main)

    assert main._cors_origins() == ["https://app.example.com", "https://staging.example.com"]


def test_cors_origins_fall_back_when_configuration_is_blank(monkeypatch):
    monkeypatch.setenv("AURA_CORS_ORIGINS", " , ")

    from app import main

    importlib.reload(main)

    assert main._cors_origins() == ["http://localhost:3000"]


def test_cors_origins_reject_wildcard_when_credentials_are_enabled(monkeypatch):
    monkeypatch.setenv("AURA_CORS_ORIGINS", "https://app.example.com, *")

    from app import main

    with pytest.raises(ValueError, match="specific origins"):
        main._cors_origins()


def test_cors_middleware_allows_only_api_methods_and_content_type(monkeypatch):
    monkeypatch.setenv("AURA_CORS_ORIGINS", "https://app.example.com")

    from app import main

    importlib.reload(main)

    cors = next(middleware for middleware in main.app.user_middleware if middleware.cls is main.CORSMiddleware)

    assert cors.kwargs["allow_methods"] == ["GET", "POST"]
    assert cors.kwargs["allow_headers"] == ["Content-Type"]
    assert cors.kwargs["allow_credentials"] is True
