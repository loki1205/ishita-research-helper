"""
Semantic Scholar fetcher — recent papers + classic high-citation papers.
"""

import requests
import random

SS_API = "https://api.semanticscholar.org/graph/v1/paper/search"
SS_FIELDS = "title,abstract,url,year,citationCount,externalIds,publicationDate"


def build_query(interests: str) -> str:
    keywords = [k.strip() for k in interests.replace(",", " ").split() if len(k.strip()) > 3]
    return " ".join(keywords[:5])


def normalize(paper: dict, source_tag: str = "semantic_scholar") -> dict | None:
    title = paper.get("title", "").strip()
    abstract = (paper.get("abstract") or "").strip()[:600]
    url = paper.get("url") or ""
    if not url:
        paper_id = paper.get("paperId", "")
        url = f"https://www.semanticscholar.org/paper/{paper_id}" if paper_id else ""
    year = paper.get("year") or ""
    citations = paper.get("citationCount") or 0
    pub_date = paper.get("publicationDate") or str(year)

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


def fetch_recent(interests: str, max_results: int = 25) -> list[dict]:
    """Recent papers sorted by date."""
    query = build_query(interests)
    params = {
        "query": query,
        "fields": SS_FIELDS,
        "limit": max_results,
        "sort": "publicationDate:desc",
    }
    try:
        resp = requests.get(SS_API, params=params, timeout=15)
        resp.raise_for_status()
        data = resp.json().get("data", [])
        papers = [normalize(p) for p in data]
        return [p for p in papers if p]
    except Exception as e:
        print(f"[SemanticScholar] Recent fetch failed: {e}")
        return []


def fetch_classic(interests: str, max_results: int = 15) -> list[dict]:
    """High-citation papers — classic & impactful."""
    query = build_query(interests)
    offset = random.randint(0, 30)
    params = {
        "query": query,
        "fields": SS_FIELDS,
        "limit": max_results,
        "offset": offset,
        "sort": "citationCount:desc",
    }
    try:
        resp = requests.get(SS_API, params=params, timeout=15)
        resp.raise_for_status()
        data = resp.json().get("data", [])
        papers = [normalize(p) for p in data]
        # Only keep papers with meaningful citations (>50)
        classic = [p for p in papers if p and p.get("citations", 0) > 50]
        return classic
    except Exception as e:
        print(f"[SemanticScholar] Classic fetch failed: {e}")
        return []


def fetch_all(interests: str) -> dict:
    recent = fetch_recent(interests, max_results=25)
    classic = fetch_classic(interests, max_results=15)
    print(f"[SemanticScholar] Fetched {len(recent)} recent, {len(classic)} classic papers")
    return {"recent": recent, "classic": classic}
