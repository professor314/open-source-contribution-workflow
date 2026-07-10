"""Property-based tests for progression, license detection, contributing summary, and linter detection.

# Feature: open-source-contribution-workflow
# Properties 5, 6, 11, 19
"""

from hypothesis import given, settings, assume
from hypothesis import strategies as st

from src.license_detection import detect_license
from src.contributing_summary import summarize_contributing
from src.progression import recommend_next_difficulty
from src.linter_detection import detect_linter_config
from src.models import ContributionTracker, ContributionRecord


# --- Strategies ---

# Known license identifiers and their corresponding text markers
LICENSE_MARKERS = {
    "MIT": "MIT License\n\nPermission is hereby granted, free of charge",
    "Apache-2.0": "Apache License\nVersion 2.0, January 2004",
    "GPL-3.0": "GNU GENERAL PUBLIC LICENSE\nVersion 3, 29 June 2007",
    "BSD-2-Clause": "BSD 2-Clause License\n\nRedistribution and use in source and binary forms",
    "BSD-3-Clause": "BSD 3-Clause License\n\nRedistribution and use in source and binary forms, with or without modification, are permitted provided that neither the name of the copyright holder nor the names of its contributors may be used to endorse or promote products",
    "ISC": "ISC License\n\nPermission to use, copy, modify",
    "MPL-2.0": "Mozilla Public License\nVersion 2.0",
}

DIFFICULTY_LEVELS = ["easy", "medium", "hard"]

CONTRIBUTION_TYPES = [
    "bug_fix", "documentation", "test_addition",
    "error_handling", "feature_addition", "type_hints",
]


def contribution_record_strategy(difficulty_level=None, contribution_type=None):
    """Strategy to generate a valid ContributionRecord."""
    return st.builds(
        ContributionRecord,
        id=st.text(min_size=1, max_size=20, alphabet="abcdefghijklmnopqrstuvwxyz0123456789-"),
        repo_full_name=st.from_regex(r"[a-z]{1,10}/[a-z]{1,10}", fullmatch=True),
        contribution_type=st.just(contribution_type) if contribution_type else st.sampled_from(CONTRIBUTION_TYPES),
        difficulty_level=st.just(difficulty_level) if difficulty_level else st.sampled_from(DIFFICULTY_LEVELS),
        branch_name=st.text(min_size=5, max_size=30, alphabet="abcdefghijklmnopqrstuvwxyz-/"),
        pr_url=st.from_regex(r"https://github\.com/[a-z]+/[a-z]+/pull/\d+", fullmatch=True),
        pr_number=st.integers(min_value=1, max_value=9999),
        pr_status=st.sampled_from(["open", "merged", "closed"]),
        commit_sha=st.text(min_size=7, max_size=40, alphabet="0123456789abcdef"),
        modified_files=st.lists(st.text(min_size=3, max_size=30, alphabet="abcdefghijklmnopqrstuvwxyz./"), min_size=1, max_size=5),
        code_snippet=st.text(min_size=0, max_size=100),
        started_at=st.just("2025-01-20T14:00:00Z"),
        completed_at=st.just("2025-01-20T15:00:00Z"),
    )


def tracker_strategy(level, count):
    """Build a tracker with a specific number of contributions at a given level."""
    records = st.lists(
        contribution_record_strategy(difficulty_level=level),
        min_size=count,
        max_size=count,
    )
    return records.map(lambda recs: ContributionTracker(
        user_level="beginner",
        contributions=recs,
        level_counts={
            "easy": count if level == "easy" else 0,
            "medium": count if level == "medium" else 0,
            "hard": count if level == "hard" else 0,
        },
        interest_areas=["math"],
        last_updated="2025-01-20T14:00:00Z",
    ))


# ============================================================
# Property 5: License Detection Accuracy
# Feature: open-source-contribution-workflow, Property 5: License Detection Accuracy
# **Validates: Requirements 2.5**
# ============================================================

