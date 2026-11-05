"""MCP-инструменты для работы с проектами TM4J."""

from __future__ import annotations

from ..tools.base import BaseTool


class ProjectsTool(BaseTool):
    """Инструменты для операций над проектами."""

    def create_project(
        self,
        *,
        project_key: str,
        enable: bool = True,
        convert_to_markdown: bool = False,
    ) -> dict:
        """
        Создать/включить проект в TM4J.

        Args:
            project_key: Ключ проекта
            enable: Включить интеграцию
            convert_to_markdown: Вернуть результат в Markdown
        """
        body = {"projectKey": project_key, "enable": enable}
        return self._execute_with_steps(
            "create_project",
            self.client.create_project,
            body,
            convert_to_markdown=convert_to_markdown,
            entity_type="project",
        )
