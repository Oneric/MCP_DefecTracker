"""MCP-инструменты для работы с вложениями TM4J."""

from __future__ import annotations

from ..tools.base import BaseTool


class AttachmentsTool(BaseTool):
    """Инструменты для операций над вложениями."""

    def delete_attachment(
        self, attachment_id: str
    ) -> dict:
        """
        Удалить вложение по ID.

        Args:
            attachment_id: ID вложения
        """
        return self._execute_with_steps(
            "delete_attachment",
            self.client.delete_attachment,
            attachment_id,
        )
