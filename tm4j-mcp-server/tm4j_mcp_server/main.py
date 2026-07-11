"""
TM4J MCP Server - Main Entry Point

This module provides the MCP server implementation for integrating with
Jira Server API, TM4J API, and Confluence API.
"""

import asyncio
import logging
import os
from typing import Any, Dict, List, Optional
from contextlib import asynccontextmanager

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import (
    Tool,
    TextContent,
    Prompt,
    PromptMessage,
    Resource,
    ResourceTemplate,
)

from tm4j_mcp_server.clients.jira.client import JiraClient
from tm4j_mcp_server.clients.tm4j.client import TM4JClient
from tm4j_mcp_server.clients.confluence.client import ConfluenceClient
from tm4j_mcp_server.storage.storage import TestStorage as Storage
from tm4j_mcp_server.playwright.playwright_client import PlaywrightClient
from tm4j_mcp_server.config import Config

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def server_lifespan(server: Server):
    """Manage server lifespan (startup and shutdown)."""
    config = Config.get_config()
    
    # Initialize clients
    jira_client = JiraClient(
        base_url=config.jira.url,
        username=config.jira.username,
        api_key=config.jira.password
    )
    
    tm4j_client = TM4JClient(
        base_url=config.tm4j.url,
        username=config.tm4j.username,
        api_key=config.tm4j.password
    )
    
    confluence_client = ConfluenceClient(
        base_url=config.confluence.url,
        username=config.confluence.username,
        api_key=config.confluence.password
    )
    
    storage = Storage(config.storage.db_path)
    playwright_client = PlaywrightClient(config.playwright)
    
    # Import scheduler here to avoid circular imports
    from tm4j_mcp_server.scheduler import TestScheduler
    scheduler = TestScheduler(
        jira_client=jira_client,
        tm4j_client=tm4j_client,
        playwright_client=playwright_client,
        storage=storage,
        check_interval=300,
        max_concurrent_sessions=2
    )
    
    logger.info("Server started successfully")
    
    yield
    
    # Cleanup on shutdown
    logger.info("Server shutting down")


# Create server instance
server = Server("tm4j-mcp-server")


# ==================== TOOLS ====================

