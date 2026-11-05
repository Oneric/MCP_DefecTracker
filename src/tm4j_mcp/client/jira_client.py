"""Клиент для Jira REST API — разрешение владельцев."""

from __future__ import annotations

import logging
import re
from typing import Any

import httpx

from ..config import AppConfig
from ..utils.errors import JiraResolutionError, TM4JAPIError
from .auth import AuthHandler

logger = logging.getLogger(__name__)

ISSUE_KEY_RE = re.compile(r"^[A-Z]+-\d+$")
ACCOUNT_ID_RE = re.compile(r"^[a-f0-9]{32}$")


class JiraClient:
    """
    Jira REST API клиент для разрешения владельцев.
    Использует те же credentials, что и TM4J-клиент (единый AuthHandler).
    """

    def __init__(self, config: AppConfig, auth: AuthHandler) -> None:
        self._config = config
        self._auth = auth
        self._base_url = config.effective_jira_host.rstrip("/")
        self._client = httpx.Client(
            base_url=self._base_url,
            timeout=config.http_timeout,
            follow_redirects=True,
        )

    def _headers(self) -> dict[str, str]:
        return {
            **self._auth.get_headers(),
            "Accept": "application/json",
            "Content-Type": "application/json",
        }

    def _request(
        self,
        method: str,
        path: str,
        *,
        params: dict | None = None,
        json_body: dict | None = None,
    ) -> Any:
        url = f"{self._base_url}{path}"
        try:
            response = self._client.request(
                method,
                url,
                headers=self._headers(),
                params=params,
                json=json_body,
            )
        except httpx.ConnectError as e:
            raise TM4JAPIError(f"Jira connection failed: {e}", http_status=0)
        except httpx.TimeoutException as e:
            raise TM4JAPIError(f"Jira request timeout: {e}", http_status=0)

        if response.status_code >= 400:
            raise TM4JAPIError(
                f"Jira API error {response.status_code}: {response.text}",
                http_status=response.status_code,
                response_body=response.text,
            )

        if response.status_code == 204 or not response.text:
            return None
        return response.json()

    # Кэш текущего пользователя — избегаем повторных запросов к /myself
    _current_user_cache: dict[str, Any] | None = None

    def get_current_user(self) -> dict[str, Any]:
        """Получить данные текущего авторизованного пользователя.

        Использует Jira API endpoint `/rest/api/2/myself`.
        Результат кэшируется для повторных вызовов.
        """
        if self._current_user_cache is not None:
            return self._current_user_cache

        data = self._request("GET", "/rest/api/2/myself")
        if not isinstance(data, dict):
            raise JiraResolutionError(
                "Unexpected response from /rest/api/2/myself",
                original_identifier="myself",
            )
        self._current_user_cache = data
        return data

    def resolve_owner(self, identifier: str) -> str:
        """
        Разрешает identifier в account_id владельца.

        Поддерживаемые форматы:
        - "myself" / "self" — текущий авторизованный пользователь (через /rest/api/2/myself)
        - "PROJ-123" — берём fields.creator/assignee из задачи
        - "user@example.com" — lookup по email
        - "5b10a284..." — напрямую account_id
        - "USER" — lookup по key/query
        """
        if not identifier:
            return self._config.tm4j_owner

        # 0. Текущий пользователь через /rest/api/2/myself
        if identifier.lower() in ("myself", "self"):
            return self._resolve_from_myself()

        # 1. Прямой account_id (32 hex symbols)
        if ACCOUNT_ID_RE.match(identifier):
            return identifier

        # 2. Jira Issue Key
        if ISSUE_KEY_RE.match(identifier):
            return self._resolve_from_issue(identifier)

        # 3. Email
        if "@" in identifier:
            return self._resolve_from_email(identifier)

        # 4. Query по key/displayName
        return self._resolve_from_query(identifier)

    def _resolve_from_issue(self, issue_key: str) -> str:
        data = self.get_issue(issue_key, "creator,assignee")
        if isinstance(data, dict):
            fields = data.get("fields", {})
            # Пробуем assignee, потом creator
            for field_name in ("assignee", "creator"):
                user_data = fields.get(field_name)
                if user_data and isinstance(user_data, dict):
                    account_id = user_data.get("accountId")
                    if account_id:
                        return str(account_id)
        raise JiraResolutionError(
            f"Could not resolve owner from issue {issue_key}",
            original_identifier=issue_key,
        )

    def _resolve_from_email(self, email: str) -> str:
        users = self.search_user(email)
        if users:
            account_id = users[0].get("accountId") or users[0].get("account_id")
            if account_id:
                return str(account_id)
        raise JiraResolutionError(
            f"Could not resolve owner from email {email}",
            original_identifier=email,
        )

    def _resolve_from_query(self, query: str) -> str:
        users = self.search_user(query)
        if users:
            account_id = users[0].get("accountId") or users[0].get("account_id")
            if account_id:
                return str(account_id)
        raise JiraResolutionError(
            f"Could not resolve owner from query '{query}'",
            original_identifier=query,
        )

    def _resolve_from_myself(self) -> str:
        """Разрешить владельца через /rest/api/2/myself.

        Поддерживает Cloud (accountId) и Server/Data Center (key) форматы.
        """
        data = self.get_current_user()
        # Cloud: accountId (32 hex символа)
        account_id = data.get("accountId") or data.get("account_id")
        if account_id:
            return str(account_id)
        # Server / Data Center: key (например, JIRAUSER11718)
        user_key = data.get("key")
        if user_key:
            return str(user_key)
        raise JiraResolutionError(
            "Could not resolve accountId/key from /rest/api/2/myself",
            original_identifier="myself",
        )

    def search_user(self, query: str) -> list[dict]:
        """Искать пользователей через /rest/api/2/user/search."""
        result = self._request(
            "GET", "/rest/api/2/user/search", params={"query": query}
        )
        return result if isinstance(result, list) else []

    def get_issue(
        self, issue_key: str, fields: str | None = None
    ) -> dict:
        """Получить задачу из Jira."""
        params: dict[str, Any] = {}
        if fields:
            params["fields"] = fields
        return self._request("GET", f"/rest/api/2/issue/{issue_key}", params=params)

    def close(self) -> None:
        self._client.close()
