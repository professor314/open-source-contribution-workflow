"""License detection module for identifying OSI-approved open-source licenses."""

from typing import Any, Dict


def detect_license(license_text: str) -> Dict[str, Any]:
    """Detect the license type from license file content.

    Checks the license text content against known OSI-approved license
    identifiers using keyword/phrase matching.

    Args:
        license_text: The raw text content of a LICENSE file.

    Returns:
        A dictionary with:
            - license_identifier: str - the SPDX identifier (e.g., "MIT") or "" if not recognized
            - license_verified: bool - True if a known license was recognized, False otherwise
    """
    if not license_text or not license_text.strip():
        return {"license_identifier": "", "license_verified": False}

    text = license_text

    # Check MIT
    if "MIT License" in text or "Permission is hereby granted, free of charge" in text:
        return {"license_identifier": "MIT", "license_verified": True}

    # Check Apache-2.0
    if "Apache License" in text and "Version 2.0" in text:
        return {"license_identifier": "Apache-2.0", "license_verified": True}

    # Check GPL-3.0
    if "GNU GENERAL PUBLIC LICENSE" in text and "Version 3" in text:
        return {"license_identifier": "GPL-3.0", "license_verified": True}

    # Check MPL-2.0
    if "Mozilla Public License" in text and "Version 2.0" in text:
        return {"license_identifier": "MPL-2.0", "license_verified": True}

    # Check BSD-3-Clause (check before BSD-2-Clause since 3-clause is more specific)
    if ("BSD" in text and "3-Clause" in text) or (
        "Redistribution and use" in text and _has_non_endorsement_clause(text)
    ):
        return {"license_identifier": "BSD-3-Clause", "license_verified": True}

    # Check BSD-2-Clause
    if ("BSD" in text and "2-Clause" in text) or (
        "Redistribution and use" in text and not _has_non_endorsement_clause(text)
    ):
        return {"license_identifier": "BSD-2-Clause", "license_verified": True}

    # Check ISC
    if "ISC License" in text or "Permission to use, copy, modify" in text:
        return {"license_identifier": "ISC", "license_verified": True}

    # Not recognized
    return {"license_identifier": "", "license_verified": False}


def _has_non_endorsement_clause(text: str) -> bool:
    """Check if the license text contains a non-endorsement clause (BSD-3 indicator).

    The non-endorsement clause typically states that the name of the copyright
    holder may not be used to endorse or promote products derived from the software.
    """
    non_endorsement_phrases = [
        "endorse or promote",
        "Neither the name",
        "nor the names of its contributors",
    ]
    return any(phrase in text for phrase in non_endorsement_phrases)
