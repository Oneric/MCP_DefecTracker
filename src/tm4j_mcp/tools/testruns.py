"""MCP-инструменты для работы с тест-прогонами TM4J."""

from __future__ import annotations

from ..tools.base import BaseTool


class TestRunsTool(BaseTool):
    """Инструменты для CRUD операций над тест-прогонами."""

    def create_test_run(
        self,
        *,
        name: str,
        folder: str | None = None,
        iteration: str | None = None,
        version: str | None = None,
        owner: str | None = None,
        items: list[dict] | None = None,
        body: dict | None = None,
        convert_to_markdown: bool = False,
    ) -> dict:
        """
        Создать новый тест-прогон.

        Args:
            name: Название тест-прогона
            folder: Папка
            iteration: Итерация
            version: Версия
            owner: Владелец
            items: Список тест-кейсов [{testCaseKey, environment, userKey}]
            body: Полный JSON-body для гибкого контроля
            convert_to_markdown: Вернуть результат в Markdown
        """
        resolved_owner = self.resolve_owner(owner)
        final_body = body or {
            "projectKey": self.config.tm4j_project_key,
            "name": name,
        }
        if folder:
            final_body["folder"] = folder
        if iteration:
            final_body["iteration"] = iteration
        if version:
            final_body["version"] = version
        if resolved_owner:
            final_body["owner"] = resolved_owner
        if items:
            final_body["items"] = items

        return self._execute_with_steps(
            "create_test_run",
            self.client.create_test_run,
            final_body,
            convert_to_markdown=convert_to_markdown,
            entity_type="test_run",
        )

    def get_test_run(
        self,
        test_run_key: str,
        *,
        fields: str | None = None,
        convert_to_markdown: bool = False,
    ) -> dict:
        """
        Получить тест-прогон по ключу.

        Args:
            test_run_key: Ключ тест-прогона
            fields: Комма-разделённый список полей
            convert_to_markdown: Вернуть результат в Markdown
        """
        return self._execute_with_steps(
            "get_test_run",
            self.client.get_test_run,
            test_run_key,
            fields=fields,
            convert_to_markdown=convert_to_markdown,
            entity_type="test_run",
        )

    def delete_test_run(
        self, test_run_key: str
    ) -> dict:
        """
        Удалить тест-прогон.

        Args:
            test_run_key: Ключ тест-прогона
        """
        return self._execute_with_steps(
            "delete_test_run",
            self.client.delete_test_run,
            test_run_key,
        )

    def search_test_runs(
        self,
        *,
        query: str = "",
        fields: str | None = None,
        start_at: int = 0,
        max_results: int = 50,
        convert_to_markdown: bool = False,
    ) -> dict:
        """
        Поиск тест-прогонов.

        Args:
            query: Строка поиска
            fields: Комма-разделённый список полей
            start_at: Смещение для пагинации
            max_results: Максимум результатов
            convert_to_markdown: Вернуть результат в Markdown
        """
        return self._execute_with_steps(
            "search_test_runs",
            self.client.search_test_runs,
            query=query,
            fields=fields,
            start_at=start_at,
            max_results=max_results,
            convert_to_markdown=convert_to_markdown,
            entity_type="test_run",
        )
