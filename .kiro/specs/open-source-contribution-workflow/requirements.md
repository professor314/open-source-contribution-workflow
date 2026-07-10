# Requirements Document

## Introduction

This feature defines a structured workflow for a beginner Python programmer to make meaningful contributions to small open-source Python repositories on GitHub, using Kiro as the interactive guide and execution engine. Kiro performs repo discovery, evaluation, environment setup, code changes, validation, and PR submission directly — the user collaborates and makes decisions while Kiro handles the mechanics. The workflow covers the entire journey from finding suitable repos, through the mechanics of forking, branching, and submitting Pull Requests, to documenting the experience in a blog post. The goal is to build contribution confidence incrementally while producing real, accepted PRs — not trivial typo fixes. The proven workflow is captured as a reusable user-level Kiro steering document for future contributions across any workspace.

## Glossary

- **Workflow_Engine**: The guided process that helps the user discover, evaluate, and contribute to open-source repositories
- **Repo_Scanner**: The component that identifies and ranks candidate repositories based on user interests and difficulty level
- **Contribution_Guide**: The step-by-step instructions that walk the user through the git/GitHub mechanics of contributing
- **Blog_Generator**: The component that produces a markdown blog post documenting the contribution journey
- **PR**: Pull Request — a proposal to merge code changes into a repository
- **Fork**: A personal copy of another user's repository on GitHub
- **Branch**: A parallel version of a repository used to develop changes in isolation
- **gh_CLI**: The GitHub command-line interface tool for interacting with GitHub from the terminal
- **Candidate_Repo**: A repository that has been identified as a potential target for contribution
- **Contribution_Type**: The category of change being made (bug fix, documentation improvement, test addition, error handling improvement, or feature addition)
- **Difficulty_Level**: A classification of how challenging a contribution is (easy, medium, hard)

## Requirements

### Requirement 1: Repository Discovery

**User Story:** As a beginner contributor, I want to find small Python repos that match my interests, so that I can contribute to projects I care about and understand.

#### Acceptance Criteria

1. WHEN the user specifies at least one and up to five interest areas as keyword strings (each between 2 and 50 characters), THE Repo_Scanner SHALL search GitHub for Python repositories matching those interests with fewer than 5000 lines of code in the main package (the top-level source directory excluding tests, docs, and configuration files)
2. WHEN scanning repositories, THE Repo_Scanner SHALL filter results to repositories with at least one open issue labeled "good first issue", "help wanted", or "beginner-friendly"
3. WHEN no labeled issues exist in a matching repository, THE Repo_Scanner SHALL identify repositories with open issues that match Contribution_Type categories of documentation improvements, test additions, or error handling based on issue title and body keyword matching
4. THE Repo_Scanner SHALL rank Candidate_Repo results by a composite score based on: number of commits within the last 90 days, presence of a CONTRIBUTING.md file, number of open issues, and codebase size (fewer lines scored higher), and SHALL return no more than 10 Candidate_Repo results ordered from highest to lowest score, presented as a batch queue of candidates ready for immediate execution
5. WHEN presenting results, THE Repo_Scanner SHALL display for each Candidate_Repo: the repository name, description (truncated to 200 characters), star count, last commit date, primary Contribution_Type opportunities, and Difficulty_Level rated as one of "beginner", "intermediate", or "advanced" based on codebase size, number of dependencies, and presence of documentation
6. WHEN presenting results, THE Repo_Scanner SHALL also identify a specific candidate contribution for each repo (the issue or improvement to work on) so that the user has a ready-to-execute queue of contributions rather than needing to evaluate each repo individually before starting
7. IF the search returns no repositories matching the specified interest areas and filters, THEN THE Repo_Scanner SHALL display a message indicating no matching repositories were found and suggest the user broaden their interest areas
8. IF the GitHub API is unavailable or returns an error, THEN THE Repo_Scanner SHALL display a message indicating the service is temporarily unavailable and prompt the user to retry after 30 seconds

### Requirement 2: Repository Evaluation

**User Story:** As a beginner contributor, I want to evaluate whether a repo is suitable for my skill level, so that I don't waste time on projects that are too complex.

#### Acceptance Criteria

