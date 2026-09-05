"""Unit tests for the pure HTML/text helpers."""

import pytest

from sortgs.sortgs import get_author, get_citations, get_year


@pytest.mark.parametrize(
    "text,expected",
    [
        ("Cited by 42 extra", 42),
        ("No citation line", 0),
        ("", 0),
    ],
)
def test_get_citations(text, expected):
    assert get_citations(text) == expected


@pytest.mark.parametrize(
    "text,expected",
    [
        ("A Author - Test Journal, 2020 - example.org", 2020),
        ("Only 1999 in this string", 1999),
        ("No year here", 0),
    ],
)
def test_get_year(text, expected):
    assert get_year(text) == expected


@pytest.mark.parametrize(
    "text,expected",
    [
        ("A Author, B Author - Test Journal, 2020 - example.org", "A Author, B Author"),
        ("A\xa0B - 2019 - x", "A B"),
        ("", ""),
    ],
)
def test_get_author(text, expected):
    assert get_author(text) == expected