class TestLicenseDetectionAccuracy:
    """Property 5: License Detection Accuracy."""

    @settings(max_examples=100)
    @given(license_key=st.sampled_from(list(LICENSE_MARKERS.keys())),
           prefix=st.text(min_size=0, max_size=50, alphabet="abcdefghijklmnopqrstuvwxyz \n"),
           suffix=st.text(min_size=0, max_size=50, alphabet="abcdefghijklmnopqrstuvwxyz \n"))
    def test_known_licenses_detected_correctly(self, license_key, prefix, suffix):
        """Known license identifiers are detected with license_verified=True."""
        license_text = prefix + LICENSE_MARKERS[license_key] + suffix
        result = detect_license(license_text)
        assert result["license_verified"] is True, (
            f"Expected license_verified=True for {license_key}, got False"
        )
        assert result["license_identifier"] == license_key, (
            f"Expected identifier '{license_key}', got '{result['license_identifier']}'"
        )

    @settings(max_examples=100)
    @given(text=st.text(min_size=0, max_size=500, alphabet="xyz0123456789 \n\t"))
    def test_unknown_text_not_verified(self, text):
        """Random text that doesn't contain license phrases returns license_verified=False."""
        # Ensure the text doesn't accidentally contain any license markers
        for marker_text in LICENSE_MARKERS.values():
            assume(marker_text[:30] not in text)
        assume("MIT License" not in text)
        assume("Permission is hereby granted" not in text)
        assume("Apache License" not in text)
        assume("GNU GENERAL PUBLIC LICENSE" not in text)
        assume("Mozilla Public License" not in text)
        assume("BSD" not in text)
        assume("Redistribution and use" not in text)
        assume("ISC License" not in text)
        assume("Permission to use, copy, modify" not in text)

        result = detect_license(text)
        assert result["license_verified"] is False, (
            f"Expected license_verified=False for unknown text, got True with "
            f"identifier='{result['license_identifier']}'"
        )


# ============================================================
# Property 6: Contributing Summary Word Count
# Feature: open-source-contribution-workflow, Property 6: Contributing Summary Word Count
# **Validates: Requirements 2.7**
# ============================================================

class TestContributingSummaryWordCount:
    """Property 6: Contributing Summary Word Count."""

    @settings(max_examples=100)
    @given(text=st.text(min_size=0, max_size=5000))
    def test_summary_at_most_200_words(self, text):
        """Output of summarize_contributing() has at most 200 words."""
        summary = summarize_contributing(text)
        word_count = len(summary.split())
        assert word_count <= 200, (
            f"Summary has {word_count} words, expected ≤200. "
            f"Summary: '{summary[:100]}...'"
        )


# ============================================================
# Property 11: Difficulty Progression Logic
# Feature: open-source-contribution-workflow, Property 11: Difficulty Progression Logic
# **Validates: Requirements 7.2, 7.3**
# ============================================================

class TestDifficultyProgressionLogic:
    """Property 11: Difficulty Progression Logic."""

    @settings(max_examples=100)
    @given(data=st.data())
    def test_no_contributions_recommends_easy(self, data):
        """When no contributions exist, recommended level is 'easy'."""
        tracker = ContributionTracker(
            user_level="beginner",
            contributions=[],
            level_counts={"easy": 0, "medium": 0, "hard": 0},
            interest_areas=data.draw(st.lists(st.text(min_size=2, max_size=20), min_size=1, max_size=3)),
            last_updated="2025-01-20T14:00:00Z",
        )
        result = recommend_next_difficulty(tracker)
        assert result["recommended_level"] == "easy", (
            f"Expected 'easy' for empty tracker, got '{result['recommended_level']}'"
        )

    @settings(max_examples=100)
    @given(
        level=st.sampled_from(DIFFICULTY_LEVELS),
        count=st.integers(min_value=1, max_value=1),
    )
    def test_below_threshold_stays_at_current_level(self, level, count):
        """When level_counts[current_level] < 2, recommended stays at current level."""
        # Generate contributions at the specified level
        records = []
        for i in range(count):
            records.append(ContributionRecord(
                id=f"contrib-{i}",
                repo_full_name="owner/repo",
                contribution_type="bug_fix",
                difficulty_level=level,
                branch_name="fix/test",
                pr_url="https://github.com/owner/repo/pull/1",
                pr_number=1,
                pr_status="merged",
                commit_sha="abc1234",
                modified_files=["src/main.py"],
                code_snippet="",
                started_at="2025-01-20T14:00:00Z",
                completed_at="2025-01-20T15:00:00Z",
            ))

        tracker = ContributionTracker(
            user_level="beginner",
            contributions=records,
            level_counts={
                "easy": count if level == "easy" else 0,
                "medium": count if level == "medium" else 0,
                "hard": count if level == "hard" else 0,
            },
            interest_areas=["math"],
            last_updated="2025-01-20T14:00:00Z",
        )

        result = recommend_next_difficulty(tracker)
        assert result["recommended_level"] == level, (
            f"Expected '{level}' (below threshold), got '{result['recommended_level']}'"
        )

    @settings(max_examples=100)
    @given(
        level=st.sampled_from(DIFFICULTY_LEVELS),
        count=st.integers(min_value=2, max_value=10),
    )
    def test_at_or_above_threshold_promotes_to_next(self, level, count):
        """When level_counts[current_level] >= 2, recommended is next higher (or same if hard)."""
        records = []
        for i in range(count):
            records.append(ContributionRecord(
                id=f"contrib-{i}",
                repo_full_name="owner/repo",
                contribution_type="test_addition",
                difficulty_level=level,
                branch_name="test/add-tests",
                pr_url="https://github.com/owner/repo/pull/1",
                pr_number=1,
                pr_status="merged",
                commit_sha="abc1234",
                modified_files=["tests/test_main.py"],
                code_snippet="",
                started_at="2025-01-20T14:00:00Z",
                completed_at="2025-01-20T15:00:00Z",
            ))

        tracker = ContributionTracker(
            user_level="beginner",
            contributions=records,
            level_counts={
                "easy": count if level == "easy" else 0,
                "medium": count if level == "medium" else 0,
                "hard": count if level == "hard" else 0,
            },
            interest_areas=["math"],
            last_updated="2025-01-20T14:00:00Z",
        )

        result = recommend_next_difficulty(tracker)

        level_index = DIFFICULTY_LEVELS.index(level)
        if level == "hard":
            expected = "hard"
        else:
            expected = DIFFICULTY_LEVELS[level_index + 1]

        assert result["recommended_level"] == expected, (
            f"Expected '{expected}' (at/above threshold for {level}), "
            f"got '{result['recommended_level']}'"
        )


