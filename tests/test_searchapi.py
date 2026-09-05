"""Offline SearchApi behavior, including observed and synthetic citation data."""

import copy
import datetime
import importlib
import json
from pathlib import Path
from types import SimpleNamespace

import pandas as pd
import pytest
import requests

from sortgs import searchapi as api
from sortgs.publication import parse_publication

cli = importlib.import_module("sortgs.sortgs")
FIXTURES = Path(__file__).parent / "fixtures" / "searchapi"
KEY = "fake-secret-sentinel"
YEAR = datetime.datetime.now().year


def row(i=1, **fields):
    result = {
        "data_cid": str(i),
        "title": "Paper " + str(i),
        "link": "https://example.org/" + str(i),
        "publication": "A Author - Journal, 2020 - example.org",
        "snippet": "Example",
        "inline_links": {"cited_by": {"total": i * 12}},
        "resource": {"format": "PDF", "link": "https://example.org/paper.pdf"},
    }
    result.update(fields)
    return result


def page(rows, more=True):
    return {
        "search_metadata": {"status": "Success"},
        "organic_results": rows,
        "pagination": {"next": "https://scholar.google.com/should-not-be-fetched"}
        if more
        else {},
    }


def response(payload=None, status=200, headers=None):
    def decode():
        if isinstance(payload, Exception):
            raise payload
        return payload

    return SimpleNamespace(status_code=status, headers=headers or {}, json=decode)


@pytest.fixture(autouse=True)
def no_network(monkeypatch):
    def fail(*args, **kwargs):
        pytest.fail("Unexpected real HTTP request")

    monkeypatch.setattr(requests.sessions.Session, "request", fail)
    monkeypatch.setattr(api, "sleep", lambda seconds: None)


@pytest.fixture
def transport(monkeypatch):
    calls = []
    queue = []

    class Session:
        def __enter__(self):
            return self

        def __exit__(self, *args):
            pass

        def get(self, url, **kwargs):
            assert url == api.ENDPOINT
            assert kwargs["headers"] == {"Authorization": "Bearer " + KEY}
            assert kwargs["timeout"] == (10, 60)
            assert kwargs["allow_redirects"] is False
            calls.append(copy.deepcopy(kwargs["params"]))
            assert queue, "Unplanned request"
            item = queue.pop(0)
            if isinstance(item, Exception):
                raise item
            return item

    monkeypatch.setattr(api.requests, "Session", Session)
    return queue, calls


def fetch(n=10, **kwargs):
    return api.fetch_searchapi_results(
        "machine learning",
        n,
        kwargs.pop("langfilter", "All"),
        kwargs.pop("start_year", None),
        kwargs.pop("end_year", YEAR),
        KEY,
        **kwargs,
    )


@pytest.mark.parametrize("n", [1, 10, 20, 50, 100, 101])
def test_exact_count_and_constant_pages(transport, n):
    queue, calls = transport
    size = min(20, n)
    for start in range(0, n, size):
        queue.append(
            response(page([row(i) for i in range(start + 1, start + size + 1)]))
        )
    data = fetch(n)
    assert len(data) == n
    assert data.index.tolist() == list(range(1, n + 1))
    assert [p["page"] for p in calls] == list(range(1, len(calls) + 1))
    assert {p["num"] for p in calls} == {size}
    assert data["Citations"].tolist() == [i * 12 for i in range(1, n + 1)]


def test_query_params(transport):
    queue, calls = transport
    queue.append(response(page([row()])))
    api.fetch_searchapi_results(
        '"a phrase" OR neural', 1, ["pt", "es"], 2020, 2022, KEY
    )
    assert calls[0] == {
        "engine": "google_scholar",
        "q": '"a phrase" OR neural',
        "num": 1,
        "page": 1,
        "hl": "en",
        "as_sdt": "0,5",
        "lr": "lang_pt|lang_es",
        "as_ylo": 2020,
        "as_yhi": 2022,
    }


def test_current_year_omitted(transport):
    transport[0].append(response(page([row()])))
    fetch(1)
    assert "as_yhi" not in transport[1][0]


def test_short_overlapping_pages(transport):
    queue, calls = transport
    queue.extend([response(page([row(1), row(2)])), response(page([row(2), row(3)]))])
    assert fetch(3)["Title"].tolist() == ["Paper 1", "Paper 2", "Paper 3"]
    assert len(calls) == 2


@pytest.mark.parametrize(
    "mode,phrase",
    [
        ("empty", "no further"),
        ("terminal", "no further"),
        ("repeat", "no new result"),
        ("budget", "page budget"),
    ],
)
def test_early_stop(transport, caplog, mode, phrase):
    queue, calls = transport
    queue.append(response(page([row(1)], more=mode != "terminal")))
    if mode in ("empty", "repeat"):
        queue.append(response(page([] if mode == "empty" else [row(1)])))
    data = fetch(10, max_pages=1 if mode == "budget" else None)
    assert len(data) == 1
    assert phrase in caplog.text


