"""Базовый класс MCP-инструмента с логированием шагов."""

from __future__ import annotations

import logging
from typing import Any

from ..client.jira_client import JiraClient
from ..client.tm4j_client import TM4JClient
from ..config import AppConfig
from ..converters.markdown import MarkdownConverter
from ..utils.step_tracker import StepStatus, StepTracker

logger = logging.getLogger(__name__)


class BaseTool:
    """Базовый класс для всех MCP-инструментов."""

    def __init__(
        self,
        client: TM4JClient,
        jira_client: JiraClient,
        config: AppConfig,
    ) -> None:
        self.client = client
        self.jira_client = jira_client
        self.config = config
        self.converter = MarkdownConverter()
        self.step_tracker = StepTracker()

    def response_wrapper(
        self,
        data: Any,
        *,
        convert_to_markdown: bool = False,
        entity_type: str = "",
        operation_id: str | None = None,
    ) -> dict:
        """Упаковывает ответ с step_status и опциональным Markdown."""
        result: dict[str, Any] = {"data": data}

        if convert_to_markdown:
            result["markdown"] = self.converter.convert(
                data, entity_type=entity_type
            )

        if operation_id:
            op = self.step_tracker.get_operation_status(operation_id)
            if op:
                result["step_status"] = op.to_dict()

        return result

    def resolve_owner(self, owner_hint: str | None = None) -> str:
        """
        Разрешает владельца:
        1. owner_hint -> Jira lookup
        2. config.TM4J_OWNER как fallback
        """
        if not owner_hint:
            return self.config.tm4j_owner
        try:
            return self.jira_client.resolve_owner(owner_hint)
        except Exception as e:
            logger.warning(
                "Failed to resolve owner '%s': %s. Using default.",
                owner_hint,
                e,
            )
            return self.config.tm4j_owner

    def _execute_with_steps(
        self,
        tool_name: str,
        func,
        *args,
        convert_to_markdown: bool = False,
        entity_type: str = "",
        **kwargs,
    ) -> dict:
        """
        Универсальный шаблон выполнения инструмента с трекингом шагов.
        """
        op_id = self.step_tracker.start_operation(tool_name)
        try:
            self.step_tracker.add_step(op_id, "Выполнение запроса")
            result = func(*args, **kwargs)
            self.step_tracker.update_step(
                op_id, 1, StepStatus.COMPLETED, result_summary="Запрос выполнен"
            )

            if convert_to_markdown:
                self.step_tracker.add_step(op_id, "Конвертация в Markdown")
                self.step_tracker.update_step(
                    op_id, 2, StepStatus.COMPLETED
                )

            self.step_tracker.complete_operation(op_id)
            return self.response_wrapper(
                result,
                convert_to_markdown=convert_to_markdown,
                entity_type=entity_type,
                operation_id=op_id,
            )
        except Exception as e:
            self.step_tracker.update_step(
                op_id, 1, StepStatus.FAILED, error=str(e)
            )
            self.step_tracker.complete_operation(op_id)
            raise
