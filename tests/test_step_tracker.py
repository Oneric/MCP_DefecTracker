"""Тесты для step_tracker."""

from __future__ import annotations

from src.tm4j_mcp.utils.step_tracker import StepStatus, StepTracker


def test_start_operation():
    """Тест создания операции."""
    tracker = StepTracker()
    op_id = tracker.start_operation("test_tool")
    assert op_id.startswith("op_")
    op = tracker.get_operation_status(op_id)
    assert op is not None
    assert op.tool_name == "test_tool"
    assert op.overall_status == StepStatus.IN_PROGRESS


def test_add_step():
    """Тест добавления шага."""
    tracker = StepTracker()
    op_id = tracker.start_operation("test_tool")
    op_id, step_id = tracker.add_step(op_id, "First step")
    op = tracker.get_operation_status(op_id)
    assert len(op.steps) == 1
    assert op.steps[0].description == "First step"
    assert op.steps[0].status == StepStatus.IN_PROGRESS


def test_update_step():
    """Тест обновления шага."""
    tracker = StepTracker()
    op_id = tracker.start_operation("test_tool")
    tracker.add_step(op_id, "Step 1")
    tracker.update_step(op_id, 1, StepStatus.COMPLETED, result_summary="Done")
    op = tracker.get_operation_status(op_id)
    assert op.steps[0].status == StepStatus.COMPLETED
    assert op.steps[0].result_summary == "Done"


def test_complete_operation():
    """Тест завершения операции."""
    tracker = StepTracker()
    op_id = tracker.start_operation("test_tool")
    tracker.add_step(op_id, "Step 1")
    tracker.update_step(op_id, 1, StepStatus.COMPLETED)
    op = tracker.complete_operation(op_id)
    assert op.overall_status == StepStatus.COMPLETED


def test_complete_operation_with_failed_step():
    """Тест завершения операции с проваленным шагом."""
    tracker = StepTracker()
    op_id = tracker.start_operation("test_tool")
    tracker.add_step(op_id, "Step 1")
    tracker.update_step(op_id, 1, StepStatus.FAILED, error="Error")
    op = tracker.complete_operation(op_id)
    assert op.overall_status == StepStatus.FAILED


def test_to_dict():
    """Тест сериализации."""
    tracker = StepTracker()
    op_id = tracker.start_operation("test_tool")
    tracker.add_step(op_id, "Step 1")
    tracker.update_step(op_id, 1, StepStatus.COMPLETED)
    tracker.complete_operation(op_id)
    op = tracker.get_operation_status(op_id)
    d = op.to_dict()
    assert d["tool_name"] == "test_tool"
    assert d["overall_status"] == "completed"
    assert len(d["steps"]) == 1
