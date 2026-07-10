"""Property-based tests for the validation engine.

# Feature: open-source-contribution-workflow, Property 15: Validation Aggregation
# Feature: open-source-contribution-workflow, Property 16: Validation Failure Reporting
# Feature: open-source-contribution-workflow, Property 17: Out-of-Scope File Detection
"""

from hypothesis import given, settings
from hypothesis import strategies as st

from src.validation import detect_out_of_scope_files, run_validation_checks


# --- Strategies ---

# Valid conventional commit messages for generating test inputs
_VALID_TYPES = [
    "fix", "feat", "docs", "test", "refactor",
    "style", "chore", "perf", "ci", "build",
]

valid_commit_message_strategy = st.builds(
    lambda t, s: f"{t}: {s}",
    st.sampled_from(_VALID_TYPES),
    st.text(
        alphabet=st.characters(whitelist_categories=("L", "N", "P", "Z"), blacklist_characters="\n\r"),
        min_size=1,
        max_size=40,
    ),
)

# File path segments and directory prefixes
path_segment = st.text(
    alphabet=st.characters(whitelist_categories=("L", "N"), blacklist_characters="/\\"),
    min_size=1,
    max_size=10,
)

directory_prefix_strategy = st.builds(
    lambda parts: "/".join(parts) + "/",
    st.lists(path_segment, min_size=1, max_size=3),
)

file_path_strategy = st.builds(
    lambda parts: "/".join(parts),
    st.lists(path_segment, min_size=1, max_size=4),
)


# --- Property 15: Validation Aggregation ---


@settings(max_examples=100)
@given(
    linter_passed=st.booleans(),
    tests_passed=st.booleans(),
    commit_messages=st.lists(valid_commit_message_strategy, min_size=1, max_size=5),
    has_merge_conflicts=st.booleans(),
    has_untracked_files=st.booleans(),
    modified_files=st.lists(file_path_strategy, min_size=0, max_size=5),
    expected_directories=st.lists(directory_prefix_strategy, min_size=1, max_size=3),
)
def test_validation_aggregation_all_passed_iff_every_check_passes(
    linter_passed: bool,
    tests_passed: bool,
    commit_messages: list,
    has_merge_conflicts: bool,
    has_untracked_files: bool,
    modified_files: list,
    expected_directories: list,
):
    """Property 15: Validation Aggregation

    all_passed is True if and only if every individual check passed.

    **Validates: Requirements 9.1**
    """
    result = run_validation_checks(
        modified_files=modified_files,
        expected_directories=expected_directories,
        commit_messages=commit_messages,
        tests_passed=tests_passed,
        has_merge_conflicts=has_merge_conflicts,
        has_untracked_files=has_untracked_files,
        linter_passed=linter_passed,
    )

    # all_passed should be True iff every individual check passed
    every_check_passed = all(check["passed"] for check in result.checks)
    assert result.all_passed == every_check_passed, (
        f"all_passed={result.all_passed} but individual checks: "
        f"{[c['name'] + '=' + str(c['passed']) for c in result.checks]}"
    )


# --- Property 16: Validation Failure Reporting ---


@settings(max_examples=100)
@given(
    linter_passed=st.booleans(),
    tests_passed=st.booleans(),
    has_merge_conflicts=st.booleans(),
    has_untracked_files=st.booleans(),
)
def test_validation_failure_reporting_has_name_and_remediation(
    linter_passed: bool,
    tests_passed: bool,
    has_merge_conflicts: bool,
    has_untracked_files: bool,
):
    """Property 16: Validation Failure Reporting

    Each failed check has a non-empty "name" and non-empty "remediation" string.

    **Validates: Requirements 9.2**
    """
    # Ensure at least one check will fail by forcing at least one failure condition
    # We use assume-like logic: if all pass, we force one to fail
    if linter_passed and tests_passed and not has_merge_conflicts and not has_untracked_files:
        # Force at least one failure for this property test
        linter_passed = False

    result = run_validation_checks(
        modified_files=["src/main.py"],
        expected_directories=["src/"],
        commit_messages=["fix: valid message"],
        tests_passed=tests_passed,
        has_merge_conflicts=has_merge_conflicts,
        has_untracked_files=has_untracked_files,
        linter_passed=linter_passed,
    )

    # At least one check should have failed
    failed_checks = [c for c in result.checks if not c["passed"]]
    assert len(failed_checks) > 0, "Expected at least one failed check"

    # Each failed check must have non-empty name and remediation
    for check in failed_checks:
        assert "name" in check and check["name"], (
            f"Failed check missing non-empty 'name': {check}"
        )
        assert "remediation" in check and check["remediation"], (
            f"Failed check '{check.get('name')}' missing non-empty 'remediation': {check}"
        )


# --- Property 17: Out-of-Scope File Detection ---


@settings(max_examples=100)
@given(
    file_paths=st.lists(file_path_strategy, min_size=1, max_size=10),
    expected_dirs=st.lists(directory_prefix_strategy, min_size=1, max_size=5),
)
def test_out_of_scope_detection_flags_only_files_outside_expected_dirs(
    file_paths: list,
    expected_dirs: list,
):
    """Property 17: Out-of-Scope File Detection

    Every returned file does NOT start with any expected directory prefix.
    No file that starts with an expected directory prefix is returned.

    **Validates: Requirements 9.4**
    """
    result = detect_out_of_scope_files(file_paths, expected_dirs)

    # Property: every file in result does NOT start with any expected dir
    for flagged_file in result:
        for directory in expected_dirs:
            assert not flagged_file.startswith(directory), (
                f"File '{flagged_file}' was flagged as out-of-scope but starts "
                f"with expected directory '{directory}'"
            )

    # Property: no file that starts with an expected dir is in the result
    for file_path in file_paths:
        is_in_scope = any(file_path.startswith(d) for d in expected_dirs)
        if is_in_scope:
            assert file_path not in result, (
                f"File '{file_path}' is within expected dirs but was flagged "
                f"as out-of-scope"
            )


@settings(max_examples=100)
@given(
    base_dirs=st.lists(directory_prefix_strategy, min_size=1, max_size=3),
    extra_segment=path_segment,
)
def test_out_of_scope_detection_in_scope_files_never_flagged(
    base_dirs: list,
    extra_segment: str,
):
    """Property 17 (supplementary): Files explicitly within expected dirs are never flagged.

    **Validates: Requirements 9.4**
    """
    # Create files that are definitely in-scope (start with an expected dir prefix)
    in_scope_files = [d + extra_segment + ".py" for d in base_dirs]

    result = detect_out_of_scope_files(in_scope_files, base_dirs)

    # None of the in-scope files should be flagged
    assert result == [], (
        f"Files {in_scope_files} are all in-scope for dirs {base_dirs} "
        f"but got flagged: {result}"
    )
