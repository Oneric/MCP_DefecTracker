"""MCP-инструменты для работы с папками TM4J."""

from __future__ import annotations

from ..tools.base import BaseTool


class FoldersTool(BaseTool):
    """Инструменты для операций над папками."""

    def create_folder(
        self,
        *,
        name: str,
        folder_type: str = "TEST",
        convert_to_markdown: bool = False,
    ) -> dict:
        """
        Создать новую папку в проекте.

        Args:
            name: Название папки
            folder_type: Тип (TEST, TEST_CYCLE, TEST_PLAN, TEST_RESULT)
            convert_to_markdown: Вернуть результат в Markdown
        """
        body = {
            "projectKey": self.config.tm4j_project_key,
            "name": name,
            "type": folder_type,
        }
        return self._execute_with_steps(
            "create_folder",
            self.client.create_folder,
            body,
            convert_to_markdown=convert_to_markdown,
            entity_type="folder",
        )

    def update_folder(
        self,
        folder_id: int,
        *,
        name: str | None = None,
        folder_type: str | None = None,
        convert_to_markdown: bool = False,
    ) -> dict:
        """
        Обновить папку.

        Args:
            folder_id: ID папки
            name: Новое название
            folder_type: Новый тип
            convert_to_markdown: Вернуть результат в Markdown
        """
        body: dict = {"projectKey": self.config.tm4j_project_key}
        if name:
            body["name"] = name
        if folder_type:
            body["type"] = folder_type
        return self._execute_with_steps(
            "update_folder",
            self.client.update_folder,
            folder_id,
            body,
            convert_to_markdown=convert_to_markdown,
            entity_type="folder",
        )
