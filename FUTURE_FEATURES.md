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

## 7. Code of Conduct Compliance (Priority: High)

Check repos for a CODE_OF_CONDUCT.md and summarize key rules before contributing.

- Parse and flag any rules that affect contribution behavior
- Ensure our workflow respects stated community norms
- If a repo has strict conduct rules (e.g., "no unsolicited PRs"), warn the user before proceeding

## 8. Contributing Guidelines Adherence (Priority: High)

Automatically parse and enforce CONTRIBUTING.md requirements.

- Detect if they require opening an issue first before PRs
- Detect branch naming conventions different from ours
- Detect required PR template fields and ensure we fill them all
- Detect testing requirements (e.g., "run tox", "all tests must pass")
- Detect commit message conventions different from conventional commits
- If the repo says "comment on the issue to claim it first," do that before working

## 9. Stale Issue Detection (Priority: Medium)

Before working on an issue, check if it's actually still relevant.

- Check issue age. If over 1 year old and no recent comments, it might be stale
- Check if someone else already has an open PR for it
- Check if the code referenced in the issue still exists
- If the repo's last commit is older than our activity filter, warn the user

## 10. Repo Relationship Tracker (Priority: High)

Track your history with each repo to inform future contribution decisions.

- First contact date
- Number of PRs submitted and how many merged/closed/open
- Whether the maintainer was responsive (and how fast)
- Whether they flagged AI concerns or rejected contributions
- A "disposition" field: friendly, neutral, cautious, avoid
- Example output: "lockwo/distreqx: 3 PRs (0 merged, 1 closed as AI, 2 pending). Disposition: cautious"
- Automatically updated when PR monitor detects status changes

## 11. GitHub Profile Sync (Priority: Medium)

Pull all PRs from GitHub and auto-populate the tracker with anything missing.

- Command: `gh pr list --author professor314 --state all --json number,title,repository,state,mergedAt`
- Compare against tracker and add any PRs not already recorded
- Catches contributions made outside this workflow (e.g., via web UI)
- Run on session start as part of Phase 0

## 12. Blacklist (Priority: High)

A simple list of repos and maintainers to avoid contributing to.

- Stored as JSON: `state/blacklist.json`
- Fields: repo name, reason, date added
- Checked during Phase 1 (Discovery) and Phase 2 (Evaluation)
- If a repo is on the blacklist, skip it silently during discovery
- If a user manually picks a blacklisted repo, warn them with the reason
- Auto-add repos when: maintainer closes PR citing AI, maintainer is hostile, repo bans AI contributions

## 13. Contribution Calendar/Pacing (Priority: Medium)

Track contribution timing and suggest healthy pacing to avoid spam patterns.

- Record timestamps of all PR submissions
- Warn if submitting more than 5 PRs in a day
- Suggest a sustainable cadence: 2-3 PRs per week spread across different repos
- Show a "contribution heatmap" in the dashboard (days with activity)
- Flag burst patterns: "You submitted 10 PRs on July 9 and nothing since. Consider spacing them out."

## 14. PR Follow-Up Reminders (Priority: Medium)

Track how long PRs have been open and suggest follow-up actions.

- 7 days with no response: suggest a polite ping comment ("Just checking in, any feedback on this?")
- 14 days with no response: suggest closing the PR yourself (repo is likely inactive)
- 30+ days: auto-flag as "abandoned" in the tracker and suggest removing from active monitoring
- Never auto-ping. Always ask the user first.

## 15. Duplicate Detection (Priority: High)

Before starting work on an issue, check if someone else already has a PR for it.

- Command: `gh pr list --repo <owner/repo> --state open --search "<issue number or keywords>"`
- Also check the issue thread for comments like "I'm working on this" or "PR incoming"
- If a duplicate PR exists, warn the user and suggest a different issue
- If someone claimed the issue in comments less than 7 days ago, suggest waiting or picking another
- Would have prevented the Foam-Agent #21 situation (someone beat us by 14 hours)

---

## Implementation Notes

- All features should integrate with the existing steering doc (Phase 0 and Phase 9)
- PR Monitor could be a Kiro hook (`userTriggered` or `promptSubmit`)
- Dashboard could be generated on demand as `DASHBOARD.md`
- Bookmarks stored as `.kiro/specs/open-source-contribution-workflow/state/bookmarks.json`
