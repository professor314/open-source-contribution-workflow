"""Property-based tests for candidate filtering, scoring, and display.

Tests Properties 1-3 from the design document using Hypothesis.

Validates: Requirements 1.2, 1.3, 1.4
"""

from __future__ import annotations

import sys
import os

# Ensure project root is on the path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from hypothesis import given, settings
from hypothesis import strategies as st

from src.filtering import (
    filter_candidates,
    BEGINNER_LABELS,
    CONTRIBUTION_KEYWORDS,
    _has_beginner_labels,
    _has_keyword_matching_issues,
)
from src.scoring import compute_composite_score, rank_candidates
from src.models import CandidateRepo


# --- Strategies ---

# Strategy: generate a random issue with optional beginner labels and keyword text
def issue_strategy(with_beginner_label: bool = False, with_keyword: bool = False):
    """Generate a random issue dict."""
    label_choices = st.sampled_from(BEGINNER_LABELS) if with_beginner_label else st.text(
        min_size=1, max_size=20, alphabet=st.characters(whitelist_categories=("L", "N", "Z"))
    )

    keyword_title = st.sampled_from(CONTRIBUTION_KEYWORDS) if with_keyword else st.text(
        min_size=0, max_size=30, alphabet=st.characters(whitelist_categories=("L", "N", "Z"))
    )

    return st.fixed_dictionaries({
        "title": keyword_title,
        "body": st.text(min_size=0, max_size=50),
        "labels": st.lists(label_choices, min_size=1 if with_beginner_label else 0, max_size=3),
    })


# Strategy: generate a repo dict that satisfies neither filtering condition
def repo_no_match_strategy():
    """Generate a repo that has NO beginner labels and NO keyword-matching issues."""
    # Use non-keyword text for issue titles/bodies, non-beginner labels
    safe_text = st.text(
        min_size=1, max_size=20,
        alphabet=st.characters(whitelist_categories=("Lu",))  # uppercase only to avoid keyword matching
    )

    non_matching_issue = st.fixed_dictionaries({
        "title": safe_text,
        "body": safe_text,
        "labels": st.lists(safe_text, min_size=0, max_size=2),
    })

    return st.fixed_dictionaries({
        "full_name": st.text(min_size=3, max_size=30),
        "main_package_lines": st.integers(min_value=0, max_value=5000),
        "good_first_issue_count": st.just(0),
        "issues": st.lists(non_matching_issue, min_size=0, max_size=3),
    })


# Strategy: generate a repo dict that satisfies at least one filtering condition
def repo_match_strategy():
    """Generate a repo that has beginner labels OR keyword-matching issues."""
    # Either has good_first_issue_count > 0, or has an issue with a matching keyword/label
    return st.one_of(
        # Case 1: Has good_first_issue_count > 0
        st.fixed_dictionaries({
            "full_name": st.text(min_size=3, max_size=30),
            "main_package_lines": st.integers(min_value=0, max_value=5000),
            "good_first_issue_count": st.integers(min_value=1, max_value=10),
            "issues": st.just([]),
        }),
        # Case 2: Has an issue with a beginner label
        st.fixed_dictionaries({
            "full_name": st.text(min_size=3, max_size=30),
            "main_package_lines": st.integers(min_value=0, max_value=5000),
            "good_first_issue_count": st.just(0),
            "issues": st.lists(issue_strategy(with_beginner_label=True), min_size=1, max_size=3),
        }),
        # Case 3: Has an issue with keyword in title
        st.fixed_dictionaries({
            "full_name": st.text(min_size=3, max_size=30),
            "main_package_lines": st.integers(min_value=0, max_value=5000),
            "good_first_issue_count": st.just(0),
            "issues": st.lists(issue_strategy(with_keyword=True), min_size=1, max_size=3),
        }),
    )


