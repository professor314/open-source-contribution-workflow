# Feature: open-source-contribution-workflow, Property 4: Difficulty Classification Boundaries
"""Property-based tests for difficulty classification boundaries.

Validates: Requirements 2.2, 2.3

Verifies that classify_difficulty() assigns exactly one difficulty level
per input and respects the boundary conditions:
- easy: deps <= 1 AND lines < 1000 AND not native
- hard: deps > 5 OR native OR lines > 3000
- medium: everything else
"""

from hypothesis import given, settings
from hypothesis import strategies as st

from src.classification import classify_difficulty


@settings(max_examples=100)
@given(
    dependency_count=st.integers(min_value=0, max_value=20),
    lines_of_code=st.integers(min_value=0, max_value=10000),
    has_native_extensions=st.booleans(),
)
def test_classify_difficulty_returns_valid_level(
    dependency_count: int, lines_of_code: int, has_native_extensions: bool
) -> None:
    """Result is exactly one of 'easy', 'medium', 'hard'."""
    result = classify_difficulty(dependency_count, lines_of_code, has_native_extensions)
    assert result in ("easy", "medium", "hard")


@settings(max_examples=100)
@given(
    dependency_count=st.integers(min_value=0, max_value=1),
    lines_of_code=st.integers(min_value=0, max_value=999),
)
def test_classify_difficulty_easy_boundary(
    dependency_count: int, lines_of_code: int
) -> None:
    """When deps <= 1 AND lines < 1000 AND not native → 'easy'."""
    result = classify_difficulty(dependency_count, lines_of_code, has_native_extensions=False)
    assert result == "easy"


@settings(max_examples=100)
@given(
    dependency_count=st.integers(min_value=6, max_value=20),
    lines_of_code=st.integers(min_value=0, max_value=10000),
    has_native_extensions=st.booleans(),
)
def test_classify_difficulty_hard_when_deps_exceed_five(
    dependency_count: int, lines_of_code: int, has_native_extensions: bool
) -> None:
    """When deps > 5 → 'hard' regardless of other factors."""
    result = classify_difficulty(dependency_count, lines_of_code, has_native_extensions)
    assert result == "hard"


@settings(max_examples=100)
@given(
    dependency_count=st.integers(min_value=0, max_value=20),
    lines_of_code=st.integers(min_value=0, max_value=10000),
)
def test_classify_difficulty_hard_when_native(
    dependency_count: int, lines_of_code: int
) -> None:
    """When has_native_extensions is True → 'hard' regardless of other factors."""
    result = classify_difficulty(dependency_count, lines_of_code, has_native_extensions=True)
    assert result == "hard"


@settings(max_examples=100)
@given(
    dependency_count=st.integers(min_value=0, max_value=20),
    lines_of_code=st.integers(min_value=3001, max_value=10000),
    has_native_extensions=st.booleans(),
)
def test_classify_difficulty_hard_when_lines_exceed_3000(
    dependency_count: int, lines_of_code: int, has_native_extensions: bool
) -> None:
    """When lines > 3000 → 'hard' regardless of other factors."""
    result = classify_difficulty(dependency_count, lines_of_code, has_native_extensions)
    assert result == "hard"


@settings(max_examples=100)
@given(
    dependency_count=st.integers(min_value=2, max_value=5),
    lines_of_code=st.integers(min_value=0, max_value=3000),
)
def test_classify_difficulty_medium_deps_in_range(
    dependency_count: int, lines_of_code: int
) -> None:
    """When deps 2-5 AND lines <= 3000 AND not native → 'medium'."""
    result = classify_difficulty(dependency_count, lines_of_code, has_native_extensions=False)
    assert result == "medium"


@settings(max_examples=100)
@given(
    dependency_count=st.integers(min_value=0, max_value=1),
    lines_of_code=st.integers(min_value=1000, max_value=3000),
)
def test_classify_difficulty_medium_lines_in_range(
    dependency_count: int, lines_of_code: int
) -> None:
    """When deps <= 1 AND lines 1000-3000 AND not native → 'medium'."""
    result = classify_difficulty(dependency_count, lines_of_code, has_native_extensions=False)
    assert result == "medium"
