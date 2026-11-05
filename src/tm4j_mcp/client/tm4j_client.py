"""HTTP-клиент для TM4J (Zephyr Scale) API."""

from __future__ import annotations

import logging
from typing import Any

import httpx
from tenacity import (
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)

from ..config import AppConfig
from ..utils.errors import TM4JAPIError
from .auth import AuthHandler

logger = logging.getLogger(__name__)


class TM4JClient:
    """Клиент для TM4J API с автоматическими retry и обработкой ошибок."""

    def __init__(self, config: AppConfig, auth: AuthHandler) -> None:
        self._config = config
        self._auth = auth
        self._base_url = config.tm4j_host.rstrip("/")
        self._api_path = config.tm4j_api_base_path
        self._client = httpx.Client(
            base_url=self._base_url,
            timeout=config.http_timeout,
            follow_redirects=True,
        )

    def _url(self, path: str) -> str:
        return f"{self._api_path}{path}"

    def _headers(self, extra: dict[str, str] | None = None) -> dict[str, str]:
        headers = {**self._auth.get_headers(), "Content-Type": "application/json"}
        if extra:
            headers.update(extra)
        return headers

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=30),
        retry=retry_if_exception_type(TM4JAPIError),
        reraise=True,
    )
    def _request(
        self,
        method: str,
        path: str,
        *,
        json_body: dict | None = None,
        params: dict | None = None,
        files: dict | None = None,
        content: bytes | None = None,
        extra_headers: dict[str, str] | None = None,
    ) -> Any:
        url = self._url(path)
        headers = self._headers(extra_headers)

        # Для multipart убираем Content-Type (httpx сам поставит boundary)
        if files:
            headers.pop("Content-Type", None)

        try:
            if files:
                response = self._client.request(
                    method, url, headers=headers, params=params, files=files
                )
            elif content:
                response = self._client.request(
                    method, url, headers=headers, params=params, content=content
                )
            else:
                response = self._client.request(
                    method, url, headers=headers, params=params, json=json_body
                )
        except httpx.ConnectError as e:
            raise TM4JAPIError(f"Connection failed: {e}", http_status=0)
        except httpx.TimeoutException as e:
            raise TM4JAPIError(f"Request timeout: {e}", http_status=0)

        if response.status_code == 429:
            raise TM4JAPIError(
                "Rate limit exceeded",
                http_status=429,
                recoverable=True,
                suggestion="Wait and retry",
            )
        if 500 <= response.status_code < 600:
            raise TM4JAPIError(
                f"Server error: {response.status_code}",
                http_status=response.status_code,
                recoverable=True,
                suggestion="Retry the request",
            )
        if response.status_code != 200 and response.status_code not in (201, 204):
            body = response.text
            raise TM4JAPIError(
                f"API error {response.status_code}: {body}",
                http_status=response.status_code,
                response_body=body,
            )

        if response.status_code == 204 or not response.text:
            return None

        return response.json()

    # ============================
    # Test Cases
    # ============================

    def create_test_case(self, body: dict) -> dict:
        return self._request("POST", "/testcase", json_body=body)

    def get_test_case(
        self, test_case_key: str, *, fields: str | None = None
    ) -> dict:
        params = {}
        if fields:
            params["fields"] = fields
        return self._request("GET", f"/testcase/{test_case_key}", params=params)

    def update_test_case(self, test_case_key: str, body: dict) -> dict:
        return self._request("PUT", f"/testcase/{test_case_key}", json_body=body)

    def delete_test_case(self, test_case_key: str) -> None:
        self._request("DELETE", f"/testcase/{test_case_key}")

    def search_test_cases(
        self,
        *,
        query: str = "",
        fields: str | None = None,
        start_at: int = 0,
        max_results: int = 50,
    ) -> dict:
        params: dict[str, Any] = {
            "query": query,
            "startAt": start_at,
            "maxResults": max_results,
        }
        if fields:
            params["fields"] = fields
        return self._request("GET", "/testcase/search", params=params)

    def get_test_case_attachments(self, test_case_key: str) -> list:
        return self._request("GET", f"/testcase/{test_case_key}/attachments")

    def get_step_attachments(
        self, test_case_key: str, step_index: int
    ) -> list:
        return self._request(
            "GET", f"/testcase/{test_case_key}/step/{step_index}/attachments"
        )

    def upload_test_case_attachment(
        self, test_case_key: str, file_content: bytes, filename: str
    ) -> dict:
        files = {"file": (filename, file_content)}
        return self._request(
            "POST",
            f"/testcase/{test_case_key}/attachments",
            files=files,
            extra_headers={"Content-Type": "multipart/form-data"},
        )

    def upload_step_attachment(
        self,
        test_case_key: str,
        step_index: int,
        file_content: bytes,
        filename: str,
    ) -> dict:
        files = {"file": (filename, file_content)}
        return self._request(
            "POST",
            f"/testcase/{test_case_key}/step/{step_index}/attachments",
            files=files,
            extra_headers={"Content-Type": "multipart/form-data"},
        )

    def get_latest_test_result(self, test_case_key: str) -> dict | None:
        return self._request(
            "GET", f"/testcase/{test_case_key}/testresult/latest"
        )

    # ============================
    # Test Plans
    # ============================

    def create_test_plan(self, body: dict) -> dict:
        return self._request("POST", "/testplan", json_body=body)

    def get_test_plan(
        self, test_plan_key: str, *, fields: str | None = None
    ) -> dict:
        params = {"fields": fields} if fields else None
        return self._request("GET", f"/testplan/{test_plan_key}", params=params)

    def update_test_plan(self, test_plan_key: str, body: dict) -> dict:
        return self._request("PUT", f"/testplan/{test_plan_key}", json_body=body)

    def delete_test_plan(self, test_plan_key: str) -> None:
        self._request("DELETE", f"/testplan/{test_plan_key}")

    def search_test_plans(
        self,
        *,
        query: str = "",
        fields: str | None = None,
        start_at: int = 0,
        max_results: int = 50,
    ) -> dict:
        params: dict[str, Any] = {
            "query": query,
            "startAt": start_at,
            "maxResults": max_results,
        }
        if fields:
            params["fields"] = fields
        return self._request("GET", "/testplan/search", params=params)

    def get_test_plan_attachments(self, test_plan_key: str) -> list:
        return self._request("GET", f"/testplan/{test_plan_key}/attachments")

    # ============================
    # Test Runs
    # ============================

    def create_test_run(self, body: dict) -> dict:
        return self._request("POST", "/testrun", json_body=body)

    def get_test_run(
        self, test_run_key: str, *, fields: str | None = None
    ) -> dict:
        params = {"fields": fields} if fields else None
        return self._request("GET", f"/testrun/{test_run_key}", params=params)

    def delete_test_run(self, test_run_key: str) -> None:
        self._request("DELETE", f"/testrun/{test_run_key}")

    def search_test_runs(
        self,
        *,
        query: str = "",
        fields: str | None = None,
        start_at: int = 0,
        max_results: int = 50,
    ) -> dict:
        params: dict[str, Any] = {
            "query": query,
            "startAt": start_at,
            "maxResults": max_results,
        }
        if fields:
            params["fields"] = fields
        return self._request("GET", "/testrun/search", params=params)

    def get_test_run_attachments(self, test_run_key: str) -> list:
        return self._request("GET", f"/testrun/{test_run_key}/attachments")

    # ============================
    # Test Results
    # ============================

    def create_test_result(self, body: dict) -> dict:
        return self._request("POST", "/testresult", json_body=body)

    def create_test_result_for_run(
        self,
        test_run_key: str,
        test_case_key: str,
        body: dict,
        *,
        environment: str,
        user_key: str,
    ) -> dict:
        params = {"environment": environment, "userKey": user_key}
        return self._request(
            "POST",
            f"/testrun/{test_run_key}/testcase/{test_case_key}/testresult",
            json_body=body,
            params=params,
        )

    def update_test_result_for_run(
        self,
        test_run_key: str,
        test_case_key: str,
        body: dict,
        *,
        environment: str,
        user_key: str,
    ) -> dict:
        params = {"environment": environment, "userKey": user_key}
        return self._request(
            "PUT",
            f"/testrun/{test_run_key}/testcase/{test_case_key}/testresult",
            json_body=body,
            params=params,
        )

    def bulk_create_test_results(
        self,
        test_run_key: str,
        body: dict,
        *,
        environment: str,
        user_key: str,
    ) -> dict:
        params = {"environment": environment, "userKey": user_key}
        return self._request(
            "POST",
            f"/testrun/{test_run_key}/testresults",
            json_body=body,
            params=params,
        )

    def get_test_results(self, test_run_key: str) -> list:
        return self._request("GET", f"/testrun/{test_run_key}/testresults")

    # ============================
    # Issue Links
    # ============================

    def get_test_cases_for_issue(
        self, issue_key: str, *, fields: str | None = None
    ) -> list:
        params = {"fields": fields} if fields else None
        return self._request(
            "GET", f"/issuelink/{issue_key}/testcases", params=params
        )

    # ============================
    # Folders
    # ============================

    def create_folder(self, body: dict) -> dict:
        return self._request("POST", "/folder", json_body=body)

    def update_folder(self, folder_id: int, body: dict) -> dict:
        return self._request("PUT", f"/folder/{folder_id}", json_body=body)

    # ============================
    # Environments
    # ============================

    def get_environments(self, project_key: str) -> list:
        return self._request(
            "GET", "/environments", params={"projectKey": project_key}
        )

    def create_environment(self, body: dict) -> dict:
        return self._request("POST", "/environments", json_body=body)

    # ============================
    # Projects
    # ============================

    def create_project(self, body: dict) -> dict:
        return self._request("POST", "/project", json_body=body)

    # ============================
    # Custom Fields
    # ============================

    def create_custom_field(self, body: dict) -> dict:
        return self._request("POST", "/customfield", json_body=body)

    def create_custom_field_option(
        self, custom_field_id: str, body: dict
    ) -> dict:
        return self._request(
            "POST", f"/customfield/{custom_field_id}/option", json_body=body
        )

    # ============================
    # Automation
    # ============================

    def import_automation_results(
        self,
        project_key: str,
        file_content: bytes,
        filename: str,
        *,
        test_cycle: str | None = None,
    ) -> dict:
        files = {"file": (filename, file_content)}
        data: dict[str, Any] = {}
        if test_cycle:
            data["testCycle"] = test_cycle
        return self._request(
            "POST",
            f"/automation/execution/{project_key}",
            files=files,
            extra_headers={"Content-Type": "multipart/form-data"},
        )

    def import_cucumber_results(
        self,
        project_key: str,
        file_content: bytes,
        filename: str,
        *,
        test_cycle: str | None = None,
    ) -> dict:
        files = {"file": (filename, file_content)}
        data: dict[str, Any] = {}
        if test_cycle:
            data["testCycle"] = test_cycle
        return self._request(
            "POST",
            f"/automation/execution/cucumber/{project_key}",
            files=files,
            extra_headers={"Content-Type": "multipart/form-data"},
        )

    def get_automation_test_cases(self, tql: str) -> list:
        return self._request("GET", "/automation/testcases", params={"tql": tql})

    # ============================
    # Execution Deletion
    # ============================

    def delete_executions(self, body: dict) -> dict:
        return self._request("POST", "/delete/executiondeletion", json_body=body)

    def get_deletion_status(self) -> dict:
        return self._request("GET", "/delete/executiondeletion/status")

    def cancel_deletion(self) -> dict:
        return self._request("POST", "/delete/executiondeletion/cancel")

    # ============================
    # Attachments
    # ============================

    def delete_attachment(self, attachment_id: str) -> None:
        self._request("DELETE", f"/attachments/{attachment_id}")

    # ============================
    # Lifecycle
    # ============================

    def close(self) -> None:
        self._client.close()
