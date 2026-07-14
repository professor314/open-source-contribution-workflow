"""Contribution Dashboard: generates a markdown summary of contribution stats.

Reads the contribution tracker and produces a formatted overview of total PRs,
merge rate, repos contributed to, difficulty progression, and status breakdown.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List

from src.models import ContributionTracker
from src.state import load_tracker


def generate_dashboard(tracker_path: str) -> str:
    """Generate a markdown dashboard from the contribution tracker.

    Args:
        tracker_path: Path to the contribution_tracker.json file

    Returns:
        A formatted markdown string with contribution statistics.
    """
    tracker = load_tracker(tracker_path)
    contributions = tracker.contributions

    total = len(contributions)
    if total == 0:
        return "# Contribution Dashboard\n\nNo contributions yet. Start contributing!"

    # Count by status
    merged = sum(1 for c in contributions if c.pr_status == "merged")
    closed = sum(1 for c in contributions if c.pr_status == "closed")
    open_prs = sum(1 for c in contributions if c.pr_status == "open")

    # Merge rate (merged / (merged + closed), excluding still-open)
    decided = merged + closed
    merge_rate = (merged / decided * 100) if decided > 0 else 0

    # Unique repos
    repos = list(set(c.repo_full_name for c in contributions))

    # By type
    type_counts: Dict[str, int] = {}
    for c in contributions:
        t = c.contribution_type
        type_counts[t] = type_counts.get(t, 0) + 1

    # By difficulty
    level_counts = tracker.level_counts

    # Build markdown
    lines = [
        "# Contribution Dashboard",
        "",
        f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M')}",
        "",
        "## Summary",
        "",
        f"| Metric | Value |",
        f"|--------|-------|",
        f"| Total PRs | {total} |",
        f"| Merged | {merged} |",
        f"| Open | {open_prs} |",
        f"| Closed (not merged) | {closed} |",
        f"| Merge rate | {merge_rate:.0f}% |",
        f"| Repos contributed to | {len(repos)} |",
        "",
        "## Difficulty Progression",
        "",
        f"| Level | Count |",
        f"|-------|-------|",
        f"| Easy | {level_counts.get('easy', 0)} |",
        f"| Medium | {level_counts.get('medium', 0)} |",
        f"| Hard | {level_counts.get('hard', 0)} |",
        "",
        f"**Current level:** {tracker.user_level}",
        "",
        "## By Contribution Type",
        "",
        f"| Type | Count |",
        f"|------|-------|",
    ]

    for t, count in sorted(type_counts.items(), key=lambda x: -x[1]):
        lines.append(f"| {t.replace('_', ' ').title()} | {count} |")

    lines.extend([
        "",
        "## Repos Contributed To",
        "",
    ])

    for repo in sorted(repos):
        repo_contributions = [c for c in contributions if c.repo_full_name == repo]
        statuses = [c.pr_status for c in repo_contributions]
        merged_count = statuses.count("merged")
        lines.append(f"- **{repo}** ({len(repo_contributions)} PRs, {merged_count} merged)")

    lines.extend([
        "",
        "## Recent Activity",
        "",
        "| Date | Repo | Type | PR | Status |",
        "|------|------|------|-----|--------|",
    ])

    for c in reversed(contributions[-10:]):
        date = c.started_at[:10] if c.started_at else "?"
        status_icon = {"merged": "✅", "closed": "❌", "open": "⏳"}.get(c.pr_status, "?")
        lines.append(
            f"| {date} | {c.repo_full_name} | {c.contribution_type} | "
            f"[#{c.pr_number}]({c.pr_url}) | {status_icon} {c.pr_status} |"
        )

    return "\n".join(lines)


def save_dashboard(content: str, workspace_path: str) -> str:
    """Save dashboard to a markdown file.

    Args:
        content: The dashboard markdown content.
        workspace_path: Directory to save the file in.

    Returns:
        The file path where the dashboard was saved.
    """
    import os
    file_path = os.path.join(workspace_path, "DASHBOARD.md")
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(content)
    return file_path
