"""
Scheduler для автоматического запуска тестирования
"""

import asyncio
import logging
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
import uuid

from tm4j_mcp_server.clients.jira.client import JiraClient
from tm4j_mcp_server.clients.tm4j.client import TM4JClient
from tm4j_mcp_server.storage.storage import TestStorage
from tm4j_mcp_server.playwright.playwright_client import PlaywrightClient


logger = logging.getLogger(__name__)


class TestScheduler:
    """Расписание для автоматического запуска тестирования"""
    
    def __init__(
        self,
        jira_client: JiraClient,
        tm4j_client: TM4JClient,
        playwright_client: PlaywrightClient,
        storage: TestStorage,
        check_interval: int = 300,  # 5 минут
        max_concurrent_sessions: int = 2
    ):
        self.jira_client = jira_client
        self.tm4j_client = tm4j_client
        self.playwright_client = playwright_client
        self.storage = storage
        self.check_interval = check_interval
        self.max_concurrent_sessions = max_concurrent_sessions
        
        self._running = False
        self._task: Optional[asyncio.Task] = None
    
    async def start(self):
        """Запустить scheduler"""
        self._running = True
        self._task = asyncio.create_task(self._run_loop())
        logger.info("Scheduler запущен")
    
    async def stop(self):
        """Остановить scheduler"""
        self._running = False
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
        logger.info("Scheduler остановлен")
    
    async def _run_loop(self):
        """Основной цикл scheduler"""
        while self._running:
            try:
                await self._check_and_run()
            except Exception as e:
                logger.error(f"Ошибка в цикле scheduler: {e}")
            
            await asyncio.sleep(self.check_interval)
    
    async def _check_and_run(self):
        """Проверить и запустить тестирование"""
        logger.info("Проверка условий для запуска тестирования...")
        
        # Получить активные сессии
        active_sessions = self.storage.get_active_sessions()
        logger.info(f"Активные сессии: {len(active_sessions)}")
        
        if len(active_sessions) >= self.max_concurrent_sessions:
            logger.info("Достигнут лимит одновременных сессий")
            return
        
        # Получить pending сессии
        pending_sessions = self.storage.get_pending_sessions()
        logger.info(f"Pending сессии: {len(pending_sessions)}")
        
        if not pending_sessions:
            logger.info("Нет pending сессий для запуска")
            return
        
        # Запустить сессии
        for session in pending_sessions:
            if len(active_sessions) >= self.max_concurrent_sessions:
                break
            
            await self._start_session(session)
    
    async def _start_session(self, session: Dict[str, Any]):
        """Запустить сессию тестирования"""
        session_id = session['id']
        test_cycle_key = session['test_cycle_key']
        
        logger.info(f"Запуск сессии {session_id} для цикла {test_cycle_key}")
        
        # Обновить статус
        self.storage.update_session_status(session_id, 'running')
        
        try:
            # Получить данные TestCycle
            test_cycle = await self._get_test_cycle(test_cycle_key)
            if not test_cycle:
                logger.error(f"TestCycle {test_cycle_key} не найден")
                return
            
            # Получить тест-кейсы
            test_cases = await self._get_test_cases(test_cycle_key)
            if not test_cases:
                logger.warning(f"Тест-кейсы не найдены для цикла {test_cycle_key}")
                return
            
            # Разбить на задачи (max 8000 символов контекста)
            tasks = self._split_into_tasks(test_cases, max_context_size=8000)
            logger.info(f"Создано {len(tasks)} задач")
            
            # Создать задачи в storage
            for task in tasks:
                self.storage.create_task(
                    session_id,
                    task['test_case_key'],
                    task['test_case_name'],
                    task['context']
                )
            
            # Запустить playwright
            await self._run_playwright_tasks(session_id, tasks)
            
        except Exception as e:
            logger.error(f"Ошибка при запуске сессии {session_id}: {e}")
            self.storage.update_session_status(session_id, 'failed')
    
    async def _get_test_cycle(self, test_cycle_key: str) -> Optional[Dict[str, Any]]:
        """Получить данные TestCycle"""
        try:
            return await self.tm4j_client.get_test_run(test_cycle_key)
        except Exception as e:
            logger.error(f"Ошибка получения TestCycle {test_cycle_key}: {e}")
            return None
    
    async def _get_test_cases(self, test_cycle_key: str) -> List[Dict[str, Any]]:
        """Получить тест-кейсы для цикла"""
        try:
            # Получить результаты тестирования
            results = await self.tm4j_client.get_test_results(test_cycle_key)
            
            test_cases = []
            for result in results:
                # Получить детали тест-кейса
                test_case = await self.tm4j_client.get_test_case(result['test_case_key'])
                if test_case:
                    test_cases.append({
                        'key': result['test_case_key'],
                        'name': test_case.get('name', ''),
                        'folder': result.get('folder', ''),
                        'description': test_case.get('description', '')
                    })
            
            return test_cases
        except Exception as e:
            logger.error(f"Ошибка получения тест-кейсов: {e}")
            return []
    
    def _split_into_tasks(self, test_cases: List[Dict[str, Any]],
                         max_context_size: int = 8000) -> List[Dict[str, Any]]:
        """Разбить тест-кейсы на задачи"""
        tasks = []
        
        for tc in test_cases:
            # Формирование контекста
            context_parts = [
                f"Тест-кейс: {tc['name']}",
                f"Ключ: {tc['key']}",
                f"Папка: {tc['folder']}",
                f"Описание: {tc['description']}"
            ]
            
            context = "\n".join(context_parts)
            
            if len(context) > max_context_size:
                # Обрезать контекст
                context = context[:max_context_size] + "..."
            
            tasks.append({
                'test_case_key': tc['key'],
                'test_case_name': tc['name'],
                'context': context
            })
        
        return tasks
    
    async def _run_playwright_tasks(self, session_id: int, tasks: List[Dict[str, Any]]):
        """Запустить задачи через Playwright"""
        # Получить задачи из storage
        storage_tasks = self.storage.get_tasks_by_session(session_id)
        
        # Запустить playwright
        await self.playwright_client.run_tests(
            session_id=session_id,
            tasks=storage_tasks,
            max_concurrent=2
        )
    
    # ==================== Ручные методы ====================
    
    async def run_manual(self, test_cycle_key: str):
        """Ручной запуск тестирования"""
        logger.info(f"Ручной запуск тестирования для цикла {test_cycle_key}")
        
        # Проверить, есть ли активная сессия
        existing_session = self.storage.get_session_by_cycle(test_cycle_key)
        if existing_session:
            logger.warning(f"Существует активная сессия: {existing_session['session_id']}")
            return
        
        # Создать новую сессию
        session_id = str(uuid.uuid4())
        self.storage.create_session(test_cycle_key, session_id)
        
        # Запустить сессию
        await self._start_session({
            'id': session_id,
            'test_cycle_key': test_cycle_key
        })
    
    async def get_status(self) -> Dict[str, Any]:
        """Получить статус scheduler"""
        return {
            "running": self._running,
            "active_sessions": len(self.storage.get_active_sessions()),
            "pending_sessions": len(self.storage.get_pending_sessions()),
            "completed_sessions": len(self.storage.get_completed_sessions())
        }