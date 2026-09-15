import importlib


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
