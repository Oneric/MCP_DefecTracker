"""MCP-инструменты для работы с тест-кейсами TM4J."""

from __future__ import annotations

from ..tools.base import BaseTool


class TestCasesTool(BaseTool):
    """Инструменты для CRUD операций над тест-кейсами."""

    def create_test_case(
        self,
        *,
        name: str,
        status: str = "Draft",
        priority: str = "Medium",
        objective: str | None = None,
        precondition: str | None = None,
        owner: str | None = None,
        folder: str | None = None,
        component: str | None = None,
        labels: list[str] | None = None,
        test_script_type: str = "STEP",
        steps: list[dict] | None = None,
        convert_to_markdown: bool = False,
    ) -> dict:
        """
        Создать новый тест-кейс в проекте.

        Args:
            name: Название тест-кейса
            status: Статус (Draft, Ready, Cancelled)
            priority: Приоритет (Critical, High, Medium, Low, Trivial)
            objective: Цель тестирования
            precondition: Предварительные условия
            owner: Владелец (account_id, email, issue key или None для системного)
            folder: Папка
            component: Компонент
            labels: Метки
            test_script_type: Тип скрипта (STEP, TEXT, EMPTY)
            steps: Шаги тестирования [{index, description, testData, expectedResult}]
            convert_to_markdown: Вернуть результат в Markdown
        """
        resolved_owner = self.resolve_owner(owner)
        body: dict = {
            "projectKey": self.config.tm4j_project_key,
            "name": name,
            "status": status,
            "priority": priority,
            "testScript": {"type": test_script_type, "steps": steps or []},
            "owner": resolved_owner,
        }
        if objective:
            body["objective"] = objective
        if precondition:
            body["precondition"] = precondition
        if folder:
            body["folder"] = folder
        if component:
            body["component"] = component
        if labels:
            body["labels"] = labels

        return self._execute_with_steps(
            "create_test_case",
            self.client.create_test_case,
            body,
            convert_to_markdown=convert_to_markdown,
            entity_type="test_case",
        )

    def get_test_case(
        self,
        test_case_key: str,
        *,
        fields: str | None = None,
        convert_to_markdown: bool = False,
    ) -> dict:
        """
        Получить тест-кейс по ключу.

        Args:
            test_case_key: Ключ тест-кейса (напр. PROJ-123)
            fields: Комма-разделённый список полей
            convert_to_markdown: Вернуть результат в Markdown
        """
        return self._execute_with_steps(
            "get_test_case",
            self.client.get_test_case,
            test_case_key,
            fields=fields,
            convert_to_markdown=convert_to_markdown,
            entity_type="test_case",
        )

    def update_test_case(
        self,
        test_case_key: str,
        *,
        name: str | None = None,
        status: str | None = None,
        priority: str | None = None,
        objective: str | None = None,
        precondition: str | None = None,
        owner: str | None = None,
        folder: str | None = None,
        component: str | None = None,
        labels: list[str] | None = None,
        steps: list[dict] | None = None,
        convert_to_markdown: bool = False,
    ) -> dict:
        """
        Обновить тест-кейс.

        Args:
            test_case_key: Ключ тест-кейса
            name: Новое название
            status: Новый статус
            priority: Новый приоритет
            objective: Цель
            precondition: Предварительные условия
            owner: Владелец
            folder: Папка
            component: Компонент
            labels: Метки
            steps: Шаги
            convert_to_markdown: Вернуть результат в Markdown
        """
        resolved_owner = self.resolve_owner(owner)
        body: dict = {"projectKey": self.config.tm4j_project_key}
        if name is not None:
            body["name"] = name
        if status is not None:
            body["status"] = status
        if priority is not None:
            body["priority"] = priority
        if objective is not None:
            body["objective"] = objective
        if precondition is not None:
            body["precondition"] = precondition
        if resolved_owner:
            body["owner"] = resolved_owner
        if folder is not None:
            body["folder"] = folder
        if component is not None:
            body["component"] = component
        if labels is not None:
            body["labels"] = labels
        if steps is not None:
            body["testScript"] = {"steps": steps}

        return self._execute_with_steps(
            "update_test_case",
            self.client.update_test_case,
            test_case_key,
            body,
            convert_to_markdown=convert_to_markdown,
            entity_type="test_case",
        )

    def delete_test_case(
        self, test_case_key: str
    ) -> dict:
        """
        Удалить тест-кейс.

        Args:
            test_case_key: Ключ тест-кейса
        """
        return self._execute_with_steps(
            "delete_test_case",
            self.client.delete_test_case,
            test_case_key,
        )

    def search_test_cases(
        self,
        *,
        query: str = "",
        fields: str | None = None,
        start_at: int = 0,
        max_results: int = 50,
        convert_to_markdown: bool = False,
    ) -> dict:
        """
        Поиск тест-кейсов.

        Args:
            query: Строка поиска
            fields: Комма-разделённый список полей
            start_at: Смещение для пагинации
            max_results: Максимум результатов
            convert_to_markdown: Вернуть результат в Markdown
        """
        return self._execute_with_steps(
            "search_test_cases",
            self.client.search_test_cases,
            query=query,
            fields=fields,
            start_at=start_at,
            max_results=max_results,
            convert_to_markdown=convert_to_markdown,
            entity_type="test_case",
        )

    def get_test_case_attachments(
        self, test_case_key: str
    ) -> dict:
        """
        Получить вложения тест-кейса.

        Args:
            test_case_key: Ключ тест-кейса
        """
        return self._execute_with_steps(
            "get_test_case_attachments",
            self.client.get_test_case_attachments,
            test_case_key,
        )

    def get_latest_test_result(
        self, test_case_key: str, *, convert_to_markdown: bool = False
    ) -> dict:
        """
        Получить последний результат выполнения тест-кейса.

        Args:
            test_case_key: Ключ тест-кейса
            convert_to_markdown: Вернуть результат в Markdown
        """
        return self._execute_with_steps(
            "get_latest_test_result",
            self.client.get_latest_test_result,
            test_case_key,
            convert_to_markdown=convert_to_markdown,
            entity_type="test_result",
        )

    def get_test_cases_for_issue(
        self,
        issue_key: str,
        *,
        fields: str | None = None,
        convert_to_markdown: bool = False,
    ) -> dict:
        """
        Получить тест-кейсы связанные с Jira задачей.

        Args:
            issue_key: Ключ Jira задачи (напр. PROJ-456)
            fields: Комма-разделённый список полей
            convert_to_markdown: Вернуть результат в Markdown
        """
        return self._execute_with_steps(
            "get_test_cases_for_issue",
            self.client.get_test_cases_for_issue,
            issue_key,
            fields=fields,
            convert_to_markdown=convert_to_markdown,
            entity_type="test_case",
        )
