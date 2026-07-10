"""Unit tests for src.state module.

Tests cover loading, saving, schema validation, and contribution tracking.
"""

import json

import pytest

from src.models import ContributionRecord, ContributionTracker
from src.state import add_contribution, load_tracker, save_tracker, validate_tracker_schema


def _make_valid_tracker_data(contributions=None):
    """Helper to build valid tracker JSON data."""
    return {
        "user_level": "beginner",
        "contributions": contributions or [],
        "level_counts": {"easy": 0, "medium": 0, "hard": 0},
        "interest_areas": ["math", "statistics"],
        "last_updated": "2025-01-20T14:00:00Z",
    }


def _make_contribution_dict(**overrides):
    """Helper to build a valid contribution record dict."""
    base = {
        "id": "contrib-001",
        "repo_full_name": "owner/repo-name",
        "contribution_type": "bug_fix",
        "difficulty_level": "easy",
        "branch_name": "fix/add-input-validation",
        "pr_url": "https://github.com/owner/repo-name/pull/42",
        "pr_number": 42,
        "pr_status": "open",
        "commit_sha": "abc1234",
        "modified_files": ["src/validator.py"],
        "code_snippet": "def validate(): pass",
        "started_at": "2025-01-20T14:30:00Z",
        "completed_at": "2025-01-20T15:00:00Z",
    }
    base.update(overrides)
    return base


class TestLoadTracker:
    """Tests for loading tracker from JSON files."""

    def test_load_tracker_empty(self, tmp_path):
        """Load tracker with empty contributions list, verify structure."""
        data = _make_valid_tracker_data()
        tracker_file = tmp_path / "tracker.json"
        tracker_file.write_text(json.dumps(data), encoding="utf-8")

        tracker = load_tracker(str(tracker_file))

        assert isinstance(tracker, ContributionTracker)
        assert tracker.user_level == "beginner"
        assert tracker.contributions == []
        assert tracker.level_counts == {"easy": 0, "medium": 0, "hard": 0}
        assert tracker.interest_areas == ["math", "statistics"]
        assert tracker.last_updated == "2025-01-20T14:00:00Z"

    def test_load_tracker_with_contributions(self, tmp_path):
        """Load tracker with populated contribution data."""
        contrib = _make_contribution_dict()
        data = _make_valid_tracker_data(contributions=[contrib])
        data["level_counts"]["easy"] = 1
        tracker_file = tmp_path / "tracker.json"
        tracker_file.write_text(json.dumps(data), encoding="utf-8")

        tracker = load_tracker(str(tracker_file))

        assert len(tracker.contributions) == 1
        record = tracker.contributions[0]
        assert record.id == "contrib-001"
        assert record.repo_full_name == "owner/repo-name"
        assert record.contribution_type == "bug_fix"
        assert record.difficulty_level == "easy"
        assert record.pr_number == 42
        assert record.pr_status == "open"
        assert record.modified_files == ["src/validator.py"]


class TestSaveAndReload:
    """Tests for save/reload round-trip."""

    def test_save_and_reload_roundtrip(self, tmp_path):
        """Save a tracker, reload it, verify all fields preserved."""
        tracker = ContributionTracker(
            user_level="intermediate",
            contributions=[
                ContributionRecord(
                    id="contrib-002",
                    repo_full_name="user/project",
                    contribution_type="test_addition",
                    difficulty_level="medium",
                    branch_name="test/add-unit-tests",
                    pr_url="https://github.com/user/project/pull/7",
                    pr_number=7,
                    pr_status="merged",
                    commit_sha="def5678",
                    modified_files=["tests/test_main.py", "tests/conftest.py"],
                    code_snippet="def test_example(): assert True",
                    started_at="2025-02-01T10:00:00Z",
                    completed_at="2025-02-01T10:30:00Z",
                )
            ],
            level_counts={"easy": 2, "medium": 1, "hard": 0},
            interest_areas=["web scraping", "CLI tools"],
            last_updated="2025-02-01T10:30:00Z",
        )

        tracker_file = tmp_path / "tracker.json"
        save_tracker(tracker, str(tracker_file))

        reloaded = load_tracker(str(tracker_file))

        assert reloaded.user_level == "intermediate"
        assert reloaded.interest_areas == ["web scraping", "CLI tools"]
        assert reloaded.level_counts == {"easy": 2, "medium": 1, "hard": 0}
        assert len(reloaded.contributions) == 1

        record = reloaded.contributions[0]
        assert record.id == "contrib-002"
        assert record.repo_full_name == "user/project"
        assert record.contribution_type == "test_addition"
        assert record.difficulty_level == "medium"
        assert record.branch_name == "test/add-unit-tests"
        assert record.pr_url == "https://github.com/user/project/pull/7"
        assert record.pr_number == 7
        assert record.pr_status == "merged"
        assert record.commit_sha == "def5678"
        assert record.modified_files == ["tests/test_main.py", "tests/conftest.py"]
        assert record.code_snippet == "def test_example(): assert True"
        assert record.started_at == "2025-02-01T10:00:00Z"
        assert record.completed_at == "2025-02-01T10:30:00Z"


class TestAddContribution:
    """Tests for adding contributions and updating counts."""

    def test_add_contribution_updates_counts(self):
        """Add a contribution and verify level_counts incremented."""
        tracker = ContributionTracker(
            user_level="beginner",
            contributions=[],
            level_counts={"easy": 0, "medium": 0, "hard": 0},
            interest_areas=["math"],
            last_updated="2025-01-20T14:00:00Z",
        )

        record = ContributionRecord(
            id="contrib-001",
            repo_full_name="owner/repo",
            contribution_type="bug_fix",
            difficulty_level="easy",
            branch_name="fix/bug",
            pr_url="https://github.com/owner/repo/pull/1",
            pr_number=1,
            pr_status="open",
            commit_sha="aaa1111",
            modified_files=["src/main.py"],
            code_snippet="pass",
            started_at="2025-01-20T15:00:00Z",
            completed_at="2025-01-20T15:30:00Z",
        )

        updated = add_contribution(tracker, record)

        assert len(updated.contributions) == 1
        assert updated.level_counts["easy"] == 1
        assert updated.level_counts["medium"] == 0
        assert updated.level_counts["hard"] == 0


class TestSchemaValidation:
    """Tests for validate_tracker_schema."""

    def test_schema_validation_rejects_missing_keys(self):
        """Malformed JSON with missing keys returns False."""
        # Missing 'level_counts' key
        data = {
            "user_level": "beginner",
            "contributions": [],
            "interest_areas": ["math"],
            "last_updated": "2025-01-20T14:00:00Z",
        }
        assert validate_tracker_schema(data) is False

    def test_schema_validation_rejects_wrong_types(self):
        """JSON with wrong types returns False."""
        data = {
            "user_level": "beginner",
            "contributions": "not a list",  # should be list
            "level_counts": {"easy": 0, "medium": 0, "hard": 0},
            "interest_areas": ["math"],
            "last_updated": "2025-01-20T14:00:00Z",
        }
        assert validate_tracker_schema(data) is False

    def test_schema_validation_rejects_invalid_user_level(self):
        """user_level 'expert' returns False."""
        data = _make_valid_tracker_data()
        data["user_level"] = "expert"
        assert validate_tracker_schema(data) is False

    def test_schema_validation_accepts_valid_data(self):
        """Well-formed data returns True."""
        data = _make_valid_tracker_data()
        assert validate_tracker_schema(data) is True
