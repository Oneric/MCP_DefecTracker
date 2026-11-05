"""MCP-инструменты для удаления результатов выполнения TM4J."""

from __future__ import annotations

from ..tools.base import BaseTool


class ExecutionsTool(BaseTool):
    """Инструменты для управления удалением результатов выполнения."""

    def delete_executions(
        self,
        *,
        delete_before: str,
        project_key: str | None = None,
    ) -> dict:
        """
        Запросить удаление результатов выполнения.

        Args:
            delete_before: Удалить результаты созданные до этой даты (ISO 8601)
            project_key: Ключ проекта (по умолчанию из config)
        """
        body: dict = {
            "deleteExecutionsCreatedBefore": delete_before,
        }
        pk = project_key or self.config.tm4j_project_key
        body["projectKey"] = pk
        return self._execute_with_steps(
            "delete_executions",
            self.client.delete_executions,
            body,
        )

    def get_deletion_status(self) -> dict:
        """
        Получить статус выполнения запроса на удаление.
        """
        return self._execute_with_steps(
            "get_deletion_status",
            self.client.get_deletion_status,
        )

    def cancel_deletion(self) -> dict:
        """
        Отменить запрос на удаление результатов.
        """
        return self._execute_with_steps(
            "cancel_deletion",
            self.client.cancel_deletion,
        )