def test_default_page_slack(transport, caplog):
    queue, calls = transport
    queue.extend(response(page([row(i)])) for i in range(1, 4))
    assert len(fetch(10)) == 3
    assert len(calls) == 3
    assert "page budget" in caplog.text


def test_identity_is_not_title_dedup(transport):
    transport[0].append(
        response(
            page(
                [
                    row(1, title="Same"),
                    row(2, title="Same"),
                    row(3, data_cid=None, link=None, title=None, publication=None),
                    row(4, data_cid=None, link=None, title=None, publication=None),
                ]
            )
        )
    )
    assert len(fetch(4)) == 4


def test_fallback_identity(transport):
    item = row(data_cid=None)
    transport[0].append(response(page([item, item, row(2, data_cid=None)])))
    assert len(fetch(2)) == 2


@pytest.mark.parametrize(
    "text", [None, "", "A - J, 2020 - as-proceeding.com", "A\xa0B - 2019 - x"]
)
def test_shared_publication_semantics(text):
    a, y, v, p = parse_publication(text)
    normalized = api._normalize(row(publication=text))
    assert [normalized[k] for k in ["Author", "Year", "Venue", "Publisher"]] == [
        a,
        y,
        v,
        p,
    ]


@pytest.mark.parametrize("value,expected", [(None, 0), (0, 0), (42, 42), ("42", 42)])
def test_citation_types(value, expected):
    assert (
        api._normalize(row(inline_links={"cited_by": {"total": value}}))["Citations"]
        == expected
    )


@pytest.mark.parametrize("value", [True, -1, 1.5, "oops", "-1", [], {}])
def test_invalid_citations(value):
    with pytest.raises(api.SearchApiError):
        api._normalize(row(inline_links={"cited_by": {"total": value}}))


def test_missing_optional_fields():
    item = api._normalize({})
    assert item["Citations"] == item["Year"] == 0
    assert item["Author"] == "Author not found"
    assert item["PDF"] == "No PDF link"
    assert item["Source"] == "Source not found"


@pytest.mark.parametrize(
    "fmt,expected",
    [("PDF", True), ("pdf", True), ("HTML", False), ("TXT", False), (None, False)],
)
def test_resource_format(fmt, expected):
    result = api._normalize(
        row(resource={"format": fmt, "link": "https://example.org/file"})
    )
    assert (result["PDF"] == "https://example.org/file") == expected


def test_observed_fixture_warns_missing_citations(transport, caplog):
    transport[0].append(response(json.loads((FIXTURES / "observed.json").read_text())))
    data = fetch(2)
    assert data["Citations"].tolist() == [0, 0]
    assert "citation ranking is unavailable" in caplog.text


def test_real_empty_envelope(transport):
    transport[0].append(response(json.loads((FIXTURES / "empty.json").read_text())))
    data = fetch()
    assert data.empty and data.index.name == "Rank"
    assert data["Citations"].dtype == "int64"


@pytest.mark.parametrize(
    "payload",
    [
        {},
        [],
        {"error": KEY},
        page(None),
        page({}),
        page([None]),
        dict(page([]), error=KEY),
        {"search_metadata": {"status": "Error"}},
        dict(page([]), pagination="bad"),
    ],
)
def test_invalid_envelope_safe(transport, payload):
    transport[0].append(response(payload))
    with pytest.raises(api.SearchApiError) as caught:
        fetch()
    assert KEY not in str(caught.value)


@pytest.mark.parametrize("status", [301, 400, 401, 403, 404, 429, 500])
def test_nonretry_http_errors(transport, status):
    transport[0].append(response({"error": KEY}, status))
    with pytest.raises(api.SearchApiError):
        fetch()
    assert len(transport[1]) == 1


@pytest.mark.parametrize(
    "first",
    [
        response(status=502),
        response(status=503),
        response(status=504),
        requests.ConnectTimeout(KEY),
    ],
)
def test_single_retry(transport, first):
    transport[0].extend([first, response(page([row()]))])
    assert len(fetch(1)) == 1
    assert transport[1][0] == transport[1][1]


@pytest.mark.parametrize(
    "failure",
    [
        requests.ReadTimeout(KEY),
        requests.ConnectionError(KEY),
        response(ValueError(KEY)),
        response(status=503, headers={"Retry-After": "120"}),
    ],
)
def test_no_unsafe_retry(transport, failure):
    transport[0].append(failure)
    with pytest.raises(api.SearchApiError) as caught:
        fetch()
    assert KEY not in str(caught.value)
    assert len(transport[1]) == 1


