"""MCP-инструменты для автоматизации TM4J."""

from __future__ import annotations

from ..tools.base import BaseTool


class AutomationTool(BaseTool):
    """Инструменты для импорта результатов автоматизации."""

    def get_automation_test_cases(
        self,
        *,
        tql: str,
        convert_to_markdown: bool = False,
    ) -> dict:
        """
        Получить тест-кейсы по TQL-запросу.

        Args:
            tql: JQL/TQL запрос (напр. "project = PROJ AND issuetype = Test")
            convert_to_markdown: Вернуть результат в Markdown
        """
        return self._execute_with_steps(
            "get_automation_test_cases",
            self.client.get_automation_test_cases,
            tql,
            convert_to_markdown=convert_to_markdown,
            entity_type="test_case",
        )
