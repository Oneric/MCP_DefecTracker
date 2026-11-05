"""MCP-инструменты для работы с окружениями TM4J."""

from __future__ import annotations

from ..tools.base import BaseTool


class EnvironmentsTool(BaseTool):
    """Инструменты для операций над окружениями."""

    def get_environments(
        self,
        *,
        project_key: str | None = None,
        convert_to_markdown: bool = False,
    ) -> dict:
        """
        Получить окружения проекта.

        Args:
            project_key: Ключ проекта (по умолчанию из config)
            convert_to_markdown: Вернуть результат в Markdown
        """
        pk = project_key or self.config.tm4j_project_key
        return self._execute_with_steps(
            "get_environments",
            self.client.get_environments,
            pk,
            convert_to_markdown=convert_to_markdown,
            entity_type="environment",
        )

    def create_environment(
        self,
        *,
        name: str,
        description: str | None = None,
        convert_to_markdown: bool = False,
    ) -> dict:
        """
        Создать новое окружение.

        Args:
            name: Название окружения
            description: Описание
            convert_to_markdown: Вернуть результат в Markdown
        """
        body: dict = {
            "projectKey": self.config.tm4j_project_key,
            "name": name,
        }
        if description:
            body["description"] = description
        return self._execute_with_steps(
            "create_environment",
            self.client.create_environment,
            body,
            convert_to_markdown=convert_to_markdown,
            entity_type="environment",
        )
