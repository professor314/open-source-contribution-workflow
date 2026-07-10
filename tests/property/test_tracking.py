"""Property-based tests for contribution tracking round-trip.

# Feature: open-source-contribution-workflow
# Property 12: Contribution Tracking Round-Trip
"""

from hypothesis import given, settings
from hypothesis import strategies as st

from src.state import add_contribution
from src.models import ContributionTracker, ContributionRecord


# --- Strategies ---

DIFFICULTY_LEVELS = ["easy", "medium", "hard"]

CONTRIBUTION_TYPES = [
    "bug_fix", "documentation", "test_addition",
    "error_handling", "feature_addition", "type_hints",
]

PR_STATUSES = ["open", "merged", "closed"]


def contribution_record_strategy(pr_status=None, difficulty_level=None):
    """Strategy to generate a valid ContributionRecord with random fields."""
    return st.builds(
        ContributionRecord,
        id=st.text(min_size=1, max_size=20, alphabet="abcdefghijklmnopqrstuvwxyz0123456789-"),
        repo_full_name=st.from_regex(r"[a-z]{1,10}/[a-z]{1,10}", fullmatch=True),
        contribution_type=st.sampled_from(CONTRIBUTION_TYPES),
        difficulty_level=st.just(difficulty_level) if difficulty_level else st.sampled_from(DIFFICULTY_LEVELS),
        branch_name=st.text(min_size=5, max_size=30, alphabet="abcdefghijklmnopqrstuvwxyz-/"),
        pr_url=st.from_regex(r"https://github\.com/[a-z]+/[a-z]+/pull/\d+", fullmatch=True),
        pr_number=st.integers(min_value=1, max_value=9999),
        pr_status=st.just(pr_status) if pr_status else st.sampled_from(PR_STATUSES),
        commit_sha=st.text(min_size=7, max_size=40, alphabet="0123456789abcdef"),
        modified_files=st.lists(
            st.text(min_size=3, max_size=30, alphabet="abcdefghijklmnopqrstuvwxyz./"),
            min_size=1, max_size=5,
        ),
        code_snippet=st.text(min_size=0, max_size=100),
        started_at=st.from_regex(r"2025-0[1-9]-[012]\dT[01]\d:[0-5]\d:[0-5]\dZ", fullmatch=True),
        completed_at=st.from_regex(r"2025-0[1-9]-[012]\dT[01]\d:[0-5]\d:[0-5]\dZ", fullmatch=True),
    )


def empty_tracker_strategy():
    """Strategy to generate an empty ContributionTracker."""
    return st.builds(
        ContributionTracker,
        user_level=st.just("beginner"),
        contributions=st.just([]),
        level_counts=st.just({"easy": 0, "medium": 0, "hard": 0}),
        interest_areas=st.lists(st.text(min_size=2, max_size=20, alphabet="abcdefghijklmnopqrstuvwxyz"), min_size=1, max_size=5),
        last_updated=st.just("2025-01-20T14:00:00Z"),
    )


# ============================================================
# Property 12: Contribution Tracking Round-Trip
# Feature: open-source-contribution-workflow, Property 12: Contribution Tracking Round-Trip
# **Validates: Requirements 7.4, 11.3**
# ============================================================

class TestContributionTrackingRoundTrip:
    """Property 12: Contribution Tracking Round-Trip."""

    @settings(max_examples=100)
    @given(record=contribution_record_strategy())
    def test_all_fields_preserved_after_add(self, record):
        """Adding a ContributionRecord and reading back preserves all original fields."""
        tracker = ContributionTracker(
            user_level="beginner",
            contributions=[],
            level_counts={"easy": 0, "medium": 0, "hard": 0},
            interest_areas=["math"],
            last_updated="2025-01-20T14:00:00Z",
        )

        add_contribution(tracker, record)

        # Retrieve the last added contribution
        retrieved = tracker.contributions[-1]

        # Assert all fields are preserved
        assert retrieved.id == record.id, (
            f"id mismatch: expected '{record.id}', got '{retrieved.id}'"
        )
        assert retrieved.repo_full_name == record.repo_full_name, (
            f"repo_full_name mismatch: expected '{record.repo_full_name}', got '{retrieved.repo_full_name}'"
        )
        assert retrieved.contribution_type == record.contribution_type, (
            f"contribution_type mismatch: expected '{record.contribution_type}', got '{retrieved.contribution_type}'"
        )
        assert retrieved.difficulty_level == record.difficulty_level, (
            f"difficulty_level mismatch: expected '{record.difficulty_level}', got '{retrieved.difficulty_level}'"
        )
        assert retrieved.branch_name == record.branch_name, (
            f"branch_name mismatch: expected '{record.branch_name}', got '{retrieved.branch_name}'"
        )
        assert retrieved.pr_url == record.pr_url, (
            f"pr_url mismatch: expected '{record.pr_url}', got '{retrieved.pr_url}'"
        )
        assert retrieved.pr_number == record.pr_number, (
            f"pr_number mismatch: expected {record.pr_number}, got {retrieved.pr_number}"
        )
        assert retrieved.pr_status == record.pr_status, (
            f"pr_status mismatch: expected '{record.pr_status}', got '{retrieved.pr_status}'"
        )
        assert retrieved.commit_sha == record.commit_sha, (
            f"commit_sha mismatch: expected '{record.commit_sha}', got '{retrieved.commit_sha}'"
        )
        assert retrieved.modified_files == record.modified_files, (
            f"modified_files mismatch: expected {record.modified_files}, got {retrieved.modified_files}"
        )
        assert retrieved.code_snippet == record.code_snippet, (
            f"code_snippet mismatch: expected '{record.code_snippet}', got '{retrieved.code_snippet}'"
        )
        assert retrieved.started_at == record.started_at, (
            f"started_at mismatch: expected '{record.started_at}', got '{retrieved.started_at}'"
        )
        assert retrieved.completed_at == record.completed_at, (
            f"completed_at mismatch: expected '{record.completed_at}', got '{retrieved.completed_at}'"
        )

    @settings(max_examples=100)
    @given(
        difficulty=st.sampled_from(DIFFICULTY_LEVELS),
        data=st.data(),
    )
    def test_pr_merge_increments_level_count_by_one(self, difficulty, data):
        """When a PR merge event is recorded, the level_count for that difficulty increases by exactly 1."""
        # Create a tracker with some existing contributions (0-5 existing records)
        existing_count = data.draw(st.integers(min_value=0, max_value=5))
        existing_records = []
        for i in range(existing_count):
            rec = data.draw(contribution_record_strategy())
            existing_records.append(rec)

        tracker = ContributionTracker(
            user_level="beginner",
            contributions=[],
            level_counts={"easy": 0, "medium": 0, "hard": 0},
            interest_areas=["math"],
            last_updated="2025-01-20T14:00:00Z",
        )

        # Add existing records to build initial state
        for rec in existing_records:
            add_contribution(tracker, rec)

        # Capture current level count for the target difficulty
        count_before = tracker.level_counts[difficulty]

        # Generate a new merged record at the target difficulty
        new_record = data.draw(contribution_record_strategy(
            pr_status="merged",
            difficulty_level=difficulty,
        ))

        add_contribution(tracker, new_record)

        # Assert: level count increased by exactly 1
        count_after = tracker.level_counts[difficulty]
        assert count_after == count_before + 1, (
            f"Expected level_counts['{difficulty}'] to increase from {count_before} "
            f"to {count_before + 1}, but got {count_after}"
        )
