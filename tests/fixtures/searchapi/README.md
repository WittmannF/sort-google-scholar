# SearchApi test fixtures

## Public reference contract

`phantom_physics.json` is a byte-for-byte copy of the JSON attached by the user on
2026-09-05, also presented in the SearchApi Google Scholar public example:
https://www.searchapi.io/google-scholar

SHA-256: `280a55da8613142c299127979b64ec1cce423178d7b324df01ae4bf7b958e9c1`

The payload describes a 2024-10-08 search for `Phantom physics`, with ten articles.
It retains all fields, including public example search metadata, pagination,
related searches and authors. No credential is present. This exact public example
is intentionally different from the minimal sanitized live fixtures below.

`phantom_physics_expected.json` specifies the expected normalized rows and
citations/year values for reference year 2024. Citation counts, publication fields
and rounded annual values were specified independently of the production parser.
Original title/snippet/article URLs and applicable PDF links are preserved.

Tests cover every output field, both sort options, rank-preserving plotting,
absence of a missing-citations warning, and safe handling of repeated/empty next
pages. The latter are transport simulations using the exact reference and the
empty fixture; they are not claimed to be real second-page captures.

Do not rewrite the public reference to imitate current API omissions. Successful
fixture tests validate the documented contract, not current supplier availability.

## Observed live behavior

- `observed.json`: minimal allowlisted sample from local live testing, which lacked
  citation counts. The success envelope/continuation URL are synthetic safe values.
- `empty.json`: observed successful zero-result envelope with the exact empty-search
  error message, without private request metadata.

These fixtures retain regression coverage for absent data and empty searches.
No test requires a real API key, accesses the public history URLs, or uses credits.
