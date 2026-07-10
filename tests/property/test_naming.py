"""Property-based tests for naming, commit formatting, and PR title generation.

# Feature: open-source-contribution-workflow, Property 7: Branch Name Format and Length
# Feature: open-source-contribution-workflow, Property 8: Commit Message Round-Trip
# Feature: open-source-contribution-workflow, Property 9: PR Title Format and Length
"""

import re

from hypothesis import given, settings, assume
from hypothesis import strategies as st

from src.naming import (
    generate_branch_name,
    validate_branch_name,
    VALID_CONTRIBUTION_TYPES,
)
from src.commit_format import (
    generate_commit_message,
    validate_commit_message,
    VALID_COMMIT_TYPES,
    MAX_SUBJECT_LINE_LENGTH,
)
from src.pr_format import (
    generate_pr_title,
    VALID_PR_TYPES,
    MAX_PR_TITLE_LENGTH,
)


# --- Strategies ---

branch_contribution_types = st.sampled_from(VALID_CONTRIBUTION_TYPES)

# Descriptions: ASCII alphanumeric + spaces, at least one ASCII alphanumeric char
branch_descriptions = st.text(
    alphabet=st.sampled_from(
        "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789 "
    ),
    min_size=1,
    max_size=60,
).filter(lambda s: any(c.isascii() and c.isalnum() for c in s))

commit_types = st.sampled_from(VALID_COMMIT_TYPES)

# Short subjects for commit messages: printable text, 1-50 chars
commit_subjects = st.text(
    alphabet=st.characters(whitelist_categories=("L", "N", "P", "Z"), whitelist_characters=" -_"),
    min_size=1,
    max_size=50,
).filter(lambda s: s.strip())

# Optional scope: alphanumeric + hyphens/dots/underscores
commit_scopes = st.one_of(
    st.none(),
    st.text(
        alphabet=st.characters(whitelist_categories=("Ll", "Nd"), whitelist_characters="-._/"),
        min_size=1,
        max_size=20,
    ).filter(lambda s: re.match(r"^[a-zA-Z0-9_\-./]+$", s)),
)

pr_contribution_types = st.sampled_from(VALID_PR_TYPES)

pr_descriptions = st.text(
    alphabet=st.characters(whitelist_categories=("L", "N", "P", "Z"), whitelist_characters=" -_"),
    min_size=1,
    max_size=80,
).filter(lambda s: s.strip())


# --- Property 7: Branch Name Format and Length ---
# **Validates: Requirements 4.4**


class TestBranchNameFormatAndLength:
    """Property 7: Branch Name Format and Length.

    For any valid contribution type and description (alphanumeric + spaces),
    the branch name generator produces output that:
    - Matches the pattern ^[a-z]+/[a-z0-9-]+$
    - Is at most 50 characters long
    - Passes validate_branch_name()
    """

    @given(
        contribution_type=branch_contribution_types,
        description=branch_descriptions,
    )
    @settings(max_examples=100)
    def test_branch_name_matches_pattern(self, contribution_type, description):
        """Generated branch names match the required pattern."""
        result = generate_branch_name(contribution_type, description)

        assert re.match(r"^[a-z]+/[a-z0-9-]+$", result), (
            f"Branch name '{result}' does not match pattern ^[a-z]+/[a-z0-9-]+$"
        )

    @given(
        contribution_type=branch_contribution_types,
        description=branch_descriptions,
    )
    @settings(max_examples=100)
    def test_branch_name_length_within_limit(self, contribution_type, description):
        """Generated branch names are at most 50 characters."""
        result = generate_branch_name(contribution_type, description)

        assert len(result) <= 50, (
            f"Branch name '{result}' is {len(result)} chars, exceeds 50"
        )

    @given(
        contribution_type=branch_contribution_types,
        description=branch_descriptions,
    )
    @settings(max_examples=100)
    def test_branch_name_passes_validator(self, contribution_type, description):
        """Generated branch names pass validate_branch_name()."""
        result = generate_branch_name(contribution_type, description)

        assert validate_branch_name(result) is True, (
            f"validate_branch_name('{result}') returned False"
        )


