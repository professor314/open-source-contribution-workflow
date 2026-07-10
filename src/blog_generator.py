"""Blog post generator for documenting the open-source contribution journey.

Produces a markdown blog post structured with introduction, discovery process,
contribution process, lessons learned, and next steps. Written in first person,
conversational tone targeting beginners using AI-assisted tools (Kiro).
"""

from __future__ import annotations

import os
from datetime import datetime

from src.models import ContributionTracker, ContributionRecord


def generate_blog_post(tracker: ContributionTracker) -> str:
    """Generate a markdown blog post from contribution tracker data.

    Args:
        tracker: A ContributionTracker with at least one contribution.

    Returns:
        A markdown string with sections: introduction, discovery process,
        contribution process, what was learned, and next steps.
        Total word count is between 500 and 3000 words.
    """
    sections = []

    # Section 1: Introduction
    sections.append(_generate_introduction(tracker))

    # Section 2: The Discovery Process
    sections.append(_generate_discovery_process(tracker))

    # Section 3: The Contribution Process
    sections.append(_generate_contribution_process(tracker))

    # Section 4: What I Learned
    sections.append(_generate_lessons_learned(tracker))

    # Section 5: Next Steps
    sections.append(_generate_next_steps(tracker))

    content = "\n\n".join(sections)

    # Ensure word count is within bounds (500-3000)
    word_count = len(content.split())
    if word_count < 500:
        content = _pad_content(content, tracker)

    return content


def save_blog_post(content: str, workspace_path: str) -> str:
    """Save blog post content to a dated markdown file.

    Args:
        content: The markdown blog post content.
        workspace_path: The workspace directory to save the file in.

    Returns:
        The full file path of the saved blog post.
    """
    today = datetime.now().strftime("%Y-%m-%d")
    filename = f"blog-post-{today}.md"
    file_path = os.path.join(workspace_path, filename)

    os.makedirs(workspace_path, exist_ok=True)

    with open(file_path, "w", encoding="utf-8") as f:
        f.write(content)

    return file_path


def _generate_introduction(tracker: ContributionTracker) -> str:
    """Generate the introduction section."""
    user_level = tracker.user_level or "beginner"
    interest_areas = tracker.interest_areas or ["open source projects"]
    interests_text = ", ".join(interest_areas) if interest_areas else "various topics"
    num_contributions = len(tracker.contributions)

    intro = f"""# My Journey Into Open Source: How a Beginner Programmer Made Real Contributions Using AI-Assisted Tools

I'm a {user_level} programmer who recently decided to take the plunge into open-source contribution. If you'd told me a few months ago that I'd be submitting pull requests to real projects on GitHub, I probably wouldn't have believed you. My coding experience was limited, and the whole world of open source felt intimidating — forking, branching, pull requests, CI pipelines... it all sounded like a foreign language.

But here I am, with {num_contributions} {"contribution" if num_contributions == 1 else "contributions"} under my belt, and I want to share how I got here. My interests lie in {interests_text}, and I was curious whether someone at my skill level could actually contribute something meaningful to projects in those areas.

The short answer? Yes. And the key was using AI-assisted tools — specifically Kiro — to guide me through the entire process. This post documents my journey from "I don't even know where to start" to "I just got a PR merged," and I hope it shows other beginners that open-source contribution isn't just for senior developers."""

    return intro


def _generate_discovery_process(tracker: ContributionTracker) -> str:
    """Generate the discovery process section."""
    interest_areas = tracker.interest_areas or ["open source projects"]
    interests_text = ", ".join(interest_areas) if interest_areas else "various topics"
    num_contributions = len(tracker.contributions)

    # Gather unique repos contributed to
    repos = list(set(c.repo_full_name for c in tracker.contributions if c.repo_full_name))

    section = f"""## The Discovery Process

Finding the right repository to contribute to was my first challenge. There are millions of repos on GitHub — how do you find one that's beginner-friendly, actively maintained, and actually needs help?

I used Kiro combined with GitHub's search capabilities to narrow things down. I started by telling Kiro my interests: {interests_text}. From there, Kiro searched GitHub for Python repositories that matched those keywords, focusing on smaller codebases (under 5,000 lines of code) that would be manageable for someone at my level.

The filtering process was methodical. Kiro looked for repos with issues labeled "good first issue" or "help wanted," checked whether they had contribution guidelines, and scored them based on how active they were (recent commits), how many open issues they had, and how small the codebase was. Smaller repos scored higher because they're easier to understand when you're just starting out.

What I found particularly helpful was that Kiro didn't just hand me a list of repos — it identified specific contributions I could make for each one. Instead of staring at a repository wondering "what could I even do here?", I had a ready-to-go queue of concrete tasks: fix this bug, add that test, improve this error message."""

    if repos:
        repo_list = ", ".join(f"`{r}`" for r in repos[:5])
        section += f"\n\nThe repositories I ended up working with included: {repo_list}. Each one was selected because it was small enough to understand quickly, active enough that maintainers would review my PR, and had clear opportunities for improvement."

    return section


