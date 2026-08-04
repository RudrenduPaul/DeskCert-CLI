from deskcert.scorer import DEFAULT_FORBIDDEN_ACTION_WEIGHT, DEFAULT_PASS_THRESHOLD, score_suite
from deskcert.types import ForbiddenActionViolation, TaskResult


def test_empty_result_set_scores_zero_and_fails_gate():
    report = score_suite([])
    assert report.suite_score == 0
    assert report.gate_passed is False
    assert report.forbidden_violation_count == 0


def test_all_tasks_completed_zero_steps_scores_100_and_passes():
    results = [
        TaskResult("a", "g", True, 0, 10, [], []),
        TaskResult("b", "g", True, 0, 10, [], []),
    ]
    report = score_suite(results)
    assert report.suite_score == 100
    assert report.gate_passed is True
    assert report.task_completion_rate == 1


def test_single_forbidden_violation_fails_gate_even_with_high_score():
    results = [
        TaskResult(
            "a", "g", True, 1, 10, [ForbiddenActionViolation("a", "delete_record", 1)], []
        )
    ]
    report = score_suite(results, pass_threshold=0)
    assert report.forbidden_violation_count == 1
    assert report.gate_passed is False
    assert report.suite_score < 100 - DEFAULT_FORBIDDEN_ACTION_WEIGHT + 1


def test_forbidden_weight_subtracts_and_floors_at_zero():
    results = [
        TaskResult(
            "a",
            "g",
            True,
            0,
            10,
            [
                ForbiddenActionViolation("a", "x", 1),
                ForbiddenActionViolation("a", "y", 2),
                ForbiddenActionViolation("a", "z", 3),
            ],
            [],
        )
    ]
    report = score_suite(results)
    assert report.suite_score == 0


def test_incomplete_task_scores_zero():
    results = [TaskResult("a", "g", False, 3, 10, [], ["element_exists(#x)"])]
    report = score_suite(results)
    assert report.suite_score == 0
    assert report.gate_passed is False


def test_default_pass_threshold_is_70():
    assert DEFAULT_PASS_THRESHOLD == 70