# Strategy: generate a CandidateRepo with random metadata
def candidate_repo_strategy():
    """Generate a CandidateRepo with random but valid metadata."""
    return st.builds(
        CandidateRepo,
        full_name=st.text(min_size=3, max_size=40, alphabet=st.characters(whitelist_categories=("L", "N", "P"))),
        description=st.text(min_size=0, max_size=200),
        stars=st.integers(min_value=0, max_value=100000),
        last_commit_date=st.just("2025-01-15T10:30:00Z"),
        open_issues_count=st.integers(min_value=0, max_value=100),
        has_contributing_md=st.booleans(),
        main_package_lines=st.integers(min_value=0, max_value=10000),
        contribution_types=st.lists(
            st.sampled_from(["bug_fix", "test_addition", "documentation", "error_handling", "feature"]),
            min_size=1, max_size=3,
        ),
        proposed_contribution=st.just({"type": "bug_fix", "summary": "Fix a bug"}),
        difficulty_level=st.sampled_from(["beginner", "intermediate", "advanced"]),
        composite_score=st.just(0.0),  # Will be computed by rank_candidates
        good_first_issue_count=st.integers(min_value=0, max_value=20),
        dependency_count=st.integers(min_value=0, max_value=20),
        commits_last_90_days=st.integers(min_value=0, max_value=200),
    )


# --- Property Tests ---


# Feature: open-source-contribution-workflow, Property 1: Candidate Filtering Correctness
class TestCandidateFilteringCorrectness:
    """Property 1: Every returned repo has a beginner label or keyword-matching issues.
    No repo satisfying neither condition is returned.

    Validates: Requirements 1.2, 1.3
    """

    @given(
        matching_repos=st.lists(repo_match_strategy(), min_size=0, max_size=5),
        non_matching_repos=st.lists(repo_no_match_strategy(), min_size=0, max_size=5),
    )
    @settings(max_examples=100)
    def test_only_matching_repos_returned(self, matching_repos, non_matching_repos):
        """Assert: every returned repo either has a beginner label or keyword-matching issues.
        Assert: no repo satisfying neither condition is returned."""
        all_repos = matching_repos + non_matching_repos
        result = filter_candidates(all_repos)

        # Every result must satisfy at least one condition
        for repo in result:
            has_labels = _has_beginner_labels(repo)
            has_keywords = _has_keyword_matching_issues(repo)
            assert has_labels or has_keywords, (
                f"Repo passed filter but has neither beginner labels nor keyword-matching issues: {repo}"
            )

    @given(repos=st.lists(repo_no_match_strategy(), min_size=1, max_size=10))
    @settings(max_examples=100)
    def test_non_matching_repos_excluded(self, repos):
        """Repos with no beginner labels and no keyword-matching issues are never returned."""
        result = filter_candidates(repos)
        assert len(result) == 0, (
            f"Expected no results from non-matching repos, got {len(result)}"
        )

    @given(repos=st.lists(repo_match_strategy(), min_size=1, max_size=10))
    @settings(max_examples=100)
    def test_matching_repos_included(self, repos):
        """Repos that meet the criteria are included (within line limit)."""
        result = filter_candidates(repos)
        # All matching repos with <=5000 lines should be returned
        expected_count = sum(
            1 for r in repos if r.get("main_package_lines", 0) <= 5000
        )
        assert len(result) == expected_count, (
            f"Expected {expected_count} results, got {len(result)}"
        )

    @given(
        repos=st.lists(
            st.fixed_dictionaries({
                "full_name": st.text(min_size=3, max_size=20),
                "main_package_lines": st.integers(min_value=5001, max_value=20000),
                "good_first_issue_count": st.integers(min_value=1, max_value=10),
                "issues": st.just([]),
            }),
            min_size=1, max_size=5,
        )
    )
    @settings(max_examples=100)
    def test_repos_over_line_limit_excluded(self, repos):
        """Repos exceeding the 5000 line limit are excluded regardless of issue criteria."""
        result = filter_candidates(repos)
        assert len(result) == 0, (
            f"Expected no results for repos over line limit, got {len(result)}"
        )