@server.list_tools()
async def list_tools() -> List[Tool]:
    """List available tools."""
    return [
        # Jira Tools
        Tool(
            name="jira_get_projects",
            description="Получить список проектов Jira",
            inputSchema={...}
        ),
        Tool(
            name="jira_get_custom_fields",
            description="Получить кастомные поля проекта",
            inputSchema={...}
        ),
        Tool(
            name="jira_get_test_cycle",
            description="Получить данные тестового цикла из Jira",
            inputSchema={...}
        ),
        Tool(
            name="jira_get_test_case",
            description="Получить тест-кейс из Jira",
            inputSchema={...}
        ),
        Tool(
            name="jira_update_test_cycle_status",
            description="Обновить статус тестового цикла",
            inputSchema={...}
        ),
        Tool(
            name="jira_update_custom_field",
            description="Обновить кастомное поле",
            inputSchema={...}
        ),
        
        # TM4J Tools
        Tool(
            name="tm4j_get_testrun",
            description="Получить данные TestCycle из TM4J",
            inputSchema={...}
        ),
        Tool(
            name="tm4j_get_testcase",
            description="Получить тест-кейс из TM4J",
            inputSchema={...}
        ),
        Tool(
            name="tm4j_get_testresults",
            description="Получить результаты тестирования",
            inputSchema={...}
        ),
        Tool(
            name="tm4j_set_testresult",
            description="Записать результат тест-кейса",
            inputSchema={...}
        ),
        Tool(
            name="tm4j_get_testcase_by_name",
            description="Найти тест-кейс по названию",
            inputSchema={...}
        ),
        
        # Confluence Tools
        Tool(
            name="confluence_get_page",
            description="Получить страницу из Confluence",
            inputSchema={...}
        ),
        Tool(
            name="confluence_search_pages",
            description="Поиск страниц в Confluence",
            inputSchema={...}
        ),
        
        # Storage Tools
        Tool(
            name="storage_get_sessions",
            description="Получить сессии тестирования",
            inputSchema={...}
        ),
        Tool(
            name="storage_get_tasks",
            description="Получить задачи тестирования",
            inputSchema={...}
        ),
        Tool(
            name="storage_create_session",
            description="Создать сессию тестирования",
            inputSchema={...}
        ),
        Tool(
            name="storage_create_task",
            description="Создать задачу тестирования",
            inputSchema={...}
        ),
        Tool(
            name="storage_update_task_status",
            description="Обновить статус задачи",
            inputSchema={...}
        ),
        Tool(
            name="storage_delete_session",
            description="Удалить сессию и все связанные задачи",
            inputSchema={...}
        ),
        
        # Playwright Tools
        Tool(
            name="playwright_run_test",
            description="Выполнить тест через Playwright",
            inputSchema={...}
        ),
        Tool(
            name="playwright_screenshot",
            description="Сделать скриншот текущей вкладки",
            inputSchema={...}
        ),
        Tool(
            name="playwright_navigate",
            description="Перейти по URL",
            inputSchema={...}
        ),
        Tool(
            name="playwright_click",
            description="Нажать на элемент",
            inputSchema={...}
        ),
        Tool(
            name="playwright_type",
            description="Ввести текст в поле",
            inputSchema={...}
        ),
        
        # Scheduler Tools
        Tool(
            name="scheduler_run_automated_cycles",
            description="Запустить автоматическое тестирование для всех доступных циклов",
            inputSchema={...}
        ),
        Tool(
            name="scheduler_get_pending_cycles",
            description="Получить список тестовых циклов, готовых к автоматическому запуску",
            inputSchema={...}
        ),
        Tool(
            name="scheduler_get_running_sessions",
            description="Получить список активных сессий",
            inputSchema={...}
        ),
        Tool(
            name="scheduler_recover_failed_sessions",
            description="Восстановить упавшие сессии",
            inputSchema={...}
        ),
    ]


# ==================== PROMPTS ====================

@server.list_prompts()
async def list_prompts() -> List[Prompt]:
    """List available prompts."""
    return []


# ==================== RESOURCES ====================

@server.list_resource_templates()
async def list_resource_templates() -> List[ResourceTemplate]:
    """List available resource templates."""
    return []


# ==================== HANDLERS ====================

