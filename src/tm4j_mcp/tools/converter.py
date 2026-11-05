"""MCP-инструмент вызова Markdown-конвертера."""

from __future__ import annotations

from ..tools.base import BaseTool
from ..utils.step_tracker import StepStatus


class ConverterTool(BaseTool):
    """Инструмент для конвертации JSON-ответов в Markdown."""

    def convert_response_to_markdown(
        self,
        *,
        data: dict | list[dict],
        entity_type: str = "data",
    ) -> dict:
        """
        Конвертировать JSON-данные в Markdown.

        Args:
            data: Данные для конвертации (dict или list[dict])
            entity_type: Тип сущности (test_case, test_run, test_result, test_plan,
                         environment, folder, project, custom_field)
        """
        op_id = self.step_tracker.start_operation("convert_response_to_markdown")
        try:
            markdown = self.converter.convert(
                data,
                entity_type=entity_type,
            )
            self.step_tracker.add_step(op_id, "Конвертация в Markdown")
            self.step_tracker.update_step(
                op_id, 1, StepStatus.COMPLETED, result_summary="Конвертация завершена"
            )
            self.step_tracker.complete_operation(op_id)
            return {
                "markdown": markdown,
                "entity_type": entity_type,
            }
        except Exception:
            self.step_tracker.complete_operation(op_id)
            raise
