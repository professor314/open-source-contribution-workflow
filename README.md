# Open Source Contribution Workflow

A structured, AI-assisted toolkit that helps beginner Python programmers make meaningful contributions to open-source projects on GitHub. Built with [Kiro](https://kiro.dev) in 57 tokens.

## What This Does

This project provides a complete workflow for discovering, evaluating, and contributing to small open-source Python repositories. It's designed for people who:

- Know basic Python but haven't contributed to open source before
- Want to submit real PRs (not just typo fixes) but don't know where to start
- Want a guided, repeatable process they can use across multiple projects

The workflow handles everything: finding repos that match your interests, evaluating difficulty, forking/branching, validating your changes, submitting PRs, and documenting the journey.

## How It Works

Kiro (an AI-powered development environment) acts as the execution engine. You collaborate and make decisions; Kiro handles the git mechanics, GitHub API interactions, code analysis, and PR formatting.

The project includes:
- **13 Python helper modules** for scoring repos, filtering candidates, classifying difficulty, generating branch names/commit messages/PR descriptions, validation, and more
- **50+ property-based tests** (using Hypothesis) verifying correctness properties
- **A reusable Kiro steering document** you can invoke in any future workspace
- **A blog post generator** that documents your contribution journey

## Quick Start

### Prerequisites

- Python 3.8+
- Git (configured with user.name and user.email)
- [GitHub CLI](https://cli.github.com/) (`gh`) installed and authenticated

### Install Dependencies

```bash
pip install -r requirements.txt
```

### Run Tests

```bash
python -m pytest tests/ -v
```

### Use the Workflow

1. Open this project in Kiro
2. Invoke the steering document: reference `open-source-contribution.md` from your `~/.kiro/steering/` directory
3. Tell Kiro your interest areas and it will find repos, propose contributions, and walk you through the entire PR process

## Project Structure

```
├── src/                          # Helper modules
│   ├── models.py                 # Data models (CandidateRepo, ContributionRecord, etc.)
│   ├── state.py                  # JSON state management (load/save tracker)
│   ├── scoring.py                # Composite scoring for repo ranking
│   ├── filtering.py              # Candidate filtering (labels + keywords + activity)
│   ├── classification.py         # Difficulty classification (easy/medium/hard)
│   ├── naming.py                 # Branch name generation and validation
│   ├── commit_format.py          # Conventional commit message generation/validation
│   ├── pr_format.py              # PR title and description generation
│   ├── validation.py             # Pre-submission validation engine
│   ├── progression.py            # Difficulty progression recommender
│   ├── license_detection.py      # OSI license detection
│   ├── contributing_summary.py   # CONTRIBUTING.md summarization
│   ├── linter_detection.py       # Linter config detection
│   ├── blog_generator.py         # Blog post generation
│   ├── steering_generator.py     # Kiro steering document generation
│   ├── pr_monitor.py             # PR status monitoring (merged/closed/waiting/CI)
│   ├── review_helper.py          # Review feedback reader and response helper
│   ├── dashboard.py              # Contribution stats dashboard generator
│   └── bookmarks.py              # Repo bookmarking for contribution backlog
├── tests/
│   ├── unit/                     # Unit tests
│   └── property/                 # Property-based tests (Hypothesis)
├── .kiro/specs/                  # Spec documents (requirements, design, tasks)
├── FUTURE_FEATURES.md            # Roadmap for v2 features
├── requirements.txt              # Python dependencies
├── LICENSE                       # MIT License
└── README.md                     # This file
```

## The Spec

This project was built spec-first using Kiro's structured workflow:

1. **Requirements** (11 requirements with EARS-patterned acceptance criteria)
2. **Technical Design** (9 modules, 19 correctness properties, data models, error handling)
3. **Task List** (46 tasks executed in dependency order)

The full spec lives in `.kiro/specs/open-source-contribution-workflow/`.

## Correctness Properties

The test suite validates 19 formal correctness properties including:
- Candidate filtering only returns repos meeting criteria
- Composite scores are sorted non-increasing, capped at 10
- Branch names match `^[a-z]+/[a-z0-9-]+$` and are ≤50 chars
- Commit messages round-trip (generated messages pass the validator)
- Difficulty progression promotes after 2 completions at a level
- Blog word count stays within 500-3000 words
- Validation reports "all passed" iff every check passes

## Built With

- **[Kiro](https://kiro.dev)** — AI-powered development environment (execution engine)
- **[Hypothesis](https://hypothesis.readthedocs.io/)** — Property-based testing
- **[pytest](https://pytest.org/)** — Test runner
- **[GitHub CLI](https://cli.github.com/)** — Fork/PR operations

## Cost

This entire project (spec + 13 modules + 50+ tests + documentation) was built in **57 tokens** using Kiro.

## License

MIT — see [LICENSE](LICENSE).

## Contributing

Contributions welcome! This project follows its own workflow:
1. Fork the repo
2. Create a feature branch (`fix/your-change` or `feat/your-feature`)
3. Make changes following existing code style
4. Run `python -m pytest tests/ -v` to verify
5. Submit a PR with a conventional commit message

## Author

Sean Connolly ([@professor314](https://github.com/professor314))
