"""Linter configuration detection for Python repositories.

Identifies linter tools configured in a repository by examining file names
and file contents for known configuration patterns.
"""

from typing import Dict, List, Optional


def detect_linter_config(
    file_list: List[str],
    file_contents: Optional[Dict[str, str]] = None,
) -> List[Dict[str, str]]:
    """Detect linter configuration files in a repository.

    Given a list of file names in a repository and optionally their contents,
    identifies which linter tools are configured.

    Recognized configurations:
        - pyproject.toml with [tool.black] section → "black"
        - pyproject.toml with [tool.ruff] section → "ruff"
        - setup.cfg with [flake8] section → "flake8"
        - .flake8 (file exists) → "flake8"
        - .pylintrc (file exists) → "pylint"

    Args:
        file_list: List of file names/paths present in the repository.
        file_contents: Optional dictionary mapping file names to their text
            contents. Needed to check for specific sections in pyproject.toml
            and setup.cfg.

    Returns:
        A list of dicts, each with:
            - "tool": str — the linter tool name (e.g., "black", "ruff",
              "flake8", "pylint")
            - "config_file": str — the config file that triggered detection

        Returns an empty list if no linter configs are found.
    """
    results: List[Dict[str, str]] = []

    if file_contents is None:
        file_contents = {}

    # Check pyproject.toml for [tool.black] and [tool.ruff] sections
    if "pyproject.toml" in file_list and "pyproject.toml" in file_contents:
        content = file_contents["pyproject.toml"]
        if "[tool.black]" in content:
            results.append({"tool": "black", "config_file": "pyproject.toml"})
        if "[tool.ruff]" in content:
            results.append({"tool": "ruff", "config_file": "pyproject.toml"})

    # Check setup.cfg for [flake8] section
    if "setup.cfg" in file_list and "setup.cfg" in file_contents:
        content = file_contents["setup.cfg"]
        if "[flake8]" in content:
            results.append({"tool": "flake8", "config_file": "setup.cfg"})

    # Check for .flake8 file existence
    if ".flake8" in file_list:
        results.append({"tool": "flake8", "config_file": ".flake8"})

    # Check for .pylintrc file existence
    if ".pylintrc" in file_list:
        results.append({"tool": "pylint", "config_file": ".pylintrc"})

    return results
