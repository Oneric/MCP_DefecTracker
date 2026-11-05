"""MCP-инструменты для работы с результатами тестирования TM4J."""

from __future__ import annotations

from ..tools.base import BaseTool


class TestResultsTool(BaseTool):
    """Инструменты для работы с результатами выполнения тестов."""

    def create_test_result(
        self,
        *,
        test_case_key: str,
        status: str,
        comment: str | None = None,
        environment: str | None = None,
        user_key: str | None = None,
        execution_time: int | None = None,
        script_results: list[dict] | None = None,
        convert_to_markdown: bool = False,
    ) -> dict:
        """
        Создать результат выполнения тест-кейса.

        Args:
            test_case_key: Ключ тест-кейса
            status: Статус (Pass, Fail, Blocked, No Check, Not Completed)
            comment: Комментарий
            environment: Окружение
            user_key: ID пользователя (account_id, email, issue key или None)
            execution_time: Время выполнения (сек)
            script_results: Результаты шагов [{index, status, comment}]
            convert_to_markdown: Вернуть результат в Markdown
        """
        resolved_user = self.resolve_owner(user_key)
        body: dict = {
            "projectKey": self.config.tm4j_project_key,
            "testCaseKey": test_case_key,
            "status": status,
            "userKey": resolved_user,
        }
        if comment:
            body["comment"] = comment
        if environment:
            body["environment"] = environment
        if execution_time is not None:
            body["executionTime"] = execution_time
        if script_results:
            body["scriptResults"] = script_results

        return self._execute_with_steps(
            "create_test_result",
            self.client.create_test_result,
            body,
            convert_to_markdown=convert_to_markdown,
            entity_type="test_result",
        )

    def create_test_result_for_run(
        self,
        *,
        test_run_key: str,
        test_case_key: str,
        status: str,
        environment: str,
        comment: str | None = None,
        user_key: str | None = None,
        execution_time: int | None = None,
        script_results: list[dict] | None = None,
        convert_to_markdown: bool = False,
    ) -> dict:
        """
        Создать результат для тест-кейса в рамках тест-прогона.

        Args:
            test_run_key: Ключ тест-прогона
            test_case_key: Ключ тест-кейса
            status: Статус
            environment: Окружение (обязательный)
            comment: Комментарий
            user_key: ID пользователя
            execution_time: Время выполнения
            script_results: Результаты шагов
            convert_to_markdown: Вернуть результат в Markdown
        """
        resolved_user = self.resolve_owner(user_key)
        body: dict = {"status": status}
        if comment:
            body["comment"] = comment
        if execution_time is not None:
            body["executionTime"] = execution_time
        if script_results:
            body["scriptResults"] = script_results

        return self._execute_with_steps(
            "create_test_result_for_run",
            self.client.create_test_result_for_run,
            test_run_key,
            test_case_key,
            body,
            environment=environment,
            user_key=resolved_user,
            convert_to_markdown=convert_to_markdown,
            entity_type="test_result",
        )

    def update_test_result_for_run(
        self,
        *,
        test_run_key: str,
        test_case_key: str,
        status: str,
        environment: str,
        comment: str | None = None,
        user_key: str | None = None,
        execution_time: int | None = None,
        script_results: list[dict] | None = None,
        convert_to_markdown: bool = False,
    ) -> dict:
        """
        Обновить результат тест-кейса в тест-прогоне.

        Args:
            test_run_key: Ключ тест-прогона
            test_case_key: Ключ тест-кейса
            status: Статус
            environment: Окружение
            comment: Комментарий
            user_key: ID пользователя
            execution_time: Время выполнения
            script_results: Результаты шагов
            convert_to_markdown: Вернуть результат в Markdown
        """
        resolved_user = self.resolve_owner(user_key)
        body: dict = {"status": status}
        if comment:
            body["comment"] = comment
        if execution_time is not None:
            body["executionTime"] = execution_time
        if script_results:
            body["scriptResults"] = script_results

        return self._execute_with_steps(
            "update_test_result_for_run",
            self.client.update_test_result_for_run,
            test_run_key,
            test_case_key,
            body,
            environment=environment,
            user_key=resolved_user,
            convert_to_markdown=convert_to_markdown,
            entity_type="test_result",
        )

    def bulk_create_test_results(
        self,
        *,
        test_run_key: str,
        results: list[dict],
        environment: str,
        user_key: str | None = None,
        convert_to_markdown: bool = False,
    ) -> dict:
        """
        Массовое создание результатов тестирования.

        Args:
            test_run_key: Ключ тест-прогона
            results: Список результатов [{testCaseKey, status, comment, ...}]
            environment: Окружение
            user_key: ID пользователя
            convert_to_markdown: Вернуть результат в Markdown
        """
        resolved_user = self.resolve_owner(user_key)
        return self._execute_with_steps(
            "bulk_create_test_results",
            self.client.bulk_create_test_results,
            test_run_key,
            results,
            environment=environment,
            user_key=resolved_user,
            convert_to_markdown=convert_to_markdown,
            entity_type="test_result",
        )

    def get_test_results(
        self,
        test_run_key: str,
        *,
        convert_to_markdown: bool = False,
    ) -> dict:
        """
        Получить все результаты тест-прогона.

        Args:
            test_run_key: Ключ тест-прогона
            convert_to_markdown: Вернуть результат в Markdown
        """
        return self._execute_with_steps(
            "get_test_results",
            self.client.get_test_results,
            test_run_key,
            convert_to_markdown=convert_to_markdown,
            entity_type="test_result",
        )
