# Implementation Plan: Open-Source Contribution Workflow

## Overview

This plan implements the Kiro-driven open-source contribution workflow as a set of Python helper modules (for scoring, filtering, validation, and generation logic), JSON state files for tracking, and the workflow execution steps themselves. Kiro uses the helper modules during interactive execution. The final deliverables are: at least one submitted PR, a blog post, and a reusable steering document.

## Tasks

- [x] 1. Set up project structure and state management
  - [x] 1.1 Create directory structure and initialize state files
    - Create `src/` directory for helper modules
    - Create `src/__init__.py`
    - Create `.kiro/specs/open-source-contribution-workflow/state/` directory
    - Initialize `contribution_tracker.json` with empty tracker schema (user_level: "beginner", contributions: [], interest_areas: ["math", "statistics"])
    - Create `tests/` directory with `unit/`, `property/`, and `integration/` subdirectories
    - Add `requirements.txt` with: hypothesis, pytest
    - _Requirements: 7.4, 7.5_

  - [x] 1.2 Implement core data models and JSON state helpers
    - Create `src/models.py` with dataclass definitions for: CandidateRepo, RepoEvaluation, ContributionRecord, ContributionTracker, EnvironmentStatus, ValidationResult
    - Create `src/state.py` with functions to load/save tracker JSON, add contribution records, and update level counts
    - Include validation that loaded JSON matches expected schema
    - _Requirements: 7.4, 9.1_

  - [x]* 1.3 Write unit tests for state management
    - Test loading/saving tracker with empty and populated data
    - Test schema validation rejects malformed JSON
    - _Requirements: 7.4_

- [x] 2. Implement repository discovery and scoring logic
  - [x] 2.1 Implement composite scoring function
    - Create `src/scoring.py` with `compute_composite_score()` function
    - Implement the formula: recent_commits (25pts) + contributing_md (20pts) + open_issues (25pts) + size_inverse (30pts)
    - Return float score, ensure sorting produces non-increasing order
    - Cap results at 10 candidates
    - _Requirements: 1.4_

  - [x] 2.2 Implement candidate filtering function
    - Create `src/filtering.py` with `filter_candidates()` function
    - Filter by: labeled issues ("good first issue", "help wanted", "beginner-friendly") OR issue title/body keyword matching contribution types (documentation, test addition, error handling)
    - Exclude repos with >5000 lines in main package
    - _Requirements: 1.2, 1.3_

  - [x] 2.3 Implement difficulty classification function
    - Create `src/classification.py` with `classify_difficulty()` function
    - Easy: pure Python, 0-1 deps, <1000 lines
    - Medium: 2-5 deps, 1000-3000 lines
    - Hard: >5 deps OR native extensions OR >3000 lines
    - Return exactly one difficulty level per repo
    - _Requirements: 2.2, 2.3_

  - [x]* 2.4 Write property tests for scoring and filtering
    - **Property 1: Candidate Filtering Correctness** — only repos with labeled issues or keyword-matching issues pass the filter
    - **Property 2: Composite Score Sorting and Cap** — output is sorted non-increasing, max 10 results
    - **Validates: Requirements 1.2, 1.3, 1.4**

  - [x]* 2.5 Write property test for difficulty classification
    - **Property 4: Difficulty Classification Boundaries** — exactly one level assigned per input, boundary conditions respected
    - **Validates: Requirements 2.2, 2.3**

