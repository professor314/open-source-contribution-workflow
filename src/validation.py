"""Pre-submission validation engine for contribution quality checks.

Runs a checklist covering code style, test passage, commit message format,
branch cleanliness, and out-of-scope file detection. Returns a ValidationResult
with per-check pass/fail status and remediation instructions for failures.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import List, Optional

from src.commit_format import validate_commit_message
from src.models import ValidationResult


def detect_out_of_scope_files(
    modified_files: List[str],
    expected_directories: List[str],
) -> List[str]:
    """Detect modified files that fall outside expected directories.

    A file is considered out-of-scope if its path does not start with any
    of the expected directory prefixes.

    Args:
        modified_files: List of file paths that were modified.
        expected_directories: List of directory prefixes considered in-scope.

    Returns:
        List of file paths that don't fall within any expected directory.
    """
    out_of_scope: List[str] = []
    for file_path in modified_files:
        in_scope = any(
            file_path.startswith(directory)
            for directory in expected_directories
        )
        if not in_scope:
            out_of_scope.append(file_path)
    return out_of_scope


def run_validation_checks(
    modified_files: List[str],
    expected_directories: List[str],
    commit_messages: List[str],
    tests_passed: bool,
    has_merge_conflicts: bool = False,
    has_untracked_files: bool = False,
    linter_passed: bool = True,
) -> ValidationResult:
    """Run pre-submission validation checklist.

    Checks:
        1. code_style — passes if linter_passed is True
        2. tests_pass — passes if tests_passed is True
        3. commit_format — validates each commit message using conventional commits
        4. branch_cleanliness — passes if no merge conflicts AND no untracked files
        5. out_of_scope_files — flags files outside expected directories

    Each check produces a dict with keys: name, passed, details, remediation.
    If passed, details and remediation are None.
    If failed, details describes the issue and remediation gives fix instructions.

    Args:
        modified_files: List of file paths modified in the contribution.
        expected_directories: List of directory prefixes that are in-scope.
        commit_messages: List of commit messages to validate.
        tests_passed: Whether the test suite passed.
        has_merge_conflicts: Whether the branch has merge conflicts.
        has_untracked_files: Whether there are untracked files in the working tree.
        linter_passed: Whether the linter passed.

    Returns:
        ValidationResult with all check results and aggregate pass/fail status.
    """
    checks: List[dict] = []

    # 1. Code style check
    checks.append(_check_code_style(linter_passed))

    # 2. Tests pass check
    checks.append(_check_tests_pass(tests_passed))

    # 3. Commit format check
    checks.append(_check_commit_format(commit_messages))

    # 4. Branch cleanliness check
    checks.append(_check_branch_cleanliness(has_merge_conflicts, has_untracked_files))

    # 5. Out-of-scope files check
    checks.append(_check_out_of_scope_files(modified_files, expected_directories))

    all_passed = all(check["passed"] for check in checks)
    checked_at = datetime.now(timezone.utc).isoformat()

    return ValidationResult(
        checks=checks,
        all_passed=all_passed,
        checked_at=checked_at,
    )


def _check_code_style(linter_passed: bool) -> dict:
    """Check code style compliance."""
    if linter_passed:
        return {
            "name": "code_style",
            "passed": True,
            "details": None,
            "remediation": None,
        }
    return {
        "name": "code_style",
        "passed": False,
        "details": "Code style check failed. The linter reported violations.",
        "remediation": (
            "1. Run the project's linter to see specific violations.\n"
            "2. Fix each reported style issue in the affected files.\n"
            "3. Re-run the linter to confirm all issues are resolved."
        ),
    }


def _check_tests_pass(tests_passed: bool) -> dict:
    """Check whether the test suite passed."""
    if tests_passed:
        return {
            "name": "tests_pass",
            "passed": True,
            "details": None,
            "remediation": None,
        }
    return {
        "name": "tests_pass",
        "passed": False,
        "details": "One or more tests failed.",
        "remediation": (
            "1. Run the test suite to identify failing tests.\n"
            "2. Review the test output to understand why each test failed.\n"
            "3. Fix the code or tests so that all tests pass.\n"
            "4. Re-run the full test suite to confirm no regressions."
        ),
    }


def _check_commit_format(commit_messages: List[str]) -> dict:
    """Check that all commit messages follow conventional commit format."""
    invalid_messages: List[str] = []
    for msg in commit_messages:
        if not validate_commit_message(msg):
            invalid_messages.append(msg)

    if not invalid_messages:
        return {
            "name": "commit_format",
            "passed": True,
            "details": None,
            "remediation": None,
        }

    details = (
        f"{len(invalid_messages)} commit message(s) do not follow conventional "
        f"commit format: {invalid_messages}"
    )
    return {
        "name": "commit_format",
        "passed": False,
        "details": details,
        "remediation": (
            "1. Use the format: type(optional-scope): subject\n"
            "2. Valid types are: fix, feat, docs, test, refactor, style, chore, perf, ci, build.\n"
            "3. Keep the subject line to 72 characters or fewer.\n"
            "4. Use `git commit --amend` to fix the most recent commit message, "
            "or `git rebase -i` for older commits."
        ),
    }


def _check_branch_cleanliness(
    has_merge_conflicts: bool, has_untracked_files: bool
) -> dict:
    """Check branch cleanliness (no merge conflicts, no untracked files)."""
    issues: List[str] = []
    if has_merge_conflicts:
        issues.append("merge conflicts detected")
    if has_untracked_files:
        issues.append("untracked files present")

    if not issues:
        return {
            "name": "branch_cleanliness",
            "passed": True,
            "details": None,
            "remediation": None,
        }

    details = f"Branch is not clean: {', '.join(issues)}."
    remediation_steps: List[str] = []
    if has_merge_conflicts:
        remediation_steps.append(
            "1. Resolve merge conflicts by editing the conflicting files.\n"
            "2. Stage the resolved files with `git add`.\n"
            "3. Complete the merge with `git commit`."
        )
    if has_untracked_files:
        remediation_steps.append(
            "1. Review untracked files with `git status`.\n"
            "2. Either add them with `git add` if they belong in the commit, "
            "or add them to .gitignore if they should be excluded."
        )

    return {
        "name": "branch_cleanliness",
        "passed": False,
        "details": details,
        "remediation": "\n".join(remediation_steps),
    }


def _check_out_of_scope_files(
    modified_files: List[str], expected_directories: List[str]
) -> dict:
    """Check for modified files outside expected directories."""
    out_of_scope = detect_out_of_scope_files(modified_files, expected_directories)

    if not out_of_scope:
        return {
            "name": "out_of_scope_files",
            "passed": True,
            "details": None,
            "remediation": None,
        }

    details = (
        f"{len(out_of_scope)} file(s) modified outside expected directories: "
        f"{out_of_scope}"
    )
    return {
        "name": "out_of_scope_files",
        "passed": False,
        "details": details,
        "remediation": (
            "1. Review the listed files to confirm they are intentional changes.\n"
            "2. If unintentional, use `git checkout -- <file>` to discard changes.\n"
            "3. If intentional, update the expected directories list or confirm "
            "with the maintainer that cross-directory changes are acceptable."
        ),
    }
