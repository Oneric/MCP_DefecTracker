"""Централизованная обработка ошибок для TM4J MCP Server."""

from __future__ import annotations


class MCPError(Exception):
    """Базовое исключение MCP-сервера."""

    def __init__(
        self,
        code: str,
        message: str,
        *,
        recoverable: bool = False,
        suggestion: str | None = None,
    ) -> None:
        super().__init__(message)
        self.code = code
        self.message = message
        self.recoverable = recoverable
        self.suggestion = suggestion

    def to_dict(self) -> dict:
        result: dict = {
            "error": True,
            "code": self.code,
            "message": self.message,
            "recoverable": self.recoverable,
        }
        if self.suggestion:
            result["suggestion"] = self.suggestion
        return result


class TM4JAPIError(MCPError):
    """Ошибка от TM4J API."""

    def __init__(
        self,
        message: str,
        *,
        http_status: int = 0,
        response_body: str | None = None,
        recoverable: bool = False,
        suggestion: str | None = None,
    ) -> None:
        super().__init__(
            code="TM4J_API_ERROR",
            message=message,
            recoverable=recoverable,
            suggestion=suggestion,
        )
        self.http_status = http_status
        self.response_body = response_body


class AuthError(MCPError):
    """Ошибка авторизации."""

    def __init__(self, message: str = "Authentication failed") -> None:
        super().__init__(code="AUTH_ERROR", message=message)


class ValidationError(MCPError):
    """Ошибка валидации входных данных."""

    def __init__(self, message: str, *, suggestion: str | None = None) -> None:
        super().__init__(
            code="VALIDATION_ERROR",
            message=message,
            suggestion=suggestion,
        )


class JiraResolutionError(MCPError):
    """Ошибка разрешения владельца через Jira."""

    def __init__(self, message: str, *, original_identifier: str = "") -> None:
        super().__init__(code="JIRA_RESOLUTION_ERROR", message=message)
        self.original_identifier = original_identifier
