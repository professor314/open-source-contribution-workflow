"""Composite scoring and ranking logic for candidate repositories.

Implements the scoring formula from the design document and provides
a ranking function that sorts candidates by score and caps results.
"""

from __future__ import annotations

from typing import List


from src.models import CandidateRepo


def compute_composite_score(
    commits_last_90_days: int,
    has_contributing_md: bool,
    open_issues: int,
    main_package_lines: int,
) -> float:
    """Compute composite score for a candidate repository.

    Formula:
        score = (min(commits_last_90_days, 50) / 50 * 25)
              + (contributing_md_present * 20)
              + (min(open_issues, 20) / 20 * 25)
              + ((1 - min(main_package_lines, 5000) / 5000) * 30)

    Components:
        - recent_commits: 25 points max (more recent activity = higher score)
        - contributing_md: 20 points (binary: present or not)
        - open_issues: 25 points max (more issues = more opportunity)
        - size_inverse: 30 points max (fewer lines = easier entry)

    Args:
        commits_last_90_days: Number of commits in the last 90 days.
        has_contributing_md: Whether the repo has a CONTRIBUTING.md file.
        open_issues: Number of open issues in the repository.
        main_package_lines: Lines of code in the main package directory.

    Returns:
        A float score between 0 and 100 (inclusive).
    """
    recent_commits_score: float = min(commits_last_90_days, 50) / 50 * 25
    contributing_md_score: float = 20.0 if has_contributing_md else 0.0
    open_issues_score: float = min(open_issues, 20) / 20 * 25
    size_score: float = (1 - min(main_package_lines, 5000) / 5000) * 30

    score: float = (
        recent_commits_score
        + contributing_md_score
        + open_issues_score
        + size_score
    )

    return score


def rank_candidates(candidates: List[CandidateRepo]) -> List[CandidateRepo]:
    """Score each candidate, sort by score descending, and cap at 10 results.

    For each candidate, the composite score is computed from its metadata
    fields and stored in the candidate's composite_score attribute. The
    list is then sorted in non-increasing order of score and truncated
    to a maximum of 10 entries.

    Args:
        candidates: List of CandidateRepo objects to rank.

    Returns:
        A sorted list of at most 10 CandidateRepo objects, ordered from
        highest to lowest composite score.
    """
    for candidate in candidates:
        candidate.composite_score = compute_composite_score(
            commits_last_90_days=candidate.commits_last_90_days,
            has_contributing_md=candidate.has_contributing_md,
            open_issues=candidate.open_issues_count,
            main_package_lines=candidate.main_package_lines,
        )

    sorted_candidates: List[CandidateRepo] = sorted(
        candidates,
        key=lambda c: c.composite_score,
        reverse=True,
    )

    return sorted_candidates[:10]
