"""Core data models for the open-source contribution workflow.

All models use Python dataclasses with from_dict/to_dict helper methods
for JSON serialization and deserialization.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class CandidateRepo:
    """A repository identified as a potential target for contribution."""

    full_name: str
    description: str
    stars: int
    last_commit_date: str
    open_issues_count: int
    has_contributing_md: bool
    main_package_lines: int
    contribution_types: List[str]
    proposed_contribution: Dict[str, Any]
    difficulty_level: str
    composite_score: float
    good_first_issue_count: int
    dependency_count: int
    commits_last_90_days: int = 0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "full_name": self.full_name,
            "description": self.description[:200],
            "stars": self.stars,
            "last_commit_date": self.last_commit_date,
            "open_issues_count": self.open_issues_count,
            "has_contributing_md": self.has_contributing_md,
            "main_package_lines": self.main_package_lines,
            "contribution_types": list(self.contribution_types),
            "proposed_contribution": dict(self.proposed_contribution),
            "difficulty_level": self.difficulty_level,
            "composite_score": self.composite_score,
            "good_first_issue_count": self.good_first_issue_count,
            "dependency_count": self.dependency_count,
            "commits_last_90_days": self.commits_last_90_days,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> CandidateRepo:
        return cls(
            full_name=data["full_name"],
            description=data["description"][:200],
            stars=data["stars"],
            last_commit_date=data["last_commit_date"],
            open_issues_count=data["open_issues_count"],
            has_contributing_md=data["has_contributing_md"],
            main_package_lines=data["main_package_lines"],
            contribution_types=data.get("contribution_types", []),
            proposed_contribution=data.get("proposed_contribution", {}),
            difficulty_level=data["difficulty_level"],
            composite_score=data.get("composite_score", 0.0),
            good_first_issue_count=data.get("good_first_issue_count", 0),
            dependency_count=data.get("dependency_count", 0),
            commits_last_90_days=data.get("commits_last_90_days", 0),
        )


@dataclass
class RepoEvaluation:
    """Deep-dive evaluation results for a selected repository."""

    full_name: str
    total_lines: int
    file_count: int
    has_tests: bool
    dependency_count: int
    difficulty_level: str
    license: str
    license_verified: bool
    has_contributing_guide: bool
    contributing_summary: str
    evaluated_at: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "full_name": self.full_name,
            "total_lines": self.total_lines,
            "file_count": self.file_count,
            "has_tests": self.has_tests,
            "dependency_count": self.dependency_count,
            "difficulty_level": self.difficulty_level,
            "license": self.license,
            "license_verified": self.license_verified,
            "has_contributing_guide": self.has_contributing_guide,
            "contributing_summary": self.contributing_summary,
            "evaluated_at": self.evaluated_at,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> RepoEvaluation:
        return cls(
            full_name=data["full_name"],
            total_lines=data["total_lines"],
            file_count=data["file_count"],
            has_tests=data["has_tests"],
            dependency_count=data["dependency_count"],
            difficulty_level=data["difficulty_level"],
            license=data["license"],
            license_verified=data["license_verified"],
            has_contributing_guide=data["has_contributing_guide"],
            contributing_summary=data["contributing_summary"],
            evaluated_at=data["evaluated_at"],
        )


@dataclass
class ContributionRecord:
    """A single contribution made by the user."""

    id: str
    repo_full_name: str
    contribution_type: str
    difficulty_level: str
    branch_name: str
    pr_url: str
    pr_number: int
    pr_status: str
    commit_sha: str
    modified_files: List[str]
    code_snippet: str
    started_at: str
    completed_at: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "repo_full_name": self.repo_full_name,
            "contribution_type": self.contribution_type,
            "difficulty_level": self.difficulty_level,
            "branch_name": self.branch_name,
            "pr_url": self.pr_url,
            "pr_number": self.pr_number,
            "pr_status": self.pr_status,
            "commit_sha": self.commit_sha,
            "modified_files": list(self.modified_files),
            "code_snippet": self.code_snippet,
            "started_at": self.started_at,
            "completed_at": self.completed_at,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> ContributionRecord:
        return cls(
            id=data["id"],
            repo_full_name=data["repo_full_name"],
            contribution_type=data["contribution_type"],
            difficulty_level=data["difficulty_level"],
            branch_name=data["branch_name"],
            pr_url=data["pr_url"],
            pr_number=data["pr_number"],
            pr_status=data["pr_status"],
            commit_sha=data["commit_sha"],
            modified_files=data.get("modified_files", []),
            code_snippet=data.get("code_snippet", ""),
            started_at=data["started_at"],
            completed_at=data["completed_at"],
        )


@dataclass
class ContributionTracker:
    """Tracks user progress through contributions over time."""

    user_level: str
    contributions: List[ContributionRecord] = field(default_factory=list)
    level_counts: Dict[str, int] = field(
        default_factory=lambda: {"easy": 0, "medium": 0, "hard": 0}
    )
    interest_areas: List[str] = field(default_factory=list)
    last_updated: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "user_level": self.user_level,
            "contributions": [c.to_dict() for c in self.contributions],
            "level_counts": dict(self.level_counts),
            "interest_areas": list(self.interest_areas),
            "last_updated": self.last_updated,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> ContributionTracker:
        contributions = [
            ContributionRecord.from_dict(c) for c in data.get("contributions", [])
        ]
        return cls(
            user_level=data["user_level"],
            contributions=contributions,
            level_counts=data.get("level_counts", {"easy": 0, "medium": 0, "hard": 0}),
            interest_areas=data.get("interest_areas", []),
            last_updated=data.get("last_updated", ""),
        )


@dataclass
class EnvironmentStatus:
    """Result of environment prerequisite checks."""

    git_installed: bool
    git_version: str
    git_user_configured: bool
    gh_installed: bool
    gh_version: str
    gh_authenticated: bool
    all_checks_passed: bool
    checked_at: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "git_installed": self.git_installed,
            "git_version": self.git_version,
            "git_user_configured": self.git_user_configured,
            "gh_installed": self.gh_installed,
            "gh_version": self.gh_version,
            "gh_authenticated": self.gh_authenticated,
            "all_checks_passed": self.all_checks_passed,
            "checked_at": self.checked_at,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> EnvironmentStatus:
        return cls(
            git_installed=data["git_installed"],
            git_version=data["git_version"],
            git_user_configured=data["git_user_configured"],
            gh_installed=data["gh_installed"],
            gh_version=data["gh_version"],
            gh_authenticated=data["gh_authenticated"],
            all_checks_passed=data["all_checks_passed"],
            checked_at=data["checked_at"],
        )


@dataclass
class ValidationResult:
    """Result of pre-submission validation checks."""

    checks: List[Dict[str, Any]] = field(default_factory=list)
    all_passed: bool = True
    checked_at: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "checks": [dict(c) for c in self.checks],
            "all_passed": self.all_passed,
            "checked_at": self.checked_at,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> ValidationResult:
        return cls(
            checks=data.get("checks", []),
            all_passed=data.get("all_passed", True),
            checked_at=data.get("checked_at", ""),
        )