@server.call_tool()
async def call_tool(name: str, arguments: Dict[str, Any]) -> List[Any]:
    """Handle tool calls."""
    logger.info(f"Tool called: {name} with arguments: {arguments}")
    
    try:
        if name == "jira_get_projects":
            return await _handle_jira_get_projects(arguments)
        elif name == "jira_get_custom_fields":
            return await _handle_jira_get_custom_fields(arguments)
        elif name == "jira_get_test_cycle":
            return await _handle_jira_get_test_cycle(arguments)
        elif name == "jira_get_test_case":
            return await _handle_jira_get_test_case(arguments)
        elif name == "jira_update_test_cycle_status":
            return await _handle_jira_update_test_cycle_status(arguments)
        elif name == "jira_update_custom_field":
            return await _handle_jira_update_custom_field(arguments)
        
        elif name == "tm4j_get_testrun":
            return await _handle_tm4j_get_testrun(arguments)
        elif name == "tm4j_get_testcase":
            return await _handle_tm4j_get_testcase(arguments)
        elif name == "tm4j_get_testresults":
            return await _handle_tm4j_get_testresults(arguments)
        elif name == "tm4j_set_testresult":
            return await _handle_tm4j_set_testresult(arguments)
        elif name == "tm4j_get_testcase_by_name":
            return await _handle_tm4j_get_testcase_by_name(arguments)
        
        elif name == "confluence_get_page":
            return await _handle_confluence_get_page(arguments)
        elif name == "confluence_search_pages":
            return await _handle_confluence_search_pages(arguments)
        
        elif name == "storage_get_sessions":
            return await _handle_storage_get_sessions(arguments)
        elif name == "storage_get_tasks":
            return await _handle_storage_get_tasks(arguments)
        elif name == "storage_create_session":
            return await _handle_storage_create_session(arguments)
        elif name == "storage_create_task":
            return await _handle_storage_create_task(arguments)
        elif name == "storage_update_task_status":
            return await _handle_storage_update_task_status(arguments)
        elif name == "storage_delete_session":
            return await _handle_storage_delete_session(arguments)
        
        elif name == "playwright_run_test":
            return await _handle_playwright_run_test(arguments)
        elif name == "playwright_screenshot":
            return await _handle_playwright_screenshot(arguments)
        elif name == "playwright_navigate":
            return await _handle_playwright_navigate(arguments)
        elif name == "playwright_click":
            return await _handle_playwright_click(arguments)
        elif name == "playwright_type":
            return await _handle_playwright_type(arguments)
        
        elif name == "scheduler_run_automated_cycles":
            return await _handle_scheduler_run_automated_cycles(arguments)
        elif name == "scheduler_get_pending_cycles":
            return await _handle_scheduler_get_pending_cycles(arguments)
        elif name == "scheduler_get_running_sessions":
            return await _handle_scheduler_get_running_sessions(arguments)
        elif name == "scheduler_recover_failed_sessions":
            return await _handle_scheduler_recover_failed_sessions(arguments)
        
        else:
            return [TextContent(type="text", text="Tool not found")]
            
    except Exception as e:
        logger.error(f"Error calling tool {name}: {e}")
        return [TextContent(type="text", text=f"Error: {str(e)}")]


async def _handle_jira_get_projects(arguments: Dict[str, Any]) -> List[TextContent]:
    """Handle Jira get projects tool."""
    project_key = arguments.get("projectKey")
    
    projects = await jira_client.get_projects(project_key)
    return [TextContent(type="text", text=str(projects))]


async def _handle_jira_get_custom_fields(arguments: Dict[str, Any]) -> List[TextContent]:
    """Handle Jira get custom fields tool."""
    project_key = arguments["projectKey"]
    
    fields = await jira_client.get_custom_fields(project_key)
    return [TextContent(type="text", text=str(fields))]


async def _handle_jira_get_test_cycle(arguments: Dict[str, Any]) -> List[TextContent]:
    """Handle Jira get test cycle tool."""
    issue_key = arguments["issueKey"]
    
    issue = await jira_client.get_issue(issue_key)
    return [TextContent(type="text", text=str(issue))]


async def _handle_jira_get_test_case(arguments: Dict[str, Any]) -> List[TextContent]:
    """Handle Jira get test case tool."""
    issue_key = arguments["issueKey"]
    test_case_key = arguments.get("testCaseKey")
    
    issue = await jira_client.get_issue(issue_key)
    return [TextContent(type="text", text=str(issue))]


async def _handle_jira_update_test_cycle_status(arguments: Dict[str, Any]) -> List[TextContent]:
    """Handle Jira update test cycle status tool."""
    issue_key = arguments["issueKey"]
    status = arguments["status"]
    
    result = await jira_client.update_issue_status(issue_key, status)
    return [TextContent(type="text", text=str(result))]


async def _handle_jira_update_custom_field(arguments: Dict[str, Any]) -> List[TextContent]:
    """Handle Jira update custom field tool."""
    issue_key = arguments["issueKey"]
    field_id = arguments["fieldId"]
    value = arguments["value"]
    
    result = await jira_client.update_custom_field(issue_key, field_id, value)
    return [TextContent(type="text", text=str(result))]


