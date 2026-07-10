# Future Features — v2 Ideas

Ideas for the next iteration of the toolkit. Captured during the first contribution session.

## 1. PR Status Monitor (Priority: High)

A `src/pr_monitor.py` module that checks all open PRs via `gh pr view`.

- Reports: merged, changes requested, commented, or still waiting
- Auto-updates the tracker and blog when PRs get merged
- Could be a Kiro hook that runs on session start
- Command: `gh pr list --author professor314 --state open --json number,title,repository,url`

## 2. Review Response Helper (Priority: High)

Help respond to PR review feedback without leaving Kiro.

- Read PR review comments via gh CLI
- Summarize what the maintainer wants
- Help draft a response or make requested changes
- Push follow-up commits to the same branch
- Command: `gh pr view <number> --repo <owner/repo> --json reviews,comments`

## 3. Contribution Dashboard (Priority: Medium)

A markdown summary showing contribution stats.

- Total PRs submitted, merge rate, repos contributed to
- Difficulty progression chart (easy → medium → hard)
- Time spent per contribution
- Auto-updates from tracker JSON

## 4. Repo Bookmarking (Priority: Medium)

Save interesting repos for future contributions.

- Tag with contribution opportunity type (docs, tests, bug fix, feature)
- Personal "contribution backlog" stored as JSON
- Filter by interest area, difficulty, or opportunity type
- Prevents losing good candidates found during discovery

## 5. Smart Batching (Priority: Medium)

Detect when making the same type of change across multiple files and suggest batching into one PR.

- Pattern: "You've done type hints on Normal and are about to do Bernoulli — want these in one PR?"
- Prevents appearing spammy to maintainers
- Configurable: always batch, always separate, or ask each time

## 6. First-Contact Template (Priority: Low)

Before submitting to a new repo for the first time, draft a courtesy comment on the issue.

- Template: "I'd like to work on this. Here's my planned approach: [X]. Any preferences or things I should know?"
- Makes you look like a collaborator, not a bot
- Configurable: always comment first, or only for medium+ difficulty

---

## Implementation Notes

- All features should integrate with the existing steering doc (Phase 0 and Phase 9)
- PR Monitor could be a Kiro hook (`userTriggered` or `promptSubmit`)
- Dashboard could be generated on demand as `DASHBOARD.md`
- Bookmarks stored as `.kiro/specs/open-source-contribution-workflow/state/bookmarks.json`
