"""Тесты для моделей TM4J."""

from __future__ import annotations

from src.tm4j_mcp.models.tm4j import (
    CustomField,
    Environment,
    Folder,
    ScriptStep,
    TestCase,
    TestResult,
    TestRun,
    TestScript,
)


def test_script_step():
    """Тест модели ScriptStep."""
    step = ScriptStep(index=1, description="Open app", expected_result="App loads")
    assert step.index == 1
    assert step.description == "Open app"


def test_test_script():
    """Тест модели TestScript."""
    script = TestScript(type="STEP", steps=[ScriptStep(index=1)])
    assert script.type == "STEP"
    assert len(script.steps) == 1


def test_test_case():
    """Тест модели TestCase."""
    tc = TestCase(
        key="PROJ-123",
        projectKey="PROJ",
        name="Test Case",
        status="Draft",
        priority="Medium",
        testScript=TestScript(type="STEP"),
    )
    assert tc.key == "PROJ-123"
    assert tc.project_key == "PROJ"


def test_test_result():
    """Тест модели TestResult."""
    tr = TestResult(
        projectKey="PROJ",
        testCaseKey="PROJ-123",
        status="Pass",
    )
    assert tr.project_key == "PROJ"
    assert tr.test_case_key == "PROJ-123"


def test_folder():
    """Тест модели Folder."""
    f = Folder(name="Tests", projectKey="PROJ", type="TEST")
    assert f.name == "Tests"
    assert f.type == "TEST"


def test_environment():
    """Тест модели Environment."""
    e = Environment(name="Staging", projectKey="PROJ")
    assert e.name == "Staging"


def test_custom_field():
    """Тест модели CustomField."""
    cf = CustomField(
        projectKey="PROJ",
        name="Severity",
        type="select",
        category="defect",
        required=True,
    )
    assert cf.required is True
    assert cf.type == "select"
