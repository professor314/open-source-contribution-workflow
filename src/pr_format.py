"""PR title and description generation utilities.

Provides functions to generate well-formatted Pull Request titles and
markdown-formatted PR descriptions for open-source contributions.

PR titles follow the format: <type>: <description> (≤72 characters)
PR descriptions include structured sections: Summary, Motivation, Testing,
and optionally a Related Issue reference.
"""

from __future__ import annotations

from typing import Optional


VALID_PR_TYPES: list[str] = [
    "fix",
    "feat",
    "docs",
    "test",
    "refactor",
    "style",
    "chore",
]

MAX_PR_TITLE_LENGTH: int = 72


def generate_pr_title(contribution_type: str, description: str) -> str:
    """Generate a PR title in the format '<type>: <description>'.

    The title is guaranteed to be at most 72 characters. If the description
    would cause the title to exceed the limit, it is truncated to fit.

    Args:
        contribution_type: The type of contribution (fix, feat, docs, etc.).
        description: A concise description of what the PR does.

    Returns:
        A formatted PR title string, at most 72 characters.

    Raises:
        ValueError: If contribution_type is not one of the valid types.
    """
    normalized_type = contribution_type.strip().lower()

    if normalized_type not in VALID_PR_TYPES:
        raise ValueError(
            f"Invalid contribution type '{contribution_type}'. "
            f"Must be one of: {', '.join(VALID_PR_TYPES)}"
        )

    prefix = f"{normalized_type}: "
    available_length = MAX_PR_TITLE_LENGTH - len(prefix)

    # Normalize whitespace in description
    cleaned_description = " ".join(description.split())

    # Truncate description if it would exceed the title length limit
    if available_length <= 0:
        truncated_description = ""
    elif len(cleaned_description) > available_length:
        truncated_description = cleaned_description[:available_length]
    else:
        truncated_description = cleaned_description

    return f"{prefix}{truncated_description}"


def generate_pr_description(
    summary: str,
    motivation: str,
    testing: str,
    issue_ref: Optional[str] = None,
) -> str:
    """Generate a markdown-formatted PR description with structured sections.

    The description includes the following sections:
    - ## Summary — what was changed
    - ## Motivation — why the change was made
    - ## Testing — how the change was verified
    - ## Related Issue — reference to a related issue (only if issue_ref is provided)

    Args:
        summary: A description of what was changed in the PR.
        motivation: The reason or motivation for making the change.
        testing: How the change was tested or can be verified.
        issue_ref: Optional reference to a related issue (e.g., "#42" or a URL).

    Returns:
        A markdown-formatted PR description string.
    """
    sections: list[str] = []

    sections.append("## Summary")
    sections.append("")
    sections.append(summary)
    sections.append("")

    sections.append("## Motivation")
    sections.append("")
    sections.append(motivation)
    sections.append("")

    sections.append("## Testing")
    sections.append("")
    sections.append(testing)

    if issue_ref is not None:
        sections.append("")
        sections.append("## Related Issue")
        sections.append("")
        sections.append(issue_ref)

    return "\n".join(sections)