1. WHEN a user selects a Candidate_Repo, THE Workflow_Engine SHALL analyze the codebase structure and report: total lines of code, number of files, test coverage presence (detected as present or absent), and dependency count
2. WHEN a user selects a Candidate_Repo, THE Workflow_Engine SHALL classify the repository as easy (pure Python, 0-1 dependencies, under 1000 lines of code), medium (2-5 dependencies, 1000-3000 lines of code), or hard (more than 5 dependencies or includes compiled/native extensions, over 3000 lines of code)
3. IF the repository Difficulty_Level exceeds the user's current level, THEN THE Workflow_Engine SHALL display a warning message indicating the difficulty mismatch and suggest an easier alternative from the user's Candidate_Repo list
4. IF the repository Difficulty_Level exceeds the user's current level and no easier alternative exists in the user's Candidate_Repo list, THEN THE Workflow_Engine SHALL display a warning message indicating the difficulty mismatch and recommend the user lower the search difficulty filter
5. WHEN evaluating a repository, THE Workflow_Engine SHALL verify that the repository has a license file containing an OSI-approved open-source license
6. IF the repository does not contain a recognized OSI-approved open-source license, THEN THE Workflow_Engine SHALL display a warning message indicating that the repository may not permit contributions and flag the repository as unverified for contribution eligibility
7. WHEN evaluating a repository, THE Workflow_Engine SHALL check for a CONTRIBUTING.md or README contribution section and summarize the maintainer's contribution expectations in no more than 200 words
8. IF the repository does not contain a CONTRIBUTING.md file or a README contribution section, THEN THE Workflow_Engine SHALL display a notice indicating that no formal contribution guidelines were found

### Requirement 3: Environment Setup

**User Story:** As a beginner contributor, I want clear setup instructions for my contribution environment, so that I can get started without struggling with tooling.

#### Acceptance Criteria

1. WHEN starting a contribution, THE Contribution_Guide SHALL verify that git is installed and configured with a non-empty user.name and user.email
2. WHEN starting a contribution, THE Contribution_Guide SHALL verify that the gh_CLI is installed and authenticated with access to repository operations
3. IF the gh_CLI is not installed, THEN THE Contribution_Guide SHALL provide installation instructions for Windows, macOS, and Linux
4. IF the gh_CLI is installed but not authenticated, THEN THE Contribution_Guide SHALL provide step-by-step instructions to authenticate using gh auth login
5. IF git is not installed, THEN THE Contribution_Guide SHALL provide installation instructions for Windows, macOS, and Linux
6. IF git credentials are not configured, THEN THE Contribution_Guide SHALL provide step-by-step instructions to configure git user.name and user.email
7. WHEN all environment checks pass, THE Contribution_Guide SHALL display a summary listing each verified tool with its version and authentication status, then proceed to the forking step

### Requirement 4: Fork and Branch Workflow

**User Story:** As a beginner contributor, I want to fork a repo and create a branch correctly, so that my changes are isolated and ready for a Pull Request.

#### Acceptance Criteria

1. WHEN the user selects a repository to contribute to, THE Contribution_Guide SHALL fork the repository to the user's GitHub account using the gh_CLI
2. IF a fork of the repository already exists in the user's GitHub account, THEN THE Contribution_Guide SHALL use the existing fork and sync it with the upstream default branch instead of creating a new fork
3. WHEN forking is complete, THE Contribution_Guide SHALL clone the fork to the local machine into a directory named after the repository
4. WHEN the local clone is ready, THE Contribution_Guide SHALL create a descriptively named feature branch from the upstream default branch using the naming convention: contribution-type/short-description (no longer than 50 characters total), for example: fix/add-input-validation or docs/improve-readme-examples
5. THE Contribution_Guide SHALL configure the upstream remote to point to the original repository URL

### Requirement 5: Making the Contribution

**User Story:** As a beginner contributor, I want guidance on making meaningful code changes, so that maintainers take my PR seriously.

#### Acceptance Criteria

