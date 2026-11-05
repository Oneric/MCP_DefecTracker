"""Тесты для модуля конфигурации."""

from __future__ import annotations

import os
from unittest.mock import patch

import pytest


def test_config_bearer_auth():
    """Тест загрузки конфигурации с Bearer auth."""
    env = {
        "TM4J_HOST": "https://test.atlassian.net",
        "TM4J_AUTH_TYPE": "bearer",
        "TM4J_BEARER_TOKEN": "test_token",
        "TM4J_PROJECT_KEY": "TEST",
        "TM4J_OWNER": "user123",
    }
    with patch.dict(os.environ, env, clear=True):
        from src.tm4j_mcp.config import AppConfig

        config = AppConfig()
        assert config.tm4j_host == "https://test.atlassian.net"
        assert config.tm4j_auth_type == "bearer"
        assert config.tm4j_bearer_token == "test_token"
        config.validate()  # Не должно бросать исключение


def test_config_basic_auth():
    """Тест загрузки конфигурации с Basic auth."""
    env = {
        "TM4J_HOST": "https://test.atlassian.net",
        "TM4J_AUTH_TYPE": "basic",
        "TM4J_BASIC_USER": "user@test.com",
        "TM4J_BASIC_PASSWORD": "api_token",
        "TM4J_PROJECT_KEY": "TEST",
        "TM4J_OWNER": "user123",
    }
    with patch.dict(os.environ, env, clear=True):
        from src.tm4j_mcp.config import AppConfig

        config = AppConfig()
        assert config.tm4j_auth_type == "basic"
        assert config.tm4j_basic_user == "user@test.com"
        config.validate()


def test_config_validate_bearer_missing_token():
    """Тест валидации: Bearer auth без токена."""
    env = {
        "TM4J_HOST": "https://test.atlassian.net",
        "TM4J_AUTH_TYPE": "bearer",
        "TM4J_PROJECT_KEY": "TEST",
        "TM4J_OWNER": "user123",
    }
    with patch.dict(os.environ, env, clear=True):
        from src.tm4j_mcp.config import AppConfig

        # Отключаем загрузку .env файла
        config = AppConfig(_env_file=None)
        with pytest.raises(ValueError, match="TM4J_BEARER_TOKEN"):
            config.validate()


def test_config_effective_jira_host_default():
    """Тест: Jira host по умолчанию равен TM4J host."""
    env = {
        "TM4J_HOST": "https://test.atlassian.net",
        "TM4J_AUTH_TYPE": "bearer",
        "TM4J_BEARER_TOKEN": "token",
        "TM4J_PROJECT_KEY": "TEST",
        "TM4J_OWNER": "user123",
    }
    with patch.dict(os.environ, env, clear=True):
        from src.tm4j_mcp.config import AppConfig

        config = AppConfig()
        assert config.effective_jira_host == "https://test.atlassian.net"


def test_config_effective_jira_host_override():
    """Тест: Jira host можно переопределить."""
    env = {
        "TM4J_HOST": "https://tm4j.example.com",
        "JIRA_HOST": "https://jira.example.com",
        "TM4J_AUTH_TYPE": "bearer",
        "TM4J_BEARER_TOKEN": "token",
        "TM4J_PROJECT_KEY": "TEST",
        "TM4J_OWNER": "user123",
    }
    with patch.dict(os.environ, env, clear=True):
        from src.tm4j_mcp.config import AppConfig

        config = AppConfig()
        assert config.effective_jira_host == "https://jira.example.com"