def test_exhausted_retry(transport):
    transport[0].extend([response(status=502), response(status=502)])
    with pytest.raises(api.SearchApiError):
        fetch()
    assert len(transport[1]) == 2


@pytest.mark.parametrize(
    "args",
    [
        ["--nresults", "0"],
        ["--nresults", "-1"],
        ["--provider", "searchapi", "--debug"],
        ["--searchapi-max-pages", "2"],
        ["--provider", "searchapi", "--searchapi-max-pages", "0"],
        ["--provider", "searchapi", "--startyear", "2030", "--endyear", "2020"],
    ],
)
def test_cli_usage_status(monkeypatch, args):
    monkeypatch.setattr("sys.argv", ["sortgs", "test"] + args)
    with pytest.raises(SystemExit) as caught:
        cli.main()
    assert caught.value.code == 2


def test_missing_key(monkeypatch):
    monkeypatch.delenv("SEARCH_API_KEY", raising=False)
    monkeypatch.setattr("sys.argv", ["sortgs", "test", "--provider", "searchapi"])
    with pytest.raises(SystemExit) as caught:
        cli.main()
    assert caught.value.code == 2


def test_failure_preserves_csv(transport, monkeypatch, tmp_path, caplog):
    target = tmp_path / "test.csv"
    target.write_text("existing output")
    transport[0].extend([response(page([row()])), response(status=429)])
    monkeypatch.setenv("SEARCH_API_KEY", KEY)
    monkeypatch.setattr(
        "sys.argv",
        [
            "sortgs",
            "test",
            "--provider",
            "searchapi",
            "--nresults",
            "2",
            "--csvpath",
            str(tmp_path),
        ],
    )
    with pytest.raises(SystemExit) as caught:
        cli.main()
    assert caught.value.code == 1
    assert target.read_text() == "existing output"
    assert "1 pages and 1 results" in caplog.text
    assert KEY not in caplog.text


@pytest.mark.parametrize("provider", ["direct", "searchapi"])
def test_shared_output(provider, transport, monkeypatch, tmp_path):
    data = pd.DataFrame(
        [api._normalize(row(1)), api._normalize(row(2))], columns=api.COLUMNS
    )
    data.index = pd.RangeIndex(1, 3, name="Rank")
    monkeypatch.setenv("SEARCH_API_KEY", KEY)
    if provider == "direct":
        monkeypatch.setattr(cli, "fetch_direct_results", lambda *a: data)
        monkeypatch.setattr(
            cli,
            "fetch_searchapi_results",
            lambda *a, **k: pytest.fail("Wrong provider"),
        )
    else:
        transport[0].append(response(page([row(1), row(2)])))
        monkeypatch.setattr(
            cli, "fetch_direct_results", lambda *a: pytest.fail("Wrong provider")
        )
    plots = []
    monkeypatch.setattr(
        cli.plt, "plot", lambda x, y, *a: plots.append((list(x), list(y)))
    )
    monkeypatch.setattr(cli.plt, "show", lambda: None)
    args = [
        "sortgs",
        "test",
        "--nresults",
        "2",
        "--endyear",
        "2022",
        "--plotresults",
        "--csvpath",
        str(tmp_path),
    ]
    if provider == "searchapi":
        args += ["--provider", provider]
    monkeypatch.setattr("sys.argv", args)
    cli.main()
    actual = pd.read_csv(tmp_path / "test.csv")
    assert actual.columns.tolist() == ["Rank"] + api.COLUMNS + ["cit/year"]
    assert actual["Citations"].tolist() == [24, 12]
    assert actual["cit/year"].tolist() == [8, 4]
    assert plots == [([1, 2], [12, 24])]
    assert KEY not in (tmp_path / "test.csv").read_text()


def test_empty_csv(transport, monkeypatch, tmp_path):
    transport[0].append(response(json.loads((FIXTURES / "empty.json").read_text())))
    monkeypatch.setenv("SEARCH_API_KEY", KEY)
    monkeypatch.setattr(
        "sys.argv",
        ["sortgs", "test", "--provider", "searchapi", "--csvpath", str(tmp_path)],
    )
    cli.main()
    assert pd.read_csv(tmp_path / "test.csv").empty


def test_notsave_and_sort_fallback(transport, monkeypatch, tmp_path):
    transport[0].append(response(page([row()])))
    monkeypatch.setenv("SEARCH_API_KEY", KEY)
    monkeypatch.setattr(
        "sys.argv",
        [
            "sortgs",
            "test",
            "--provider",
            "searchapi",
            "--nresults",
            "1",
            "--notsavecsv",
            "--sortby",
            "missing",
            "--csvpath",
            str(tmp_path),
        ],
    )
    cli.main()
    assert not list(tmp_path.iterdir())


