"""Тесты для Markdown-конвертера."""

from __future__ import annotations

from src.tm4j_mcp.converters.markdown import MarkdownConverter


def test_convert_none():
    """Тест конвертации None."""
    converter = MarkdownConverter()
    result = converter.convert(None)
    assert "Нет данных" in result


def test_convert_empty_list():
    """Тест конвертации пустого списка."""
    converter = MarkdownConverter()
    result = converter.convert([])
    assert "Пустой" in result


def test_convert_simple_dict():
    """Тест конвертации простого dict."""
    converter = MarkdownConverter()
    data = {"key": "PROJ-123", "name": "Test Case 1", "status": "Pass"}
    result = converter.convert(data, entity_type="test_case")
    assert "PROJ-123" in result
    assert "Test Case" in result


def test_convert_list_of_dicts():
    """Тест конвертации списка dict."""
    converter = MarkdownConverter()
    data = [
        {"key": "PROJ-1", "name": "Case 1", "status": "Pass"},
        {"key": "PROJ-2", "name": "Case 2", "status": "Fail"},
    ]
    result = converter.convert(data, entity_type="test_case")
    # 'name' is in skip_fields, so it is not rendered as a separate field
    # but 'key' appears both as list item header and as entity title
    assert "PROJ-1" in result
    assert "PROJ-2" in result
    assert "Pass" in result
    assert "Fail" in result


def test_convert_with_steps():
    """Тест конвертации с шагами."""
    converter = MarkdownConverter()
    data = {
        "key": "PROJ-123",
        "name": "Login Test",
        "steps": [
            {"index": 1, "description": "Open app", "expectedResult": "App loads"},
            {"index": 2, "description": "Enter credentials", "expectedResult": "Logged in"},
        ],
    }
    result = converter.convert(data, entity_type="test_case")
    assert "Steps" in result.lower() or "Шаги" in result or "1." in result


def test_format_value_bool():
    """Тест форматирования boolean."""
    converter = MarkdownConverter()
    assert converter._format_value(True) == "✅"
    assert converter._format_value(False) == "❌"


def test_format_value_list():
    """Тест форматирования списка."""
    converter = MarkdownConverter()
    result = converter._format_value(["a", "b", "c"])
    assert "a" in result
    assert "b" in result
    assert "c" in result


def test_format_value_long_text():
    """Тест обрезки длинного текста."""
    converter = MarkdownConverter()
    long_text = "x" * 300
    result = converter._format_value(long_text)
    assert len(result) <= 203  # 200 + "..."


def test_friendly_name():
    """Тест преобразования имён полей."""
    converter = MarkdownConverter()
    assert converter._friendly_name("projectKey") == "Project"
    assert converter._friendly_name("testCaseKey") == "Test Case"
    assert converter._friendly_name("executionDate") == "Execution Date"