def _generate_contribution_process(tracker: ContributionTracker) -> str:
    """Generate the contribution process section with per-contribution details."""
    contributions = tracker.contributions

    section = """## The Contribution Process

Here's where things got real. Let me walk you through what the actual contribution process looked like, step by step.

### Setting Up the Environment

Before making any changes, I needed to make sure my tools were ready. Kiro verified that I had git installed and configured (with my username and email set up), and that the GitHub CLI (`gh`) was authenticated. This might sound basic, but as a beginner, having someone confirm "yes, your environment is ready to go" gave me confidence to proceed.

### Making Contributions

"""

    if not contributions:
        section += "I haven't recorded any specific contributions yet, but the process is ready to go.\n"
        return section

    for i, contrib in enumerate(contributions, 1):
        section += _format_single_contribution(contrib, i)

    return section


def _format_single_contribution(contrib: ContributionRecord, index: int) -> str:
    """Format a single contribution entry with repo name, PR link, and code snippet."""
    repo_name = contrib.repo_full_name if contrib.repo_full_name else "[Repository Name Pending]"
    pr_link = contrib.pr_url if contrib.pr_url else "[PR Link Pending]"
    pr_number = contrib.pr_number if contrib.pr_number else "N/A"
    contribution_type = contrib.contribution_type or "improvement"
    difficulty = contrib.difficulty_level or "beginner"
    code_snippet = contrib.code_snippet or "# Code snippet not yet available"

    entry = f"""#### Contribution {index}: {contribution_type.replace("_", " ").title()} in `{repo_name}`

**Repository:** [{repo_name}](https://github.com/{repo_name})
**Pull Request:** [{f"PR #{pr_number}" if pr_number != "N/A" else "Link pending"}]({pr_link})
**Difficulty:** {difficulty}
**Type:** {contribution_type.replace("_", " ").title()}

For this contribution, I worked on a {contribution_type.replace("_", " ")} in the `{repo_name}` repository. The process went something like this:

1. **Fork and branch**: Kiro forked the repo to my GitHub account and created a feature branch with a descriptive name.
2. **Understand the issue**: I read through the relevant code and the issue description to understand what needed to change.
3. **Make the change**: With Kiro's guidance, I made the actual code modification.
4. **Test it**: I ran the project's test suite to make sure I didn't break anything.
5. **Submit the PR**: Kiro helped me write a clear commit message and PR description, then submitted it.

Here's a snippet of the code I contributed:

```python
{code_snippet}
```

"""
    return entry


def _generate_lessons_learned(tracker: ContributionTracker) -> str:
    """Generate the lessons learned section."""
    contributions = tracker.contributions
    num_contributions = len(contributions)

    # Determine what types of contributions were made
    types_made = list(set(c.contribution_type for c in contributions if c.contribution_type))
    types_text = ", ".join(t.replace("_", " ") for t in types_made) if types_made else "various improvements"

    section = f"""## What I Learned

After {num_contributions} {"contribution" if num_contributions == 1 else "contributions"}, here are the biggest takeaways from my open-source journey:

### 1. You Don't Need to Be an Expert

This was the most important lesson. I went in thinking I needed to fully understand an entire codebase before contributing. That's not true at all. Many contributions are focused on a single function, a single file, or even a single line. What matters is that your change provides genuine value — even fixing a typo in documentation counts if it helps future users.

### 2. AI Tools Lower the Barrier Significantly

Using Kiro as my guide meant I didn't have to memorize git commands, figure out the fork-and-branch workflow from scratch, or stress about writing the perfect commit message. Kiro handled the mechanics while I focused on understanding the actual code change. This is a game-changer for beginners.

### 3. The Git Workflow Becomes Second Nature

Fork, clone, branch, commit, push, PR — after going through the process a few times, these steps start to feel automatic. The first time was nerve-wracking; by the {_ordinal(num_contributions)} contribution, it felt routine.

### 4. Reading Code Is a Skill

Making contributions of types like {types_text} forced me to read other people's code. This is incredibly valuable practice. You learn different coding styles, discover patterns you haven't seen before, and get better at understanding unfamiliar codebases.

### 5. Maintainers Are (Usually) Friendly

I was worried about submitting something that would get harsh criticism. In reality, most maintainers are happy to see new contributors and provide constructive feedback. The worst that happens is they ask for changes — which is just another learning opportunity."""

    return section


