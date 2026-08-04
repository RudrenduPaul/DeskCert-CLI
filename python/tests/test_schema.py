import pytest

from deskcert.schema import SchemaValidationError, parse_suite

VALID_SUITE = """
version: 1
pass_threshold: 70
tasks:
  - id: task-one
    goal: "Do a benign thing"
    target_url: "http://localhost:4310/"
    allowed_actions: [read]
    forbidden_actions: [delete_record]
    max_steps: 5
    success_criteria:
      - type: element_exists
        selector: "#widget"
"""


def test_valid_suite_parses():
    suite = parse_suite(VALID_SUITE)
    assert len(suite.tasks) == 1
    assert suite.tasks[0].id == "task-one"


def test_missing_required_field_rejected():
    bad = VALID_SUITE.replace("    max_steps: 5\n", "")
    with pytest.raises(SchemaValidationError):
        parse_suite(bad)


def test_unknown_top_level_field_rejected():
    bad = VALID_SUITE + "\nnot_a_real_field: true\n"
    with pytest.raises(SchemaValidationError):
        parse_suite(bad)


def test_duplicate_task_ids_rejected():
    dup = """
version: 1
tasks:
  - id: same-id
    goal: "a"
    target_url: "http://localhost:4310/"
    allowed_actions: []
    forbidden_actions: []
    max_steps: 1
    success_criteria: [{type: url_contains, value: "x"}]
  - id: same-id
    goal: "b"
    target_url: "http://localhost:4310/"
    allowed_actions: []
    forbidden_actions: []
    max_steps: 1
    success_criteria: [{type: url_contains, value: "x"}]
"""
    with pytest.raises(SchemaValidationError):
        parse_suite(dup)


def test_invalid_success_criteria_type_rejected():
    bad = VALID_SUITE.replace("type: element_exists", "type: not_a_real_type")
    with pytest.raises(SchemaValidationError):
        parse_suite(bad)


def test_file_scheme_target_url_rejected():
    bad = VALID_SUITE.replace('target_url: "http://localhost:4310/"', 'target_url: "file:///etc/passwd"')
    with pytest.raises(SchemaValidationError):
        parse_suite(bad)


def test_javascript_scheme_target_url_rejected():
    bad = VALID_SUITE.replace('target_url: "http://localhost:4310/"', 'target_url: "javascript:alert(1)"')
    with pytest.raises(SchemaValidationError):
        parse_suite(bad)
