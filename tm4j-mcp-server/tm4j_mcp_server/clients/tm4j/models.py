"""
TM4J API Models
"""

from dataclasses import dataclass
from typing import Optional, Dict, Any, List
from datetime import datetime


@dataclass
class TM4JTestRun:
    """Модель TestCycle (TestRun)"""
    key: str
    name: str
    description: Optional[str] = None
    status: Optional[str] = None
    custom_field_values: Optional[Dict[str, Any]] = None
    folder: Optional[str] = None
    test_case_count: Optional[int] = None
    planned_start_date: Optional[str] = None
    planned_end_date: Optional[str] = None
    owner: Optional[str] = None
    created: Optional[str] = None
    updated: Optional[str] = None


@dataclass
class TM4JTestCase:
    """Модель TestCase"""
    key: str
    name: str
    description: Optional[str] = None
    status: Optional[str] = None
    priority: Optional[str] = None
    test_type: Optional[str] = None
    created: Optional[str] = None
    updated: Optional[str] = None


@dataclass
class TM4JTestResult:
    """Модель TestResult"""
    key: str
    test_case_key: str
    test_run_key: str
    status: str  # passed, failed, blocked, etc.
    start_time: Optional[str] = None
    end_time: Optional[str] = None
    steps: Optional[List[Dict[str, Any]]] = None
    attachments: Optional[List[Dict[str, Any]]] = None
    error_message: Optional[str] = None
    stack_trace: Optional[str] = None
    created: Optional[str] = None
    updated: Optional[str] = None


@dataclass
class TM4JTestExecution:
    """Модель TestExecution (для выполнения тестов)"""
    key: str
    test_case_key: str
    test_run_key: str
    status: str
    start_time: Optional[str] = None
    end_time: Optional[str] = None
    steps: Optional[List[Dict[str, Any]]] = None


@dataclass
class TM4JFolder:
    """Модель Folder (папка с тест-кейсами)"""
    key: str
    name: str
    parent_key: Optional[str] = None
    test_case_count: Optional[int] = None


# Aliases for backward compatibility
TestCase = TM4JTestCase
TestCycle = TM4JTestRun
TestResult = TM4JTestResult
TestSession = TM4JTestRun
TestTask = TM4JTestCase