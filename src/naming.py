"""Branch name generation and validation utilities.

Generates branch names in the format <contribution-type>/<short-description>
with a maximum of 50 characters total, using only lowercase alphanumeric
characters, hyphens, and a single slash separator.
"""

import re

VALID_CONTRIBUTION_TYPES = (
    "fix", "docs", "test", "feat", "refactor", "style", "chore"
)

MAX_BRANCH_LENGTH = 50
BRANCH_PATTERN = re.compile(r"^[a-z]+/[a-z0-9-]+$")


def generate_branch_name(contribution_type: str, short_description: str) -> str:
    """Generate a valid branch name from contribution type and description.

    Format: <contribution-type>/<short-description>
    - Max 50 characters total
    - Lowercase alphanumeric + hyphens + single slash separator
    - Truncates description if needed to fit within limit
    - Strips/replaces invalid characters from description

    Args:
        contribution_type: The type of contribution (e.g., "fix", "docs", "feat").
        short_description: A brief description of the change.

    Returns:
        A valid branch name string.

    Raises:
        ValueError: If contribution_type is not a valid type or description
            results in an empty string after normalization.
    """
    # Step 1: Normalize contribution_type to lowercase
    normalized_type = contribution_type.strip().lower()

    if normalized_type not in VALID_CONTRIBUTION_TYPES:
        raise ValueError(
            f"Invalid contribution type '{contribution_type}'. "
            f"Must be one of: {', '.join(VALID_CONTRIBUTION_TYPES)}"
        )

    # Step 2: Normalize short_description
    desc = short_description.lower()
    # Replace spaces and underscores with hyphens
    desc = desc.replace(" ", "-").replace("_", "-")
    # Remove any character that's not alphanumeric or hyphen
    desc = re.sub(r"[^a-z0-9-]", "", desc)
    # Collapse multiple consecutive hyphens into one
    desc = re.sub(r"-{2,}", "-", desc)
    # Strip leading/trailing hyphens
    desc = desc.strip("-")

    if not desc:
        raise ValueError(
            "Description results in an empty string after normalization. "
            "Provide a description with at least one alphanumeric character."
        )

    # Step 3: Combine as type/description
    prefix = f"{normalized_type}/"
    available_length = MAX_BRANCH_LENGTH - len(prefix)

    # Step 4: Truncate description if total length > 50
    if len(desc) > available_length:
        desc = desc[:available_length]
        # Remove trailing hyphens after truncation
        desc = desc.rstrip("-")

    if not desc:
        raise ValueError(
            "Description is too short to fit within the 50-character limit "
            "after accounting for the contribution type prefix."
        )

    branch_name = f"{prefix}{desc}"

    # Step 5: Validate result matches expected pattern
    if not BRANCH_PATTERN.match(branch_name):
        raise ValueError(
            f"Generated branch name '{branch_name}' does not match "
            f"the required pattern: ^[a-z]+/[a-z0-9-]+$"
        )

    return branch_name


def validate_branch_name(name: str) -> bool:
    """Validate that a branch name conforms to the required format.

    A valid branch name:
    - Matches pattern: lowercase type, single slash, lowercase alphanumeric+hyphens description
    - Total length ≤ 50 characters
    - Contains exactly one slash separating type from description

    Args:
        name: The branch name to validate.

    Returns:
        True if valid, False otherwise.
    """
    if not name or len(name) > MAX_BRANCH_LENGTH:
        return False

    if not BRANCH_PATTERN.match(name):
        return False

    # Ensure exactly one slash
    if name.count("/") != 1:
        return False

    # Ensure both parts are non-empty
    parts = name.split("/")
    if len(parts) != 2 or not parts[0] or not parts[1]:
        return False

    return True
