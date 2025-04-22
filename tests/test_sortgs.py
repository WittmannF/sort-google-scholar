import os
from pathlib import Path
import pandas as pd
import pytest


@pytest.fixture
def df_top_10_cli(tmp_path):
    """Run sortgs CLI to get top 10 results sorted by citations."""
    cmd = f"sortgs 'machine learning' --debug --nresults 10 --endyear 2022 --csvpath {tmp_path}"
    os.system(cmd)
    csv_file = Path(tmp_path) / "machine_learning.csv"
    assert csv_file.exists(), f"CSV file not created: {csv_file}"
    return pd.read_csv(csv_file)


@pytest.fixture
def df_top_sorted_cit_per_year_cli(tmp_path):
    """Run sortgs CLI to get top 10 results sorted by citations per year."""
    cmd = f"sortgs 'machine learning' --debug --nresults 10 --endyear 2022 --sortby 'cit/year' --csvpath {tmp_path}"
    os.system(cmd)
    csv_file = Path(tmp_path) / "machine_learning.csv"
    assert csv_file.exists(), f"CSV file not created: {csv_file}"
    return pd.read_csv(csv_file)


def test_get_10_results_cli(df_top_10_cli):
    assert len(df_top_10_cli) == 10


def test_is_sorted_by_citations(df_top_10_cli):
    top_citations = list(df_top_10_cli.Citations.values[:5])
    assert top_citations == [3166, 2853, 2416, 948, 830]


def test_top_result_cli(df_top_10_cli):
    top_author = str(df_top_10_cli.Author.values[0]).strip()
    top_citation = int(df_top_10_cli.Citations.values[0])
    top_cit_per_year = int(df_top_10_cli["cit/year"].values[0])
    assert [top_author, top_citation, top_cit_per_year] == [
        "S Shalev-Shwartz, S Ben-David",
        3166,
        352,
    ]


def test_cit_per_year_sorted(df_top_sorted_cit_per_year_cli):
    top_cit_per_year = list(df_top_sorted_cit_per_year_cli["cit/year"].values[:5])
    assert top_cit_per_year == [571, 352, 302, 85, 79]


def test_csv_exists(df_top_10_cli):
    # DataFrame loaded implies CSV file was created and read successfully
    assert not df_top_10_cli.empty


def test_cli_cit_per_year_sorted(df_top_sorted_cit_per_year_cli):
    top_citations = [
        int(c) for c in df_top_sorted_cit_per_year_cli.Citations.values[:5]
    ]
    top_cit_per_year = [
        int(c) for c in df_top_sorted_cit_per_year_cli["cit/year"].values[:5]
    ]
    assert [top_citations, top_cit_per_year] == [
        [2853, 3166, 2416, 598, 948],
        [571, 352, 302, 85, 79],
    ]


def test_top_5_authors(df_top_10_cli):
    expected_authors = [
        "S Shalev-Shwartz, S Ben-David",
        "M Mohri, A Rostamizadeh, A Talwalkar",
        "MI Jordan, TM Mitchell",
        "C Sammut, GI Webb",
        "P Langley",
    ]
    assert list(df_top_10_cli.Author.values[:5]) == expected_authors


def test_top_5_titles(df_top_10_cli):
    expected_titles = [
        "Understanding machine learning: From theory to algorithms",
        "Foundations of machine learning",
        "Machine learning: Trends, perspectives, and prospects",
        "Encyclopedia of machine learning",
        "Elements of machine learning",
    ]
    assert list(df_top_10_cli.Title.values[:5]) == expected_titles


def test_pdf_links(df_top_10_cli):
    assert "PDF" in df_top_10_cli.columns
    first_pdf = df_top_10_cli.PDF.values[0]
    assert "9781107057135_foreword_pdf_1.pdf" in first_pdf, (
        f"Expected PDF filename not found in: {first_pdf}"
    )
