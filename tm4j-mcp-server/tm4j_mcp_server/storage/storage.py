"""
SQLite Storage для хранения сессий и задач тестирования
"""

import sqlite3
import json
from typing import Optional, List, Dict, Any
from datetime import datetime
from contextlib import contextmanager


class TestStorage:
    """Хранилище для тестовых сессий и задач"""
    
    def __init__(self, db_path: str = "test_storage.db"):
        self.db_path = db_path
        self._init_db()
    
    def _get_connection(self) -> sqlite3.Connection:
        """Получить подключение к базе данных"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn
    
    def _init_db(self):
        """Инициализация базы данных"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            # Таблица сессий
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS test_sessions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    test_cycle_key TEXT NOT NULL,
                    session_id TEXT UNIQUE NOT NULL,
                    status TEXT NOT NULL DEFAULT 'pending',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Таблица задач
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS test_tasks (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id TEXT NOT NULL,
                    test_case_key TEXT NOT NULL,
                    test_case_name TEXT NOT NULL,
                    context TEXT NOT NULL,
                    status TEXT NOT NULL DEFAULT 'pending',
                    step_results TEXT,
                    attachments TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (session_id) REFERENCES test_sessions(id)
                )
            """)
            
            # Индексы
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_sessions_status 
                ON test_sessions(status)
            """)
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_tasks_session 
                ON test_tasks(session_id)
            """)
            
            conn.commit()
    
    @contextmanager
    def get_connection(self):
        """Контекстный менеджер для подключения"""
        conn = self._get_connection()
        try:
            yield conn
            conn.commit()
        finally:
            conn.close()
    
    # ==================== Сессии ====================
    
    def create_session(self, test_cycle_key: str, session_id: str) -> bool:
        """Создать новую сессию"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            try:
                cursor.execute("""
                    INSERT INTO test_sessions (test_cycle_key, session_id, status)
                    VALUES (?, ?, 'pending')
                """, (test_cycle_key, session_id))
                return True
            except sqlite3.IntegrityError:
                return False
    
    def get_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Получить сессию по ID"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM test_sessions WHERE id = ?", (session_id,))
            row = cursor.fetchone()
            if row:
                return dict(row)
            return None
    
    def get_session_by_cycle(self, test_cycle_key: str) -> Optional[Dict[str, Any]]:
        """Получить сессию по ключу цикла"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM test_sessions 
                WHERE test_cycle_key = ? AND status != 'completed'
                ORDER BY updated_at DESC
                LIMIT 1
            """, (test_cycle_key,))
            row = cursor.fetchone()
            if row:
                return dict(row)
            return None
    
    def update_session_status(self, session_id: str, status: str) -> bool:
        """Обновить статус сессии"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE test_sessions 
                SET status = ?, updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
            """, (status, session_id))
            return cursor.rowcount > 0
    
    def get_active_sessions(self) -> List[Dict[str, Any]]:
        """Получить активные сессии (pending, running)"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM test_sessions 
                WHERE status IN ('pending', 'running')
            """)
            return [dict(row) for row in cursor.fetchall()]
    
    def get_pending_sessions(self) -> List[Dict[str, Any]]:
        """Получить сессии в статусе pending"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM test_sessions 
                WHERE status = 'pending'
            """)
            return [dict(row) for row in cursor.fetchall()]
    
    def get_completed_sessions(self) -> List[Dict[str, Any]]:
        """Получить завершенные сессии"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM test_sessions 
                WHERE status = 'completed'
            """)
            return [dict(row) for row in cursor.fetchall()]
    
    def delete_session(self, session_id: str) -> bool:
        """Удалить сессию"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM test_sessions WHERE id = ?", (session_id,))
            return cursor.rowcount > 0
    
    # ==================== Задачи ====================
    
    def create_task(self, session_id: int, test_case_key: str, test_case_name: str,
                   context: str) -> bool:
        """Создать новую задачу"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO test_tasks 
                (session_id, test_case_key, test_case_name, context, status)
                VALUES (?, ?, ?, ?, 'pending')
            """, (session_id, test_case_key, test_case_name, context))
            return True
    
    def get_tasks_by_session(self, session_id: int) -> List[Dict[str, Any]]:
        """Получить задачи по сессии"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM test_tasks 
                WHERE session_id = ?
                ORDER BY created_at
            """, (session_id,))
            return [dict(row) for row in cursor.fetchall()]
    
    def get_pending_tasks(self, session_id: int) -> List[Dict[str, Any]]:
        """Получить задачи в статусе pending"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM test_tasks 
                WHERE session_id = ? AND status = 'pending'
            """, (session_id,))
            return [dict(row) for row in cursor.fetchall()]
    
    def get_failed_tasks(self, session_id: int) -> List[Dict[str, Any]]:
        """Получить упавшие задачи"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM test_tasks 
                WHERE session_id = ? AND status = 'failed'
            """, (session_id,))
            return [dict(row) for row in cursor.fetchall()]
    
    def update_task_status(self, task_id: int, status: str) -> bool:
        """Обновить статус задачи"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE test_tasks 
                SET status = ?
                WHERE id = ?
            """, (status, task_id))
            return cursor.rowcount > 0
    
    def update_task_step_results(self, task_id: int, step_results: str) -> bool:
        """Обновить результаты шагов задачи"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE test_tasks 
                SET step_results = ?
                WHERE id = ?
            """, (step_results, task_id))
            return cursor.rowcount > 0
    
    def update_task_attachments(self, task_id: int, attachments: str) -> bool:
        """Обновить вложения задачи"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE test_tasks 
                SET attachments = ?
                WHERE id = ?
            """, (attachments, task_id))
            return cursor.rowcount > 0
    
    def get_task(self, task_id: int) -> Optional[Dict[str, Any]]:
        """Получить задачу по ID"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM test_tasks WHERE id = ?", (task_id,))
            row = cursor.fetchone()
            if row:
                return dict(row)
            return None
    
    def delete_tasks_by_session(self, session_id: int) -> int:
        """Удалить все задачи сессии"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM test_tasks WHERE session_id = ?", (session_id,))
            return cursor.rowcount
    
    # ==================== Утилиты ====================
    
    def get_session_stats(self) -> Dict[str, Any]:
        """Получить статистику сессий"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Всего сессий
            cursor.execute("SELECT COUNT(*) FROM test_sessions")
            total_sessions = cursor.fetchone()[0]
            
            # Активные сессии
            cursor.execute("SELECT COUNT(*) FROM test_sessions WHERE status IN ('pending', 'running')")
            active_sessions = cursor.fetchone()[0]
            
            # Завершенные сессии
            cursor.execute("SELECT COUNT(*) FROM test_sessions WHERE status = 'completed'")
            completed_sessions = cursor.fetchone()[0]
            
            return {
                "total_sessions": total_sessions,
                "active_sessions": active_sessions,
                "completed_sessions": completed_sessions
            }
    
    def get_tasks_stats(self) -> Dict[str, Any]:
        """Получить статистику задач"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Всего задач
            cursor.execute("SELECT COUNT(*) FROM test_tasks")
            total_tasks = cursor.fetchone()[0]
            
            # По статусам
            cursor.execute("SELECT status, COUNT(*) FROM test_tasks GROUP BY status")
            tasks_by_status = {row[0]: row[1] for row in cursor.fetchall()}
            
            return {
                "total_tasks": total_tasks,
                "by_status": tasks_by_status
            }