- [x] 3. Implement naming, formatting, and validation utilities
  - [x] 3.1 Implement branch name generator
    - Create `src/naming.py` with `generate_branch_name()` function
    - Format: `<contribution-type>/<short-description>`, max 50 chars
    - Lowercase alphanumeric + hyphens + single slash separator
    - Truncate description if needed to fit within limit
    - _Requirements: 4.4_

  - [x] 3.2 Implement commit message generator and validator
    - Create `src/commit_format.py` with `generate_commit_message()` and `validate_commit_message()` functions
    - Conventional commit format: `type(optional-scope): subject` (subject ≤72 chars)
    - Generator produces valid messages; validator rejects invalid ones
    - _Requirements: 5.7, 9.3_

  - [x] 3.3 Implement PR title and description generators
    - Create `src/pr_format.py` with `generate_pr_title()` and `generate_pr_description()` functions
    - Title format: `<type>: <description>` (≤72 chars)
    - Description includes: summary, motivation, testing, issue reference
    - _Requirements: 6.1, 6.2_

  - [x] 3.4 Implement pre-submission validation engine
    - Create `src/validation.py` with `run_validation_checks()` function
    - Checks: code_style, tests_pass, commit_format, branch_cleanliness, out_of_scope_files
    - Each check returns pass/fail + remediation text on failure
    - Aggregate "all_passed" is True only if every check passes
    - _Requirements: 9.1, 9.2, 9.4_

  - [x]* 3.5 Write property tests for naming and formatting
    - **Property 7: Branch Name Format and Length** — output matches pattern, ≤50 chars
    - **Property 8: Commit Message Round-Trip** — generated messages pass validator; invalid strings fail
    - **Property 9: PR Title Format and Length** — output matches `<type>: <desc>`, ≤72 chars
    - **Validates: Requirements 4.4, 5.7, 6.1, 9.3**

  - [x]* 3.6 Write property tests for validation engine
    - **Property 15: Validation Aggregation** — all_passed iff every check passes
    - **Property 16: Validation Failure Reporting** — failed checks include name + non-empty remediation
    - **Property 17: Out-of-Scope File Detection** — files outside expected dirs flagged, files inside not flagged
    - **Validates: Requirements 9.1, 9.2, 9.4**

- [x] 4. Implement progression, license detection, and contribution summary utilities
  - [x] 4.1 Implement difficulty progression recommender
    - Create `src/progression.py` with `recommend_next_difficulty()` function
    - Same level until 2 completions, then suggest next level up
    - Reference the Contribution_Type of most recent contribution in recommendation
    - _Requirements: 7.2, 7.3_

  - [x] 4.2 Implement license detection function
    - Create `src/license_detection.py` with `detect_license()` function
    - Recognize: MIT, Apache-2.0, GPL-3.0, BSD-2-Clause, BSD-3-Clause, ISC, MPL-2.0
    - Return `license_verified: true` with identifier if matched, `false` otherwise
    - _Requirements: 2.5_

  - [x] 4.3 Implement contributing summary function
    - Create `src/contributing_summary.py` with `summarize_contributing()` function
    - Accept raw CONTRIBUTING.md text, produce summary ≤200 words
    - Handle empty input gracefully (return notice that no guide found)
    - _Requirements: 2.7_

  - [x] 4.4 Implement linter config detection
    - Create `src/linter_detection.py` with `detect_linter_config()` function
    - Recognize: pyproject.toml with [tool.black] or [tool.ruff], setup.cfg with [flake8], .flake8, .pylintrc
    - Return identified linter tool name, or empty result if none found
    - _Requirements: 5.3_

  - [x]* 4.5 Write property tests for progression and detection
    - **Property 5: License Detection Accuracy** — known licenses verified correctly, unknown returns false
    - **Property 6: Contributing Summary Word Count** — output ≤200 words for any input
    - **Property 11: Difficulty Progression Logic** — same level until 2 completions, then escalate
    - **Property 19: Linter Config Detection** — correct tool identified per config, empty when none
    - **Validates: Requirements 2.5, 2.7, 5.3, 7.2, 7.3**

- [x] 5. Checkpoint - Verify all helper modules work correctly
  - Ensure all tests pass, ask the user if questions arise.

