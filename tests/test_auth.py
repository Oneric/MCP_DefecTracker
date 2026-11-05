"""Тесты для модуля авторизации."""

from __future__ import annotations

import base64
import os
from unittest.mock import patch

import pytest

from src.tm4j_mcp.config import AppConfig


def _make_config(auth_type: str, **kwargs) -> AppConfig:
    """Хелпер для создания конфигурации."""
    env = {
        "TM4J_HOST": "https://test.atlassian.net",
        "TM4J_AUTH_TYPE": auth_type,
        "TM4J_PROJECT_KEY": "TEST",
        "TM4J_OWNER": "user123",
    }
    if auth_type == "basic":
        env["TM4J_BASIC_USER"] = kwargs.get("user", "user@test.com")
        env["TM4J_BASIC_PASSWORD"] = kwargs.get("password", "secret")
    elif auth_type == "bearer":
        env["TM4J_BEARER_TOKEN"] = kwargs.get("token", "test_token")
    with patch.dict(os.environ, env, clear=True):
        return AppConfig()


def test_bearer_headers():
    """Тест генерации Bearer заголовков."""
    config = _make_config("bearer", token="my_secret_token")
    from src.tm4j_mcp.client.auth import AuthHandler

    auth = AuthHandler(config=config)
    headers = auth.get_headers()
    assert "Authorization" in headers
    assert headers["Authorization"] == "Bearer my_secret_token"


def test_basic_headers():
    """Тест генерации Basic заголовков."""
    config = _make_config("basic", user="user@test.com", password="secret123")
    from src.tm4j_mcp.client.auth import AuthHandler

    auth = AuthHandler(config=config)
    headers = auth.get_headers()
    assert "Authorization" in headers
    assert headers["Authorization"].startswith("Basic ")

    # Проверим декодирование
    encoded = headers["Authorization"].split(" ")[1]
    decoded = base64.b64decode(encoded).decode()
    assert decoded == "user@test.com:secret123"


def test_basic_missing_credentials():
    """Тест: Basic auth без credentials."""
    env = {
        "TM4J_HOST": "https://test.atlassian.net",
        "TM4J_AUTH_TYPE": "basic",
        "TM4J_PROJECT_KEY": "TEST",
        "TM4J_OWNER": "user123",
    }
    with patch.dict(os.environ, env, clear=True):
        config = AppConfig()
        from src.tm4j_mcp.client.auth import AuthHandler

        auth = AuthHandler(config=config)
        with pytest.raises(ValueError, match="TM4J_BASIC_USER"):
            auth.get_headers()


def test_bearer_missing_token():
    """Тест: Bearer auth без токена."""
    env = {
        "TM4J_HOST": "https://test.atlassian.net",
        "TM4J_AUTH_TYPE": "bearer",
        "TM4J_PROJECT_KEY": "TEST",
        "TM4J_OWNER": "user123",
    }
    with patch.dict(os.environ, env, clear=True):
        # Отключаем загрузку .env файла
        config = AppConfig(_env_file=None)
        from src.tm4j_mcp.client.auth import AuthHandler

        auth = AuthHandler(config=config)
        with pytest.raises(ValueError, match="TM4J_BEARER_TOKEN"):
            auth.get_headers()
