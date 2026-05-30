"""
OpenAlex fetcher — open, no API key needed.
"""

import requests
import random
from datetime import datetime, timedelta

OA_API = "https://api.openalex.org/works"


def build_query(interests: str) -> str:
    keywords = [k.strip() for k in interests.replace(",", " ").split() if len(k.strip()) > 3]
    return " ".join(keywords[:5])


def normalize(work: dict, source_tag: str = "openalex") -> dict | None:
    title = (work.get("title") or "").strip()
    abstract_index = work.get("abstract_inverted_index") or {}
    # Reconstruct abstract from inverted index
    abstract = ""
    if abstract_index:
        word_positions = []
        for word, positions in abstract_index.items():
            for pos in positions:
                word_positions.append((pos, word))
        word_positions.sort(key=lambda x: x[0])
        abstract = " ".join(w for _, w in word_positions)[:600]

    url = work.get("primary_location", {}).get("landing_page_url") or work.get("doi") or ""
    if not url and work.get("doi"):
        url = f"https://doi.org/{work['doi']}"

    pub_date = work.get("publication_date") or str(work.get("publication_year") or "")
    citations = work.get("cited_by_count") or 0

    if not title or not url:
        return None

    return {
        "title": title,
        "abstract": abstract,
        "url": url,
        "source": source_tag,
        "published": pub_date,
        "citations": citations,
    }


def fetch_recent(interests: str, max_results: int = 20) -> list[dict]:
    """Papers from last 14 days."""
    query = build_query(interests)
    cutoff = (datetime.utcnow() - timedelta(days=14)).strftime("%Y-%m-%d")
    params = {
        "search": query,
        "filter": f"from_publication_date:{cutoff},is_oa:true",
        "sort": "publication_date:desc",
        "per-page": max_results,
        "select": "title,abstract_inverted_index,primary_location,doi,publication_date,publication_year,cited_by_count",
        "mailto": "research-digest@example.com",
    }
    try:
        resp = requests.get(OA_API, params=params, timeout=15)
        resp.raise_for_status()
        results = resp.json().get("results", [])
        papers = [normalize(w) for w in results]
        return [p for p in papers if p]
    except Exception as e:
        print(f"[OpenAlex] Recent fetch failed: {e}")
        return []


def fetch_classic(interests: str, max_results: int = 15) -> list[dict]:
    """High-citation open access papers."""
    query = build_query(interests)
    page = random.randint(1, 3)
    params = {
        "search": query,
        "filter": "is_oa:true,cited_by_count:>100",
        "sort": "cited_by_count:desc",
        "per-page": max_results,
        "page": page,
        "select": "title,abstract_inverted_index,primary_location,doi,publication_date,publication_year,cited_by_count",
        "mailto": "research-digest@example.com",
    }
    try:
        resp = requests.get(OA_API, params=params, timeout=15)
        resp.raise_for_status()
        results = resp.json().get("results", [])
        papers = [normalize(w) for w in results]
        return [p for p in papers if p]
    except Exception as e:
        print(f"[OpenAlex] Classic fetch failed: {e}")
        return []


def fetch_all(interests: str) -> dict:
    recent = fetch_recent(interests, max_results=20)
    classic = fetch_classic(interests, max_results=15)
    print(f"[OpenAlex] Fetched {len(recent)} recent, {len(classic)} classic papers")
    return {"recent": recent, "classic": classic}
