"""Автономный модуль Markdown-конвертера для TM4J-сущностей."""

from __future__ import annotations

from typing import Any


class MarkdownConverter:
    """Преобразует TM4J-сущности в Markdown."""

    def convert(
        self,
        data: dict | list[dict] | None,
        *,
        entity_type: str = "data",
        indent: int = 0,
    ) -> str:
        if data is None:
            return "*Нет данных*"
        if isinstance(data, list):
            if not data:
                return "*Пустой список*"
            return self._list_to_md(data, entity_type, indent)
        if isinstance(data, dict):
            return self._dict_to_md(data, entity_type, indent)
        return str(data)

    def _list_to_md(
        self, items: list[dict], entity_type: str, indent: int = 0
    ) -> str:
        lines: list[str] = []
        prefix = " " * indent
        for idx, item in enumerate(items, 1):
            key = item.get("key") or item.get("name") or item.get("id", f"#{idx}")
            lines.append(f"{prefix}### {idx}. {key}")
            lines.append(self._dict_to_md(item, entity_type, indent + 4))
        return "\n".join(lines)

    def _dict_to_md(self, data: dict, entity_type: str, indent: int = 0) -> str:
        prefix = " " * indent
        lines: list[str] = []

        # Заголовок
        key = data.get("key") or data.get("name") or data.get("id", "")
        title = self._get_title(entity_type)
        if key:
            lines.append(f"{prefix}**{title}:** `{key}`")
            lines.append("")

        # Основные поля
        skip_fields = {"key", "name", "id", "customFields", "custom_fields"}
        custom_fields: list[dict] = []

        for field_key, value in data.items():
            fk = field_key.lower()
            if fk in skip_fields:
                continue
            # Собираем кастомные поля отдельно
            if fk.startswith("customfield_") or fk == "customfields":
                if isinstance(value, dict) and value:
                    custom_fields.append(
                        {"name": field_key, "value": value}
                    )
                continue

            friendly_name = self._friendly_name(field_key)
            formatted_value = self._format_value(value)
            lines.append(f"{prefix}| {friendly_name} | {formatted_value} |")

        if lines and lines[-1].startswith("|"):
            lines.insert(0, f"{prefix}| Поле | Значение |")
            lines.insert(
                1,
                f"{prefix}|---|---|",
            )
            lines.append("")

        # Кастомные поля
        if custom_fields:
            lines.append(f"{prefix}**Кастомные поля:**")
            lines.append("")
            lines.append(f"{prefix}| Поле | Значение |")
            lines.append(f"{prefix}|---|---|")
            for cf in custom_fields:
                val = self._format_value(cf["value"])
                lines.append(f"{prefix}| {cf['name']} | {val} |")
            lines.append("")

        # Вложенные шаги
        steps = data.get("steps") or data.get("testScript", {}).get("steps")
        if isinstance(steps, list) and steps:
            lines.append(f"{prefix}**Шаги:**")
            lines.append("")
            for step in steps:
                step_idx = step.get("index", "?")
                desc = step.get("description") or step.get("testData") or ""
                expected = step.get("expectedResult", "")
                lines.append(f"{prefix}{step_idx}. **{desc[:80]}**")
                if expected:
                    lines.append(f"{prefix}   Ожидаемый: {expected[:100]}")
            lines.append("")

        return "\n".join(lines)

    def _format_value(self, value: Any) -> str:
        if value is None:
            return "*—" * 1
        if isinstance(value, bool):
            return "✅" if value else "❌"
        if isinstance(value, list):
            items = [str(v) for v in value[:5]]
            suffix = f" (+{len(value) - 5})" if len(value) > 5 else ""
            return f"[{', '.join(items)}]{suffix}"
        if isinstance(value, dict):
            parts = [f"{k}={v}" for k, v in list(value.items())[:3]]
            suffix = "..." if len(value) > 3 else ""
            return f"{{{', '.join(parts)}}}{suffix}"
        text = str(value)
        if len(text) > 200:
            return text[:200] + "..."
        return text

    def _friendly_name(self, field: str) -> str:
        replacements = {
            "projectKey": "Project",
            "testCaseKey": "Test Case",
            "testRunKey": "Test Run",
            "testScript": "Test Script",
            "executionTime": "Execution Time",
            "executionDate": "Execution Date",
            "userKey": "User",
            "plannedStartDate": "Planned Start",
            "plannedEndDate": "Planned End",
            "precondition": "Precondition",
            "estimatedTime": "Est. Time",
            "scriptResults": "Script Results",
        }
        result = replacements.get(field, field)
        return result.replace("_", " ").replace("-", " ").title()

    def _get_title(self, entity_type: str) -> str:
        titles = {
            "test_case": "Test Case",
            "testrun": "Test Run",
            "test_run": "Test Run",
            "test_result": "Test Result",
            "test_plan": "Test Plan",
            "environment": "Environment",
            "folder": "Folder",
            "project": "Project",
            "custom_field": "Custom Field",
        }
        return titles.get(entity_type, "Entity")
