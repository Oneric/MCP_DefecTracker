"""Загрузка и валидация переменных окружения."""

from __future__ import annotations

from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict


class AppConfig(BaseSettings):
    # TM4J / Jira — единые credentials
    tm4j_host: str
    tm4j_api_base_path: str = "/rest/atmosphere/public/latest"
    tm4j_auth_type: Literal["basic", "bearer"] = "bearer"
    tm4j_basic_user: str | None = None
    tm4j_basic_password: str | None = None
    tm4j_bearer_token: str | None = None
    tm4j_project_key: str
    tm4j_owner: str

    # Jira хост — опционально, по умолчанию берётся TM4J_HOST
    jira_host: str | None = None

    # HTTP
    http_timeout: int = 30
    http_retries: int = 3

    # Logging
    log_level: str = "INFO"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    @property
    def effective_jira_host(self) -> str:
        return self.jira_host or self.tm4j_host

    def validate(self) -> None:
        if self.tm4j_auth_type == "basic":
            if not self.tm4j_basic_user or not self.tm4j_basic_password:
                raise ValueError(
                    "Basic auth требует TM4J_BASIC_USER и TM4J_BASIC_PASSWORD"
                )
        elif self.tm4j_auth_type == "bearer" and not self.tm4j_bearer_token:
            raise ValueError("Bearer auth требует TM4J_BEARER_TOKEN")
