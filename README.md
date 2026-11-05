# TM4J MCP Server

MCP-сервер (Model Context Protocol) для взаимодействия с **TM4J (Zephyr Scale)** API через stdio-транспорт. Построен на [FastMCP](https://github.com/punkpeye/fastmcp).

## Возможности

- **35+ инструментов MCP** для работы с TM4J API (тест-кейсы, тест-прогоны, тест-планы, окружения, папки, кастомные поля)
- **8 MCP Resources** с предопределёнными запросами данных TM4J
- **8 MCP Prompts** для типичных рабочих процессов
- **Markdown-конвертер** — любой инструмент может возвращать результат в Markdown через флаг `convert_to_markdown=true`
- **Единая авторизация** — одни credentials для TM4J и Jira (Basic / Bearer)
- **Композитные виды** — инструменты, объединяющие несколько API-вызовов (полные детали кейса, обзор проекта)
- **Разрешение владельца** — конвертация issue key / email / query в Jira account_id
- **Отслеживание шагов** — контроль прогресса выполнения операций
- **Минимальное логирование** — скрытый баннер, только ошибки в stdout

## Установка

```bash
# Клонировать репозиторий
git clone <repo-url>
cd MCP_DefecTracker

# Установить зависимости
uv sync

# Настроить переменные окружения
cp .env.example .env
# Отредактировать .env
```

## Конфигурация

Все параметры передаются через переменные окружения (файл `.env`):

```env
# === TM4J / Jira Configuration ===
TM4J_HOST=https://example.atlassian.net
TM4J_API_BASE_PATH=/rest/atmosphere/public/latest
TM4J_AUTH_TYPE=bearer                    # bearer | basic
TM4J_BEARER_TOKEN=your_token_here        # для Bearer auth
# TM4J_BASIC_USER=user@example.com       # для Basic auth
# TM4J_BASIC_PASSWORD=your_api_token_here
TM4J_PROJECT_KEY=PROJ
TM4J_OWNER=5b10a2844f25c16c440aef95

# Jira использует те же credentials.
# JIRA_HOST=https://other-jira.example.com  # если Jira на другом хосте

# === HTTP ===
HTTP_TIMEOUT=30
HTTP_RETRIES=3

# === Logging ===
LOG_LEVEL=ERROR

# === FastMCP ===
FASTMCP_SHOW_SERVER_BANNER=false
```

### Авторизация

| Параметр | Описание |
|----------|----------|
| `TM4J_AUTH_TYPE=bearer` | Использует `TM4J_BEARER_TOKEN` |
| `TM4J_AUTH_TYPE=basic` | Использует `TM4J_BASIC_USER` + `TM4J_BASIC_PASSWORD` |

Jira API использует **те же credentials** — укажите `JIRA_HOST` только при размещении на другом домене.

## Запуск

```bash
# Через uv
uv run python -m src.tm4j_mcp.main

# Вывод в stderr:
# {"status": "started", "transport": "stdio", "server": "tm4j-mcp"}
```

### Интеграция с Claude Desktop

```json
{
  "mcpServers": {
    "tm4j": {
      "command": "uv",
      "args": ["run", "python", "-m", "src.tm4j_mcp.main"],
      "cwd": "/path/to/MCP_DefecTracker",
      "env": {
        "TM4J_HOST": "https://example.atlassian.net",
        "TM4J_AUTH_TYPE": "bearer",
        "TM4J_BEARER_TOKEN": "your_token_here",
        "TM4J_PROJECT_KEY": "PROJ",
        "TM4J_OWNER": "5b10a2844f25c16c440aef95"
      }
    }
  }
}
```

## Инструменты MCP (Tools)

### Тест-кейсы
| Инструмент | Описание |
|-----------|----------|
| `create_test_case` | Создать новый тест-кейс |
| `get_test_case` | Получить тест-кейс по ключу |
| `update_test_case` | Обновить тест-кейс |
| `delete_test_case` | Удалить тест-кейс |
| `search_test_cases` | Поиск по фильтру (TQL) |
| `get_test_case_attachments` | Вложения тест-кейса |
| `get_latest_test_result` | Последний результат выполнения |
| `get_test_cases_for_issue` | Кейсы, связанные с Jira задачей |
| `get_test_case_full_details` | Полные детали (шаги, результаты, вложения) |

### Тест-прогоны
| Инструмент | Описание |
|-----------|----------|
| `create_test_run` | Создать тест-прогон |
| `get_test_run` | Получить тест-прогон по ключу |
| `delete_test_run` | Удалить тест-прогон |
| `search_test_runs` | Поиск тест-прогонов |
| `get_test_run_full_details` | Полные детали (результаты, статистика) |

### Тест-результаты
| Инструмент | Описание |
|-----------|----------|
| `create_test_result` | Создать результат выполнения |
| `create_test_result_for_run` | Результат в рамках прогона |
| `update_test_result_for_run` | Обновить результат в прогоне |
| `bulk_create_test_results` | Массовое создание результатов |
| `get_test_results` | Все результаты прогона |

### Тест-планы
| Инструмент | Описание |
|-----------|----------|
| `create_test_plan` | Создать тест-план |
| `get_test_plan` | Получить тест-план |
| `update_test_plan` | Обновить тест-план |
| `delete_test_plan` | Удалить тест-план |
| `search_test_plans` | Поиск тест-планов |

### Окружения и папки
| Инструмент | Описание |
|-----------|----------|
| `get_environments` | Получить окружения проекта |
| `create_environment` | Создать окружение |
| `create_folder` | Создать папку |
| `update_folder` | Обновить папку |

### Кастомные поля
| Инструмент | Описание |
|-----------|----------|
| `create_custom_field` | Создать кастомное поле |
| `create_custom_field_option` | Добавить опцию в поле select |

### Проекты
| Инструмент | Описание |
|-----------|----------|
| `create_project` | Создать/включить проект в TM4J |

### Автоматизация
| Инструмент | Описание |
|-----------|----------|
| `get_automation_test_cases` | Получить автоматизированные кейсы по TQL |

### Управление результатами
| Инструмент | Описание |
|-----------|----------|
| `delete_executions` | Удалить старые результаты |
| `get_deletion_status` | Статус удаления |
| `cancel_deletion` | Отменить удаление |

### Вложения
| Инструмент | Описание |
|-----------|----------|
| `delete_attachment` | Удалить вложение по ID |

### Композитные
| Инструмент | Описание |
|-----------|----------|
| `get_project_test_overview` | Полный обзор тестирования проекта |
| `search_and_aggregate_results` | Поиск с агрегацией статистики |

### Утилиты
| Инструмент | Описание |
|-----------|----------|
| `resolve_owner` | Разрешить identifier в account_id |
| `convert_response_to_markdown` | Конвертировать JSON в Markdown |

## Ресурсы MCP (Resources)

Предопределённые URI для получения данных:

| Resource URI | Описание |
|-------------|----------|
| `resource://tm4j/project/{key}/overview` | Обзор тестирования проекта |
| `resource://tm4j/project/{key}/environments` | Окружения проекта |
| `resource://tm4j/project/{key}/test-cases/ready` | Готовые тест-кейсы (status=Ready) |
| `resource://tm4j/project/{key}/test-cases/all` | Все тест-кейсы |
| `resource://tm4j/project/{key}/test-runs/open` | Открытые тест-прогоны |
| `resource://tm4j/project/{key}/test-plans/all` | Все тест-планы |
| `resource://tm4j/system/info` | Информация о системе |

## Промпты MCP (Prompts)

| Промпт | Описание |
|-------|----------|
| `project-overview` | Получить обзор тестирования |
| `search-test-cases` | Найти тест-кейсы по критериям |
| `test-case-details` | Детали тест-кейса |
| `test-run-details` | Детали тест-прогона |
| `create-test-run` | Создать тест-прогон с кейсами |
| `ready-test-cases` | Список готовых кейсов |
| `test-cases-for-issue` | Кейсы для Jira задачи |
| `list-environments` | Список окружений |

## Примеры использования

### Получить тест-кейс в Markdown

```
Инструмент: get_test_case
Параметры:
  test_case_key: "PROJ-123"
  convert_to_markdown: true
```

### Создать тест-кейс

```
Инструмент: create_test_case
Параметры:
  name: "Проверить авторизацию"
  priority: "High"
  objective: "Тестирование входа в систему"
  steps: '[{"index":1,"description":"Открыть логин","expected_result":"Форма логина"}]'
```

### Поиск тест-кейсов

```
Инструмент: search_test_cases
Параметры:
  query: 'project = "PROJ" AND status = "Ready"'
  max_results: 20
  convert_to_markdown: true
```

### Получить полный обзор проекта

```
Инструмент: get_project_test_overview
Параметры:
  convert_to_markdown: true
```

## Структура проекта

```
src/tm4j_mcp/
├── main.py                 # Точка входа + регистрация MCP tools/resources/prompts
├── config.py               # Pydantic-конфигурация из переменных окружения
├── client/
│   ├── auth.py             # Unified AuthHandler (Basic + Bearer)
│   ├── tm4j_client.py      # TM4J API клиент
│   └── jira_client.py      # Jira API клиент (resolve_owner)
├── converters/
│   └── markdown.py         # Markdown-конвертер
├── models/
│   ├── tm4j.py             # Pydantic модели TM4J
│   └── jira.py             # Pydantic модели Jira
├── tools/                  # MCP инструменты
│   ├── testcases.py
│   ├── testruns.py
│   ├── testresults.py
│   ├── testplans.py
│   ├── environments.py
│   ├── folders.py
│   ├── projects.py
│   ├── customfields.py
│   ├── automation.py
│   ├── executions.py
│   ├── attachments.py
│   ├── composite.py        # Композитные виды
│   └── converter.py        # Markdown конвертер
└── utils/
    ├── errors.py           # Иерархия ошибок
    └── step_tracker.py     # Отслеживание шагов

tests/                      # Тесты (38 passed)
docs/tm4j_api.json          # Swagger-спецификация TM4J API
plans/architecture.md       # Архитектурная документация
```

## Тестирование

```bash
# Запустить все тесты
uv run pytest tests/ -v

# С покрытием
uv run pytest tests/ -v --cov=src/tm4j_mcp --cov-report=term-missing
```

## Архитектура

Подробное описание архитектуры см. в [`plans/architecture.md`](plans/architecture.md).

## Лицензия

MIT