1. WHEN the user is ready to make changes, THE Workflow_Engine SHALL analyze the selected issue or improvement area and propose a specific, scoped change that can be completed in under 30 minutes total (including the PR submission process), where even a single-line change is acceptable if it provides genuine value to the project
2. WHEN proposing changes, THE Workflow_Engine SHALL explain what the change does, why it improves the project, and how to verify it works
3. WHILE making changes, THE Workflow_Engine SHALL ensure modifications follow the repository's existing code style and conventions by checking for linter configuration files (pyproject.toml, setup.cfg, .flake8, .pylintrc) and applying matching style rules
4. WHEN changes are complete, THE Workflow_Engine SHALL run the repository's existing test suite to verify no regressions are introduced
5. IF the test suite fails after changes are made, THEN THE Workflow_Engine SHALL identify which tests failed, explain the likely cause, and suggest specific corrections before proceeding
6. IF the repository has no test suite, THEN THE Workflow_Engine SHALL suggest adding a basic test for the contributed change
7. WHEN changes are complete, THE Workflow_Engine SHALL guide the user through staging only modified files, committing with a message that includes a type prefix, a concise subject line under 72 characters, and an optional body explaining the rationale, then pushing to the fork

### Requirement 6: Pull Request Submission

**User Story:** As a beginner contributor, I want to submit a well-formatted PR, so that maintainers can easily review and accept my contribution.

#### Acceptance Criteria

1. WHEN changes are pushed to the fork, THE Contribution_Guide SHALL create a Pull Request using the gh_CLI targeting the default branch of the original repository, with a title that follows the format "contribution-type: short description" and does not exceed 72 characters
2. THE Contribution_Guide SHALL generate PR descriptions that include: a summary of what was changed, the motivation for the change, how the change was tested, and a reference to any related issue
3. WHEN a PR template exists in the target repository, THE Contribution_Guide SHALL follow the template format instead of the default description structure in criterion 2
4. IF the user has permission to add labels to the target repository, THEN THE Contribution_Guide SHALL add labels that correspond to the Contribution_Type of the change when submitting the PR
5. IF the contribution includes UI changes, modifies behavior not covered by existing tests, or spans more than 3 files, THEN THE Contribution_Guide SHALL suggest adding screenshots, code examples, or before/after comparisons in the PR description
6. IF the fork branch has merge conflicts with the target default branch, THEN THE Contribution_Guide SHALL notify the user and provide instructions to resolve conflicts before submitting the PR

### Requirement 7: Contribution Difficulty Progression

**User Story:** As a beginner contributor, I want to start with easy contributions and work up to harder ones, so that I build confidence gradually.

#### Acceptance Criteria

1. THE Workflow_Engine SHALL define three Difficulty_Level tiers: easy (documentation fixes, adding type hints, improving error messages, single-line bug fixes, adding missing imports), medium (adding tests, fixing bugs referenced in issues), and hard (adding features, refactoring code)
2. WHEN the user completes a contribution (defined as the PR being merged or the contribution being recorded in the tracker as submitted), THE Workflow_Engine SHALL suggest the next contribution at the same Difficulty_Level until the user has completed at least 2 contributions at that level, after which it SHALL suggest a contribution at the next higher level
3. WHEN recommending a new contribution, THE Workflow_Engine SHALL reference at least one specific skill from the user's most recent contribution by naming the Contribution_Type completed and how it relates to the recommended next contribution
4. THE Workflow_Engine SHALL track completed contributions with their Difficulty_Level, repository name, Contribution_Type, and completion date
5. IF the user has no previously tracked contributions, THEN THE Workflow_Engine SHALL recommend an easy Difficulty_Level contribution as the first suggestion

### Requirement 8: Blog Post Generation

**User Story:** As a new contributor, I want a blog post documenting my journey, so that I can share my experience and show that beginners can contribute to open source using AI-assisted tools.

#### Acceptance Criteria

1. WHEN the user completes at least one contribution where a pull request has been opened or merged, THE Blog_Generator SHALL produce a markdown file documenting the contribution journey within 60 seconds of invocation
2. THE Blog_Generator SHALL structure the blog post with the following sections in order: introduction (who the author is and their starting skill level), the discovery process (how repos were found), the contribution process (step-by-step walkthrough), what was learned, and next steps, where each section contains at least one paragraph of content
3. THE Blog_Generator SHALL include the narrative angle: how someone with limited coding experience can become a contributor using AI-assisted tools
4. WHEN generating the blog post, THE Blog_Generator SHALL include at least one specific example per contribution made, including the repository name, PR link, and a relevant code snippet for each
5. IF contribution data is incomplete such that a repository name or PR link is unavailable, THEN THE Blog_Generator SHALL generate the blog post using available data and indicate placeholders for missing information
6. THE Blog_Generator SHALL write in first person, conversational tone at a reading level accessible to beginners with no more than 10% jargon terms left undefined in context
7. WHEN the blog post is complete, THE Blog_Generator SHALL save the output as a markdown file named with the pattern "blog-post-YYYY-MM-DD.md" in the project workspace
8. THE Blog_Generator SHALL produce a blog post between 500 and 3000 words in total length