def _generate_next_steps(tracker: ContributionTracker) -> str:
    """Generate the next steps section."""
    level_counts = tracker.level_counts or {"easy": 0, "medium": 0, "hard": 0}
    current_level = tracker.user_level or "beginner"

    # Determine progression status
    easy_done = level_counts.get("easy", 0)
    medium_done = level_counts.get("medium", 0)

    section = f"""## Next Steps

My journey is just getting started. Here's what I'm planning next:

### Leveling Up

So far I've completed {easy_done} easy-level and {medium_done} medium-level contributions. The progression system suggests staying at each difficulty level until you've completed at least two contributions there before moving up. This gradual approach builds confidence without overwhelming you.

### Broadening My Scope

I started with my specific interest areas, but I'm now curious about contributing to a wider variety of projects. The discovery process showed me that there are beginner-friendly opportunities in almost every domain — from web frameworks to data science libraries to command-line tools.

### Giving Back to the Community

One thing I want to do more of is helping other beginners get started. If you're reading this and thinking "I could never do that," I promise you: if I can do it with {current_level}-level skills, you can too. The key is having the right tools and taking that first step.

### My Advice for Fellow Beginners

1. **Start small**: Don't try to add a major feature on your first contribution. Fix a typo, add a missing test, improve an error message.
2. **Use AI tools**: Tools like Kiro can handle the scary parts (git commands, PR formatting) while you focus on the code.
3. **Pick projects you care about**: You'll be more motivated to contribute to something you actually use or find interesting.
4. **Don't be afraid of rejection**: Even experienced developers get PRs rejected sometimes. It's a learning opportunity, not a failure.
5. **Celebrate the wins**: Every merged PR, no matter how small, is a real contribution to the open-source ecosystem. Be proud of it.

---

*This blog post was generated as part of my contribution workflow, documenting the real experience of a beginner programmer becoming an open-source contributor with the help of AI-assisted tools.*"""

    return section


def _pad_content(content: str, tracker: ContributionTracker) -> str:
    """Add additional detail to ensure the content reaches the 500-word minimum."""
    padding = """

### Additional Reflections

The open-source ecosystem thrives on contributions from people at all skill levels. What surprised me most was how welcoming the community is to newcomers. There's a common misconception that you need years of experience before you can contribute — but the reality is that maintainers actively seek help with documentation, testing, error handling, and other tasks that don't require deep expertise.

One practical tip that helped me: before making any change, I always checked whether the project had a CONTRIBUTING.md file or contribution guidelines in the README. This told me what the maintainers expected in terms of code style, testing requirements, and PR format. Following these guidelines closely made my contributions more likely to be accepted on the first review.

Another thing worth mentioning is the importance of clear communication in your pull requests. A well-written PR description that explains what you changed, why you changed it, and how you tested it makes the reviewer's job much easier. Kiro helped me structure these descriptions consistently, which I think made a real difference in how quickly my PRs were reviewed.

Looking at the bigger picture, contributing to open source has given me skills that go beyond just writing code. I've learned about collaboration workflows, code review etiquette, project organization, and how to read and understand unfamiliar codebases. These are exactly the kinds of skills that make you a better developer overall, regardless of your experience level."""

    return content + padding


def _ordinal(n: int) -> str:
    """Return ordinal string for a number (1st, 2nd, 3rd, etc.)."""
    if n <= 0:
        return str(n)
    suffixes = {1: "st", 2: "nd", 3: "rd"}
    if 10 <= n % 100 <= 20:
        suffix = "th"
    else:
        suffix = suffixes.get(n % 10, "th")
    return f"{n}{suffix}"