# Feature: open-source-contribution-workflow, Property 2: Composite Score Sorting and Cap
class TestCompositeScoreSortingAndCap:
    """Property 2: Output is sorted in non-increasing order of composite_score
    and has at most 10 elements.

    Validates: Requirements 1.4
    """

    @given(candidates=st.lists(candidate_repo_strategy(), min_size=0, max_size=30))
    @settings(max_examples=100)
    def test_output_sorted_non_increasing(self, candidates):
        """Assert: output is sorted in non-increasing order of composite_score."""
        ranked = rank_candidates(candidates)

        for i in range(len(ranked) - 1):
            assert ranked[i].composite_score >= ranked[i + 1].composite_score, (
                f"Score at index {i} ({ranked[i].composite_score}) < "
                f"score at index {i+1} ({ranked[i+1].composite_score})"
            )

    @given(candidates=st.lists(candidate_repo_strategy(), min_size=0, max_size=30))
    @settings(max_examples=100)
    def test_output_capped_at_10(self, candidates):
        """Assert: output has at most 10 elements."""
        ranked = rank_candidates(candidates)
        assert len(ranked) <= 10, f"Expected at most 10 results, got {len(ranked)}"

    @given(candidates=st.lists(candidate_repo_strategy(), min_size=11, max_size=20))
    @settings(max_examples=100)
    def test_exactly_10_when_more_candidates(self, candidates):
        """When input has more than 10 candidates, output is exactly 10."""
        ranked = rank_candidates(candidates)
        assert len(ranked) == 10, f"Expected exactly 10 results, got {len(ranked)}"

    @given(candidates=st.lists(candidate_repo_strategy(), min_size=1, max_size=10))
    @settings(max_examples=100)
    def test_preserves_count_when_under_cap(self, candidates):
        """When input has 10 or fewer candidates, all are returned."""
        ranked = rank_candidates(candidates)
        assert len(ranked) == len(candidates), (
            f"Expected {len(candidates)} results, got {len(ranked)}"
        )

    @given(candidates=st.lists(candidate_repo_strategy(), min_size=1, max_size=15))
    @settings(max_examples=100)
    def test_score_is_within_bounds(self, candidates):
        """Composite scores are between 0 and 100."""
        ranked = rank_candidates(candidates)
        for candidate in ranked:
            assert 0 <= candidate.composite_score <= 100, (
                f"Score {candidate.composite_score} out of bounds [0, 100]"
            )


# Feature: open-source-contribution-workflow, Property 3: Candidate Display Completeness
class TestCandidateDisplayCompleteness:
    """Property 3: CandidateRepo.to_dict() includes all required display fields.

    Validates: Requirements 1.5
    """

    @given(candidate=candidate_repo_strategy())
    @settings(max_examples=100)
    def test_to_dict_includes_all_required_fields(self, candidate):
        """Verify CandidateRepo.to_dict() includes all required display fields."""
        display = candidate.to_dict()

        # Required display fields per Requirements 1.5
        required_fields = [
            "full_name",
            "description",
            "stars",
            "last_commit_date",
            "contribution_types",
            "difficulty_level",
        ]

        for field_name in required_fields:
            assert field_name in display, (
                f"Required display field '{field_name}' missing from to_dict() output"
            )

    @given(candidate=candidate_repo_strategy())
    @settings(max_examples=100)
    def test_description_truncated_to_200_chars(self, candidate):
        """Description in display output is truncated to at most 200 characters."""
        display = candidate.to_dict()
        assert len(display["description"]) <= 200, (
            f"Description length {len(display['description'])} exceeds 200 chars"
        )

    @given(candidate=candidate_repo_strategy())
    @settings(max_examples=100)
    def test_display_has_scoring_metadata(self, candidate):
        """Display output includes scoring and metadata fields."""
        display = candidate.to_dict()

        metadata_fields = [
            "open_issues_count",
            "has_contributing_md",
            "main_package_lines",
            "composite_score",
            "good_first_issue_count",
            "dependency_count",
        ]

        for field_name in metadata_fields:
            assert field_name in display, (
                f"Metadata field '{field_name}' missing from to_dict() output"
            )
