"""PR Status Monitor: checks all open PRs for updates.

Runs gh CLI commands to check the status of all PRs in the contribution
tracker. Reports merges, change requests, comments, and CI status.
Updates the tracker automatically when PRs are merged or closed.
"""

from __future__ import annotations

import json
import subprocess
from datetime import datetime, timezone
from typing import Any, Dict, List

from src.models import ContributionTracker
from src.state import load_tracker, save_tracker


# Status categories for reporting
STATUS_MERGED = "merged"
STATUS_CLOSED = "closed"
STATUS_CHANGES_REQUESTED = "changes_requested"
STATUS_COMMENTED = "commented"
STATUS_WAITING = "waiting"
STATUS_CI_FAILED = "ci_failed"


def check_pr_status(repo: str, pr_number: int) -> Dict[str, Any]:
    """Check the current status of a single PR via gh CLI.

    Args:
        repo: Full repo name (e.g., "owner/repo-name")
        pr_number: The PR number to check

    Returns:
        Dict with keys: state, merged, reviews, comments, ci_status
    """
    cmd = [
        "gh", "pr", "view", str(pr_number),
        "--repo", repo,
        "--json", "state,mergedAt,reviews,comments,statusCheckRollup"
    ]

    try:
        result = subprocess.run(
            cmd, capture_output=True, text=True, timeout=30
        )
    except (subprocess.TimeoutExpired, FileNotFoundError):
        return {"state": "unknown", "error": "gh CLI unavailable or timed out"}

    if result.returncode != 0:
        return {"state": "unknown", "error": result.stderr.strip()}

    try:
        data = json.loads(result.stdout)
    except json.JSONDecodeError:
        return {"state": "unknown", "error": "Failed to parse gh output"}

    return data


def classify_pr_status(pr_data: Dict[str, Any]) -> str:
    """Classify a PR into a simple status category.

    Args:
        pr_data: Raw data from check_pr_status()

    Returns:
        One of: merged, closed, changes_requested, commented, ci_failed, waiting
    """
    if pr_data.get("state") == "unknown":
        return STATUS_WAITING

    state = pr_data.get("state", "").upper()

    if state == "MERGED" or pr_data.get("mergedAt"):
        return STATUS_MERGED

    if state == "CLOSED":
        return STATUS_CLOSED

    # Check reviews for change requests
    reviews = pr_data.get("reviews", [])
    for review in reviews:
        if review.get("state") == "CHANGES_REQUESTED":
            return STATUS_CHANGES_REQUESTED

    # Check for CI failures
    checks = pr_data.get("statusCheckRollup", [])
    for check in checks:
        if check.get("conclusion") == "FAILURE":
            return STATUS_CI_FAILED

    # Check for new comments
    comments = pr_data.get("comments", [])
    if comments:
        return STATUS_COMMENTED

    return STATUS_WAITING


def get_latest_feedback(pr_data: Dict[str, Any]) -> str:
    """Extract the most recent feedback from a PR.

    Args:
        pr_data: Raw data from check_pr_status()

    Returns:
        A human-readable summary of the latest feedback, or empty string.
    """
    # Check reviews first (most actionable)
    reviews = pr_data.get("reviews", [])
    if reviews:
        latest_review = reviews[-1]
        author = latest_review.get("author", {}).get("login", "unknown")
        body = latest_review.get("body", "").strip()
        state = latest_review.get("state", "")
        if body:
            return f"Review from {author} ({state}): {body[:200]}"

    # Then comments
    comments = pr_data.get("comments", [])
    if comments:
        latest_comment = comments[-1]
        author = latest_comment.get("author", {}).get("login", "unknown")
        body = latest_comment.get("body", "").strip()
        if body:
            return f"Comment from {author}: {body[:200]}"

    return ""