# ============================================================
# Property 19: Linter Config Detection
# Feature: open-source-contribution-workflow, Property 19: Linter Config Detection
# **Validates: Requirements 5.3**
# ============================================================

class TestLinterConfigDetection:
    """Property 19: Linter Config Detection."""

    @settings(max_examples=100)
    @given(
        has_black=st.booleans(),
        has_ruff=st.booleans(),
        has_flake8_in_setup=st.booleans(),
        has_flake8_file=st.booleans(),
        has_pylintrc=st.booleans(),
    )
    def test_correct_tools_detected_for_config_combinations(
        self, has_black, has_ruff, has_flake8_in_setup, has_flake8_file, has_pylintrc
    ):
        """Correct tool name returned for each config file pattern present."""
        file_list = []
        file_contents = {}

        # Build pyproject.toml content
        if has_black or has_ruff:
            file_list.append("pyproject.toml")
            content_parts = ["[project]\nname = \"mypackage\"\n"]
            if has_black:
                content_parts.append("[tool.black]\nline-length = 88\n")
            if has_ruff:
                content_parts.append("[tool.ruff]\nline-length = 88\n")
            file_contents["pyproject.toml"] = "\n".join(content_parts)

        # Build setup.cfg content
        if has_flake8_in_setup:
            file_list.append("setup.cfg")
            file_contents["setup.cfg"] = "[flake8]\nmax-line-length = 88\n"

        # .flake8 file existence
        if has_flake8_file:
            file_list.append(".flake8")

        # .pylintrc file existence
        if has_pylintrc:
            file_list.append(".pylintrc")

        results = detect_linter_config(file_list, file_contents)
        detected_tools = [(r["tool"], r["config_file"]) for r in results]

        # Verify expected tools
        if has_black:
            assert ("black", "pyproject.toml") in detected_tools, (
                f"Expected black in results, got {detected_tools}"
            )
        if has_ruff:
            assert ("ruff", "pyproject.toml") in detected_tools, (
                f"Expected ruff in results, got {detected_tools}"
            )
        if has_flake8_in_setup:
            assert ("flake8", "setup.cfg") in detected_tools, (
                f"Expected flake8 (setup.cfg) in results, got {detected_tools}"
            )
        if has_flake8_file:
            assert ("flake8", ".flake8") in detected_tools, (
                f"Expected flake8 (.flake8) in results, got {detected_tools}"
            )
        if has_pylintrc:
            assert ("pylint", ".pylintrc") in detected_tools, (
                f"Expected pylint in results, got {detected_tools}"
            )

    @settings(max_examples=100)
    @given(
        file_list=st.lists(
            st.text(min_size=3, max_size=20, alphabet="abcdefghijklmnopqrstuvwxyz_"),
            min_size=0,
            max_size=10,
        )
    )
    def test_empty_result_when_no_known_configs(self, file_list):
        """Returns empty result when no linter config files are found."""
        # Ensure no known config files are in the list
        known_configs = {"pyproject.toml", "setup.cfg", ".flake8", ".pylintrc"}
        assume(not any(f in known_configs for f in file_list))

        results = detect_linter_config(file_list, {})
        assert results == [], (
            f"Expected empty result for file list {file_list}, got {results}"
        )
