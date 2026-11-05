"""Тесты для системы ошибок."""

from __future__ import annotations

import pytest

from src.tm4j_mcp.utils.errors import (
    AuthError,
    JiraResolutionError,
    MCPError,
    TM4JAPIError,
    ValidationError,
)


def test_mcp_error():
    """Тест базового исключения."""
    err = MCPError(code="TEST", message="Test error")
    assert err.code == "TEST"
    assert err.message == "Test error"
    assert not err.recoverable
    d = err.to_dict()
    assert d["error"] is True
    assert d["code"] == "TEST"


def test_mcp_error_with_suggestion():
    """Тест исключения с подсказкой."""
    err = MCPError(
        code="TEST", message="Error", recoverable=True, suggestion="Retry"
    )
    d = err.to_dict()
    assert d["recoverable"] is True
    assert d["suggestion"] == "Retry"


def test_tm4j_api_error():
    """Тест ошибки API TM4J."""
    err = TM4JAPIError("Server error", http_status=500, recoverable=True)
    assert err.http_status == 500
    assert err.recoverable is True
    assert err.code == "TM4J_API_ERROR"


def test_auth_error():
    """Тест ошибки авторизации."""
    err = AuthError("Invalid token")
    assert err.code == "AUTH_ERROR"
    assert err.message == "Invalid token"


def test_validation_error():
    """Тест ошибки валидации."""
    err = ValidationError("Invalid field", suggestion="Check format")
    assert err.code == "VALIDATION_ERROR"
    assert err.suggestion == "Check format"


def test_jira_resolution_error():
    """Тест ошибки разрешения Jira."""
    err = JiraResolutionError("Not found", original_identifier="PROJ-999")
    assert err.code == "JIRA_RESOLUTION_ERROR"
    assert err.original_identifier == "PROJ-999"


def test_errors_are_exceptions():
    """Тест что все ошибки — исключения."""
    for err_class in [MCPError, TM4JAPIError, AuthError, ValidationError, JiraResolutionError]:
        assert issubclass(err_class, Exception)
