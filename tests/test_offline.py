"""Deterministic regressions; no Web Archive or live Scholar required."""

import importlib
from pathlib import Path
from types import SimpleNamespace

import pandas as pd
import pytest

cli = importlib.import_module("sortgs.sortgs")
HTML = Path(__file__).parent / "fixtures" / "scholar_sample.html"
BLOCKED = Path(__file__).parent / "fixtures" / "scholar_blocked.html"


@pytest.fixture(autouse=True)
def no_sleep(monkeypatch):
    monkeypatch.setattr(cli, "sleep", lambda _: None)


def test_session_sends_browser_user_agent():
    session = cli.build_session()
    assert "Chrome/" in session.headers["User-Agent"]
    assert session.headers["Accept-Language"].startswith("en")
    assert "python-requests" not in session.headers["User-Agent"]


def test_robot_html_detects_block_page():
    assert cli.is_robot_html(BLOCKED.read_bytes())
    assert not cli.is_robot_html(HTML.read_bytes())


def test_direct_baseline(monkeypatch, tmp_path):
    calls = []

    def get(url, **kwargs):
        calls.append((url, kwargs))
        return SimpleNamespace(content=HTML.read_bytes(), status_code=200)

    session = cli.build_session()
    session.get = get
    monkeypatch.setattr(cli, "build_session", lambda: session)
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
    assert data["PDF"].tolist() == [
        "https://example.org/one.pdf",
        "No PDF link",
        "No PDF link",
    ]
    assert len(calls) == 1
    assert calls[0][0].startswith("https://scholar.google.com/")


def test_blocked_pages_do_not_write_empty_csv(monkeypatch, tmp_path):
    target = tmp_path / "test.csv"
    target.write_text("existing output", encoding="utf-8")
    sleeps = []

    session = cli.build_session()
    session.get = lambda url, **kwargs: SimpleNamespace(
        content=BLOCKED.read_bytes(), status_code=429
    )
    monkeypatch.setattr(cli, "build_session", lambda: session)
    monkeypatch.setattr(cli, "sleep", lambda seconds: sleeps.append(seconds))
    monkeypatch.setattr(
        cli,
        "get_content_with_selenium",
        lambda url: (_ for _ in ()).throw(RuntimeError("no chrome")),
    )
    monkeypatch.setattr(
        "sys.argv",
        ["sortgs", "test", "--nresults", "20", "--csvpath", str(tmp_path)],
    )
    with pytest.raises(SystemExit) as caught:
        cli.main()
    assert caught.value.code == 1
    assert target.read_text(encoding="utf-8") == "existing output"
    assert len(sleeps) == 2
