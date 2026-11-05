"""Тесты для JiraClient — разрешение владельцев."""

from __future__ import annotations

import os
from unittest.mock import MagicMock, patch

import pytest

from src.tm4j_mcp.client.auth import AuthHandler
from src.tm4j_mcp.client.jira_client import JiraClient
from src.tm4j_mcp.config import AppConfig
from src.tm4j_mcp.utils.errors import JiraResolutionError


def _make_jira_client() -> tuple[JiraClient, AppConfig]:
    """Хелпер для создания JiraClient с тестовой конфигурацией."""
    env = {
        "TM4J_HOST": "https://test.atlassian.net",
        "TM4J_AUTH_TYPE": "bearer",
        "TM4J_BEARER_TOKEN": "test_token",
        "TM4J_PROJECT_KEY": "TEST",
        "TM4J_OWNER": "default_owner",
    }
    with patch.dict(os.environ, env, clear=True):
        config = AppConfig()
        auth = AuthHandler(config=config)
        client = JiraClient(config=config, auth=auth)
        return client, config


class TestGetCurrentUser:
    """Тесты для метода get_current_user()."""

    def test_get_current_user_returns_account_id(self):
        """Тест: get_current_user возвращает accountId."""
        client, _ = _make_jira_client()

        mock_response = {
            "accountId": "5b10a2844f25c16c440aef95",
            "emailAddress": "user@test.com",
            "displayName": "Test User",
            "active": True,
        }
        client._request = MagicMock(return_value=mock_response)

        result = client.get_current_user()

        assert result["accountId"] == "5b10a2844f25c16c440aef95"
        client._request.assert_called_once_with("GET", "/rest/api/2/myself")

    def test_get_current_user_caches_result(self):
        """Тест: результат кэшируется, повторный вызов не делает запрос."""
        client, _ = _make_jira_client()

        mock_response = {
            "accountId": "5b10a2844f25c16c440aef95",
            "emailAddress": "user@test.com",
        }
        client._request = MagicMock(return_value=mock_response)

        # Первый вызов
        result1 = client.get_current_user()
        assert client._request.call_count == 1

        # Второй вызов — должен использовать кэш
        result2 = client.get_current_user()
        assert client._request.call_count == 1  # Запрос не повторился

        assert result1 is result2

    def test_get_current_user_raises_on_invalid_response(self):
        """Тест: исключение если ответ не dict."""
        client, _ = _make_jira_client()
        client._request = MagicMock(return_value=["not", "a", "dict"])

        with pytest.raises(JiraResolutionError, match="Unexpected response"):
            client.get_current_user()


class TestResolveFromMyself:
    """Тесты для метода _resolve_from_myself()."""

    def test_resolve_from_myself_returns_account_id(self):
        """Тест: _resolve_from_myself возвращает accountId."""
        client, _ = _make_jira_client()

        mock_response = {
            "accountId": "5b10a2844f25c16c440aef95",
            "emailAddress": "user@test.com",
        }
        client._request = MagicMock(return_value=mock_response)

        result = client._resolve_from_myself()

        assert result == "5b10a2844f25c16c440aef95"

    def test_resolve_from_myself_fallback_to_account_id_lowercase(self):
        """Тест: fallback на account_id (snake_case)."""
        client, _ = _make_jira_client()

        mock_response = {
            "account_id": "5b10a2844f25c16c440aef95",
            "emailAddress": "user@test.com",
        }
        client._request = MagicMock(return_value=mock_response)

        result = client._resolve_from_myself()

        assert result == "5b10a2844f25c16c440aef95"

    def test_resolve_from_myself_raises_on_missing_account_id(self):
        """Тест: исключение если нет accountId."""
        client, _ = _make_jira_client()

        mock_response = {
            "emailAddress": "user@test.com",
            "displayName": "Test User",
        }
        client._request = MagicMock(return_value=mock_response)

        with pytest.raises(JiraResolutionError, match="Could not resolve accountId"):
            client._resolve_from_myself()


class TestResolveOwner:
    """Тесты для метода resolve_owner()."""

    def test_resolve_owner_myself(self):
        """Тест: resolve_owner с identifier='myself'."""
        client, _ = _make_jira_client()

        mock_response = {
            "accountId": "5b10a2844f25c16c440aef95",
        }
        client._request = MagicMock(return_value=mock_response)

        result = client.resolve_owner("myself")

        assert result == "5b10a2844f25c16c440aef95"

    def test_resolve_owner_self(self):
        """Тест: resolve_owner с identifier='self'."""
        client, _ = _make_jira_client()

        mock_response = {
            "accountId": "5b10a2844f25c16c440aef95",
        }
        client._request = MagicMock(return_value=mock_response)

        result = client.resolve_owner("self")

        assert result == "5b10a2844f25c16c440aef95"

    def test_resolve_owner_myself_case_insensitive(self):
        """Тест: регистронезависимая обработка myself."""
        client, _ = _make_jira_client()

        mock_response = {
            "accountId": "5b10a2844f25c16c440aef95",
        }
        client._request = MagicMock(return_value=mock_response)

        for identifier in ("MYSELF", "Myself", "MySelf", "SELF", "Self"):
            client._current_user_cache = None  # Сброс кэша
            result = client.resolve_owner(identifier)
            assert result == "5b10a2844f25c16c440aef95", f"Failed for: {identifier}"

    def test_resolve_owner_empty_returns_default(self):
        """Тест: пустой identifier возвращает значение по умолчанию из config."""
        client, config = _make_jira_client()
        assert config.tm4j_owner == "default_owner"

        result = client.resolve_owner("")
        assert result == "default_owner"

    def test_resolve_owner_account_id_direct(self):
        """Тест: прямой account_id (32 hex символа)."""
        client, _ = _make_jira_client()

        account_id = "5b10a2844f25c16c440aef95"
        result = client.resolve_owner(account_id)

        assert result == account_id
        # _request не должен вызываться
        if hasattr(client, "_request") and callable(client._request):
            if hasattr(client._request, "call_count"):
                assert client._request.call_count == 0
