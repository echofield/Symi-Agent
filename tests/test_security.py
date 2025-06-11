import pytest

pytest.importorskip("pydantic")
pytest.importorskip("pydantic_settings")

from config.security import SecurityConfig


def test_security_config_env(monkeypatch):
    monkeypatch.setenv('JWT_SECRET', 'secret')
    monkeypatch.setenv('ENCRYPTION_KEY', 'enc')
    cfg = SecurityConfig()
    assert cfg.JWT_SECRET == 'secret'
    assert cfg.ENCRYPTION_KEY == 'enc'
    assert cfg.API_RATE_LIMITS == {}
