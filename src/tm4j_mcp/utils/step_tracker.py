"""Трекер прогресса шагов для ИИ-агента."""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import Enum


class StepStatus(str, Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class StepRecord:
    step_id: int
    description: str
    status: StepStatus = StepStatus.PENDING
    result_summary: str | None = None
    error: str | None = None
    started_at: datetime | None = None
    completed_at: datetime | None = None

    def to_dict(self) -> dict:
        result: dict = {
            "step_id": self.step_id,
            "description": self.description,
            "status": self.status.value,
        }
        if self.result_summary:
            result["result_summary"] = self.result_summary
        if self.error:
            result["error"] = self.error
        if self.started_at:
            result["started_at"] = self.started_at.isoformat()
        if self.completed_at:
            result["completed_at"] = self.completed_at.isoformat()
        return result


@dataclass
class OperationContext:
    operation_id: str
    tool_name: str
    steps: list[StepRecord] = field(default_factory=list)
    overall_status: StepStatus = StepStatus.PENDING
    started_at: datetime | None = None
    completed_at: datetime | None = None

    def to_dict(self) -> dict:
        return {
            "operation_id": self.operation_id,
            "tool_name": self.tool_name,
            "overall_status": self.overall_status.value,
            "steps": [step.to_dict() for step in self.steps],
        }


class StepTracker:
    """Отслеживание прогресса составных операций для ИИ-агента."""

    def __init__(self) -> None:
        self._operations: dict[str, OperationContext] = {}

    def start_operation(self, tool_name: str) -> str:
        operation_id = f"op_{uuid.uuid4().hex[:12]}"
        self._operations[operation_id] = OperationContext(
            operation_id=operation_id,
            tool_name=tool_name,
            overall_status=StepStatus.IN_PROGRESS,
            started_at=datetime.now(UTC),
        )
        return operation_id

    def add_step(
        self, operation_id: str, description: str
    ) -> tuple[str, int]:
        op = self._operations.get(operation_id)
        if op is None:
            raise ValueError(f"Unknown operation: {operation_id}")
        step_id = len(op.steps) + 1
        op.steps.append(
            StepRecord(
                step_id=step_id,
                description=description,
                status=StepStatus.IN_PROGRESS,
                started_at=datetime.now(UTC),
            )
        )
        return operation_id, step_id

    def update_step(
        self,
        operation_id: str,
        step_id: int,
        status: StepStatus,
        *,
        result_summary: str | None = None,
        error: str | None = None,
    ) -> None:
        op = self._operations.get(operation_id)
        if op is None:
            return
        for step in op.steps:
            if step.step_id == step_id:
                step.status = status
                step.result_summary = result_summary
                step.error = error
                if status in (StepStatus.COMPLETED, StepStatus.FAILED):
                    step.completed_at = datetime.now(UTC)
                break

    def complete_operation(self, operation_id: str) -> OperationContext:
        op = self._operations.get(operation_id)
        if op is None:
            return OperationContext(
                operation_id=operation_id,
                tool_name="unknown",
                overall_status=StepStatus.FAILED,
            )
        failed_steps = [s for s in op.steps if s.status == StepStatus.FAILED]
        op.overall_status = (
            StepStatus.FAILED if failed_steps else StepStatus.COMPLETED
        )
        op.completed_at = datetime.now(UTC)
        return op

    def get_operation_status(self, operation_id: str) -> OperationContext | None:
        return self._operations.get(operation_id)
