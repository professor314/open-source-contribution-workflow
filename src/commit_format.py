"""Commit message generator and validator using Conventional Commits format.

Provides functions to generate well-formatted commit messages and validate
that existing messages conform to the conventional commit specification.

Valid commit types: fix, feat, docs, test, refactor, style, chore, perf, ci, build
"""

from __future__ import annotations

import re
from typing import Optional


VALID_COMMIT_TYPES: list[str] = [
    "fix",
    "feat",
    "docs",
    "test",
    "refactor",
    "style",
    "chore",
    "perf",
    "ci",
    "build",
]

# Pattern: type(optional-scope): subject
_CONVENTIONAL_COMMIT_PATTERN: re.Pattern[str] = re.compile(
    r"^(?P<type>" + "|".join(VALID_COMMIT_TYPES) + r")"
    r"(?:\((?P<scope>[a-zA-Z0-9_\-./]+)\))?"
    r": (?P<subject>.+)$"
)

MAX_SUBJECT_LINE_LENGTH: int = 72


def generate_commit_message(
    commit_type: str,
    subject: str,
    scope: Optional[str] = None,
    body: Optional[str] = None,
) -> str:
    """Generate a conventional commit message.

    Produces a message in the format:
        type(scope): subject
    or:
        type: subject

    The subject line (first line) is guaranteed to be at most 72 characters.
    If the subject would exceed the limit, it is truncated to fit.

    Args:
        commit_type: The type of commit (fix, feat, docs, etc.).
        subject: A concise description of the change.
        scope: Optional scope of the change (e.g., module name).
        body: Optional longer description, added after a blank line.

    Returns:
        A formatted commit message string.

    Raises:
        ValueError: If commit_type is not one of the valid types.
    """
    if commit_type not in VALID_COMMIT_TYPES:
        raise ValueError(
            f"Invalid commit type '{commit_type}'. "
            f"Must be one of: {', '.join(VALID_COMMIT_TYPES)}"
        )

    # Build the prefix: "type(scope): " or "type: "
    if scope:
        prefix = f"{commit_type}({scope}): "
    else:
        prefix = f"{commit_type}: "

    # Calculate available space for the subject text
    available_length = MAX_SUBJECT_LINE_LENGTH - len(prefix)

    # Truncate subject if it would exceed the line length limit
    if available_length <= 0:
        # Edge case: prefix itself is too long, use minimal subject
        truncated_subject = ""
    elif len(subject) > available_length:
        truncated_subject = subject[:available_length]
    else:
        truncated_subject = subject

    first_line = f"{prefix}{truncated_subject}"

    # Build the full message
    if body:
        return f"{first_line}\n\n{body}"
    return first_line


def validate_commit_message(message: str) -> bool:
    """Validate that a commit message follows conventional commit format.

    Returns True if:
        - The first line matches: type(optional-scope): subject
        - The type is one of the valid conventional commit types
        - The first line (subject line) is at most 72 characters
        - If more than one line exists, the second line must be blank (empty)

    Returns False otherwise.

    Args:
        message: The full commit message string to validate.

    Returns:
        True if the message is valid conventional commit format, False otherwise.
    """
    if not message or not message.strip():
        return False

    lines = message.split("\n")
    first_line = lines[0]

    # Check subject line length
    if len(first_line) > MAX_SUBJECT_LINE_LENGTH:
        return False

    # Check conventional commit pattern on first line
    match = _CONVENTIONAL_COMMIT_PATTERN.match(first_line)
    if not match:
        return False

    # If there are additional lines, the second line must be blank
    if len(lines) > 1 and lines[1].strip() != "":
        return False

    return True