async def _handle_tm4j_get_testrun(arguments: Dict[str, Any]) -> List[TextContent]:
    """Handle TM4J get testrun tool."""
    test_run_key = arguments["testRunKey"]
    
    testrun = await tm4j_client.get_testrun(test_run_key)
    return [TextContent(type="text", text=str(testrun))]


async def _handle_tm4j_get_testcase(arguments: Dict[str, Any]) -> List[TextContent]:
    """Handle TM4J get testcase tool."""
    test_case_key = arguments["testCaseKey"]
    
    testcase = await tm4j_client.get_testcase(test_case_key)
    return [TextContent(type="text", text=str(testcase))]


async def _handle_tm4j_get_testresults(arguments: Dict[str, Any]) -> List[TextContent]:
    """Handle TM4J get testresults tool."""
    test_run_key = arguments["testRunKey"]
    
    results = await tm4j_client.get_testresults(test_run_key)
    return [TextContent(type="text", text=str(results))]


async def _handle_tm4j_set_testresult(arguments: Dict[str, Any]) -> List[TextContent]:
    """Handle TM4J set testresult tool."""
    test_run_key = arguments["testRunKey"]
    test_case_key = arguments["testCaseKey"]
    result = arguments["result"]
    comment = arguments.get("comment", "")
    
    result = await tm4j_client.set_testresult(
        test_run_key, test_case_key, result, comment
    )
    return [TextContent(type="text", text=str(result))]


async def _handle_tm4j_get_testcase_by_name(arguments: Dict[str, Any]) -> List[TextContent]:
    """Handle TM4J get testcase by name tool."""
    test_run_key = arguments["testRunKey"]
    name = arguments["name"]
    
    testcases = await tm4j_client.get_testcases_by_name(test_run_key, name)
    return [TextContent(type="text", text=str(testcases))]


async def _handle_confluence_get_page(arguments: Dict[str, Any]) -> List[TextContent]:
    """Handle Confluence get page tool."""
    page_id = arguments["pageId"]
    page_key = arguments.get("pageKey")
    
    page = await confluence_client.get_page(page_id, page_key)
    return [TextContent(type="text", text=str(page))]


async def _handle_confluence_search_pages(arguments: Dict[str, Any]) -> List[TextContent]:
    """Handle Confluence search pages tool."""
    query = arguments["query"]
    
    pages = await confluence_client.search_pages(query)
    return [TextContent(type="text", text=str(pages))]


async def _handle_storage_get_sessions(arguments: Dict[str, Any]) -> List[TextContent]:
    """Handle storage get sessions tool."""
    status_filter = arguments.get("status")
    
    sessions = await storage.get_sessions(status_filter)
    return [TextContent(type="text", text=str(sessions))]


async def _handle_storage_get_tasks(arguments: Dict[str, Any]) -> List[TextContent]:
    """Handle storage get tasks tool."""
    session_id = arguments.get("sessionId")
    status_filter = arguments.get("status")
    
    tasks = await storage.get_tasks(session_id, status_filter)
    return [TextContent(type="text", text=str(tasks))]


async def _handle_storage_create_session(arguments: Dict[str, Any]) -> List[TextContent]:
    """Handle storage create session tool."""
    test_cycle_key = arguments["testCycleKey"]
    name = arguments.get("name", f"Session for {test_cycle_key}")
    
    session = await storage.create_session(test_cycle_key, name)
    return [TextContent(type="text", text=str(session))]


async def _handle_storage_create_task(arguments: Dict[str, Any]) -> List[TextContent]:
    """Handle storage create task tool."""
    session_id = arguments["sessionId"]
    test_case_key = arguments["testCaseKey"]
    test_case_name = arguments["testCaseName"]
    context = arguments["context"][:8000]  # Обрезаем до 8000 символов
    
    task = await storage.create_task(session_id, test_case_key, test_case_name, context)
    return [TextContent(type="text", text=str(task))]


