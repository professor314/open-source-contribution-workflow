"""Property-based tests for blog generation and steering document generation.

# Feature: open-source-contribution-workflow, Property 13: Blog Structure and Content Completeness
# Feature: open-source-contribution-workflow, Property 14: Blog Word Count Bounds
# Feature: open-source-contribution-workflow, Property 18: Steering Document Structure Completeness
"""

from hypothesis import given, settings
from hypothesis import strategies as st

from src.blog_generator import generate_blog_post
from src.steering_generator import generate_steering_doc
from src.models import ContributionTracker, ContributionRecord


# --- Strategies ---

CONTRIBUTION_TYPES = [
    "bug_fix", "documentation", "test_addition",
    "error_handling", "feature_addition", "type_hints",
]

DIFFICULTY_LEVELS = ["easy", "medium", "hard"]

USER_LEVELS = ["beginner", "intermediate", "advanced"]


def contribution_record_strategy():
    """Strategy to generate a valid ContributionRecord for blog/steering tests."""
    return st.builds(
        ContributionRecord,
        id=st.text(min_size=1, max_size=20, alphabet="abcdefghijklmnopqrstuvwxyz0123456789-"),
        repo_full_name=st.from_regex(r"[a-z]{1,10}/[a-z]{1,10}", fullmatch=True),
        contribution_type=st.sampled_from(CONTRIBUTION_TYPES),
        difficulty_level=st.sampled_from(DIFFICULTY_LEVELS),
        branch_name=st.text(min_size=5, max_size=30, alphabet="abcdefghijklmnopqrstuvwxyz-/"),
        pr_url=st.from_regex(r"https://github\.com/[a-z]+/[a-z]+/pull/\d+", fullmatch=True),
        pr_number=st.integers(min_value=1, max_value=9999),
        pr_status=st.sampled_from(["open", "merged", "closed"]),
        commit_sha=st.text(min_size=7, max_size=40, alphabet="0123456789abcdef"),
        modified_files=st.lists(
            st.text(min_size=3, max_size=30, alphabet="abcdefghijklmnopqrstuvwxyz./"),
            min_size=1,
            max_size=5,
        ),
        code_snippet=st.text(min_size=10, max_size=100, alphabet="abcdefghijklmnopqrstuvwxyz _=():\n"),
        started_at=st.just("2025-01-20T14:00:00Z"),
        completed_at=st.just("2025-01-20T15:00:00Z"),
    )


def blog_tracker_strategy(min_contributions=1, max_contributions=3):
    """Build a tracker with 1-3 contributions for blog generation tests."""
    return st.lists(
        contribution_record_strategy(),
        min_size=min_contributions,
        max_size=max_contributions,
    ).flatmap(lambda recs: st.builds(
        ContributionTracker,
        user_level=st.sampled_from(USER_LEVELS),
        contributions=st.just(recs),
        level_counts=st.just({
            "easy": sum(1 for r in recs if r.difficulty_level == "easy"),
            "medium": sum(1 for r in recs if r.difficulty_level == "medium"),
            "hard": sum(1 for r in recs if r.difficulty_level == "hard"),
        }),
        interest_areas=st.lists(
            st.text(min_size=2, max_size=20, alphabet="abcdefghijklmnopqrstuvwxyz "),
            min_size=1,
            max_size=5,
        ),
        last_updated=st.just("2025-01-20T14:00:00Z"),
    ))


def steering_tracker_strategy():
    """Build a tracker with varying interest areas and user levels for steering tests."""
    return st.builds(
        ContributionTracker,
        user_level=st.sampled_from(USER_LEVELS),
        contributions=st.lists(contribution_record_strategy(), min_size=0, max_size=3),
        level_counts=st.just({"easy": 0, "medium": 0, "hard": 0}),
        interest_areas=st.lists(
            st.text(min_size=2, max_size=20, alphabet="abcdefghijklmnopqrstuvwxyz "),
            min_size=1,
            max_size=5,
        ),
        last_updated=st.just("2025-01-20T14:00:00Z"),
    )


# ============================================================
# Property 13: Blog Structure and Content Completeness
# Feature: open-source-contribution-workflow, Property 13: Blog Structure and Content Completeness
# **Validates: Requirements 8.2, 8.4, 8.7**
# ============================================================

