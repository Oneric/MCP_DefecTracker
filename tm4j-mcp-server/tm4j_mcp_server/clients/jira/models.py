"""
Jira Server API Models
"""

from dataclasses import dataclass
from typing import Optional, Dict, Any, List
from datetime import datetime


@dataclass
class JiraProject:
    """Модель Jira проекта"""
    key: str
    name: str
    project_type: str
    lead: Optional[str] = None
    description: Optional[str] = None


@dataclass
class JiraUser:
    """Модель Jira пользователя"""
    account_id: str
    key: str
    name: str
    email_address: Optional[str] = None
    display_name: Optional[str] = None


@dataclass
class JiraIssue:
    """Модель Jira issue"""
    key: str
    summary: str
    issue_type: str
    status: str
    priority: str
    project_key: str
    created: Optional[str] = None
    updated: Optional[str] = None
    assignee: Optional[str] = None
    reporter: Optional[str] = None
    description: Optional[str] = None
    custom_fields: Optional[Dict[str, Any]] = None


@dataclass
class JiraCustomField:
    """Модель кастомного поля Jira"""
    id: str
    name: str
    field_type: str
    schema_type: str
    custom: bool = True


@dataclass
class JiraFieldOption:
    """Модель опции поля"""
    id: str
    value: str
    disabled: bool = False


@dataclass
class JiraTestCase:
    """Модель Jira тест-кейса"""
    id: str
    name: str
    issue_key: str
    status: str
    priority: str
    test_type: str
    steps: Optional[str] = None
    expected_result: Optional[str] = None
    test_data: Optional[Dict[str, Any]] = None


@dataclass
class JiraTestResult:
    """Модель результата тестирования Jira"""
    id: str
    test_case_id: str
    issue_key: str
    status: str
    executed_by: Optional[str] = None
    executed_at: Optional[str] = None
    duration: Optional[int] = None
    comments: Optional[str] = None
    actual_result: Optional[str] = None