# --- Property 8: Commit Message Round-Trip ---
# **Validates: Requirements 5.7, 9.3**


class TestCommitMessageRoundTrip:
    """Property 8: Commit Message Round-Trip.

    - Generated commit messages always pass the validator.
    - Invalid strings (no colon, wrong type, too long subject) fail the validator.
    """

    @given(
        commit_type=commit_types,
        subject=commit_subjects,
        scope=commit_scopes,
    )
    @settings(max_examples=100)
    def test_generated_messages_pass_validator(self, commit_type, subject, scope):
        """Commit messages produced by the generator always pass validation."""
        message = generate_commit_message(commit_type, subject, scope=scope)

        assert validate_commit_message(message) is True, (
            f"Generated message failed validation: '{message}'"
        )

    @given(
        text=st.text(min_size=1, max_size=100).filter(
            lambda s: ":" not in s and s.strip()
        ),
    )
    @settings(max_examples=100)
    def test_strings_without_colon_fail_validator(self, text):
        """Strings without a colon separator are rejected by the validator."""
        assert validate_commit_message(text) is False, (
            f"Validator accepted invalid message (no colon): '{text}'"
        )

    @given(
        fake_type=st.text(
            alphabet=st.characters(whitelist_categories=("Ll",)),
            min_size=2,
            max_size=10,
        ).filter(lambda s: s not in VALID_COMMIT_TYPES),
        subject=commit_subjects,
    )
    @settings(max_examples=100)
    def test_wrong_type_fails_validator(self, fake_type, subject):
        """Messages with an invalid type prefix are rejected."""
        invalid_message = f"{fake_type}: {subject}"

        assert validate_commit_message(invalid_message) is False, (
            f"Validator accepted message with invalid type: '{invalid_message}'"
        )

    @given(
        commit_type=commit_types,
        long_subject=st.text(
            alphabet=st.characters(whitelist_categories=("Ll", "Nd"), whitelist_characters=" "),
            min_size=70,
            max_size=120,
        ),
    )
    @settings(max_examples=100)
    def test_too_long_subject_fails_validator(self, commit_type, long_subject):
        """Messages whose first line exceeds 72 chars are rejected."""
        # Manually construct a message that exceeds the limit
        message = f"{commit_type}: {long_subject}"
        assume(len(message) > MAX_SUBJECT_LINE_LENGTH)

        assert validate_commit_message(message) is False, (
            f"Validator accepted message exceeding 72 chars: '{message}' ({len(message)} chars)"
        )


# --- Property 9: PR Title Format and Length ---
# **Validates: Requirements 6.1**


class TestPrTitleFormatAndLength:
    """Property 9: PR Title Format and Length.

    For any valid contribution type and description, the PR title generator
    produces output that:
    - Matches the format '<type>: <desc>'
    - Is at most 72 characters long
    """

    @given(
        contribution_type=pr_contribution_types,
        description=pr_descriptions,
    )
    @settings(max_examples=100)
    def test_pr_title_matches_format(self, contribution_type, description):
        """Generated PR titles match the '<type>: <description>' format."""
        result = generate_pr_title(contribution_type, description)

        # Should contain exactly one ": " separating type from description
        assert ": " in result, (
            f"PR title '{result}' does not contain ': ' separator"
        )
        parts = result.split(": ", 1)
        assert parts[0] in VALID_PR_TYPES, (
            f"PR title type '{parts[0]}' is not a valid PR type"
        )

    @given(
        contribution_type=pr_contribution_types,
        description=pr_descriptions,
    )
    @settings(max_examples=100)
    def test_pr_title_length_within_limit(self, contribution_type, description):
        """Generated PR titles are at most 72 characters."""
        result = generate_pr_title(contribution_type, description)

        assert len(result) <= MAX_PR_TITLE_LENGTH, (
            f"PR title '{result}' is {len(result)} chars, exceeds 72"
        )
