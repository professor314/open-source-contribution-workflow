"""Review Response Helper: read and respond to PR review feedback.

Fetches review comments, inline suggestions, and general comments from PRs
via the gh CLI. Summarizes what maintainers want and helps draft responses
or push follow-up commits.
"""

from __future__ import annotations

import json
import subprocess
from typing import Any, Dict, List, Optional


def get_pr_reviews(repo: str, pr_number: int) -> List[Dict[str, Any]]:
    """Fetch all reviews for a PR.

    Args:
        repo: Full repo name (e.g., "owner/repo-name")
        pr_number: The PR number

    Returns:
        List of review dicts with author, state, body, and submitted date.
    """
    cmd = [
        "gh", "pr", "view", str(pr_number),
        "--repo", repo,
        "--json", "reviews"
    ]
    result = _run_gh(cmd)
    if result is None:
        return []
    return result.get("reviews", [])


def get_pr_comments(repo: str, pr_number: int) -> List[Dict[str, Any]]:
    """Fetch all comments on a PR (not inline review comments).

    Args:
        repo: Full repo name
        pr_number: The PR number

    Returns:
        List of comment dicts with author, body, and created date.
    """
    cmd = [
        "gh", "pr", "view", str(pr_number),
        "--repo", repo,
        "--json", "comments"
    ]
    result = _run_gh(cmd)
    if result is None:
        return []
    return result.get("comments", [])


def get_review_comments(repo: str, pr_number: int) -> List[Dict[str, Any]]:
    """Fetch inline review comments (comments on specific lines of code).

    Args:
        repo: Full repo name
        pr_number: The PR number

    Returns:
        List of inline comment dicts with path, line, body, and author.
    """
    cmd = [
        "gh", "api",
        f"repos/{repo}/pulls/{pr_number}/comments",
        "--jq", ".[] | {path: .path, line: .line, body: .body, author: .user.login, created_at: .created_at}"
    ]

    try:
        proc = subprocess.run(cmd, capture_output=True, text=True, timeout=30, errors="replace")
    except (subprocess.TimeoutExpired, FileNotFoundError):
        return []

    if proc.returncode != 0 or not proc.stdout:
        return []

    comments = []
    for line in proc.stdout.strip().split("\n"):
        if line.strip():
            try:
                comments.append(json.loads(line))
            except json.JSONDecodeError:
                continue
    return comments


def summarize_feedback(repo: str, pr_number: int) -> Dict[str, Any]:
    """Get a complete summary of all feedback on a PR.

    Args:
        repo: Full repo name
        pr_number: The PR number

    Returns:
        Dict with:
        - status: overall review state (approved, changes_requested, commented, pending)
        - reviews: list of reviews with author and state
        - action_items: list of specific things the maintainer wants changed
        - comments: general discussion comments
        - inline_comments: code-specific feedback
    """
    reviews = get_pr_reviews(repo, pr_number)
    comments = get_pr_comments(repo, pr_number)
    inline_comments = get_review_comments(repo, pr_number)

    # Determine overall status from latest review
    status = "pending"
    for review in reversed(reviews):
        state = review.get("state", "").upper()
        if state in ("APPROVED", "CHANGES_REQUESTED"):
            status = state.lower()
            break
        elif state == "COMMENTED":
            status = "commented"

    # Extract action items from reviews that request changes
    action_items = []
    for review in reviews:
        if review.get("state") == "CHANGES_REQUESTED":
            body = review.get("body", "").strip()
            if body:
                action_items.append({
                    "from": review.get("author", {}).get("login", "unknown"),
                    "request": body,
                })

    # Add inline comments as action items too
    for comment in inline_comments:
        action_items.append({
            "from": comment.get("author", "unknown"),
            "file": comment.get("path", ""),
            "line": comment.get("line", ""),
            "request": comment.get("body", ""),
        })

    return {
        "status": status,
        "reviews": [
            {
                "author": r.get("author", {}).get("login", "unknown"),
                "state": r.get("state", ""),
                "body": r.get("body", "")[:500],
                "date": r.get("submittedAt", ""),
            }
            for r in reviews
        ],
        "action_items": action_items,
        "comments": [
            {
                "author": c.get("author", {}).get("login", "unknown"),
                "body": c.get("body", "")[:500],
                "date": c.get("createdAt", ""),
            }
            for c in comments
        ],
        "inline_comments": inline_comments,
    }


def post_pr_comment(repo: str, pr_number: int, body: str) -> bool:
    """Post a comment on a PR.

    Args:
        repo: Full repo name
        pr_number: The PR number
        body: Comment text to post

    Returns:
        True if successful, False otherwise.
    """
    cmd = [
        "gh", "pr", "comment", str(pr_number),
        "--repo", repo,
        "--body", body
    ]

    try:
        proc = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        return proc.returncode == 0
    except (subprocess.TimeoutExpired, FileNotFoundError):
        return False


def format_feedback_summary(summary: Dict[str, Any]) -> str:
    """Format a feedback summary into a readable report.

    Args:
        summary: Output from summarize_feedback()

    Returns:
        A formatted string showing all feedback and action items.
    """
    lines = []

    lines.append(f"**Status:** {summary['status']}")
    lines.append("")

    if summary["action_items"]:
        lines.append("**Action items (things they want changed):**")
        for i, item in enumerate(summary["action_items"], 1):
            author = item.get("from", "unknown")
            request = item.get("request", "").strip()
            file_info = ""
            if item.get("file"):
                file_info = f" ({item['file']}:{item.get('line', '?')})"
            lines.append(f"  {i}. [{author}]{file_info}: {request[:200]}")
        lines.append("")

    if summary["comments"]:
        lines.append("**Comments:**")
        for comment in summary["comments"]:
            author = comment.get("author", "unknown")
            body = comment.get("body", "").strip()
            if body:
                lines.append(f"  - {author}: {body[:150]}")
        lines.append("")

    if not summary["action_items"] and not summary["comments"]:
        lines.append("No feedback yet. Still waiting for review.")

    return "\n".join(lines)


def _run_gh(cmd: List[str]) -> Optional[Dict[str, Any]]:
    """Run a gh CLI command and return parsed JSON output.

    Args:
        cmd: Command list to execute

    Returns:
        Parsed JSON dict, or None on failure.
    """
    try:
        proc = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
    except (subprocess.TimeoutExpired, FileNotFoundError):
        return None

    if proc.returncode != 0:
        return None

    try:
        return json.loads(proc.stdout)
    except json.JSONDecodeError:
        return None