def test_unknown_values_not_logged(monkeypatch, caplog):
    monkeypatch.setattr("sys.argv", ["sortgs", "test", "--unknown", KEY])
    cli.get_command_line_args()
    assert "Unrecognized" in caplog.text
    assert KEY not in caplog.text


def test_console_exit_status(monkeypatch):
    import os
    import subprocess
    import sys

    env = dict(os.environ)
    env.pop("SEARCH_API_KEY", None)
    executable = str(Path(sys.executable).with_name("sortgs"))
    completed = subprocess.run(
        [executable, "test", "--provider", "searchapi"],
        env=env,
        capture_output=True,
        text=True,
        timeout=20,
    )
    assert completed.returncode == 2
    assert "Set SEARCH_API_KEY" in completed.stderr
    assert "Traceback" not in completed.stderr


@pytest.fixture
def phantom_reference():
    """Full user-supplied public example, with no response fields stripped."""
    return json.loads((FIXTURES / "phantom_physics.json").read_text())


@pytest.fixture
def phantom_expected():
    expected = json.loads((FIXTURES / "phantom_physics_expected.json").read_text())
    assert expected["end_year"] == 2024
    return pd.DataFrame(expected["rows"]).set_index("Rank")


def test_exact_reference_normalization(
    transport, phantom_reference, phantom_expected, caplog
):
    original = copy.deepcopy(phantom_reference)
    transport[0].append(response(phantom_reference))
    data = api.fetch_searchapi_results("Phantom physics", 10, "All", None, 2024, KEY)
    pd.testing.assert_frame_equal(data, phantom_expected[api.COLUMNS])
    assert phantom_reference == original  # Do not mutate the supplied response.
    assert len(transport[1]) == 1
    assert "citation ranking is unavailable" not in caplog.text
    # First article: 192 citations versus 5 versions, even with no resource object.
    assert data.loc[1, "Citations"] == 192
    assert data.loc[1, "PDF"] == "No PDF link"
    # Full author text is retained, not the smaller structured authors list.
    assert data.loc[1, "Author"] == "LA DeWerd, M Kissick"


@pytest.mark.parametrize("sortby", ["Citations", "cit/year"])
def test_reference_cli_csv_and_plot(
    transport,
    phantom_reference,
    phantom_expected,
    monkeypatch,
    tmp_path,
    caplog,
    sortby,
):
    transport[0].append(response(phantom_reference))
    monkeypatch.setenv("SEARCH_API_KEY", KEY)
    monkeypatch.setattr(
        "sys.argv",
        [
            "sortgs",
            "Phantom physics",
            "--provider",
            "searchapi",
            "--nresults",
            "10",
            "--endyear",
            "2024",
            "--sortby",
            sortby,
            "--plotresults",
            "--csvpath",
            str(tmp_path),
        ],
    )
    plots = []
    monkeypatch.setattr(
        cli.plt, "plot", lambda x, y, *args: plots.append((list(x), list(y)))
    )
    monkeypatch.setattr(cli.plt, "show", lambda: None)
    cli.main()
    actual = pd.read_csv(
        tmp_path / "Phantom_physics.csv", keep_default_na=False, index_col="Rank"
    )
    assert actual.columns.tolist() == api.COLUMNS + ["cit/year"]
    pd.testing.assert_frame_equal(actual.sort_index(), phantom_expected)
    assert actual[sortby].is_monotonic_decreasing
    if sortby == "Citations":
        assert actual.index.tolist() == [9, 1, 6, 8, 4, 7, 10, 2, 3, 5]
    else:
        assert actual["cit/year"].tolist() == [30, 17, 8, 8, 7, 7, 5, 4, 3, 2]
    assert plots == [
        (list(range(1, 11)), [192, 34, 11, 137, 10, 171, 88, 144, 332, 73])
    ]
    assert "citation ranking is unavailable" not in caplog.text


@pytest.mark.parametrize("next_page", ["repeated", "empty"])
def test_reference_continuation_stops_safely(
    transport, phantom_reference, phantom_expected, caplog, next_page
):
    # This is a transport simulation, not an invented second public response.
    following = (
        phantom_reference
        if next_page == "repeated"
        else json.loads((FIXTURES / "empty.json").read_text())
    )
    transport[0].extend([response(phantom_reference), response(following)])
    data = api.fetch_searchapi_results("Phantom physics", 25, "All", None, 2024, KEY)
    pd.testing.assert_frame_equal(data, phantom_expected[api.COLUMNS])
    assert [params["page"] for params in transport[1]] == [1, 2]
    assert [params["num"] for params in transport[1]] == [20, 20]
    assert (
        "no new result identities" if next_page == "repeated" else "no further results"
    ) in caplog.text
