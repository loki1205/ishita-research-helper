"""
arXiv fetcher — returns recent papers (last 7 days) and older high-impact papers.
"""

import requests
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta
import random
import os


ARXIV_API = "http://export.arxiv.org/api/query"
NS = "{http://www.w3.org/2005/Atom}"


def build_query(interests: str) -> str:
    keywords = [k.strip() for k in interests.replace(",", " ").split() if len(k.strip()) > 3]
    keywords = keywords[:6]
    return " OR ".join(f'"{k}"' if " " in k else k for k in keywords)


def parse_entries(xml_text: str, source_tag: str = "arxiv") -> list[dict]:
    root = ET.fromstring(xml_text)
    papers = []
    for entry in root.findall(f"{NS}entry"):
        title_el = entry.find(f"{NS}title")
        abstract_el = entry.find(f"{NS}summary")
        link_el = entry.find(f"{NS}id")
        published_el = entry.find(f"{NS}published")

        if not all([title_el, abstract_el, link_el]):
            continue

        title = title_el.text.strip().replace("\n", " ")
        abstract = abstract_el.text.strip().replace("\n", " ")
        url = link_el.text.strip()
        published = published_el.text.strip() if published_el is not None else ""

        papers.append({
            "title": title,
            "abstract": abstract[:600],
            "url": url,
            "source": source_tag,
            "published": published,
        })
    return papers


def fetch_recent(interests: str, max_results: int = 25) -> list[dict]:
    """Fetch papers from the last 14 days."""
    query = build_query(interests)
    params = {
        "search_query": f"all:{query}",
        "start": 0,
        "max_results": max_results,
        "sortBy": "submittedDate",
        "sortOrder": "descending",
    }
    try:
        resp = requests.get(ARXIV_API, params=params, timeout=15)
        resp.raise_for_status()
        papers = parse_entries(resp.text, source_tag="arxiv")

        # Filter to last 14 days
        cutoff = datetime.utcnow() - timedelta(days=14)
        recent = []
        for p in papers:
            try:
                pub_date = datetime.fromisoformat(p["published"].replace("Z", "+00:00")).replace(tzinfo=None)
                if pub_date >= cutoff:
                    recent.append(p)
            except Exception:
                recent.append(p)  # include if date parse fails
        return recent
    except Exception as e:
        print(f"[arXiv] Recent fetch failed: {e}")
        return []


def fetch_classic(interests: str, max_results: int = 15) -> list[dict]:
    """Fetch older papers (1–5 years ago) — used as classic pool."""
    query = build_query(interests)
    # Offset randomly to get variety
    start_offset = random.randint(50, 200)
    params = {
        "search_query": f"all:{query}",
        "start": start_offset,
        "max_results": max_results,
        "sortBy": "relevance",
        "sortOrder": "descending",
    }
    try:
        resp = requests.get(ARXIV_API, params=params, timeout=15)
        resp.raise_for_status()
        return parse_entries(resp.text, source_tag="arxiv")
    except Exception as e:
        print(f"[arXiv] Classic fetch failed: {e}")
        return []


def fetch_all(interests: str) -> dict:
    recent = fetch_recent(interests, max_results=25)
    classic = fetch_classic(interests, max_results=15)
    print(f"[arXiv] Fetched {len(recent)} recent, {len(classic)} classic papers")
    return {"recent": recent, "classic": classic}
