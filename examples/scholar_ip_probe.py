"""One-page Google Scholar probe: egress IP, HTTP status, robot page, result cards.

Used to compare block rates across environments (GitHub Actions, Cloud Run, Colab).
Does not write a CSV and does not start Selenium.
"""

from __future__ import annotations

import json
import sys

import requests
from bs4 import BeautifulSoup

from sortgs.sortgs import GSCHOLAR_URL, build_session, is_robot_html

QUERY = "generative ai"
TIMEOUT = (10, 30)


def egress_ip() -> dict:
    try:
        info = requests.get("https://ipinfo.io/json", timeout=10).json()
    except requests.RequestException as exc:
        return {"error": str(exc)}
    return {
        "ip": info.get("ip"),
        "org": info.get("org"),
        "city": info.get("city"),
        "region": info.get("region"),
        "country": info.get("country"),
    }


def probe_scholar() -> dict:
    session = build_session()
    url = GSCHOLAR_URL.format("0", QUERY.replace(" ", "+"))
    page = session.get(url, timeout=TIMEOUT)
    content = page.content
    soup = BeautifulSoup(content, "html.parser", from_encoding="utf-8")
    cards = soup.find_all("div", {"class": "gs_or"})
    titles = []
    for div in cards[:3]:
        h3 = div.find("h3")
        if h3 is not None:
            titles.append(h3.get_text(" ", strip=True))
    blocked = is_robot_html(content)
    verdict = "BLOCKED" if blocked or page.status_code >= 400 or not cards else "OK"
    return {
        "verdict": verdict,
        "status_code": page.status_code,
        "robot_html": blocked,
        "result_cards": len(cards),
        "sample_titles": titles,
        "content_bytes": len(content),
        "final_url": page.url,
    }


def main() -> int:
    report = {
        "query": QUERY,
        "egress": egress_ip(),
        "scholar": probe_scholar(),
    }
    json.dump(report, sys.stdout, indent=2)
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
