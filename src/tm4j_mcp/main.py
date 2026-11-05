"""Точка входа MCP-сервера TM4J (Zephyr Scale)."""

from __future__ import annotations

import json
import logging
import os

# Отключаем баннер FastMCP (должно быть ДО любого импорта FastMCP)
os.environ.setdefault("FASTMCP_SHOW_SERVER_BANNER", "false")

from fastmcp import FastMCP

from .client.auth import AuthHandler
from .client.jira_client import JiraClient
from .client.tm4j_client import TM4JClient
from .config import AppConfig
from .tools.attachments import AttachmentsTool
from .tools.automation import AutomationTool
from .tools.composite import CompositeTool
from .tools.converter import ConverterTool
from .tools.customfields import CustomFieldsTool
from .tools.environments import EnvironmentsTool
from .tools.executions import ExecutionsTool
from .tools.folders import FoldersTool
from .tools.projects import ProjectsTool
from .tools.testcases import TestCasesTool
from .tools.testplans import TestPlansTool
from .tools.testresults import TestResultsTool
from .tools.testruns import TestRunsTool

logging.basicConfig(
    level=logging.ERROR,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
# Suppress FastMCP internal INFO logs
logging.getLogger("fastmcp").setLevel(logging.ERROR)
logger = logging.getLogger("tm4j_mcp")


def create_app() -> FastMCP:
    """Создать и настроить MCP-сервер с зарегистрированными инструментами."""
    config = AppConfig()
    config.validate()

    # Единый AuthHandler — одни credentials для TM4J и Jira
    auth = AuthHandler(config=config)

    tm4j_client = TM4JClient(config=config, auth=auth)
    jira_client = JiraClient(config=config, auth=auth)

    mcp = FastMCP(
        name="tm4j-mcp-server",
        version="1.0.0",
        instructions=(
            "MCP-сервер для работы с TM4J (Zephyr Scale) API. "
            f"Проект: {config.tm4j_project_key}, "
            f"Владелец: {config.tm4j_owner}. "
            "Используйте convert_to_markdown=true для удобного чтения результатов. "
            "Проверяйте step_status в ответах для контроля прогресса."
        ),
    )

    # Создаём экземпляры инструментов
    test_cases = TestCasesTool(tm4j_client, jira_client, config)
    test_plans = TestPlansTool(tm4j_client, jira_client, config)
    test_runs = TestRunsTool(tm4j_client, jira_client, config)
    test_results = TestResultsTool(tm4j_client, jira_client, config)
    folders = FoldersTool(tm4j_client, jira_client, config)
    environments = EnvironmentsTool(tm4j_client, jira_client, config)
    projects = ProjectsTool(tm4j_client, jira_client, config)
    custom_fields = CustomFieldsTool(tm4j_client, jira_client, config)
    automation = AutomationTool(tm4j_client, jira_client, config)
    executions = ExecutionsTool(tm4j_client, jira_client, config)
    attachments = AttachmentsTool(tm4j_client, jira_client, config)
    composite = CompositeTool(tm4j_client, jira_client, config)
    converter = ConverterTool(tm4j_client, jira_client, config)

    # ==================== Test Cases ====================

    @mcp.tool(description="Создать новый тест-кейс в проекте TM4J")
    def create_test_case(
        name: str,
        status: str = "Draft",
        priority: str = "Medium",
        objective: str | None = None,
        precondition: str | None = None,
        owner: str | None = None,
        folder: str | None = None,
        component: str | None = None,
        labels: str | None = None,
        test_script_type: str = "STEP",
        steps: str | None = None,
        convert_to_markdown: bool = False,
    ) -> str:
        """Создать новый тест-кейс в проекте.

        Args:
            name: Название тест-кейса (обязательно).
            status: Статус тест-кейса. Значения: Draft, Ready, Obsolete. По умолчанию: Draft.
            priority: Приоритет тест-кейса. Значения: Critical, High, Medium, Low, Trivial. По умолчанию: Medium.
            objective: Цель тест-кейса — что тестируется.
            precondition: Предусловия для выполнения тест-кейса.
            owner: Владелец тест-кейса (Jira account_id или email). Если не указан, используется значение из конфига.
            folder: Ключ папки для размещения тест-кейса (например, PRO-123).
            component: Компонент Jira, связанный с тест-кейсом.
            labels: Метка для тест-кейса в формате JSON-массива строк (например, '["regression","smoke"]').
            test_script_type: Тип скрипта теста. Значения: STEP (по шагам), TEXT (свободный текст), CHECKLIST. По умолчанию: STEP.
            steps: Шаги тест-кейса в формате JSON-массива объектов с полями index, description, expected_result.
            convert_to_markdown: Преобразовать ответ в формат Markdown. По умолчанию: false.

        Returns:
            JSON с информацией о созданном тест-кейсе или Markdown-представление.
        """
        labels_list = json.loads(labels) if labels else None
        steps_list = json.loads(steps) if steps else None
        try:
            result = test_cases.create_test_case(
                name=name,
                status=status,
                priority=priority,
                objective=objective,
                precondition=precondition,
                owner=owner,
                folder=folder,
                component=component,
                labels=labels_list,
                test_script_type=test_script_type,
                steps=steps_list,
                convert_to_markdown=convert_to_markdown,
            )
            return json.dumps(result, ensure_ascii=False, default=str)
        except Exception as e:
            return json.dumps({"error": True, "message": str(e)}, ensure_ascii=False)

    @mcp.tool(description="Получить тест-кейс по ключу (например, PRO-123)")
    def get_test_case(
        test_case_key: str,
        fields: str | None = None,
        convert_to_markdown: bool = False,
    ) -> str:
        """Получить тест-кейс по ключу.

        Args:
            test_case_key: Ключ тест-кейса в формате {PROJECT}-{NUMBER} (например, PRO-123).
            fields: Запятая разделённый список полей для извлечения (например, 'key,name,status'). Если не указано, возвращает все поля.
            convert_to_markdown: Преобразовать ответ в формат Markdown. По умолчанию: false.

        Returns:
            JSON с данными тест-кейса или Markdown-представление.
        """
        try:
            result = test_cases.get_test_case(
                test_case_key, fields=fields, convert_to_markdown=convert_to_markdown
            )
            return json.dumps(result, ensure_ascii=False, default=str)
        except Exception as e:
            return json.dumps({"error": True, "message": str(e)}, ensure_ascii=False)

    @mcp.tool(description="Обновить существующий тест-кейс")
    def update_test_case(
        test_case_key: str,
        name: str | None = None,
        status: str | None = None,
        priority: str | None = None,
        objective: str | None = None,
        precondition: str | None = None,
        owner: str | None = None,
        folder: str | None = None,
        component: str | None = None,
        labels: str | None = None,
        steps: str | None = None,
        convert_to_markdown: bool = False,
    ) -> str:
        """Обновить существующий тест-кейс.

        Args:
            test_case_key: Ключ тест-кейса в формате {PROJECT}-{NUMBER} (например, PRO-123).
            name: Новое название тест-кейса.
            status: Новый статус (Draft, Ready, Obsolete).
            priority: Новый приоритет (Critical, High, Medium, Low, Trivial).
            objective: Новая цель тест-кейса.
            precondition: Новые предусловия.
            owner: Новый владелец (Jira account_id или email).
            folder: Новая папка (ключ папки).
            component: Новый компонент Jira.
            labels: Новые метки в формате JSON-массива строк.
            steps: Новые шаги теста в формате JSON-массива объектов.
            convert_to_markdown: Преобразовать ответ в формат Markdown. По умолчанию: false.

        Returns:
            JSON с обновлёнными данными тест-кейса или Markdown-представление.
        """
        labels_list = json.loads(labels) if labels else None
        steps_list = json.loads(steps) if steps else None
        try:
            result = test_cases.update_test_case(
                test_case_key,
                name=name,
                status=status,
                priority=priority,
                objective=objective,
                precondition=precondition,
                owner=owner,
                folder=folder,
                component=component,
                labels=labels_list,
                steps=steps_list,
                convert_to_markdown=convert_to_markdown,
            )
            return json.dumps(result, ensure_ascii=False, default=str)
        except Exception as e:
            return json.dumps({"error": True, "message": str(e)}, ensure_ascii=False)

    @mcp.tool(description="Удалить тест-кейс по ключу")
    def delete_test_case(test_case_key: str) -> str:
        """Удалить тест-кейс.

        Args:
            test_case_key: Ключ тест-кейса в формате {PROJECT}-{NUMBER} (например, PRO-123).

        Returns:
            JSON подтверждение удаления.
        """
        try:
            result = test_cases.delete_test_case(test_case_key)
            return json.dumps(result, ensure_ascii=False, default=str)
        except Exception as e:
            return json.dumps({"error": True, "message": str(e)}, ensure_ascii=False)

    @mcp.tool(description="Поиск тест-кейсов по фильтру")
    def search_test_cases(
        query: str = "",
        fields: str | None = None,
        start_at: int = 0,
        max_results: int = 50,
        convert_to_markdown: bool = False,
    ) -> str:
        """Поиск тест-кейсов.

        Args:
            query: Строка фильтрации (TQL). Например, 'project = "PRO" AND status = "Ready"'. Пустая строка — все кейсы.
            fields: Запятая разделённый список полей для извлечения. Если не указано, возвращает все поля.
            start_at: Смещение для пагинации (номер первого результата). По умолчанию: 0.
            max_results: Максимальное количество результатов. По умолчанию: 50.
            convert_to_markdown: Преобразовать ответ в формат Markdown. По умолчанию: false.

        Returns:
            JSON с массивом найденных тест-кейсов или Markdown-представление.
        """
        try:
            result = test_cases.search_test_cases(
                query=query,
                fields=fields,
                start_at=start_at,
                max_results=max_results,
                convert_to_markdown=convert_to_markdown,
            )
            return json.dumps(result, ensure_ascii=False, default=str)
        except Exception as e:
            return json.dumps({"error": True, "message": str(e)}, ensure_ascii=False)

    @mcp.tool(description="Получить вложения тест-кейса")
    def get_test_case_attachments(test_case_key: str) -> str:
        """Получить вложения тест-кейса.

        Args:
            test_case_key: Ключ тест-кейса в формате {PROJECT}-{NUMBER}.

        Returns:
            JSON с информацией о вложениях.
        """
        try:
            result = test_cases.get_test_case_attachments(test_case_key)
            return json.dumps(result, ensure_ascii=False, default=str)
        except Exception as e:
            return json.dumps({"error": True, "message": str(e)}, ensure_ascii=False)

    @mcp.tool(description="Получить последний результат выполнения тест-кейса")
    def get_latest_test_result(
        test_case_key: str, convert_to_markdown: bool = False
    ) -> str:
        """Получить последний результат выполнения тест-кейса.

        Args:
            test_case_key: Ключ тест-кейса в формате {PROJECT}-{NUMBER}.
            convert_to_markdown: Преобразовать ответ в формат Markdown. По умолчанию: false.

        Returns:
            JSON с последним результатом или Markdown-представление.
        """
        try:
            result = test_cases.get_latest_test_result(
                test_case_key, convert_to_markdown=convert_to_markdown
            )
            return json.dumps(result, ensure_ascii=False, default=str)
        except Exception as e:
            return json.dumps({"error": True, "message": str(e)}, ensure_ascii=False)

    @mcp.tool(description="Получить тест-кейсы связанные с Jira задачей")
    def get_test_cases_for_issue(
        issue_key: str,
        fields: str | None = None,
        convert_to_markdown: bool = False,
    ) -> str:
        """Получить тест-кейсы связанные с Jira задачей.

        Args:
            issue_key: Ключ Jira задачи в формате {PROJECT}-{NUMBER} (например, PRO-456).
            fields: Запятая разделённый список полей для извлечения.
            convert_to_markdown: Преобразовать ответ в формат Markdown. По умолчанию: false.

        Returns:
            JSON с массивом связанных тест-кейсов или Markdown-представление.
        """
        try:
            result = test_cases.get_test_cases_for_issue(
                issue_key, fields=fields, convert_to_markdown=convert_to_markdown
            )
            return json.dumps(result, ensure_ascii=False, default=str)
        except Exception as e:
            return json.dumps({"error": True, "message": str(e)}, ensure_ascii=False)

    # ==================== Test Plans ====================

    @mcp.tool(description="Создать новый тест-план")
    def create_test_plan(name: str, body: str | None = None, convert_to_markdown: bool = False) -> str:
        """Создать новый тест-план.

        Args:
            name: Название тест-плана (обязательно).
            body: Дополнительные данные тест-плана в формате JSON-объекта.
            convert_to_markdown: Преобразовать ответ в формат Markdown. По умолчанию: false.

        Returns:
            JSON с информацией о созданном тест-плане или Markdown-представление.
        """
        body_dict = json.loads(body) if body else None
        try:
            result = test_plans.create_test_plan(
                name=name, body=body_dict, convert_to_markdown=convert_to_markdown
            )
            return json.dumps(result, ensure_ascii=False, default=str)
        except Exception as e:
            return json.dumps({"error": True, "message": str(e)}, ensure_ascii=False)

    @mcp.tool(description="Получить тест-план по ключу")
    def get_test_plan(
        test_plan_key: str, fields: str | None = None, convert_to_markdown: bool = False
    ) -> str:
        """Получить тест-план по ключу.

        Args:
            test_plan_key: Ключ тест-плана в формате {PROJECT}-{NUMBER}.
            fields: Запятая разделённый список полей для извлечения.
            convert_to_markdown: Преобразовать ответ в формат Markdown. По умолчанию: false.

        Returns:
            JSON с данными тест-плана или Markdown-представление.
        """
        try:
            result = test_plans.get_test_plan(
                test_plan_key, fields=fields, convert_to_markdown=convert_to_markdown
            )
            return json.dumps(result, ensure_ascii=False, default=str)
        except Exception as e:
            return json.dumps({"error": True, "message": str(e)}, ensure_ascii=False)

    @mcp.tool(description="Обновить тест-план")
    def update_test_plan(
        test_plan_key: str, body: str, convert_to_markdown: bool = False
    ) -> str:
        """Обновить тест-план.

        Args:
            test_plan_key: Ключ тест-плана в формате {PROJECT}-{NUMBER}.
            body: Обновлённые данные тест-плана в формате JSON-объекта (обязательно).
            convert_to_markdown: Преобразовать ответ в формат Markdown. По умолчанию: false.

        Returns:
            JSON с обновлёнными данными тест-плана или Markdown-представление.
        """
        body_dict = json.loads(body)
        try:
            result = test_plans.update_test_plan(
                test_plan_key, body=body_dict, convert_to_markdown=convert_to_markdown
            )
            return json.dumps(result, ensure_ascii=False, default=str)
        except Exception as e:
            return json.dumps({"error": True, "message": str(e)}, ensure_ascii=False)

    @mcp.tool(description="Удалить тест-план по ключу")
    def delete_test_plan(test_plan_key: str) -> str:
        """Удалить тест-план.

        Args:
            test_plan_key: Ключ тест-плана в формате {PROJECT}-{NUMBER}.

        Returns:
            JSON подтверждение удаления.
        """
        try:
            result = test_plans.delete_test_plan(test_plan_key)
            return json.dumps(result, ensure_ascii=False, default=str)
        except Exception as e:
            return json.dumps({"error": True, "message": str(e)}, ensure_ascii=False)

    @mcp.tool(description="Поиск тест-планов по фильтру")
    def search_test_plans(
        query: str = "",
        fields: str | None = None,
        start_at: int = 0,
        max_results: int = 50,
        convert_to_markdown: bool = False,
    ) -> str:
        """Поиск тест-планов.

        Args:
            query: Строка фильтрации (TQL). Например, 'project = "PRO"'. Пустая строка — все планы.
            fields: Запятая разделённый список полей для извлечения.
            start_at: Смещение для пагинации. По умолчанию: 0.
            max_results: Максимальное количество результатов. По умолчанию: 50.
            convert_to_markdown: Преобразовать ответ в формат Markdown. По умолчанию: false.

        Returns:
            JSON с массивом найденных тест-планов или Markdown-представление.
        """
        try:
            result = test_plans.search_test_plans(
                query=query,
                fields=fields,
                start_at=start_at,
                max_results=max_results,
                convert_to_markdown=convert_to_markdown,
            )
            return json.dumps(result, ensure_ascii=False, default=str)
        except Exception as e:
            return json.dumps({"error": True, "message": str(e)}, ensure_ascii=False)

    # ==================== Test Runs ====================

    @mcp.tool(description="Создать новый тест-прогон")
    def create_test_run(
        name: str,
        folder: str | None = None,
        iteration: str | None = None,
        version: str | None = None,
        owner: str | None = None,
        items: str | None = None,
        body: str | None = None,
        convert_to_markdown: bool = False,
    ) -> str:
        """Создать новый тест-прогон.

        Args:
            name: Название тест-прогона (обязательно).
            folder: Ключ папки для размещения тест-прогона.
            iteration: Номер итерации (например, Sprint 5).
            version: Версия продукта (например, v2.1.0).
            owner: Владелец тест-прогона (Jira account_id или email).
            items: Список тест-кейсов для включения в прогон в формате JSON-массива ключей (например, '["PRO-1","PRO-2"]').
            body: Дополнительные данные тест-прогона в формате JSON-объекта.
            convert_to_markdown: Преобразовать ответ в формат Markdown. По умолчанию: false.

        Returns:
            JSON с информацией о созданном тест-прогоне или Markdown-представление.
        """
        items_list = json.loads(items) if items else None
        body_dict = json.loads(body) if body else None
        try:
            result = test_runs.create_test_run(
                name=name,
                folder=folder,
                iteration=iteration,
                version=version,
                owner=owner,
                items=items_list,
                body=body_dict,
                convert_to_markdown=convert_to_markdown,
            )
            return json.dumps(result, ensure_ascii=False, default=str)
        except Exception as e:
            return json.dumps({"error": True, "message": str(e)}, ensure_ascii=False)

    @mcp.tool(description="Получить тест-прогон по ключу")
    def get_test_run(
        test_run_key: str, fields: str | None = None, convert_to_markdown: bool = False
    ) -> str:
        """Получить тест-прогон по ключу.

        Args:
            test_run_key: Ключ тест-прогона в формате {PROJECT}-{NUMBER}.
            fields: Запятая разделённый список полей для извлечения.
            convert_to_markdown: Преобразовать ответ в формат Markdown. По умолчанию: false.

        Returns:
            JSON с данными тест-прогона или Markdown-представление.
        """
        try:
            result = test_runs.get_test_run(
                test_run_key, fields=fields, convert_to_markdown=convert_to_markdown
            )
            return json.dumps(result, ensure_ascii=False, default=str)
        except Exception as e:
            return json.dumps({"error": True, "message": str(e)}, ensure_ascii=False)

    @mcp.tool(description="Удалить тест-прогон по ключу")
    def delete_test_run(test_run_key: str) -> str:
        """Удалить тест-прогон.

        Args:
            test_run_key: Ключ тест-прогона в формате {PROJECT}-{NUMBER}.

        Returns:
            JSON подтверждение удаления.
        """
        try:
            result = test_runs.delete_test_run(test_run_key)
            return json.dumps(result, ensure_ascii=False, default=str)
        except Exception as e:
            return json.dumps({"error": True, "message": str(e)}, ensure_ascii=False)

    @mcp.tool(description="Поиск тест-прогонов по фильтру")
    def search_test_runs(
        query: str = "",
        fields: str | None = None,
        start_at: int = 0,
        max_results: int = 50,
        convert_to_markdown: bool = False,
    ) -> str:
        """Поиск тест-прогонов.

        Args:
            query: Строка фильтрации (TQL). Например, 'project = "PRO" AND status = "OPEN"'. Пустая строка — все прогоны.
            fields: Запятая разделённый список полей для извлечения.
            start_at: Смещение для пагинации. По умолчанию: 0.
            max_results: Максимальное количество результатов. По умолчанию: 50.
            convert_to_markdown: Преобразовать ответ в формат Markdown. По умолчанию: false.

        Returns:
            JSON с массивом найденных тест-прогонов или Markdown-представление.
        """
        try:
            result = test_runs.search_test_runs(
                query=query,
                fields=fields,
                start_at=start_at,
                max_results=max_results,
                convert_to_markdown=convert_to_markdown,
            )
            return json.dumps(result, ensure_ascii=False, default=str)
        except Exception as e:
            return json.dumps({"error": True, "message": str(e)}, ensure_ascii=False)

    # ==================== Test Results ====================

    @mcp.tool(description="Создать результат выполнения тест-кейса")
    def create_test_result(
        test_case_key: str,
        status: str,
        comment: str | None = None,
        environment: str | None = None,
        user_key: str | None = None,
        execution_time: int | None = None,
        script_results: str | None = None,
        convert_to_markdown: bool = False,
    ) -> str:
        """Создать результат выполнения тест-кейса.

        Args:
            test_case_key: Ключ тест-кейса в формате {PROJECT}-{NUMBER}.
            status: Статус выполнения. Значения: Pass, Fail, Blocked, NoGO (обязательно).
            comment: Комментарий к результату.
            environment: Название окружения где выполнялся тест.
            user_key: Jira account_id пользователя выполнившего тест.
            execution_time: Время выполнения теста в секундах.
            script_results: Результаты скриптов в формате JSON-массива объектов.
            convert_to_markdown: Преобразовать ответ в формат Markdown. По умолчанию: false.

        Returns:
            JSON с данными созданного результата или Markdown-представление.
        """
        sr_list = json.loads(script_results) if script_results else None
        try:
            result = test_results.create_test_result(
                test_case_key=test_case_key,
                status=status,
                comment=comment,
                environment=environment,
                user_key=user_key,
                execution_time=execution_time,
                script_results=sr_list,
                convert_to_markdown=convert_to_markdown,
            )
            return json.dumps(result, ensure_ascii=False, default=str)
        except Exception as e:
            return json.dumps({"error": True, "message": str(e)}, ensure_ascii=False)

    @mcp.tool(description="Создать результат для тест-кейса в рамках тест-прогона")
    def create_test_result_for_run(
        test_run_key: str,
        test_case_key: str,
        status: str,
        environment: str,
        comment: str | None = None,
        user_key: str | None = None,
        execution_time: int | None = None,
        script_results: str | None = None,
        convert_to_markdown: bool = False,
    ) -> str:
        """Создать результат для тест-кейса в тест-прогоне.

        Args:
            test_run_key: Ключ тест-прогона в формате {PROJECT}-{NUMBER}.
            test_case_key: Ключ тест-кейса в формате {PROJECT}-{NUMBER}.
            status: Статус выполнения. Значения: Pass, Fail, Blocked, NoGO (обязательно).
            environment: Название окружения (обязательно).
            comment: Комментарий к результату.
            user_key: Jira account_id пользователя выполнившего тест.
            execution_time: Время выполнения теста в секундах.
            script_results: Результаты скриптов в формате JSON-массива объектов.
            convert_to_markdown: Преобразовать ответ в формат Markdown. По умолчанию: false.

        Returns:
            JSON с данными созданного результата или Markdown-представление.
        """
        sr_list = json.loads(script_results) if script_results else None
        try:
            result = test_results.create_test_result_for_run(
                test_run_key=test_run_key,
                test_case_key=test_case_key,
                status=status,
                environment=environment,
                comment=comment,
                user_key=user_key,
                execution_time=execution_time,
                script_results=sr_list,
                convert_to_markdown=convert_to_markdown,
            )
            return json.dumps(result, ensure_ascii=False, default=str)
        except Exception as e:
            return json.dumps({"error": True, "message": str(e)}, ensure_ascii=False)

    @mcp.tool(description="Обновить результат тест-кейса в тест-прогоне")
    def update_test_result_for_run(
        test_run_key: str,
        test_case_key: str,
        status: str,
        environment: str,
        comment: str | None = None,
        user_key: str | None = None,
        execution_time: int | None = None,
        script_results: str | None = None,
        convert_to_markdown: bool = False,
    ) -> str:
        """Обновить результат тест-кейса в тест-прогоне.

        Args:
            test_run_key: Ключ тест-прогона в формате {PROJECT}-{NUMBER}.
            test_case_key: Ключ тест-кейса в формате {PROJECT}-{NUMBER}.
            status: Статус выполнения. Значения: Pass, Fail, Blocked, NoGO (обязательно).
            environment: Название окружения (обязательно).
            comment: Комментарий к результату.
            user_key: Jira account_id пользователя выполнившего тест.
            execution_time: Время выполнения теста в секундах.
            script_results: Результаты скриптов в формате JSON-массива объектов.
            convert_to_markdown: Преобразовать ответ в формат Markdown. По умолчанию: false.

        Returns:
            JSON с обновлёнными данными результата или Markdown-представление.
        """
        sr_list = json.loads(script_results) if script_results else None
        try:
            result = test_results.update_test_result_for_run(
                test_run_key=test_run_key,
                test_case_key=test_case_key,
                status=status,
                environment=environment,
                comment=comment,
                user_key=user_key,
                execution_time=execution_time,
                script_results=sr_list,
                convert_to_markdown=convert_to_markdown,
            )
            return json.dumps(result, ensure_ascii=False, default=str)
        except Exception as e:
            return json.dumps({"error": True, "message": str(e)}, ensure_ascii=False)

    @mcp.tool(description="Массовое создание результатов тестирования для тест-прогона")
    def bulk_create_test_results(
        test_run_key: str,
        results: str,
        environment: str,
        user_key: str | None = None,
        convert_to_markdown: bool = False,
    ) -> str:
        """Массовое создание результатов тестирования.

        Args:
            test_run_key: Ключ тест-прогона в формате {PROJECT}-{NUMBER}.
            results: Массив результатов в формате JSON. Каждый элемент: {"testCaseKey": "PRO-1", "status": "Pass", "comment": "..."}.
            environment: Название окружения (обязательно).
            user_key: Jira account_id пользователя выполнившего тесты.
            convert_to_markdown: Преобразовать ответ в формат Markdown. По умолчанию: false.

        Returns:
            JSON с массивом созданных результатов или Markdown-представление.
        """
        results_list = json.loads(results)
        try:
            result = test_results.bulk_create_test_results(
                test_run_key=test_run_key,
                results=results_list,
                environment=environment,
                user_key=user_key,
                convert_to_markdown=convert_to_markdown,
            )
            return json.dumps(result, ensure_ascii=False, default=str)
        except Exception as e:
            return json.dumps({"error": True, "message": str(e)}, ensure_ascii=False)

    @mcp.tool(description="Получить все результаты тест-прогона")
    def get_test_results(
        test_run_key: str, convert_to_markdown: bool = False
    ) -> str:
        """Получить все результаты тест-прогона.

        Args:
            test_run_key: Ключ тест-прогона в формате {PROJECT}-{NUMBER}.
            convert_to_markdown: Преобразовать ответ в формат Markdown. По умолчанию: false.

        Returns:
            JSON с массивом результатов или Markdown-представление.
        """
        try:
            result = test_results.get_test_results(
                test_run_key, convert_to_markdown=convert_to_markdown
            )
            return json.dumps(result, ensure_ascii=False, default=str)
        except Exception as e:
            return json.dumps({"error": True, "message": str(e)}, ensure_ascii=False)

    # ==================== Folders ====================

    @mcp.tool(description="Создать новую папку в проекте")
    def create_folder(
        name: str, folder_type: str = "TEST", convert_to_markdown: bool = False
    ) -> str:
        """Создать новую папку в проекте.

        Args:
            name: Название папки (обязательно).
            folder_type: Тип папки. Значения: TEST, PLAN, RUN. По умолчанию: TEST.
            convert_to_markdown: Преобразовать ответ в формат Markdown. По умолчанию: false.

        Returns:
            JSON с данными созданной папки или Markdown-представление.
        """
        try:
            result = folders.create_folder(
                name=name, folder_type=folder_type, convert_to_markdown=convert_to_markdown
            )
            return json.dumps(result, ensure_ascii=False, default=str)
        except Exception as e:
            return json.dumps({"error": True, "message": str(e)}, ensure_ascii=False)

    @mcp.tool(description="Обновить папку")
    def update_folder(
        folder_id: int,
        name: str | None = None,
        folder_type: str | None = None,
        convert_to_markdown: bool = False,
    ) -> str:
        """Обновить папку.

        Args:
            folder_id: ID папки (число).
            name: Новое название папки.
            folder_type: Новый тип папки (TEST, PLAN, RUN).
            convert_to_markdown: Преобразовать ответ в формат Markdown. По умолчанию: false.

        Returns:
            JSON с обновлёнными данными папки или Markdown-представление.
        """
        try:
            result = folders.update_folder(
                folder_id,
                name=name,
                folder_type=folder_type,
                convert_to_markdown=convert_to_markdown,
            )
            return json.dumps(result, ensure_ascii=False, default=str)
        except Exception as e:
            return json.dumps({"error": True, "message": str(e)}, ensure_ascii=False)

    # ==================== Environments ====================

    @mcp.tool(description="Получить окружения проекта")
    def get_environments(
        project_key: str | None = None, convert_to_markdown: bool = False
    ) -> str:
        """Получить окружения проекта.

        Args:
            project_key: Ключ Jira проекта (например, PRO). Если не указан, используется значение из конфига.
            convert_to_markdown: Преобразовать ответ в формат Markdown. По умолчанию: false.

        Returns:
            JSON с массивом окружений или Markdown-представление.
        """
        try:
            result = environments.get_environments(
                project_key=project_key, convert_to_markdown=convert_to_markdown
            )
            return json.dumps(result, ensure_ascii=False, default=str)
        except Exception as e:
            return json.dumps({"error": True, "message": str(e)}, ensure_ascii=False)

    @mcp.tool(description="Создать новое окружение")
    def create_environment(
        name: str, description: str | None = None, convert_to_markdown: bool = False
    ) -> str:
        """Создать новое окружение.

        Args:
            name: Название окружения (обязательно).
            description: Описание окружения.
            convert_to_markdown: Преобразовать ответ в формат Markdown. По умолчанию: false.

        Returns:
            JSON с данными созданного окружения или Markdown-представление.
        """
        try:
            result = environments.create_environment(
                name=name, description=description, convert_to_markdown=convert_to_markdown
            )
            return json.dumps(result, ensure_ascii=False, default=str)
        except Exception as e:
            return json.dumps({"error": True, "message": str(e)}, ensure_ascii=False)

    # ==================== Projects ====================

    @mcp.tool(description="Создать или включить проект в TM4J")
    def create_project(
        project_key: str, enable: bool = True, convert_to_markdown: bool = False
    ) -> str:
        """Создать/включить проект в TM4J.

        Args:
            project_key: Ключ Jira проекта (например, PRO).
            enable: Включить проект для использования в TM4J. По умолчанию: true.
            convert_to_markdown: Преобразовать ответ в формат Markdown. По умолчанию: false.

        Returns:
            JSON с данными проекта или Markdown-представление.
        """
        try:
            result = projects.create_project(
                project_key=project_key,
                enable=enable,
                convert_to_markdown=convert_to_markdown,
            )
            return json.dumps(result, ensure_ascii=False, default=str)
        except Exception as e:
            return json.dumps({"error": True, "message": str(e)}, ensure_ascii=False)

    # ==================== Custom Fields ====================

    @mcp.tool(description="Создать кастомное поле для проекта")
    def create_custom_field(
        name: str,
        field_type: str,
        category: str,
        description: str | None = None,
        required: bool = False,
        convert_to_markdown: bool = False,
    ) -> str:
        """Создать кастомное поле для проекта.

        Args:
            name: Название кастомного поля (обязательно).
            field_type: Тип поля. Значения: text, number, date, select, multiSelect, truefalse, user, customstatus.
            category: Категория поля (например, test-case, test-plan, test-run).
            description: Описание поля.
            required: Является ли поле обязательным. По умолчанию: false.
            convert_to_markdown: Преобразовать ответ в формат Markdown. По умолчанию: false.

        Returns:
            JSON с данными созданного поля или Markdown-представление.
        """
        try:
            result = custom_fields.create_custom_field(
                name=name,
                field_type=field_type,
                category=category,
                description=description,
                required=required,
                convert_to_markdown=convert_to_markdown,
            )
            return json.dumps(result, ensure_ascii=False, default=str)
        except Exception as e:
            return json.dumps({"error": True, "message": str(e)}, ensure_ascii=False)

    @mcp.tool(description="Добавить опцию в кастомное поле типа select")
    def create_custom_field_option(
        custom_field_id: str, name: str, convert_to_markdown: bool = False
    ) -> str:
        """Добавить опцию в кастомное поле.

        Args:
            custom_field_id: ID кастомного поля (строка).
            name: Название новой опции.
            convert_to_markdown: Преобразовать ответ в формат Markdown. По умолчанию: false.

        Returns:
            JSON с данными созданной опции или Markdown-представление.
        """
        try:
            result = custom_fields.create_custom_field_option(
                custom_field_id, name=name, convert_to_markdown=convert_to_markdown
            )
            return json.dumps(result, ensure_ascii=False, default=str)
        except Exception as e:
            return json.dumps({"error": True, "message": str(e)}, ensure_ascii=False)

    # ==================== Automation ====================

    @mcp.tool(description="Получить автоматизированные тест-кейсы по TQL-запросу")
    def get_automation_test_cases(
        tql: str, convert_to_markdown: bool = False
    ) -> str:
        """Получить тест-кейсы по TQL-запросу.

        Args:
            tql: TQL-запрос для фильтрации тест-кейсов. Например, 'project = "PRO" AND type = "Automation"'.
            convert_to_markdown: Преобразовать ответ в формат Markdown. По умолчанию: false.

        Returns:
            JSON с массивом найденных тест-кейсов или Markdown-представление.
        """
        try:
            result = automation.get_automation_test_cases(
                tql=tql, convert_to_markdown=convert_to_markdown
            )
            return json.dumps(result, ensure_ascii=False, default=str)
        except Exception as e:
            return json.dumps({"error": True, "message": str(e)}, ensure_ascii=False)

    # ==================== Execution Deletion ====================

    @mcp.tool(description="Запросить удаление старых результатов выполнения")
    def delete_executions(delete_before: str, project_key: str | None = None) -> str:
        """Запросить удаление результатов выполнения.

        Args:
            delete_before: Дата в формате ISO 8601 (например, 2025-01-01T00:00:00Z). Удалит результаты раньше этой даты.
            project_key: Ключ Jira проекта для фильтрации. Если не указан, удаляет для всех проектов.

        Returns:
            JSON со статусом запроса на удаление.
        """
        try:
            result = executions.delete_executions(
                delete_before=delete_before, project_key=project_key
            )
            return json.dumps(result, ensure_ascii=False, default=str)
        except Exception as e:
            return json.dumps({"error": True, "message": str(e)}, ensure_ascii=False)

    @mcp.tool(description="Получить статус текущего удаления результатов")
    def get_deletion_status() -> str:
        """Получить статус удаления результатов.

        Returns:
            JSON со статусом операции удаления.
        """
        try:
            result = executions.get_deletion_status()
            return json.dumps(result, ensure_ascii=False, default=str)
        except Exception as e:
            return json.dumps({"error": True, "message": str(e)}, ensure_ascii=False)

    @mcp.tool(description="Отменить запрос на удаление результатов")
    def cancel_deletion() -> str:
        """Отменить запрос на удаление результатов.

        Returns:
            JSON подтверждение отмены.
        """
        try:
            result = executions.cancel_deletion()
            return json.dumps(result, ensure_ascii=False, default=str)
        except Exception as e:
            return json.dumps({"error": True, "message": str(e)}, ensure_ascii=False)

    # ==================== Attachments ====================

    @mcp.tool(description="Удалить вложение по ID")
    def delete_attachment(attachment_id: str) -> str:
        """Удалить вложение по ID.

        Args:
            attachment_id: ID вложения (строка).

        Returns:
            JSON подтверждение удаления.
        """
        try:
            result = attachments.delete_attachment(attachment_id)
            return json.dumps(result, ensure_ascii=False, default=str)
        except Exception as e:
            return json.dumps({"error": True, "message": str(e)}, ensure_ascii=False)

    # ==================== Composite Views ====================

    @mcp.tool(description="Получить полную информацию о тест-кейсе (шаги, результаты, вложения)")
    def get_test_case_full_details(
        test_case_key: str, convert_to_markdown: bool = False
    ) -> str:
        """Получить полную информацию о тест-кейсе с шагами, результатами и вложениями.

        Агрегирует данные из нескольких API вызовов для полного представления тест-кейса.

        Args:
            test_case_key: Ключ тест-кейса в формате {PROJECT}-{NUMBER}.
            convert_to_markdown: Преобразовать ответ в формат Markdown. По умолчанию: false.

        Returns:
            JSON с полными данными тест-кейса или Markdown-представление.
        """
        try:
            result = composite.get_test_case_full_details(
                test_case_key, convert_to_markdown=convert_to_markdown
            )
            return json.dumps(result, ensure_ascii=False, default=str)
        except Exception as e:
            return json.dumps({"error": True, "message": str(e)}, ensure_ascii=False)

    @mcp.tool(description="Получить полную информацию о тест-прогоне (результаты, статистика)")
    def get_test_run_full_details(
        test_run_key: str, convert_to_markdown: bool = False
    ) -> str:
        """Получить полную информацию о тест-прогоне с результатами и статистикой.

        Агрегирует данные тест-прогона, результаты выполнения и вычисляет статистику.

        Args:
            test_run_key: Ключ тест-прогона в формате {PROJECT}-{NUMBER}.
            convert_to_markdown: Преобразовать ответ в формат Markdown. По умолчанию: false.

        Returns:
            JSON с полными данными тест-прогона и статистикой или Markdown-представление.
        """
        try:
            result = composite.get_test_run_full_details(
                test_run_key, convert_to_markdown=convert_to_markdown
            )
            return json.dumps(result, ensure_ascii=False, default=str)
        except Exception as e:
            return json.dumps({"error": True, "message": str(e)}, ensure_ascii=False)

    @mcp.tool(description="Полный обзор тестирования проекта (окружения, прогоны, кейсы)")
    def get_project_test_overview(
        project_key: str | None = None, convert_to_markdown: bool = False
    ) -> str:
        """Полный обзор тестирования проекта: окружения, прогоны, кейсы.

        Агрегирует статистику тестирования для указанного проекта.

        Args:
            project_key: Ключ Jira проекта. Если не указан, используется значение из конфига.
            convert_to_markdown: Преобразовать ответ в формат Markdown. По умолчанию: false.

        Returns:
            JSON с полным обзором проекта или Markdown-представление.
        """
        try:
            result = composite.get_project_test_overview(
                project_key=project_key, convert_to_markdown=convert_to_markdown
            )
            return json.dumps(result, ensure_ascii=False, default=str)
        except Exception as e:
            return json.dumps({"error": True, "message": str(e)}, ensure_ascii=False)

    @mcp.tool(description="Поиск тест-кейсов с агрегацией результатов и статистикой")
    def search_and_aggregate_results(
        query: str = "",
        max_results: int = 50,
        convert_to_markdown: bool = False,
    ) -> str:
        """Поиск тест-кейсов с агрегацией результатов и статистикой.

        Выполняет поиск тест-кейсов и агрегирует результаты их выполнения.

        Args:
            query: Строка фильтрации (TQL). Пустая строка — все кейсы.
            max_results: Максимальное количество результатов. По умолчанию: 50.
            convert_to_markdown: Преобразовать ответ в формат Markdown. По умолчанию: false.

        Returns:
            JSON с результатами поиска и агрегированной статистикой или Markdown-представление.
        """
        try:
            result = composite.search_and_aggregate_results(
                query=query,
                max_results=max_results,
                convert_to_markdown=convert_to_markdown,
            )
            return json.dumps(result, ensure_ascii=False, default=str)
        except Exception as e:
            return json.dumps({"error": True, "message": str(e)}, ensure_ascii=False)

    # ==================== Owner Resolution ====================

    @mcp.tool(description="Разрешить identifier в account_id владельца через Jira API")
    def resolve_owner(identifier: str) -> str:
        """Разрешить identifier в account_id владельца.

        Поддерживает: myself, issue key (PROJ-123), email, account_id (32 hex символа), query.

        Args:
            identifier: Идентификатор для разрешения. Варианты:
                - "myself" / "self" — вернёт account_id текущего авторизованного пользователя (через /rest/api/2/myself)
                - Jira issue key (например, PRO-123) — вернёт account_id автора задачи
                - Email (например, user@example.com) — вернёт account_id пользователя
                - Account ID (32 hex символа) — вернёт тот же ID
                - Query строка — поищет пользователя по имени

        Returns:
            JSON с account_id владельца.
        """
        try:
            account_id = jira_client.resolve_owner(identifier)
            return json.dumps({"account_id": account_id}, ensure_ascii=False)
        except Exception as e:
            return json.dumps(
                {"error": True, "message": str(e), "identifier": identifier},
                ensure_ascii=False,
            )

    # ==================== Markdown Converter ====================

    @mcp.tool(description="Конвертировать JSON-данные TM4J в формат Markdown")
    def convert_response_to_markdown(
        data: str, entity_type: str = "data"
    ) -> str:
        """Конвертировать JSON-данные в Markdown.

        Args:
            data: JSON-строка с данными для конвертации.
            entity_type: Тип TM4J-сущности для форматирования. Значения: test_case, test_run, test_result, test_plan, folder, environment, project, custom_field, data (универсальный). По умолчанию: data.

        Returns:
            JSON с полем markdown содержащим отформатированный текст.
        """
        try:
            data_obj = json.loads(data)
            result = converter.convert_response_to_markdown(
                data=data_obj, entity_type=entity_type
            )
            return json.dumps(result, ensure_ascii=False, default=str)
        except Exception as e:
            return json.dumps({"error": True, "message": str(e)}, ensure_ascii=False)

    # ==================== MCP Resources ====================

    @mcp.resource(
        f"resource://tm4j/project/{config.tm4j_project_key}/overview",
        description=f"Обзор тестирования проекта {config.tm4j_project_key}: окружения, прогоны, кейсы",
    )
    async def resource_project_overview() -> str:
        """Ресурс: полный обзор тестирования проекта."""
        try:
            result = composite.get_project_test_overview(
                project_key=config.tm4j_project_key, convert_to_markdown=True
            )
            return result.get("markdown", str(result))
        except Exception as e:
            return f"Ошибка получения обзора проекта: {e}"

    @mcp.resource(
        "resource://tm4j/environments",
        description=f"Окружения проекта {config.tm4j_project_key}",
    )
    async def resource_environments() -> str:
        """Ресурс: список окружений проекта."""
        try:
            result = environments.get_environments(
                project_key=config.tm4j_project_key, convert_to_markdown=True
            )
            return result.get("markdown", str(result))
        except Exception as e:
            return f"Ошибка получения окружений: {e}"

    @mcp.resource(
        "resource://tm4j/test-cases/ready",
        description=f"Готовые к выполнению тест-кейсы проекта {config.tm4j_project_key}",
    )
    async def resource_ready_test_cases() -> str:
        """Ресурс: готовые тест-кейсы (status=Ready)."""
        try:
            result = test_cases.search_test_cases(
                query=f'project = "{config.tm4j_project_key}" AND status = "Ready"',
                convert_to_markdown=True,
            )
            return result.get("markdown", str(result))
        except Exception as e:
            return f"Ошибка получения готовых тест-кейсов: {e}"

    @mcp.resource(
        "resource://tm4j/test-cases/all",
        description=f"Все тест-кейсы проекта {config.tm4j_project_key}",
    )
    async def resource_all_test_cases() -> str:
        """Ресурс: все тест-кейсы проекта."""
        try:
            result = test_cases.search_test_cases(
                query=f'project = "{config.tm4j_project_key}"',
                convert_to_markdown=True,
            )
            return result.get("markdown", str(result))
        except Exception as e:
            return f"Ошибка получения тест-кейсов: {e}"

    @mcp.resource(
        "resource://tm4j/test-runs/open",
        description=f"Открытые тест-прогоны проекта {config.tm4j_project_key}",
    )
    async def resource_open_test_runs() -> str:
        """Ресурс: открытые тест-прогоны."""
        try:
            result = test_runs.search_test_runs(
                query=f'project = "{config.tm4j_project_key}" AND status = "OPEN"',
                convert_to_markdown=True,
            )
            return result.get("markdown", str(result))
        except Exception as e:
            return f"Ошибка получения открытых тест-прогонов: {e}"

    @mcp.resource(
        "resource://tm4j/test-plans/all",
        description=f"Все тест-планы проекта {config.tm4j_project_key}",
    )
    async def resource_all_test_plans() -> str:
        """Ресурс: все тест-планы проекта."""
        try:
            result = test_plans.search_test_plans(
                query=f'project = "{config.tm4j_project_key}"',
                convert_to_markdown=True,
            )
            return result.get("markdown", str(result))
        except Exception as e:
            return f"Ошибка получения тест-планов: {e}"

    @mcp.resource(
        "resource://tm4j/system/info",
        description="Информация о конфигурации MCP-сервера TM4J",
    )
    async def resource_system_info() -> str:
        """Ресурс: информация о сервере."""
        info = {
            "server": "tm4j-mcp-server",
            "version": "1.0.0",
            "tm4j_host": config.tm4j_host,
            "project_key": config.tm4j_project_key,
            "owner": config.tm4j_owner,
            "auth_type": config.tm4j_auth_type,
            "effective_jira_host": config.effective_jira_host,
        }
        return json.dumps(info, ensure_ascii=False, indent=2)

    @mcp.tool(description="Получить данные текущего авторизованного пользователя через Jira API")
    def get_current_user_info() -> str:
        """Получить полную информацию о текущем пользователе.

        Вызывает /rest/api/2/myself для получения displayName, email, accountID и др.

        Returns:
            JSON с данными пользователя.
        """
        try:
            data = jira_client.get_current_user()
            return json.dumps(data, ensure_ascii=False, indent=2)
        except Exception as e:
            return json.dumps(
                {"error": True, "message": str(e)},
                ensure_ascii=False,
            )

    @mcp.tool(description="Показать содержимое кэша текущего пользователя")
    def get_user_cache() -> str:
        """Показать что хранится в кэше пользователя JiraClient.

        Returns:
            JSON с данными кэша или сообщение о том, что кэш пуст.
        """
        try:
            cache = jira_client._current_user_cache
            if cache is None:
                return json.dumps(
                    {"cached": False, "data": None, "note": "Кэш пуст — запрос к API ещё не выполнялся"},
                    ensure_ascii=False, indent=2,
                )
            return json.dumps(
                {"cached": True, "data": cache},
                ensure_ascii=False, indent=2,
            )
        except Exception as e:
            return json.dumps(
                {"error": True, "message": str(e)},
                ensure_ascii=False,
            )

    # ==================== MCP Prompts ====================

    @mcp.prompt(
        name="get-project-overview",
        description="Получить полный обзор тестирования проекта (окружения, прогоны, кейсы)",
    )
    async def prompt_project_overview(project_key: str | None = None) -> str:
        """Промпт: получить обзор проекта."""
        key = project_key or config.tm4j_project_key
        return (
            f"Получи полный обзор тестирования проекта `{key}`.\n\n"
            f"Вызови инструмент `get_project_test_overview` с параметром `project_key=\"{key}\"` "
            f"и `convert_to_markdown=true`.\n\n"
            f"Проанализируй результаты и отчёт о состоянии тестирования проекта."
        )

    @mcp.prompt(
        name="search-test-cases",
        description="Найти тест-кейсы по заданным критериям",
    )
    async def prompt_search_test_cases(query: str, max_results: str = "50") -> str:
        """Промпт: поиск тест-кейсов."""
        return (
            f"Найди тест-кейсы по фильтру: `{query}`\n\n"
            f"Вызови инструмент `search_test_cases` с параметрами:\n"
            f"- `query=\"{query}\"`\n"
            f"- `max_results={max_results}`\n"
            f"- `convert_to_markdown=true`\n\n"
            f"Представь результаты в удобном виде."
        )

    @mcp.prompt(
        name="get-test-case-details",
        description="Получить полную информацию о тест-кейсе",
    )
    async def prompt_test_case_details(test_case_key: str) -> str:
        """Промпт: детали тест-кейса."""
        return (
            f"Получи полную информацию о тест-кейсе `{test_case_key}`.\n\n"
            f"Вызови инструмент `get_test_case_full_details` с параметрами:\n"
            f"- `test_case_key=\"{test_case_key}\"`\n"
            f"- `convert_to_markdown=true`\n\n"
            f"Представь результаты с шагами, последним результатом и вложениями."
        )

    @mcp.prompt(
        name="get-test-run-details",
        description="Получить полную информацию о тест-прогоне",
    )
    async def prompt_test_run_details(test_run_key: str) -> str:
        """Промпт: детали тест-прогона."""
        return (
            f"Получи полную информацию о тест-прогоне `{test_run_key}`.\n\n"
            f"Вызови инструмент `get_test_run_full_details` с параметрами:\n"
            f"- `test_run_key=\"{test_run_key}\"`\n"
            f"- `convert_to_markdown=true`\n\n"
            f"Представь результаты со статистикой прогона."
        )

    @mcp.prompt(
        name="create-test-run-and-results",
        description="Создать тест-прогон и выполнить массовое тестирование",
    )
    async def prompt_create_test_run(name: str, test_cases_json: str) -> str:
        """Промпт: создать тест-прогон и результаты."""
        return (
            f"Создай тест-прогон `{name}` с тест-кейсами.\n\n"
            f"Шаг 1: Вызови `create_test_run` с параметрами:\n"
            f"- `name=\"{name}\"`\n"
            f"- `items={test_cases_json}`\n\n"
            f"Шаг 2: После получения ключа тест-прогона вызови `bulk_create_test_results` "
            f"для каждого тест-кейса.\n\n"
            f"Шаг 3: Вызови `get_test_run_full_details` для проверки результатов."
        )

    @mcp.prompt(
        name="get-ready-test-cases",
        description="Получить все готовые к выполнению тест-кейсы",
    )
    async def prompt_ready_test_cases() -> str:
        """Промпт: готовые тест-кейсы."""
        key = config.tm4j_project_key
        return (
            f"Получи все готовые к выполнению тест-кейсы проекта `{key}`.\n\n"
            f"Вызови `search_test_cases` с параметром:\n"
            f'- `query="project = \\"{key}\\" AND status = \\"Ready\\""`\n'
            f"- `convert_to_markdown=true`\n\n"
            f"Представь результаты в виде списка с приоритетами."
        )

    @mcp.prompt(
        name="get-test-case-for-issue",
        description="Получить тест-кейсы связанные с Jira задачей",
    )
    async def prompt_test_cases_for_issue(issue_key: str) -> str:
        """Промпт: тест-кейсы для Jira задачи."""
        return (
            f"Получи тест-кейсы связанные с задачей `{issue_key}`.\n\n"
            f"Вызови `get_test_cases_for_issue` с параметрами:\n"
            f"- `issue_key=\"{issue_key}\"`\n"
            f"- `convert_to_markdown=true`\n\n"
            f"Представь результаты с кратким описанием каждого кейса."
        )

    @mcp.prompt(
        name="list-environments",
        description="Получить список окружений проекта",
    )
    async def prompt_list_environments() -> str:
        """Промпт: список окружений."""
        key = config.tm4j_project_key
        return (
            f"Получи список окружений проекта `{key}`.\n\n"
            f"Вызови `get_environments` с параметром:\n"
            f'- `project_key="{key}"`\n'
            f"- `convert_to_markdown=true`"
        )

    return mcp


def main() -> None:
    """Запуск MCP-сервера."""
    app = create_app()
    import sys
    print(json.dumps({"status": "started", "transport": "stdio", "server": "tm4j-mcp"}), file=sys.stderr, flush=True)
    app.run(transport="stdio")


if __name__ == "__main__":
    main()