- [x] 6. Implement blog and steering document generators
  - [x] 6.1 Implement blog post generator
    - Create `src/blog_generator.py` with `generate_blog_post()` function
    - Input: ContributionTracker data
    - Output: markdown string with sections in order: introduction, discovery process, contribution process, what was learned, next steps
    - Include repo name, PR link, and code snippet for each contribution
    - First person, conversational tone, 500-3000 words
    - Save as `blog-post-YYYY-MM-DD.md`
    - _Requirements: 8.1, 8.2, 8.3, 8.4, 8.6, 8.7, 8.8_

  - [x] 6.2 Implement steering document generator
    - Create `src/steering_generator.py` with `generate_steering_doc()` function
    - Front-matter: `inclusion: manual`
    - Configurable parameters at top: interest_areas, difficulty_level, time_budget
    - Step-by-step workflow directives in second person ("you shall...")
    - Cover all phases: discovery, evaluation, environment, fork/branch, changes, validate, submit, post-submission
    - Save to `~/.kiro/steering/open-source-contribution.md`
    - _Requirements: 10.1, 10.2, 10.3, 10.4, 10.6_

  - [x]* 6.3 Write property tests for blog and steering generators
    - **Property 13: Blog Structure and Content Completeness** — all sections present, per-contribution examples included, filename matches pattern
    - **Property 14: Blog Word Count Bounds** — 500-3000 words
    - **Property 18: Steering Document Structure Completeness** — all workflow phases present, configurable parameters in header
    - **Validates: Requirements 8.2, 8.4, 8.7, 8.8, 10.2, 10.6**

  - [x]* 6.4 Write property test for contribution tracking round-trip
    - **Property 12: Contribution Tracking Round-Trip** — add record then retrieve preserves all fields; PR merge increments level count by exactly 1
    - **Validates: Requirements 7.4, 11.3**

- [x] 7. Checkpoint - Ensure all modules and tests pass
  - Ensure all tests pass, ask the user if questions arise.

- [x] 8. Execute the live workflow: environment setup and repo discovery
  - [x] 8.1 Verify environment prerequisites
    - Run `git --version`, `git config user.name`, `git config user.email`
    - Run `gh --version`, `gh auth status`
    - Display summary of verified tools with versions
    - Provide remediation instructions for any failures
    - _Requirements: 3.1, 3.2, 3.3, 3.4, 3.5, 3.6, 3.7_

  - [x] 8.2 Execute repository discovery for math/statistics interests
    - Use `gh search repos` with keywords: math, statistics
    - Apply filtering logic from `src/filtering.py`
    - Score and rank using `src/scoring.py`
    - Identify a specific candidate contribution for each repo
    - Present batch queue of up to 10 candidates to user for selection
    - _Requirements: 1.1, 1.2, 1.3, 1.4, 1.5, 1.6, 1.7, 1.8_

  - [x] 8.3 Evaluate user-selected repository
    - Analyze codebase structure: lines of code, files, test presence, dependency count
    - Classify difficulty using `src/classification.py`
    - Verify OSI-approved license using `src/license_detection.py`
    - Summarize contribution guidelines using `src/contributing_summary.py`
    - Warn if difficulty exceeds beginner level
    - _Requirements: 2.1, 2.2, 2.3, 2.5, 2.6, 2.7, 2.8_

- [x] 9. Execute the live workflow: fork, contribute, and submit PR
  - [x] 9.1 Fork repository and create feature branch
    - Fork using `gh repo fork` (or sync existing fork)
    - Clone to local directory
    - Configure upstream remote
    - Create descriptively named branch using `src/naming.py`
    - _Requirements: 4.1, 4.2, 4.3, 4.4, 4.5_

  - [x] 9.2 Make the contribution
    - Analyze selected issue or improvement area
    - Propose a scoped change completable in under 30 minutes (single-line changes are valid)
    - Present proposal to user for approval
    - Make code changes following repo's existing style
    - Detect linter config using `src/linter_detection.py` and apply style rules
    - _Requirements: 5.1, 5.2, 5.3_

  - [x] 9.3 Validate and commit changes
    - Run repository's test suite (if exists)
    - Run pre-submission validation using `src/validation.py`
    - Stage modified files, generate commit message using `src/commit_format.py`
    - Push to fork
    - _Requirements: 5.4, 5.5, 5.6, 5.7, 9.1, 9.2, 9.3, 9.4, 9.5, 9.6_

  - [x] 9.4 Submit Pull Request
    - Check for merge conflicts with target branch
    - Detect PR template if present
    - Generate PR title and description using `src/pr_format.py`
    - Submit using `gh pr create`
    - Record contribution in tracker using `src/state.py`
    - _Requirements: 6.1, 6.2, 6.3, 6.4, 6.5, 6.6_

  - [x] 9.5 Provide post-submission guidance
    - Display expected review timeline
    - Explain CI checks and how to monitor PR status
    - Explain how to push additional commits if changes requested
    - Explain GitHub notification settings
    - _Requirements: 11.1, 11.2, 11.3, 11.4, 11.5, 11.6_

