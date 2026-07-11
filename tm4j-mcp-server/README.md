# TM4J MCP Server

MCP сервер для интеграции с Jira Server, TM4J (Zephyr Test Management) и Confluence.

## Возможности

- **TM4J API**: Работа с тестовыми циклами, тест-кейсами, результатами тестирования
- **Jira Server API**: Управление проектами, пользователями, кастомными полями
- **Confluence API**: Работа с документацией
- **SQLite Storage**: Хранение сессий тестирования
- **Scheduler**: Автоматический запуск тестирования
- **Playwright Integration**: Выполнение тестов через Docker

## Структура проекта

```
tm4j-mcp-server/
├── tm4j_mcp_server/           # Пакет Python
│   ├── __init__.py
│   ├── config.py              # Конфигурация
│   ├── main.py                # Основной сервер MCP
│   ├── scheduler.py           # Scheduler для автоматического запуска
│   ├── clients/
│   │   ├── __init__.py
│   │   ├── jira/
│   │   │   ├── client.py      # Jira API client
│   │   │   ├── models.py      # Модели Jira
│   │   │   └── __init__.py
│   │   ├── tm4j/
│   │   │   ├── client.py      # TM4J API client
│   │   │   ├── models.py      # Модели TM4J
│   │   │   └── __init__.py
│   │   └── confluence/
│   │       ├── client.py      # Confluence API client
│   │       ├── models.py      # Модели Confluence
│   │       └── __init__.py
│   ├── storage/
│   │   ├── __init__.py
│   │   └── storage.py         # SQLite storage
│   └── playwright/
│       ├── __init__.py
│       └── playwright_client.py # Playwright integration
├── pyproject.toml             # PyPI configuration
├── requirements.txt           # Python dependencies
├── config.example.yaml        # Пример конфигурации
├── config.yaml                # Конфигурация (создать из примера)
├── .env                       # Переменные окружения (создать из .env.example)
├── .env.example               # Пример переменных окружения
├── .dockerignore              # Docker ignore rules
├── Dockerfile                 # Docker image для сервера
├── Dockerfile.playwright      # Docker image для Playwright
├── data/                      # Папка для данных
│   └── storage.db             # SQLite база данных
├── logs/                      # Папка для логов
└── docs/                      # Документация
    └── tm4j_api.json          # API референс TM4J
```

## Установка

### 1. Установка зависимостей

```bash
cd tm4j-mcp-server
pip install -e .
```

### 2. Конфигурация

Создайте файл `config.yaml` на основе `config.example.yaml`:

```bash
cp config.example.yaml config.yaml
```

Создайте файл `.env` на основе `.env.example`:

```bash
cp .env.example .env
```

### 3. Docker (для Playwright)

```bash
docker build -f Dockerfile.playwright -t tm4j-playwright .
```

### 4. Перемещение базы данных

База данных перемещена в папку `data/`. При запуске сервис будет использовать путь из конфигурации:

```bash
# Если база данных уже перемещена, ничего делать не нужно
# Если нужно переместить вручную:
mv storage.db data/
```

## Использование

### Запуск сервера

```bash
python -m tm4j_mcp_server.main
```

### Запуск через Docker

```bash
docker run -p 8080:8080 tm4j-mcp-server
```

### Запуск с кастомным путём к базе данных

```bash
docker run -p 8080:8080 -v /путь/к/бд:/app/data/storage.db tm4j-mcp-server
```

### MCP Tools

Доступные инструменты:

- `jira_get_projects` — Получить проекты Jira
- `jira_get_custom_fields` — Получить кастомные поля проекта
- `jira_get_test_cycle` — Получить данные тестового цикла из Jira
- `jira_get_test_case` — Получить тест-кейс из Jira
- `jira_update_test_cycle_status` — Обновить статус тестового цикла
- `jira_update_custom_field` — Обновить кастомное поле
- `tm4j_get_testrun` — Получить данные TestCycle из TM4J
- `tm4j_get_testcase` — Получить тест-кейс из TM4J
- `tm4j_get_testresults` — Получить результаты тестирования
- `tm4j_set_testresult` — Записать результат тест-кейса
- `tm4j_get_testcase_by_name` — Найти тест-кейс по названию
- `confluence_get_page` — Получить страницу из Confluence
- `confluence_search_pages` — Поиск страниц в Confluence
- `storage_get_sessions` — Получить сессии тестирования
- `storage_get_tasks` — Получить задачи тестирования
- `storage_create_session` — Создать сессию тестирования
- `storage_create_task` — Создать задачу тестирования
- `storage_update_task_status` — Обновить статус задачи
- `storage_delete_session` — Удалить сессию и все связанные задачи
- `playwright_run_test` — Выполнить тест через Playwright
- `playwright_screenshot` — Сделать скриншот текущей вкладки
- `playwright_navigate` — Перейти по URL
- `playwright_click` — Нажать на элемент
- `playwright_type` — Ввести текст в поле
- `scheduler_run_automated_cycles` — Запустить автоматическое тестирование для всех доступных циклов
- `scheduler_get_pending_cycles` — Получить список тестовых циклов, готовых к автоматическому запуску
- `scheduler_get_running_sessions` — Получить список активных сессий
- `scheduler_recover_failed_sessions` — Восстановить упавшие сессии

## Конфигурация

### Jira Server

```yaml
jira:
  url: "https://jira.example.com"
  username: "admin"
  password: "your-api-token"
```

### TM4J

```yaml
tm4j:
  url: "https://tm4j.example.com"
  username: "admin"
  password: "your-api-token"
```

### Confluence

```yaml
confluence:
  url: "https://confluence.example.com"
  username: "admin"
  password: "your-api-token"
```

### Scheduler

```yaml
scheduler:
  check_interval: 300  # 5 минут
  max_concurrent_sessions: 2
```

### Storage

```yaml
storage:
  db_path: "./data/storage.db"  # Путь к базе данных
```

### Переменные окружения для Storage

```bash
STORAGE_DB_PATH=./data/storage.db
```

### Playwright

```yaml
playwright:
  docker_image: "playwright:latest"
  browser: "chromium"
```

## Алгоритм работы

### Автоматический запуск

1. Scheduler проверяет TestCycles каждые N минут
2. Для циклов со статусом `In Progress` и `Automated=true`:
   - Создать сессию в SQLite
   - Получить тест-кейсы
   - Разбить на задачи (max 8000 символов контекста)
   - Запустить через Playwright
   - Записать результаты в TM4J
3. После первого круга → повторить упавшие кейсы
4. После второго круга → установить статус `Завершен`

## Лицензия

MIT