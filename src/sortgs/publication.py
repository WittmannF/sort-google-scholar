"""Shared publication-summary parsing, preserving the legacy CSV semantics."""

import re


def get_year(content: str) -> int:
    match = re.search(r"\b(19|20)\d{2}\b", content)
    return int(match.group(0)) if match else 0


def get_author(content: str) -> str:
    clean_content = content.replace("\xa0", " ")
    return clean_content.split(" - ")[0] if clean_content else ""


def parse_publication(text):
    """Return author, year, venue, publisher; None means a missing element."""
    if text is None:
        return "Author not found", 0, "Venue not fount", "Publisher not found"
    # Deliberately retain legacy hyphen splitting, even for hyphenated domains.
    publisher = text.split("-")[-1]
    try:
        venue = " ".join(text.split("-")[-2].split(",")[:-1])
    except IndexError:
        venue = "Venue not fount"
    return get_author(text), get_year(text), venue, publisher
