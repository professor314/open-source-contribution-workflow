"""Repo Bookmarking: save interesting repos for future contributions.

Maintains a JSON file of bookmarked repos tagged with opportunity type,
difficulty, and interest area. Acts as a personal contribution backlog.
"""

from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional


DEFAULT_BOOKMARKS_PATH = ".kiro/specs/open-source-contribution-workflow/state/bookmarks.json"


def load_bookmarks(path: str = DEFAULT_BOOKMARKS_PATH) -> List[Dict[str, Any]]:
    """Load bookmarks from JSON file.

    Args:
        path: Path to the bookmarks JSON file.

    Returns:
        List of bookmark dicts. Empty list if file doesn't exist.
    """
    if not os.path.exists(path):
        return []

    with open(path, "r", encoding="utf-8") as f:
        try:
            data = json.load(f)
        except json.JSONDecodeError:
            return []

    return data if isinstance(data, list) else []


def save_bookmarks(bookmarks: List[Dict[str, Any]], path: str = DEFAULT_BOOKMARKS_PATH) -> None:
    """Save bookmarks to JSON file.

    Args:
        bookmarks: List of bookmark dicts to save.
        path: Path to the bookmarks JSON file.
    """
    directory = os.path.dirname(path)
    if directory:
        os.makedirs(directory, exist_ok=True)

    with open(path, "w", encoding="utf-8") as f:
        json.dump(bookmarks, f, indent=2, ensure_ascii=False)
        f.write("\n")


def add_bookmark(
    repo: str,
    description: str,
    opportunity_type: str,
    difficulty: str = "unknown",
    interest_area: str = "",
    issue_url: str = "",
    notes: str = "",
    path: str = DEFAULT_BOOKMARKS_PATH,
) -> Dict[str, Any]:
    """Add a repo to the bookmarks.

    Args:
        repo: Full repo name (e.g., "owner/repo-name")
        description: Short description of the repo
        opportunity_type: Type of contribution opportunity (docs, tests, bug_fix, feature, etc.)
        difficulty: Estimated difficulty (easy, medium, hard, unknown)
        interest_area: Which interest area this matches
        issue_url: Optional URL to a specific issue
        notes: Optional notes about what to contribute

    Returns:
        The bookmark dict that was added.
    """
    bookmarks = load_bookmarks(path)

    # Don't duplicate
    for b in bookmarks:
        if b.get("repo") == repo and b.get("issue_url") == issue_url:
            return b  # Already bookmarked

    bookmark = {
        "repo": repo,
        "description": description,
        "opportunity_type": opportunity_type,
        "difficulty": difficulty,
        "interest_area": interest_area,
        "issue_url": issue_url,
        "notes": notes,
        "added_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "status": "pending",  # pending, in_progress, done, skipped
    }

    bookmarks.append(bookmark)
    save_bookmarks(bookmarks, path)
    return bookmark


def remove_bookmark(
    repo: str,
    issue_url: str = "",
    path: str = DEFAULT_BOOKMARKS_PATH,
) -> bool:
    """Remove a bookmark by repo name and optional issue URL.

    Args:
        repo: Full repo name
        issue_url: Optional issue URL to match specific bookmark

    Returns:
        True if a bookmark was removed, False if not found.
    """
    bookmarks = load_bookmarks(path)
    original_len = len(bookmarks)

    if issue_url:
        bookmarks = [b for b in bookmarks if not (b["repo"] == repo and b.get("issue_url") == issue_url)]
    else:
        bookmarks = [b for b in bookmarks if b["repo"] != repo]

    if len(bookmarks) < original_len:
        save_bookmarks(bookmarks, path)
        return True
    return False


def update_bookmark_status(
    repo: str,
    status: str,
    issue_url: str = "",
    path: str = DEFAULT_BOOKMARKS_PATH,
) -> bool:
    """Update the status of a bookmark.

    Args:
        repo: Full repo name
        status: New status (pending, in_progress, done, skipped)
        issue_url: Optional issue URL to match specific bookmark

    Returns:
        True if updated, False if not found.
    """
    bookmarks = load_bookmarks(path)

    for b in bookmarks:
        if b["repo"] == repo:
            if issue_url and b.get("issue_url") != issue_url:
                continue
            b["status"] = status
            save_bookmarks(bookmarks, path)
            return True

    return False


def list_bookmarks(
    filter_type: Optional[str] = None,
    filter_difficulty: Optional[str] = None,
    filter_interest: Optional[str] = None,
    filter_status: str = "pending",
    path: str = DEFAULT_BOOKMARKS_PATH,
) -> List[Dict[str, Any]]:
    """List bookmarks with optional filters.

    Args:
        filter_type: Only show this opportunity type
        filter_difficulty: Only show this difficulty
        filter_interest: Only show this interest area
        filter_status: Only show this status (default: pending)

    Returns:
        Filtered list of bookmarks.
    """
    bookmarks = load_bookmarks(path)
    results = []

    for b in bookmarks:
        if filter_status and b.get("status") != filter_status:
            continue
        if filter_type and b.get("opportunity_type") != filter_type:
            continue
        if filter_difficulty and b.get("difficulty") != filter_difficulty:
            continue
        if filter_interest and filter_interest.lower() not in b.get("interest_area", "").lower():
            continue
        results.append(b)

    return results


def format_bookmarks(bookmarks: List[Dict[str, Any]]) -> str:
    """Format bookmarks into a readable list.

    Args:
        bookmarks: List of bookmark dicts

    Returns:
        Formatted markdown string.
    """
    if not bookmarks:
        return "No bookmarks found."

    lines = ["# Bookmarked Repos", ""]
    lines.append("| # | Repo | Type | Difficulty | Interest | Notes |")
    lines.append("|---|------|------|------------|----------|-------|")

    for i, b in enumerate(bookmarks, 1):
        repo = b.get("repo", "?")
        opp_type = b.get("opportunity_type", "?")
        difficulty = b.get("difficulty", "?")
        interest = b.get("interest_area", "")
        notes = b.get("notes", "")[:50]
        lines.append(f"| {i} | {repo} | {opp_type} | {difficulty} | {interest} | {notes} |")

    return "\n".join(lines)