- [x] 10. Checkpoint - Verify PR submitted successfully
  - Ensure all tests pass, ask the user if questions arise.

- [x] 11. Generate documentation deliverables
  - [x] 11.1 Generate the blog post
    - Use `src/blog_generator.py` to produce blog post from contribution tracker data
    - Verify sections are complete: intro, discovery, contribution, lessons, next steps
    - Verify word count is 500-3000
    - Save as `blog-post-YYYY-MM-DD.md` in workspace root
    - _Requirements: 8.1, 8.2, 8.3, 8.4, 8.5, 8.6, 8.7, 8.8_

  - [x] 11.2 Generate the steering document
    - Use `src/steering_generator.py` to produce the reusable workflow guide
    - Save to `~/.kiro/steering/open-source-contribution.md`
    - Verify front-matter `inclusion: manual` is present
    - Verify all workflow phases are covered
    - Verify configurable parameters are at the top
    - _Requirements: 10.1, 10.2, 10.3, 10.4, 10.5, 10.6_

  - [x] 11.3 Update contribution tracker with final state
    - Record PR status (open/merged)
    - Update difficulty level counts
    - Suggest next contribution based on progression logic from `src/progression.py`
    - _Requirements: 7.2, 7.3, 7.4, 7.5, 11.3_

- [x] 12. Final checkpoint - All deliverables complete
  - Ensure all tests pass, ask the user if questions arise.
  - Verify: PR submitted, blog post saved, steering document at ~/.kiro/steering/, tracker updated.

## Notes

- Tasks marked with `*` are optional and can be skipped for faster MVP
- Each task references specific requirements for traceability
- Checkpoints ensure incremental validation
- Property tests validate universal correctness properties from the design document
- Unit tests validate specific examples and edge cases
- Tasks 1-7 build the helper infrastructure; Tasks 8-12 execute the live workflow using that infrastructure
- All shell commands use Windows cmd syntax (the user's environment)
- The user is a beginner — Kiro handles all git/gh mechanics with clear explanations at each step
- Single-line contributions are explicitly acceptable per Requirement 5.1

## Task Dependency Graph

```json
{
  "waves": [
    { "id": 0, "tasks": ["1.1"] },
    { "id": 1, "tasks": ["1.2"] },
    { "id": 2, "tasks": ["1.3", "2.1", "2.2", "2.3", "3.1", "3.2", "3.3", "3.4", "4.1", "4.2", "4.3", "4.4"] },
    { "id": 3, "tasks": ["2.4", "2.5", "3.5", "3.6", "4.5", "6.1", "6.2"] },
    { "id": 4, "tasks": ["6.3", "6.4"] },
    { "id": 5, "tasks": ["8.1"] },
    { "id": 6, "tasks": ["8.2"] },
    { "id": 7, "tasks": ["8.3"] },
    { "id": 8, "tasks": ["9.1"] },
    { "id": 9, "tasks": ["9.2"] },
    { "id": 10, "tasks": ["9.3"] },
    { "id": 11, "tasks": ["9.4"] },
    { "id": 12, "tasks": ["9.5"] },
    { "id": 13, "tasks": ["11.1", "11.2", "11.3"] }
  ]
}
```
