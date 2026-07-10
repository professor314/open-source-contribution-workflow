"""Difficulty progression recommender for the contribution workflow.

Suggests the next difficulty level based on the user's contribution history,
encouraging gradual skill building from easy → medium → hard.
"""

from typing import Dict

from src.models import ContributionTracker


# Ordered difficulty levels for progression
DIFFICULTY_LEVELS = ["easy", "medium", "hard"]

# Minimum completions at a level before recommending the next level up
COMPLETIONS_BEFORE_PROMOTION = 2


def recommend_next_difficulty(tracker: ContributionTracker) -> Dict[str, str]:
    """Recommend the next difficulty level based on contribution history.

    Logic:
    - If no contributions exist, recommend "easy" (starting point).
    - Stay at the same difficulty level until the user has completed at least 2
      contributions at that level.
    - After 2 completions at a level, suggest the next higher level.
    - If already at "hard" with 2+ completions, stay at "hard".
    - Always reference the Contribution_Type of the most recent contribution.

    Args:
        tracker: The user's ContributionTracker with contribution history.

    Returns:
        A dict with keys:
            - "recommended_level": "easy" | "medium" | "hard"
            - "reason": explanation referencing recent contribution type
            - "recent_contribution_type": the type of the last contribution, or ""
    """
    # No contributions yet — start at easy
    if not tracker.contributions:
        return {
            "recommended_level": "easy",
            "reason": "This is your starting point. Begin with easy contributions to build confidence.",
            "recent_contribution_type": "",
        }

    # Get the most recent contribution
    most_recent = tracker.contributions[-1]
    recent_type = most_recent.contribution_type
    current_level = most_recent.difficulty_level

    # Count completions at the current level
    completions_at_current = tracker.level_counts.get(current_level, 0)

    # Determine recommended level
    if completions_at_current >= COMPLETIONS_BEFORE_PROMOTION:
        # Promote to next level if possible
        current_index = DIFFICULTY_LEVELS.index(current_level) if current_level in DIFFICULTY_LEVELS else 0
        next_index = min(current_index + 1, len(DIFFICULTY_LEVELS) - 1)
        recommended_level = DIFFICULTY_LEVELS[next_index]
    else:
        # Stay at current level
        recommended_level = current_level

    # Build the reason string
    if recommended_level == current_level:
        if current_level == "hard":
            reason = (
                f"You've completed {completions_at_current} hard contribution(s) "
                f"including {recent_type}. Continue at hard level to deepen your expertise."
            )
        else:
            remaining = COMPLETIONS_BEFORE_PROMOTION - completions_at_current
            reason = (
                f"Your recent {recent_type} contribution was at {current_level} level. "
                f"Complete {remaining} more at this level before advancing."
            )
    else:
        reason = (
            f"Great work completing {completions_at_current} {current_level} contributions "
            f"including {recent_type}. You're ready to move up to {recommended_level} level."
        )

    return {
        "recommended_level": recommended_level,
        "reason": reason,
        "recent_contribution_type": recent_type,
    }
