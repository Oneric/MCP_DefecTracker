"""Pydantic-модели сущностей TM4J (Zephyr Scale)."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class ScriptStep(BaseModel):
    index: int
    description: str | None = None
    test_data: str | None = None
    expected_result: str | None = None


class TestScript(BaseModel):
    type: str
    text: str | None = None
    steps: list[ScriptStep] | None = None


class TestCase(BaseModel):
    key: str
    project_key: str = Field(alias="projectKey")
    name: str
    objective: str | None = None
    precondition: str | None = None
    folder: str | None = None
    status: str
    priority: str
    component: str | None = None
    owner: str | None = None
    estimated_time: int | None = None
    labels: list[str] | None = None
    test_script: TestScript = Field(alias="testScript")
    custom_fields: dict[str, Any] | None = None


class ScriptResult(BaseModel):
    index: int
    status: str
    comment: str | None = None


class TestResult(BaseModel):
    id: int | None = None
    project_key: str = Field(alias="projectKey")
    test_case_key: str = Field(alias="testCaseKey")
    status: str | None = None
    environment: str | None = None
    comment: str | None = None
    user_key: str | None = Field(default=None, alias="userKey")
    execution_time: int | None = Field(default=None, alias="executionTime")
    execution_date: str | None = Field(default=None, alias="executionDate")
    script_results: list[ScriptResult] | None = Field(
        default=None, alias="scriptResults"
    )


class EmbeddedTestResult(BaseModel):
    status: str | None = None
    environment: str | None = None
    comment: str | None = None
    user_key: str | None = Field(default=None, alias="userKey")
    execution_time: int | None = Field(default=None, alias="executionTime")
    execution_date: str | None = Field(default=None, alias="executionDate")
    script_results: list[ScriptResult] | None = Field(
        default=None, alias="scriptResults"
    )


class TestRunItem(BaseModel):
    test_case_key: str = Field(alias="testCaseKey")
    environment: str | None = None
    user_key: str | None = Field(default=None, alias="userKey")


class TestRun(BaseModel):
    project_key: str = Field(alias="projectKey")
    name: str
    test_plan_key: str | None = Field(default=None, alias="testPlanKey")
    status: str | None = None
    folder: str | None = None
    iteration: str | None = None
    version: str | None = None
    owner: str | None = None
    planned_start_date: str | None = Field(default=None, alias="plannedStartDate")
    planned_end_date: str | None = Field(default=None, alias="plannedEndDate")
    items: list[TestRunItem] | None = None


class TestPlan(BaseModel):
    key: str | None = None
    project_key: str | None = Field(default=None, alias="projectKey")
    name: str | None = None


class Folder(BaseModel):
    name: str
    project_key: str = Field(alias="projectKey")
    type: str
    id: int | None = None


class Environment(BaseModel):
    name: str
    project_key: str = Field(alias="projectKey")
    description: str | None = None
    id: int | None = None


class Project(BaseModel):
    project_key: str = Field(alias="projectKey")
    enable: bool


class CustomFieldOption(BaseModel):
    name: str
    id: str | None = None


class CustomField(BaseModel):
    project_key: str = Field(alias="projectKey")
    name: str
    description: str | None = None
    required: bool = False
    type: str
    category: str
    options: list[CustomFieldOption] | None = None
    custom_statuses: list[str] | None = None
    id: str | None = None


class ExecutionDeletion(BaseModel):
    delete_executions_created_before: str = Field(alias="deleteExecutionsCreatedBefore")
    project_key: str | None = Field(default=None, alias="projectKey")


class SearchResult(BaseModel):
    total: int
    start_at: int = Field(0, alias="startAt")
    max_results: int = Field(50, alias="maxResults")
    items: list[dict[str, Any]] = Field(default_factory=list)


class AttachmentInfo(BaseModel):
    id: str
    filename: str
    size: int | None = None
    content_type: str | None = Field(default=None, alias="contentType")
