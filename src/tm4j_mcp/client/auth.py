"""Единый модуль авторизации для TM4J и Jira API."""

from __future__ import annotations

import base64
import logging

from ..config import AppConfig

logger = logging.getLogger(__name__)


class AuthHandler:
    """
    Единый обработчик авторизации.
    Поддерживает Basic Auth и Bearer Token.
    Используется одинаково для TM4J и Jira клиентов.
    """

    def __init__(self, config: AppConfig) -> None:
        self._config = config

    @property
    def auth_type(self) -> str:
        return self._config.tm4j_auth_type

    def get_headers(self) -> dict[str, str]:
        """Получить заголовки авторизации для HTTP-запроса."""
        if self.auth_type == "basic":
            return self._basic_headers()
        elif self.auth_type == "bearer":
            return self._bearer_headers()
        else:
            raise ValueError(f"Unknown auth type: {self.auth_type}")

    def _basic_headers(self) -> dict[str, str]:
        user = self._config.tm4j_basic_user
        password = self._config.tm4j_basic_password
        if not user or not password:
            raise ValueError(
                "Basic auth requires TM4J_BASIC_USER and TM4J_BASIC_PASSWORD"
            )
        credentials = f"{user}:{password}"
        encoded = base64.b64encode(credentials.encode()).decode()
        return {"Authorization": f"Basic {encoded}"}

    def _bearer_headers(self) -> dict[str, str]:
        token = self._config.tm4j_bearer_token
        if not token:
            raise ValueError("Bearer auth requires TM4J_BEARER_TOKEN")
        return {"Authorization": f"Bearer {token}"}