class TestBlogStructureAndContentCompleteness:
    """Property 13: Blog Structure and Content Completeness.

    For any tracker with 1-3 contributions, generate_blog_post() produces output that:
    - Contains all section headers (Introduction, Discovery Process, Contribution Process,
      What I Learned, Next Steps)
    - For each contribution, contains the repo_full_name and pr_url
    - Contains "blog-post" when tested via save filename pattern
    """

    @given(tracker=blog_tracker_strategy(min_contributions=1, max_contributions=3))
    @settings(max_examples=100)
    def test_all_section_headers_present(self, tracker):
        """Generated blog post contains all required section headers."""
        content = generate_blog_post(tracker)

        # Check for section headers (case-insensitive search in content)
        content_lower = content.lower()
        assert "introduction" in content_lower or "journey" in content_lower, (
            "Blog post missing Introduction section"
        )
        assert "discovery process" in content_lower, (
            "Blog post missing Discovery Process section"
        )
        assert "contribution process" in content_lower, (
            "Blog post missing Contribution Process section"
        )
        assert "what i learned" in content_lower, (
            "Blog post missing What I Learned section"
        )
        assert "next steps" in content_lower, (
            "Blog post missing Next Steps section"
        )

    @given(tracker=blog_tracker_strategy(min_contributions=1, max_contributions=3))
    @settings(max_examples=100)
    def test_each_contribution_repo_and_pr_included(self, tracker):
        """For each contribution, the blog contains the repo_full_name and pr_url."""
        content = generate_blog_post(tracker)

        for contrib in tracker.contributions:
            assert contrib.repo_full_name in content, (
                f"Blog post does not contain repo_full_name '{contrib.repo_full_name}'"
            )
            assert contrib.pr_url in content, (
                f"Blog post does not contain pr_url '{contrib.pr_url}'"
            )

    @given(tracker=blog_tracker_strategy(min_contributions=1, max_contributions=3))
    @settings(max_examples=100)
    def test_blog_post_filename_contains_pattern(self, tracker):
        """The blog-post filename pattern is 'blog-post-YYYY-MM-DD.md'."""
        # We test that the save function would produce a filename containing "blog-post"
        # by checking the save_blog_post function's naming logic
        from src.blog_generator import save_blog_post
        import tempfile
        import os

        content = generate_blog_post(tracker)
        with tempfile.TemporaryDirectory() as tmpdir:
            file_path = save_blog_post(content, tmpdir)
            filename = os.path.basename(file_path)
            assert "blog-post" in filename, (
                f"Filename '{filename}' does not contain 'blog-post'"
            )
            assert filename.endswith(".md"), (
                f"Filename '{filename}' does not end with '.md'"
            )


# ============================================================
# Property 14: Blog Word Count Bounds
# Feature: open-source-contribution-workflow, Property 14: Blog Word Count Bounds
# **Validates: Requirements 8.8**
# ============================================================

class TestBlogWordCountBounds:
    """Property 14: Blog Word Count Bounds.

    For any tracker with 1-5 contributions, generate_blog_post() produces
    a document with word count between 500 and 3000 inclusive.
    """

    @given(tracker=blog_tracker_strategy(min_contributions=1, max_contributions=5))
    @settings(max_examples=100)
    def test_word_count_within_bounds(self, tracker):
        """Generated blog post has between 500 and 3000 words."""
        content = generate_blog_post(tracker)
        word_count = len(content.split())

        assert 500 <= word_count <= 3000, (
            f"Blog word count is {word_count}, expected between 500 and 3000"
        )


# ============================================================
# Property 18: Steering Document Structure Completeness
# Feature: open-source-contribution-workflow, Property 18: Steering Document Structure Completeness
# **Validates: Requirements 10.2, 10.6**
# ============================================================

class TestSteeringDocumentStructureCompleteness:
    """Property 18: Steering Document Structure Completeness.

    For any tracker with varying interest areas and user levels,
    generate_steering_doc() produces output that:
    - Contains "inclusion: manual" in front-matter
    - Contains all phase headings (Discovery, Evaluation, Environment,
      Fork/Branch, Contribution, Validation, Submit PR, Post-Submission)
    - Contains configurable parameters (interest_areas, difficulty_level, time_budget)
    """

    @given(tracker=steering_tracker_strategy())
    @settings(max_examples=100)
    def test_inclusion_manual_in_frontmatter(self, tracker):
        """Steering doc contains 'inclusion: manual' in front-matter."""
        content = generate_steering_doc(tracker)

        assert "inclusion: manual" in content, (
            "Steering document does not contain 'inclusion: manual'"
        )

    @given(tracker=steering_tracker_strategy())
    @settings(max_examples=100)
    def test_all_phase_headings_present(self, tracker):
        """Steering doc contains all workflow phase headings."""
        content = generate_steering_doc(tracker)
        content_lower = content.lower()

        required_phases = [
            "discovery",
            "evaluation",
            "environment",
            "fork/branch",
            "contribution",
            "validation",
            "submit pr",
            "post-submission",
        ]

        for phase in required_phases:
            assert phase in content_lower, (
                f"Steering document missing phase heading: '{phase}'"
            )

    @given(tracker=steering_tracker_strategy())
    @settings(max_examples=100)
    def test_configurable_parameters_present(self, tracker):
        """Steering doc contains configurable parameters: interest_areas, difficulty_level, time_budget."""
        content = generate_steering_doc(tracker)

        assert "interest_areas" in content, (
            "Steering document does not contain 'interest_areas' parameter"
        )
        assert "difficulty_level" in content, (
            "Steering document does not contain 'difficulty_level' parameter"
        )
        assert "time_budget" in content, (
            "Steering document does not contain 'time_budget' parameter"
        )