### Requirement 9: Contribution Validation

**User Story:** As a beginner contributor, I want to verify my contribution meets quality standards before submitting, so that I don't submit work that will be rejected.

#### Acceptance Criteria

1. WHEN the contributor initiates pre-submission validation, THE Workflow_Engine SHALL run a checklist covering: code style compliance, test passage, commit message format, and branch cleanliness (no merge conflicts, no untracked files, and a linear commit history relative to the target branch)
2. IF any checklist item fails, THEN THE Workflow_Engine SHALL display the name of the failed item and a step-by-step remediation instruction for each failure before allowing submission to proceed
3. WHEN validating commit messages, THE Workflow_Engine SHALL ensure messages follow conventional commit format (type, optional scope, description with subject line no longer than 72 characters) or the repository's stated conventions if defined in repository configuration
4. WHEN validating changes, THE Workflow_Engine SHALL compare the set of modified files against the directories and modules touched by the contributor's commits and flag any modified file that falls outside those directories as a potential unintended change
5. IF the contribution modifies existing tests, THEN THE Workflow_Engine SHALL execute the full test suite and report pass or fail within a repository-configured timeout (default 300 seconds)
6. WHEN all checklist items pass, THE Workflow_Engine SHALL display a confirmation summary indicating the contribution is ready for submission
7. IF the validation infrastructure is unavailable (linter, test runner, or repository metadata cannot be accessed), THEN THE Workflow_Engine SHALL inform the contributor which validation step could not be completed and prevent submission until validation can be re-run successfully

### Requirement 10: Reusable Steering Document

**User Story:** As a repeat contributor, I want a reusable Kiro steering document that captures the proven contribution workflow, so that I can invoke it in any future project without re-explaining the process.

#### Acceptance Criteria

1. WHEN the first contribution is successfully submitted (PR opened), THE Workflow_Engine SHALL produce a steering file at the user-level location (~/.kiro/steering/open-source-contribution.md)
2. THE steering document SHALL include the complete contribution workflow as step-by-step instructions Kiro can follow: repo discovery, evaluation, environment check, fork/branch, make changes, validate, submit PR, and post-submission guidance
3. THE steering document SHALL use the "inclusion: manual" front-matter so the user can invoke it on demand via the # context key in any workspace
4. THE steering document SHALL be written as directives to Kiro (second person: "you shall...") rather than documentation for a human reader
5. WHEN the user completes additional contributions and identifies workflow improvements, THE Workflow_Engine SHALL update the steering document to incorporate lessons learned
6. THE steering document SHALL include configurable parameters at the top (interest areas, difficulty level, time budget) that the user can adjust per session

### Requirement 11: Post-Submission Guidance

**User Story:** As a beginner contributor, I want to know what happens after I submit a PR, so that I can respond to maintainer feedback appropriately.


#### Acceptance Criteria

1. WHEN a PR is submitted, THE Contribution_Guide SHALL display a post-submission overview that includes the expected review timeline (stated as a range in business days), a description of automated CI checks that will run, and instructions on how to monitor the PR status
2. WHEN a maintainer requests changes, THE Contribution_Guide SHALL explain how to push additional commits to the same PR branch, including at least the steps to make changes locally, commit them, and push to the existing branch
3. WHEN a PR is merged, THE Contribution_Guide SHALL display a success confirmation message and increment the user's contribution count in the contribution tracker
4. IF a PR is rejected, THEN THE Contribution_Guide SHALL display at least 3 common rejection reasons and for each reason provide at least one actionable suggestion for improvement on the next attempt
5. THE Contribution_Guide SHALL explain GitHub notification settings so the user can monitor PR activity
6. IF one or more CI checks fail after PR submission, THEN THE Contribution_Guide SHALL explain how to view the CI check results and how to push fixes to the same PR branch to re-trigger the checks
