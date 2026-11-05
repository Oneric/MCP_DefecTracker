"""Составные вью — агрегирующие MCP-инструменты."""

from __future__ import annotations

import logging
from typing import Any

from ..tools.base import BaseTool
from ..utils.step_tracker import StepStatus

logger = logging.getLogger(__name__)


class CompositeTool(BaseTool):
    """Составные вью с агрегацией данных из нескольких API-вызовов."""

    def get_test_case_full_details(
        self,
        test_case_key: str,
        *,
        convert_to_markdown: bool = False,
    ) -> dict:
        """
        Получить полную информацию о тест-кейсе:
        - Тест-кейс с шагами
        - Последний результат выполнения
        - Вложения тест-кейса
        - Вложения по шагам

        Args:
            test_case_key: Ключ тест-кейса
            convert_to_markdown: Вернуть результат в Markdown
        """
        op_id = self.step_tracker.start_operation("get_test_case_full_details")
        result: dict[str, Any] = {}

        try:
            # Шаг 1: Загрузка тест-кейса
            self.step_tracker.add_step(op_id, "Загрузка тест-кейса")
            try:
                tc = self.client.get_test_case(test_case_key)
                result["test_case"] = tc
                self.step_tracker.update_step(
                    op_id, 1, StepStatus.COMPLETED, result_summary=f"Получен TC {tc.get('key', '?')}"
                )
            except Exception as e:
                self.step_tracker.update_step(
                    op_id, 1, StepStatus.FAILED, error=str(e)
                )
                raise

            # Шаг 2: Загрузка последнего результата
            self.step_tracker.add_step(op_id, "Загрузка последнего результата")
            try:
                latest = self.client.get_latest_test_result(test_case_key)
                result["latest_result"] = latest
                status = latest.get("status", "N/A") if latest else "Нет результатов"
                self.step_tracker.update_step(
                    op_id, 2, StepStatus.COMPLETED, result_summary=f"Статус: {status}"
                )
            except Exception as e:
                self.step_tracker.update_step(
                    op_id, 2, StepStatus.FAILED, error=str(e)
                )
                result["latest_result"] = None

            # Шаг 3: Загрузка вложений тест-кейса
            self.step_tracker.add_step(op_id, "Загрузка вложений тест-кейса")
            try:
                attachments = self.client.get_test_case_attachments(test_case_key)
                result["attachments"] = attachments
                count = len(attachments) if isinstance(attachments, list) else 0
                self.step_tracker.update_step(
                    op_id, 3, StepStatus.COMPLETED, result_summary=f"Вложений: {count}"
                )
            except Exception as e:
                self.step_tracker.update_step(
                    op_id, 3, StepStatus.FAILED, error=str(e)
                )
                result["attachments"] = []

            # Шаг 4: Вложения по шагам
            self.step_tracker.add_step(op_id, "Загрузка вложений по шагам")
            step_attachments: dict[int, list] = {}
            try:
                steps = []
                if isinstance(tc, dict):
                    ts = tc.get("testScript", {})
                    steps = ts.get("steps", []) if isinstance(ts, dict) else []
                for step in steps:
                    idx = step.get("index", 0)
                    try:
                        sa = self.client.get_step_attachments(test_case_key, idx)
                        if sa:
                            step_attachments[idx] = sa
                    except Exception:
                        pass
                result["step_attachments"] = step_attachments
                self.step_tracker.update_step(
                    op_id,
                    4,
                    StepStatus.COMPLETED,
                    result_summary=f"Шагов с вложениями: {len(step_attachments)}",
                )
            except Exception as e:
                self.step_tracker.update_step(
                    op_id, 4, StepStatus.FAILED, error=str(e)
                )

            self.step_tracker.complete_operation(op_id)
            return self.response_wrapper(
                result,
                convert_to_markdown=convert_to_markdown,
                entity_type="test_case",
                operation_id=op_id,
            )
        except Exception:
            self.step_tracker.complete_operation(op_id)
            raise

    def get_test_run_full_details(
        self,
        test_run_key: str,
        *,
        convert_to_markdown: bool = False,
    ) -> dict:
        """
        Получить полную информацию о тест-прогоне:
        - Тест-прогон со списком тест-кейсов
        - Результаты выполнения всех тест-кейсов
        - Статистика PASSED/FAILED/BLOCKED/SKIPPED

        Args:
            test_run_key: Ключ тест-прогона
            convert_to_markdown: Вернуть результат в Markdown
        """
        op_id = self.step_tracker.start_operation("get_test_run_full_details")
        result: dict[str, Any] = {}

        try:
            # Шаг 1: Загрузка тест-прогона
            self.step_tracker.add_step(op_id, "Загрузка тест-прогона")
            try:
                tr = self.client.get_test_run(test_run_key)
                result["test_run"] = tr
                self.step_tracker.update_step(
                    op_id, 1, StepStatus.COMPLETED, result_summary=f"Получен TR {tr.get('name', '?')}"
                )
            except Exception as e:
                self.step_tracker.update_step(
                    op_id, 1, StepStatus.FAILED, error=str(e)
                )
                raise

            # Шаг 2: Загрузка результатов
            self.step_tracker.add_step(op_id, "Загрузка результатов тестирования")
            try:
                test_results = self.client.get_test_results(test_run_key)
                result["test_results"] = test_results
                self.step_tracker.update_step(
                    op_id,
                    2,
                    StepStatus.COMPLETED,
                    result_summary=f"Результатов: {len(test_results) if isinstance(test_results, list) else 0}",
                )
            except Exception as e:
                self.step_tracker.update_step(
                    op_id, 2, StepStatus.FAILED, error=str(e)
                )
                result["test_results"] = []

            # Шаг 3: Статистика
            self.step_tracker.add_step(op_id, "Подсчёт статистики")
            try:
                stats = self._compute_stats(
                    result.get("test_results", [])
                )
                result["statistics"] = stats
                self.step_tracker.update_step(
                    op_id, 3, StepStatus.COMPLETED, result_summary=str(stats)
                )
            except Exception as e:
                self.step_tracker.update_step(
                    op_id, 3, StepStatus.FAILED, error=str(e)
                )
                result["statistics"] = {}

            self.step_tracker.complete_operation(op_id)
            return self.response_wrapper(
                result,
                convert_to_markdown=convert_to_markdown,
                entity_type="test_run",
                operation_id=op_id,
            )
        except Exception:
            self.step_tracker.complete_operation(op_id)
            raise

    def get_project_test_overview(
        self,
        *,
        project_key: str | None = None,
        convert_to_markdown: bool = False,
    ) -> dict:
        """
        Полный обзор тестирования проекта:
        - Все окружения
        - Последние тест-прогоны
        - Последние тест-кейсы

        Args:
            project_key: Ключ проекта (по умолчанию из config)
            convert_to_markdown: Вернуть результат в Markdown
        """
        op_id = self.step_tracker.start_operation("get_project_test_overview")
        pk = project_key or self.config.tm4j_project_key
        result: dict[str, Any] = {}

        try:
            # Шаг 1: Окружения
            self.step_tracker.add_step(op_id, "Загрузка окружений")
            try:
                envs = self.client.get_environments(pk)
                result["environments"] = envs
                self.step_tracker.update_step(
                    op_id,
                    1,
                    StepStatus.COMPLETED,
                    result_summary=f"Окружений: {len(envs) if isinstance(envs, list) else 0}",
                )
            except Exception as e:
                self.step_tracker.update_step(
                    op_id, 1, StepStatus.FAILED, error=str(e)
                )
                result["environments"] = []

            # Шаг 2: Последние тест-прогоны
            self.step_tracker.add_step(op_id, "Поиск тест-прогонов")
            try:
                runs = self.client.search_test_runs(
                    query=f"projectKey={pk}", max_results=10
                )
                result["recent_test_runs"] = runs
                self.step_tracker.update_step(
                    op_id, 2, StepStatus.COMPLETED, result_summary="Тест-прогоны получены"
                )
            except Exception as e:
                self.step_tracker.update_step(
                    op_id, 2, StepStatus.FAILED, error=str(e)
                )
                result["recent_test_runs"] = {}

            # Шаг 3: Последние тест-кейсы
            self.step_tracker.add_step(op_id, "Поиск тест-кейсов")
            try:
                cases = self.client.search_test_cases(
                    query=f"projectKey={pk}", max_results=10
                )
                result["recent_test_cases"] = cases
                self.step_tracker.update_step(
                    op_id, 2, StepStatus.COMPLETED, result_summary="Тест-кейсы получены"
                )
            except Exception as e:
                self.step_tracker.update_step(
                    op_id, 3, StepStatus.FAILED, error=str(e)
                )
                result["recent_test_cases"] = {}

            self.step_tracker.complete_operation(op_id)
            return self.response_wrapper(
                result,
                convert_to_markdown=convert_to_markdown,
                entity_type="project",
                operation_id=op_id,
            )
        except Exception:
            self.step_tracker.complete_operation(op_id)
            raise

    def search_and_aggregate_results(
        self,
        *,
        query: str = "",
        max_results: int = 50,
        convert_to_markdown: bool = False,
    ) -> dict:
        """
        Поиск тест-кейсов с агрегацией результатов:
        1. Поиск тест-кейсов
        2. Для каждого — получение последнего результата
        3. Агрегация статистики

        Args:
            query: Строка поиска
            max_results: Максимум результатов
            convert_to_markdown: Вернуть результат в Markdown
        """
        op_id = self.step_tracker.start_operation("search_and_aggregate_results")
        result: dict[str, Any] = {}

        try:
            # Шаг 1: Поиск
            self.step_tracker.add_step(op_id, "Поиск тест-кейсов")
            try:
                search_result = self.client.search_test_cases(
                    query=query,
                    max_results=max_results,
                )
                result["search"] = search_result
                items = search_result.get("items", []) if isinstance(search_result, dict) else []
                self.step_tracker.update_step(
                    op_id, 1, StepStatus.COMPLETED, result_summary=f"Найдено: {len(items)}"
                )
            except Exception as e:
                self.step_tracker.update_step(
                    op_id, 1, StepStatus.FAILED, error=str(e)
                )
                raise

            # Шаг 2: Агрегация результатов
            self.step_tracker.add_step(op_id, "Агрегация результатов")
            aggregated: list[dict] = []
            try:
                for item in items[:20]:  # Лимит для производительности
                    tc_key = item.get("key", "")
                    entry: dict = {"test_case": item, "latest_result": None}
                    try:
                        latest = self.client.get_latest_test_result(tc_key)
                        entry["latest_result"] = latest
                    except Exception:
                        pass
                    aggregated.append(entry)
                result["aggregated"] = aggregated
                self.step_tracker.update_step(
                    op_id, 2, StepStatus.COMPLETED, result_summary=f"Агрегировано: {len(aggregated)}"
                )
            except Exception as e:
                self.step_tracker.update_step(
                    op_id, 2, StepStatus.FAILED, error=str(e)
                )

            # Шаг 3: Статистика
            self.step_tracker.add_step(op_id, "Подсчёт статистики")
            try:
                stats = {"total": len(aggregated), "with_results": 0, "statuses": {}}
                for entry in aggregated:
                    lr = entry.get("latest_result")
                    if lr and isinstance(lr, dict):
                        stats["with_results"] += 1
                        status = lr.get("status", "Unknown")
                        stats["statuses"][status] = stats["statuses"].get(status, 0) + 1
                result["statistics"] = stats
                self.step_tracker.update_step(
                    op_id, 3, StepStatus.COMPLETED, result_summary=str(stats)
                )
            except Exception as e:
                self.step_tracker.update_step(
                    op_id, 3, StepStatus.FAILED, error=str(e)
                )

            self.step_tracker.complete_operation(op_id)
            return self.response_wrapper(
                result,
                convert_to_markdown=convert_to_markdown,
                entity_type="test_case",
                operation_id=op_id,
            )
        except Exception:
            self.step_tracker.complete_operation(op_id)
            raise

    @staticmethod
    def _compute_stats(results: list) -> dict:
        """Подсчитать статистику по результатам."""
        stats: dict[str, int] = {}
        total = 0
        for r in results:
            if isinstance(r, dict):
                total += 1
                status = r.get("status", "Unknown")
                stats[status] = stats.get(status, 0) + 1
        return {"total": total, "by_status": stats}
