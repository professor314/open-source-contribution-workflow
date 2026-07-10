"""Steering document generator for the open-source contribution workflow.

Produces a reusable Kiro steering document that captures the proven
contribution workflow as step-by-step directives.
"""

import os
from src.models import ContributionTracker


def generate_steering_doc(tracker: ContributionTracker) -> str:
    """Generate a Kiro steering document from the contribution tracker.

    Args:
        tracker: The ContributionTracker containing user preferences and history.

    Returns:
        A markdown string for a Kiro steering document with front-matter,
        configurable parameters, and step-by-step workflow directives.
    """
    interest_areas = tracker.interest_areas if tracker.interest_areas else ["python"]
    difficulty_level = tracker.user_level if tracker.user_level else "easy"

    doc = f"""---
inclusion: manual
---

# Open Source Contribution Workflow

## Parameters
- interest_areas: {interest_areas}
- difficulty_level: "{difficulty_level}"
- time_budget: "30 minutes"

## Phase 1: Discovery

You shall search GitHub for Python repositories matching the user's interest areas using the `gh search repos` command with language and keyword filters.

You shall filter results to repositories with fewer than 5000 lines of code in the main package directory (excluding tests, docs, and configuration files).

You shall prioritize repositories that have open issues labeled "good first issue", "help wanted", or "beginner-friendly". If no labeled issues exist, you shall identify repositories with issues matching contribution types: documentation improvements, test additions, or error handling improvements.

You shall rank candidates using the composite scoring formula (recent commits, contributing guide presence, open issues, codebase size) and present the top 10 results sorted by score descending.

You shall identify a specific candidate contribution for each repository so the user has a ready-to-execute queue of contributions.

## Phase 2: Evaluation

You shall analyze the selected repository's codebase structure: total lines of code, number of files, test coverage presence, and dependency count.

You shall classify the repository difficulty as easy (pure Python, 0-1 dependencies, under 1000 lines), medium (2-5 dependencies, 1000-3000 lines), or hard (more than 5 dependencies or native extensions, over 3000 lines).

You shall check for an OSI-approved open-source license (MIT, Apache-2.0, GPL-3.0, BSD-2-Clause, BSD-3-Clause, ISC, MPL-2.0) and warn the user if no recognized license is found.

You shall check for a CONTRIBUTING.md or README contribution section and summarize the maintainer's contribution expectations in no more than 200 words.

You shall warn the user if the repository difficulty exceeds their current level and suggest an easier alternative.

## Phase 3: Environment

You shall verify that git is installed and configured with a non-empty user.name and user.email by running `git --version`, `git config user.name`, and `git config user.email`.

You shall verify that the GitHub CLI (gh) is installed and authenticated by running `gh --version` and `gh auth status`.

You shall provide platform-specific installation instructions if any tool is missing or not configured.

You shall display a summary of all verified tools with their versions and authentication status before proceeding.

## Phase 4: Fork/Branch

You shall fork the selected repository to the user's GitHub account using `gh repo fork`. If a fork already exists, you shall sync it with the upstream default branch using `gh repo sync`.

You shall clone the fork to a local directory named after the repository.

You shall configure the upstream remote to point to the original repository URL.

You shall create a descriptively named feature branch using the convention `contribution-type/short-description` (no longer than 50 characters total, lowercase alphanumeric with hyphens and a single slash separator).

## Phase 5: Contribution

You shall analyze the selected issue or improvement area and propose a specific, scoped change that can be completed in under 30 minutes total (including the PR submission process). Even single-line changes are acceptable if they provide genuine value.

You shall explain what the change does, why it improves the project, and how to verify it works.

You shall present the proposal to the user and wait for approval before making changes.

You shall ensure modifications follow the repository's existing code style by checking for linter configuration files (pyproject.toml, setup.cfg, .flake8, .pylintrc) and applying matching style rules.

You shall run the repository's existing test suite to verify no regressions are introduced. If tests fail, you shall identify which tests failed, explain the likely cause, and suggest corrections.

You shall stage only modified files, commit with a conventional commit message (type, optional scope, subject under 72 characters), and push to the fork.

## Phase 6: Validation

You shall run the pre-submission validation checklist covering: code style compliance, test passage, commit message format, and branch cleanliness (no merge conflicts, no untracked files, linear commit history).

You shall verify that no modified files fall outside the expected directories or modules (flag potential unintended changes).

You shall display remediation instructions for any failed checks before allowing submission to proceed.

You shall display a confirmation summary when all checks pass indicating the contribution is ready for submission.

## Phase 7: Submit PR

You shall check for merge conflicts with the target default branch and provide rebase instructions if conflicts exist.

You shall detect any PR template in the target repository (.github/PULL_REQUEST_TEMPLATE.md) and follow its format.

You shall generate a PR title following the format "contribution-type: short description" (no more than 72 characters).

You shall generate a PR description including: a summary of what was changed, the motivation for the change, how the change was tested, and a reference to any related issue.

You shall submit the PR using `gh pr create --base <default_branch> --title "..." --body "..."`.

## Phase 8: Post-Submission

You shall explain the expected review timeline (typically 2-7 business days for small repos, though it can vary significantly).

You shall describe the automated CI checks that will run and how to monitor PR status on GitHub.

You shall explain how to push additional commits to the same PR branch if the maintainer requests changes: make changes locally, commit them, and push to the existing branch.

You shall explain GitHub notification settings so the user can monitor PR activity.

You shall explain common PR rejection reasons and provide actionable suggestions for improvement on the next attempt.

You shall update the contribution tracker and suggest the next contribution based on the difficulty progression logic.
"""
    return doc


def save_steering_doc(content: str) -> str:
    """Save the steering document to the user-level Kiro steering directory.

    Args:
        content: The markdown content of the steering document.

    Returns:
        The absolute path where the file was saved.
    """
    home = os.path.expanduser("~")
    steering_dir = os.path.join(home, ".kiro", "steering")
    os.makedirs(steering_dir, exist_ok=True)

    file_path = os.path.join(steering_dir, "open-source-contribution.md")
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(content)

    return file_path
