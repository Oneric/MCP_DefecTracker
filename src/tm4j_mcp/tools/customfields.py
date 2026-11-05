"""MCP-инструменты для работы с кастомными полями TM4J."""

from __future__ import annotations

from ..tools.base import BaseTool


class CustomFieldsTool(BaseTool):
    """Инструменты для операций над кастомными полями."""

    def create_custom_field(
        self,
        *,
        name: str,
        field_type: str,
        category: str,
        description: str | None = None,
        required: bool = False,
        convert_to_markdown: bool = False,
    ) -> dict:
        """
        Создать кастомное поле для проекта.

        Args:
            name: Название поля
            field_type: Тип (text, number, date, select, multiSelect, truefalse, user)
            category: Категория
            description: Описание
            required: Обязательно ли поле
            convert_to_markdown: Вернуть результат в Markdown
        """
        body: dict = {
            "projectKey": self.config.tm4j_project_key,
            "name": name,
            "type": field_type,
            "category": category,
            "required": required,
        }
        if description:
            body["description"] = description
        return self._execute_with_steps(
            "create_custom_field",
            self.client.create_custom_field,
            body,
            convert_to_markdown=convert_to_markdown,
            entity_type="custom_field",
        )

    def create_custom_field_option(
        self,
        custom_field_id: str,
        *,
        name: str,
        convert_to_markdown: bool = False,
    ) -> dict:
        """
        Добавить опцию в кастомное поле типа select/multiSelect.

        Args:
            custom_field_id: ID кастомного поля
            name: Название опции
            convert_to_markdown: Вернуть результат в Markdown
        """
        return self._execute_with_steps(
            "create_custom_field_option",
            self.client.create_custom_field_option,
            custom_field_id,
            {"name": name},
            convert_to_markdown=convert_to_markdown,
        )
