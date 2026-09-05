"""Optional SearchApi Scholar retrieval. No browser, paid fallback or disk writes."""

import datetime
import logging
from time import sleep

import pandas as pd
import requests

from .publication import parse_publication

logger = logging.getLogger(__name__)
ENDPOINT = "https://www.searchapi.io/api/v1/search"
EMPTY_MESSAGE = "Google Scholar didn't return any results."
COLUMNS = [
    "Author",
    "Title",
    "Citations",
    "Year",
    "Publisher",
    "Venue",
    "Content",
    "Source",
    "PDF",
]


class SearchApiError(Exception):
    """An expected retrieval failure whose message is safe to show to the user."""


def _object(value):
    if value is None:
        return {}
    if not isinstance(value, dict):
        raise SearchApiError("SearchApi returned an invalid result structure.")
    return value


def _text(result, field, default=""):
    value = result.get(field)
    if value is None:
        return default
    if not isinstance(value, str):
        raise SearchApiError("SearchApi returned an invalid text field.")
    return value or default


def _citation_value(result):
    links = _object(result.get("inline_links"))
    value = _object(links.get("cited_by")).get("total")
    if value is None:
        return None
    if isinstance(value, str) and value.isascii() and value.isdigit():
        value = int(value)
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        raise SearchApiError("SearchApi returned an invalid citation count.")
    return value


def _normalize(result):
    publication = result.get("publication")
    if publication is not None and not isinstance(publication, str):
        raise SearchApiError("SearchApi returned invalid publication information.")
    author, year, venue, publisher = parse_publication(publication)
    resource = _object(result.get("resource"))
    pdf = (
        _text(resource, "link", "No PDF link")
        if _text(resource, "format").strip().upper() == "PDF"
        else "No PDF link"
    )
    return dict(
        zip(
            COLUMNS,
            [
                author,
                _text(result, "title", "Could not catch title"),
                _citation_value(result) or 0,
                year,
                publisher,
                venue,
                _text(result, "snippet", "Content not found"),
                _text(result, "link", "Source not found"),
                pdf,
            ],
        )
    )


def _identity(result):
    cid = _text(result, "data_cid")
    if cid:
        return ("id", cid)
    link, title, publication = (
        _text(result, key) for key in ("link", "title", "publication")
    )
    if link and title:
        return ("link", link, title, publication)
    if title and publication:
        return ("text", title, publication)
    return None


def _request_page(session, params, api_key):
    for attempt in range(2):
        try:
            response = session.get(
                ENDPOINT,
                params=params,
                headers={"Authorization": "Bearer " + api_key},
                timeout=(10, 60),
                allow_redirects=False,
            )
        except requests.ConnectTimeout:
            if attempt == 0:
                sleep(1)
                continue
            raise SearchApiError("SearchApi connection timed out.") from None
        except requests.RequestException:
            raise SearchApiError(
                "SearchApi connection failed or timed out; upstream usage may have been charged."
            ) from None
        status = response.status_code
        if status in (502, 503, 504) and attempt == 0:
            retry_after = response.headers.get("Retry-After", "0")
            if retry_after.isdigit() and int(retry_after) <= 1:
                sleep(1)
                continue
        if status in (401, 403):
            raise SearchApiError(
                "SearchApi rejected access. Check SEARCH_API_KEY and your account permissions."
            )
        if status == 429:
            raise SearchApiError(
                "SearchApi rate limit reached. Check your account allowance and try later."
            )
        if status != 200:
            raise SearchApiError(
                "SearchApi request failed (HTTP {}). Check your account or try later.".format(
                    status
                )
            )
        try:
            payload = response.json()
        except ValueError:
            raise SearchApiError("SearchApi returned invalid JSON.") from None
        if not isinstance(payload, dict):
            raise SearchApiError("SearchApi returned an invalid response.")
        metadata = _object(payload.get("search_metadata"))
        if metadata.get("status") != "Success":
            raise SearchApiError(
                "SearchApi did not report a successful search. Check your account and query."
            )
        # Live zero-hit searches use Success + this exact error, with no result list.
        error = payload.get("error")
        if error and not (
            error == EMPTY_MESSAGE and not payload.get("organic_results")
        ):
            raise SearchApiError(
                "SearchApi reported a search error. Check your account allowance and query."
            )
        results = payload.get("organic_results", [])
        if not isinstance(results, list) or any(
            not isinstance(row, dict) for row in results
        ):
            raise SearchApiError("SearchApi returned an invalid result list.")
        pagination = _object(payload.get("pagination"))
        return results, bool(pagination.get("next"))
    raise SearchApiError("SearchApi could not complete the request.")


def fetch_searchapi_results(
    keyword,
    number_of_results,
    langfilter,
    start_year,
    end_year,
    api_key,
    max_pages=None,
):
    """Return at most N rows; warn on bounded early completion, raise on failure."""
    if not api_key or not api_key.strip():
        raise SearchApiError("Set SEARCH_API_KEY before selecting SearchApi.")
    if number_of_results <= 0 or (max_pages is not None and max_pages <= 0):
        raise SearchApiError("Result and page limits must be positive.")
    page_size = min(20, number_of_results)
    page_limit = (
        max_pages
        if max_pages is not None
        else (number_of_results + page_size - 1) // page_size + 2
    )
    params = {
        "engine": "google_scholar",
        "q": keyword,
        "num": page_size,
        "hl": "en",
        "as_sdt": "0,5",
    }
    if start_year:
        params["as_ylo"] = start_year
    if end_year != datetime.datetime.now().year:
        params["as_yhi"] = end_year
    if langfilter != "All":
        params["lr"] = "|".join("lang_" + code for code in langfilter)
    rows, seen = [], set()
    pages_received = 0
    citations_available = 0
    reason = (
        "page budget reached; increase --searchapi-max-pages to allow more requests"
    )
    try:
        with requests.Session() as session:
            for page in range(1, page_limit + 1):
                logger.info(
                    "SearchApi: requesting page %d (limit %d)", page, page_limit
                )
                results, has_next = _request_page(
                    session, dict(params, page=page), api_key.strip()
                )
                pages_received += 1
                if not results:
                    reason = "no further results available"
                    break
                previous_count = len(rows)
                for result in results:
                    identity = _identity(result)
                    if identity is not None and identity in seen:
                        continue
                    rows.append(_normalize(result))
                    citations_available += _citation_value(result) is not None
                    if identity is not None:
                        seen.add(identity)
                    if len(rows) == number_of_results:
                        break
                if len(rows) == number_of_results:
                    break
                if len(rows) == previous_count:
                    reason = "no new result identities on the next page"
                    break
                if not has_next:
                    reason = "no further results available"
                    break
    except SearchApiError as error:
        raise SearchApiError(
            "{} Received {} pages and {} results. No CSV was written; earlier successful requests may have consumed credits.".format(
                error, pages_received, len(rows)
            )
        ) from None
    if len(rows) < number_of_results:
        logger.warning(
            "SearchApi returned %d of %d results: %s.",
            len(rows),
            number_of_results,
            reason,
        )
    if rows and citations_available == 0:
        logger.warning(
            "SearchApi supplied no citation counts. Missing counts are shown as 0 for CSV compatibility; citation ranking is unavailable for this response."
        )
    data = pd.DataFrame(rows, columns=COLUMNS)
    data.index = pd.RangeIndex(1, len(rows) + 1, name="Rank")
    data = data.astype({"Citations": "int64", "Year": "int64"})
    return data