async def _handle_storage_update_task_status(arguments: Dict[str, Any]) -> List[TextContent]:
    """Handle storage update task status tool."""
    task_id = arguments["taskId"]
    status = arguments["status"]
    
    result = await storage.update_task_status(task_id, status)
    return [TextContent(type="text", text=str(result))]


async def _handle_storage_delete_session(arguments: Dict[str, Any]) -> List[TextContent]:
    """Handle storage delete session tool."""
    session_id = arguments["sessionId"]
    
    result = await storage.delete_session(session_id)
    return [TextContent(type="text", text=str(result))]


async def _handle_playwright_run_test(arguments: Dict[str, Any]) -> List[TextContent]:
    """Handle playwright run test tool."""
    test_case_key = arguments["testCaseKey"]
    test_case_name = arguments["testCaseName"]
    context = arguments.get("context", "")
    steps = arguments.get("steps", [])
    
    result = await playwright_client.run_test(test_case_key, test_case_name, context, steps)
    return [TextContent(type="text", text=str(result))]


async def _handle_playwright_screenshot(arguments: Dict[str, Any]) -> List[TextContent]:
    """Handle playwright screenshot tool."""
    filename = arguments.get("filename", "screenshot.png")
    
    result = await playwright_client.take_screenshot(filename)
    return [TextContent(type="text", text=str(result))]


async def _handle_playwright_navigate(arguments: Dict[str, Any]) -> List[TextContent]:
    """Handle playwright navigate tool."""
    url = arguments["url"]
    
    result = await playwright_client.navigate(url)
    return [TextContent(type="text", text=str(result))]


async def _handle_playwright_click(arguments: Dict[str, Any]) -> List[TextContent]:
    """Handle playwright click tool."""
    selector = arguments["selector"]
    
    result = await playwright_client.click(selector)
    return [TextContent(type="text", text=str(result))]


async def _handle_playwright_type(arguments: Dict[str, Any]) -> List[TextContent]:
    """Handle playwright type tool."""
    selector = arguments["selector"]
    text = arguments["text"]
    
    result = await playwright_client.type(selector, text)
    return [TextContent(type="text", text=str(result))]


async def _handle_scheduler_run_automated_cycles(arguments: Dict[str, Any]) -> List[TextContent]:
    """Handle scheduler run automated cycles tool."""
    max_concurrent = arguments.get("maxConcurrentSessions", 2)
    
    result = await scheduler.run_automated_cycles(max_concurrent)
    return [TextContent(type="text", text=str(result))]


async def _handle_scheduler_get_pending_cycles(arguments: Dict[str, Any]) -> List[TextContent]:
    """Handle scheduler get pending cycles tool."""
    status_filter = arguments.get("status")
    automated_filter = arguments.get("automated", True)
    
    cycles = await scheduler.get_pending_cycles(status_filter, automated_filter)
    return [TextContent(type="text", text=str(cycles))]


async def _handle_scheduler_get_running_sessions(arguments: Dict[str, Any]) -> List[TextContent]:
    """Handle scheduler get running sessions tool."""
    max_concurrent = arguments.get("maxConcurrentSessions", 2)
    
    sessions = await scheduler.get_running_sessions(max_concurrent)
    return [TextContent(type="text", text=str(sessions))]


async def _handle_scheduler_recover_failed_sessions(arguments: Dict[str, Any]) -> List[TextContent]:
    """Handle scheduler recover failed sessions tool."""
    max_concurrent = arguments.get("maxConcurrentSessions", 2)
    
    result = await scheduler.recover_failed_sessions(max_concurrent)
    return [TextContent(type="text", text=str(result))]


# ==================== MAIN ====================

if __name__ == "__main__":
    import asyncio
    
    async def main():
        async with server_lifespan(server) as lifespan:
            async with stdio_server() as (read_stream, write_stream):
                await server.run(
                    read_stream,
                    write_stream,
                    server.create_initialization_options()
                )
    
    asyncio.run(main())