"""Deterministic regressions; no Web Archive or real HTTP required."""

import importlib
from pathlib import Path
from types import SimpleNamespace

import pandas as pd

cli = importlib.import_module("sortgs.sortgs")
HTML = Path(__file__).parent / "fixtures" / "scholar_sample.html"


def test_direct_baseline(monkeypatch, tmp_path):
    calls = []

    def get(url):
        calls.append(url)
        return SimpleNamespace(content=HTML.read_bytes())

    monkeypatch.setattr(cli.requests, "Session", lambda: SimpleNamespace(get=get))
    monkeypatch.setattr(cli, "sleep", lambda _: None)
    monkeypatch.setattr(
        "sys.argv",
        [
            "sortgs",
            "test",
            "--nresults",
            "10",
            "--endyear",
            "2022",
            "--csvpath",
            str(tmp_path),
        ],
    )
    cli.main()
    data = pd.read_csv(tmp_path / "test.csv", keep_default_na=False)
    assert data.columns.tolist() == [
        "Rank",
        "Author",
        "Title",
        "Citations",
        "Year",
        "Publisher",
        "Venue",
        "Content",
        "Source",
        "PDF",
        "cit/year",
    ]
    assert data["Citations"].tolist() == [42, 12, 0]
    assert data["cit/year"].tolist() == [14, 6, 0]
    assert data["Author"].tolist() == [
        "A Author, B Author",
        "C Author",
        "Author not found",
    ]
    assert data["Year"].tolist() == [2020, 2021, 0]
    assert data["Publisher"].tolist() == [
        " example.org",
        "proceeding.com",
        "Publisher not found",
    ]
    assert data["Venue"].tolist() == [" Test Journal", "", "Venue not fount"]
    assert data["Rank"].tolist() == [1, 2, 3]
    assert data["PDF"].tolist() == [
        "https://example.org/one.pdf",
        "No PDF link",
        "No PDF link",
    ]
    assert len(calls) == 1 and calls[0].startswith("https://scholar.google.com/")
