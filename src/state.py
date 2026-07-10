"""JSON state management for the contribution tracker.

Provides functions to load, save, validate, and update the contribution
tracker state file.
"""

from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from typing import Any, Dict

from src.models import ContributionRecord, ContributionTracker


# Required top-level keys and their expected types for schema validation
_TRACKER_SCHEMA = {
    "user_level": str,
    "contributions": list,
    "level_counts": dict,
    "interest_areas": list,
    "last_updated": str,
}

# Required keys in level_counts
_LEVEL_COUNTS_KEYS = {"easy", "medium", "hard"}

# Required keys for each contribution record
_CONTRIBUTION_RECORD_KEYS = {
    "id": str,
    "repo_full_name": str,
    "contribution_type": str,
    "difficulty_level": str,
    "branch_name": str,
    "pr_url": str,
    "pr_number": int,
    "pr_status": str,
    "commit_sha": str,
    "modified_files": list,
    "code_snippet": str,
    "started_at": str,
    "completed_at": str,
}


def validate_tracker_schema(data: Dict[str, Any]) -> bool:
    """Check that the given dictionary matches the expected tracker schema.

    Validates:
    - All required top-level keys are present with correct types
    - level_counts contains easy, medium, hard keys with int values
    - Each contribution record has required keys with correct types

    Args:
        data: Dictionary to validate against the tracker schema.

    Returns:
        True if the data matches the expected schema, False otherwise.
    """
    # Check top-level keys and types
    for key, expected_type in _TRACKER_SCHEMA.items():
        if key not in data:
            return False
        if not isinstance(data[key], expected_type):
            return False

    # Validate user_level is one of the allowed values
    if data["user_level"] not in ("beginner", "intermediate", "advanced"):
        return False

    # Validate level_counts structure
    level_counts = data["level_counts"]
    if set(level_counts.keys()) != _LEVEL_COUNTS_KEYS:
        return False
    for value in level_counts.values():
        if not isinstance(value, int):
            return False

    # Validate each contribution record
    for record in data["contributions"]:
        if not isinstance(record, dict):
            return False
        for key, expected_type in _CONTRIBUTION_RECORD_KEYS.items():
            if key not in record:
                return False
            if not isinstance(record[key], expected_type):
                return False
        # Validate pr_status
        if record["pr_status"] not in ("open", "merged", "closed"):
            return False

    # Validate interest_areas contains only strings
    for area in data["interest_areas"]:
        if not isinstance(area, str):
            return False

    return True


def load_tracker(path: str) -> ContributionTracker:
    """Load contribution tracker from a JSON file.

    Reads the file, validates the schema, and returns a ContributionTracker
    dataclass instance.

    Args:
        path: Path to the tracker JSON file.

    Returns:
        A ContributionTracker instance populated from the file.

    Raises:
        FileNotFoundError: If the file does not exist.
        ValueError: If the JSON is invalid or does not match the schema.
    """
    if not os.path.exists(path):
        raise FileNotFoundError(f"Tracker file not found: {path}")

    with open(path, "r", encoding="utf-8") as f:
        try:
            data = json.load(f)
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON in tracker file: {e}")

    if not isinstance(data, dict):
        raise ValueError("Tracker file must contain a JSON object")

    if not validate_tracker_schema(data):
        raise ValueError("Tracker file does not match expected schema")

    return ContributionTracker.from_dict(data)


def save_tracker(tracker: ContributionTracker, path: str) -> None:
    """Serialize and save the contribution tracker to a JSON file.

    Updates the last_updated timestamp before saving.

    Args:
        tracker: The ContributionTracker instance to save.
        path: Path where the JSON file should be written.
    """
    tracker.last_updated = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    data = tracker.to_dict()

    # Ensure the directory exists
    directory = os.path.dirname(path)
    if directory:
        os.makedirs(directory, exist_ok=True)

    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
        f.write("\n")


def add_contribution(
    tracker: ContributionTracker, record: ContributionRecord
) -> ContributionTracker:
    """Add a contribution record to the tracker and update level counts.

    Appends the record to the contributions list and increments the
    appropriate level count based on the record's difficulty_level.

    Args:
        tracker: The current ContributionTracker state.
        record: The ContributionRecord to add.

    Returns:
        The updated ContributionTracker with the new record added.
    """
    tracker.contributions.append(record)
    _update_level_counts(tracker)
    return tracker


def _update_level_counts(tracker: ContributionTracker) -> None:
    """Recalculate level counts from the contributions list.

    Counts contributions that are merged or have been submitted (any status),
    grouped by difficulty_level.

    Args:
        tracker: The tracker whose level_counts to recalculate.
    """
    counts = {"easy": 0, "medium": 0, "hard": 0}
    for contribution in tracker.contributions:
        level = contribution.difficulty_level
        if level in counts:
            counts[level] += 1
    tracker.level_counts = counts