def check_all_prs(tracker_path: str) -> List[Dict[str, Any]]:
    """Check status of all PRs in the contribution tracker.

    Args:
        tracker_path: Path to the contribution_tracker.json file

    Returns:
        List of status reports, one per PR, each containing:
        - repo, pr_number, pr_url, title (from tracker)
        - status (classified category)
        - feedback (latest feedback text)
        - changed (bool: whether status changed from what tracker had)
    """
    tracker = load_tracker(tracker_path)
    reports = []

    for contribution in tracker.contributions:
        if not contribution.pr_url or not contribution.repo_full_name:
            continue

        pr_data = check_pr_status(
            contribution.repo_full_name,
            contribution.pr_number
        )

        status = classify_pr_status(pr_data)
        feedback = get_latest_feedback(pr_data)
        old_status = contribution.pr_status

        # Determine if status changed
        changed = False
        if status == STATUS_MERGED and old_status != "merged":
            changed = True
        elif status == STATUS_CLOSED and old_status != "closed":
            changed = True
        elif status in (STATUS_CHANGES_REQUESTED, STATUS_COMMENTED, STATUS_CI_FAILED):
            changed = True  # Always flag these as needing attention

        reports.append({
            "repo": contribution.repo_full_name,
            "pr_number": contribution.pr_number,
            "pr_url": contribution.pr_url,
            "contribution_type": contribution.contribution_type,
            "old_status": old_status,
            "new_status": status,
            "feedback": feedback,
            "changed": changed,
            "needs_attention": status in (
                STATUS_CHANGES_REQUESTED, STATUS_COMMENTED, STATUS_CI_FAILED
            ),
        })

    return reports


def update_tracker_from_reports(
    tracker_path: str, reports: List[Dict[str, Any]]
) -> int:
    """Update the tracker with new PR statuses from monitoring reports.

    Args:
        tracker_path: Path to the contribution_tracker.json file
        reports: List of reports from check_all_prs()

    Returns:
        Number of contributions whose status was updated.
    """
    tracker = load_tracker(tracker_path)
    updated_count = 0

    for report in reports:
        if not report["changed"]:
            continue

        for contribution in tracker.contributions:
            if contribution.pr_number == report["pr_number"] and \
               contribution.repo_full_name == report["repo"]:
                new_status = report["new_status"]
                if new_status == STATUS_MERGED:
                    contribution.pr_status = "merged"
                    updated_count += 1
                elif new_status == STATUS_CLOSED:
                    contribution.pr_status = "closed"
                    updated_count += 1

    if updated_count > 0:
        save_tracker(tracker, tracker_path)

    return updated_count


def format_status_report(reports: List[Dict[str, Any]]) -> str:
    """Format monitoring reports into a readable summary.

    Args:
        reports: List of reports from check_all_prs()

    Returns:
        A formatted string summarizing all PR statuses.
    """
    if not reports:
        return "No PRs to monitor."

    lines = ["# PR Status Report", ""]

    # Group by status
    merged = [r for r in reports if r["new_status"] == STATUS_MERGED]
    needs_attention = [r for r in reports if r["needs_attention"]]
    waiting = [r for r in reports if r["new_status"] == STATUS_WAITING]
    closed = [r for r in reports if r["new_status"] == STATUS_CLOSED]

    if merged:
        lines.append("## Merged!")
        for r in merged:
            lines.append(f"- [{r['repo']} #{r['pr_number']}]({r['pr_url']})")
        lines.append("")

    if needs_attention:
        lines.append("## Needs Your Attention")
        for r in needs_attention:
            status_label = r["new_status"].replace("_", " ").title()
            lines.append(f"- [{r['repo']} #{r['pr_number']}]({r['pr_url']}) ({status_label})")
            if r["feedback"]:
                lines.append(f"  > {r['feedback']}")
        lines.append("")

    if waiting:
        lines.append("## Waiting for Review")
        for r in waiting:
            lines.append(f"- [{r['repo']} #{r['pr_number']}]({r['pr_url']})")
        lines.append("")

    if closed:
        lines.append("## Closed")
        for r in closed:
            lines.append(f"- [{r['repo']} #{r['pr_number']}]({r['pr_url']})")
        lines.append("")

    # Summary
    lines.append(f"**Total:** {len(reports)} PRs tracked | "
                 f"{len(merged)} merged | {len(needs_attention)} need attention | "
                 f"{len(waiting)} waiting | {len(closed)} closed")

    return "\n".join(lines)
