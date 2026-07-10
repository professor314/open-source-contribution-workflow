"""Difficulty classification for repository evaluation.

Classifies repositories into easy, medium, or hard based on
dependency count, lines of code, and presence of native extensions.
"""


def classify_difficulty(
    dependency_count: int,
    lines_of_code: int,
    has_native_extensions: bool = False,
) -> str:
    """Classify repository difficulty based on complexity indicators.

    Classification rules (checked in priority order):
    1. Hard: dependency_count > 5 OR has_native_extensions OR lines_of_code > 3000
    2. Easy: dependency_count <= 1 AND lines_of_code < 1000 AND no native extensions
    3. Medium: everything else (the gap between easy and hard)

    Args:
        dependency_count: Number of external dependencies in the repository.
        lines_of_code: Total lines of code in the main package (excluding
            tests, docs, and configuration files).
        has_native_extensions: Whether the repository includes compiled or
            native extensions (e.g., C extensions, Cython).

    Returns:
        Exactly one of: "easy", "medium", "hard".
    """
    # Check hard conditions first (highest priority)
    if has_native_extensions or dependency_count > 5 or lines_of_code > 3000:
        return "hard"

    # Check easy conditions
    if dependency_count <= 1 and lines_of_code < 1000:
        return "easy"

    # Everything else is medium
    return "medium"
