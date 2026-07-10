"""Candidate repository filtering logic.

Filters GitHub repository search results based on issue labels,
contribution-type keyword matching, and code size constraints.

Validates: Requirements 1.2, 1.3
"""

from __future__ import annotations

from typing import Any, Dict, List


# Labels that indicate beginner-friendly contribution opportunities
BEGINNER_LABELS: List[str] = [
    "good first issue",
    "help wanted",
    "beginner-friendly",
]

# Keywords indicating contribution-type opportunities in issue titles/bodies
CONTRIBUTION_KEYWORDS: List[str] = [
    "documentation",
    "docs",
    "readme",
    "test",
    "testing",
    "error",
    "exception",
    "type hint",
    "typing",
    "bug",
    "fix",
    "improve",
    "enhancement",
]


def has_contribution_keywords(issue_title: str, issue_body: str) -> bool:
    """Check if an issue title or body matches contribution-type keywords.

    Performs case-insensitive matching against a predefined set of keywords
    related to: documentation, testing, error handling, type hints, bug fixes,
    and improvements.

    Args:
        issue_title: The title text of a GitHub issue.
        issue_body: The body text of a GitHub issue.

    Returns:
        True if at least one contribution keyword is found in the title or body.
    """
    combined_text: str = f"{issue_title} {issue_body}".lower()

    for keyword in CONTRIBUTION_KEYWORDS:
        if keyword in combined_text:
            return True

    return False


def _has_beginner_labels(repo: Dict[str, Any]) -> bool:
    """Check if a repository has issues with beginner-friendly labels.

    Looks for issues labeled "good first issue", "help wanted", or
    "beginner-friendly" in the repo's issue data.

    Args:
        repo: Repository data dictionary containing issue information.

    Returns:
        True if the repo has at least one issue with a matching label.
    """
    # Check for a count of good-first-issue labeled issues
    if repo.get("good_first_issue_count", 0) > 0:
        return True

    # Check issue labels in the issues list if provided
    issues: List[Dict[str, Any]] = repo.get("issues", [])
    for issue in issues:
        labels: List[str] = [
            label.lower() if isinstance(label, str) else label.get("name", "").lower()
            for label in issue.get("labels", [])
        ]
        for beginner_label in BEGINNER_LABELS:
            if beginner_label in labels:
                return True

    return False


def _has_keyword_matching_issues(repo: Dict[str, Any]) -> bool:
    """Check if a repository has issues matching contribution-type keywords.

    Scans issue titles and bodies for keywords related to documentation,
    testing, error handling, type hints, bug fixes, and improvements.

    Args:
        repo: Repository data dictionary containing issue information.

    Returns:
        True if at least one issue matches contribution-type keywords.
    """
    issues: List[Dict[str, Any]] = repo.get("issues", [])
    for issue in issues:
        title: str = issue.get("title", "")
        body: str = issue.get("body", "")
        if has_contribution_keywords(title, body):
            return True

    return False


def _passes_issue_criteria(repo: Dict[str, Any]) -> bool:
    """Check if a repo passes the issue-based filtering criteria.

    A repo passes if it has beginner-friendly labeled issues OR issues
    with contribution-type keyword matches in title/body.

    Args:
        repo: Repository data dictionary.

    Returns:
        True if the repo meets at least one issue criterion.
    """
    return _has_beginner_labels(repo) or _has_keyword_matching_issues(repo)


def filter_candidates(
    repos: List[Dict[str, Any]],
    max_lines: int = 5000,
    max_inactive_days: int = 120,
) -> List[Dict[str, Any]]:
    """Filter candidate repositories based on issue criteria, code size, and activity.

    Applies three filters:
    1. Activity filter: Excludes repos with no updates in the last
       max_inactive_days (default 120 days / ~4 months). This filters out
       abandoned projects unlikely to review PRs.
    2. Line count filter: Excludes repos with more than max_lines in the
       main package directory.
    3. Issue criteria filter: Includes only repos that have labeled issues
       ("good first issue", "help wanted", "beginner-friendly") OR repos
       with issues whose title/body matches contribution-type keywords.

    A repository must pass ALL filters to be included in the results.

    Args:
        repos: List of raw repository data dictionaries from GitHub API results.
            Each dict should contain at minimum:
            - "main_package_lines" (int): Lines of code in the main package.
            - "good_first_issue_count" (int, optional): Count of labeled issues.
            - "issues" (list, optional): List of issue dicts with "title",
              "body", and "labels" fields.
            - "updated_at" (str, optional): ISO 8601 timestamp of last update.
        max_lines: Maximum allowed lines of code in the main package.
            Defaults to 5000.
        max_inactive_days: Maximum days since last update before a repo is
            considered abandoned. Defaults to 120 (~4 months).

    Returns:
        List of repository dictionaries that pass all filters.
    """
    from datetime import datetime, timezone

    now = datetime.now(timezone.utc)
    filtered: List[Dict[str, Any]] = []

    for repo in repos:
        # Filter 1: Exclude abandoned repos (no activity in max_inactive_days)
        updated_at: str = repo.get("updated_at", "") or repo.get("updatedAt", "")
        if updated_at:
            try:
                last_update = datetime.fromisoformat(
                    updated_at.replace("Z", "+00:00")
                )
                days_since_update = (now - last_update).days
                if days_since_update > max_inactive_days:
                    continue
            except (ValueError, TypeError):
                pass  # If we can't parse the date, don't filter on it

        # Filter 2: Exclude repos exceeding the line count limit
        main_package_lines: int = repo.get("main_package_lines", 0)
        if main_package_lines > max_lines:
            continue

        # Filter 3: Must have beginner-friendly labels or keyword-matching issues
        if not _passes_issue_criteria(repo):
            continue

        filtered.append(repo)

    return filtered
