"""MCP-инструменты для работы с тест-планами TM4J."""

from __future__ import annotations

from ..tools.base import BaseTool


class TestPlansTool(BaseTool):
    """Инструменты для CRUD операций над тест-планами."""

    def create_test_plan(
        self,
        *,
        name: str,
        body: dict | None = None,
        convert_to_markdown: bool = False,
    ) -> dict:
        """
        Создать новый тест-план.

        Args:
            name: Название тест-плана
            body: Дополнительные данные в формате JSON
            convert_to_markdown: Вернуть результат в Markdown
        """
        final_body = body or {"name": name, "projectKey": self.config.tm4j_project_key}
        return self._execute_with_steps(
            "create_test_plan",
            self.client.create_test_plan,
            final_body,
            convert_to_markdown=convert_to_markdown,
            entity_type="test_plan",
        )

    def get_test_plan(
        self,
        test_plan_key: str,
        *,
        fields: str | None = None,
        convert_to_markdown: bool = False,
    ) -> dict:
        """
        Получить тест-план по ключу.

        Args:
            test_plan_key: Ключ тест-плана
            fields: Комма-разделённый список полей
            convert_to_markdown: Вернуть результат в Markdown
        """
        return self._execute_with_steps(
            "get_test_plan",
            self.client.get_test_plan,
            test_plan_key,
            fields=fields,
            convert_to_markdown=convert_to_markdown,
            entity_type="test_plan",
        )

    def update_test_plan(
        self,
        test_plan_key: str,
        *,
        body: dict,
        convert_to_markdown: bool = False,
    ) -> dict:
        """
        Обновить тест-план.

        Args:
            test_plan_key: Ключ тест-плана
            body: Данные для обновления
            convert_to_markdown: Вернуть результат в Markdown
        """
        return self._execute_with_steps(
            "update_test_plan",
            self.client.update_test_plan,
            test_plan_key,
            body,
            convert_to_markdown=convert_to_markdown,
            entity_type="test_plan",
        )

    def delete_test_plan(
        self, test_plan_key: str
    ) -> dict:
        """
        Удалить тест-план.

        Args:
            test_plan_key: Ключ тест-плана
        """
        return self._execute_with_steps(
            "delete_test_plan",
            self.client.delete_test_plan,
            test_plan_key,
        )

    def search_test_plans(
        self,
        *,
        query: str = "",
        fields: str | None = None,
        start_at: int = 0,
        max_results: int = 50,
        convert_to_markdown: bool = False,
    ) -> dict:
        """
        Поиск тест-планов.

        Args:
            query: Строка поиска
            fields: Комма-разделённый список полей
            start_at: Смещение для пагинации
            max_results: Максимум результатов
            convert_to_markdown: Вернуть результат в Markdown
        """
        return self._execute_with_steps(
            "search_test_plans",
            self.client.search_test_plans,
            query=query,
            fields=fields,
            start_at=start_at,
            max_results=max_results,
            convert_to_markdown=convert_to_markdown,
            entity_type="test_plan",
        )
