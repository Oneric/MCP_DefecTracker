# Форматы вызовов MCP-инструментов

## Паттерн вызова

```json
tool_call: {
  "name": "get_test_case",
  "arguments": {
    "test_case_key": "PROJ-123",
    "fields": "key,name,status,priority,testScript",
    "convert_to_markdown": true
  }
}
```

## Параметр convert_to_markdown

При `true` ответ содержит `markdown` поле с отформатированным выводом.
Рекомендуется использовать для всех read-операций.

## Параметр fields

Комма-разделённый список полей для оптимизации объёма ответа.
Доступные поля зависят от сущности (смотри документацию инструмента).

## JSON-строки для массивов

Сложные параметры (массивы, объекты) передаются как JSON-строки:

```
steps: "[{\"index\": 1, \"description\": \"Открыть приложение\", \"expectedResult\": \"Приложение загружено\"}]"
labels: "[\"regression\", \"smoke\"]"
results: "[{\"testCaseKey\": \"PROJ-1\", \"status\": \"Pass\"}]"
```

## Разрешение владельца

```json
tool_call: {
  "name": "resolve_owner",
  "arguments": { "identifier": "PROJ-456" }
}
```

Возвращает `account_id` для использования в `owner` или `userKey`.

Поддерживаемые форматы identifier:
- `"myself"` / `"self"` — account_id текущего авторизованного пользователя (через /rest/api/2/myself)
- `"PROJ-123"` — берём creator/assignee из Jira задачи
- `"user@example.com"` — lookup по email
- `"5b10a2844f25c16c440aef95"` — напрямую account_id
- `"USER"` — lookup по key

## Составные вью

Для получения агрегированных данных используй:

| Инструмент | Описание |
|---|---|
| `get_test_case_full_details` | TC + шаги + последний результат + вложения |
| `get_test_run_full_details` | Прогон + результаты + статистика |
| `get_project_test_overview` | Окружения + прогоны + кейсы |
| `search_and_aggregate_results` | Поиск + агрегация результатов + статистика |

## Статусы тестирования

Типовые статусы: `Pass`, `Fail`, `Blocked`, `No Check`, `Not Completed`

Типовые приоритеты: `Critical`, `High`, `Medium`, `Low`, `Trivial`

Типовые статусы тест-кейса: `Draft`, `Ready`, `Cancelled`
