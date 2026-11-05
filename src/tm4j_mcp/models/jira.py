"""Pydantic-модели для Jira REST API."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel


class JiraUser(BaseModel):
    account_id: str | None = None
    email_address: str | None = None
    display_name: str | None = None
    key: str | None = None
    active: bool | None = None


class JiraIssueFields(BaseModel):
    summary: str | None = None
    creator: JiraUser | None = None
    assignee: JiraUser | None = None
    reporter: JiraUser | None = None
    status: dict[str, Any] | None = None
    issuetype: dict[str, Any] | None = None


class JiraIssue(BaseModel):
    key: str
    fields: JiraIssueFields | dict[str, Any] | None = None
