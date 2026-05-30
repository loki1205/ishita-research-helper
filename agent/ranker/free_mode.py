"""
FREE MODE ranker — heuristic bucket-based selection.
No AI, no external calls. Fully deterministic with controlled randomness.

Selection strategy:
  - 3 recent papers (high/medium relevance)
  - 2 classic papers (high citation count)
"""

import hashlib
import random
from typing import Any


def title_hash(paper: dict) -> str:
    return hashlib.md5(paper["title"].lower().strip().encode()).hexdigest()


def deduplicate(papers: list[dict]) -> list[dict]:
    seen = set()
    unique = []
    for p in papers:
        h = title_hash(p)
        if h not in seen:
            seen.add(h)
            unique.append(p)
    return unique


def keyword_score(paper: dict, interests: str) -> int:
    """Count how many interest keywords appear in title + abstract."""
    keywords = [k.strip().lower() for k in interests.replace(",", " ").split() if len(k.strip()) > 3]
    text = (paper.get("title", "") + " " + paper.get("abstract", "")).lower()
    return sum(1 for kw in keywords if kw in text)


def bucket_papers(papers: list[dict], interests: str) -> dict:
    """Divide papers into high / medium / exploratory buckets."""
    high, medium, exploratory = [], [], []
    for p in papers:
        score = keyword_score(p, interests)
        if score >= 3:
            high.append(p)
        elif score >= 1:
            medium.append(p)
        else:
            exploratory.append(p)
    return {"high": high, "medium": medium, "exploratory": exploratory}


def pick_from(pool: list[dict], n: int) -> list[dict]:
    """Randomly pick n items from pool."""
    random.shuffle(pool)
    return pool[:n]


def ensure_source_diversity(selected: list[dict], all_papers: list[dict], target: int = 5) -> list[dict]:
    """Try to ensure at least 2 different sources in final selection."""
    sources = {p["source"] for p in selected}
    if len(sources) >= 2 or len(selected) >= target:
        return selected

    # Try to add a paper from a different source
    for p in all_papers:
        if p["source"] not in sources and p not in selected:
            selected.append(p)
            if len(selected) >= target:
                break
    return selected


def rank(recent_papers: list[dict], classic_papers: list[dict], interests: str, n: int = 5) -> list[dict]:
    """
    Main ranking entry point.
    
    Args:
        recent_papers: Papers from last 14 days (all sources merged)
        classic_papers: High-citation older papers (all sources merged)
        interests: User interests string
        n: Number of papers to return (default 5)
    
    Returns:
        List of n selected papers
    """
    random.seed()  # fresh seed each run for variation

    # Deduplicate within each pool
    recent_papers = deduplicate(recent_papers)
    classic_papers = deduplicate(classic_papers)

    # ── RECENT POOL: pick 3 ──────────────────────────────────────────
    buckets = bucket_papers(recent_papers, interests)

    recent_selected = []

    # Fill from high bucket first
    high_picks = pick_from(buckets["high"], min(3, len(buckets["high"])))
    recent_selected.extend(high_picks)

    # If not enough, fill from medium
    if len(recent_selected) < 3:
        needed = 3 - len(recent_selected)
        medium_picks = pick_from(buckets["medium"], min(needed, len(buckets["medium"])))
        recent_selected.extend(medium_picks)

    # If still not enough, fill from exploratory
    if len(recent_selected) < 3:
        needed = 3 - len(recent_selected)
        exp_picks = pick_from(buckets["exploratory"], min(needed, len(buckets["exploratory"])))
        recent_selected.extend(exp_picks)

    # Final fallback — just take any recent papers
    if len(recent_selected) < 3:
        all_recent = deduplicate(recent_papers)
        random.shuffle(all_recent)
        for p in all_recent:
            if p not in recent_selected:
                recent_selected.append(p)
            if len(recent_selected) >= 3:
                break

    recent_selected = recent_selected[:3]

    # ── CLASSIC POOL: pick 2 by citation count ───────────────────────
    # Sort by citation count descending, then pick top candidates randomly
    classic_sorted = sorted(classic_papers, key=lambda p: p.get("citations", 0), reverse=True)
    # Take top 10 by citations, then randomly pick 2 for variation
    top_classics = classic_sorted[:10]
    random.shuffle(top_classics)
    
    # Exclude any titles already in recent selection
    recent_titles = {title_hash(p) for p in recent_selected}
    classic_selected = []
    for p in top_classics:
        if title_hash(p) not in recent_titles:
            classic_selected.append(p)
        if len(classic_selected) >= 2:
            break

    # Fallback if not enough classics
    if len(classic_selected) < 2:
        for p in classic_papers:
            if title_hash(p) not in recent_titles and p not in classic_selected:
                classic_selected.append(p)
            if len(classic_selected) >= 2:
                break

    classic_selected = classic_selected[:2]

    # ── MERGE & DIVERSITY CHECK ───────────────────────────────────────
    final = recent_selected + classic_selected
    all_pool = recent_papers + classic_papers
    final = ensure_source_diversity(final, all_pool, target=n)

    print(f"[FREE MODE] Selected {len(final)} papers ({len(recent_selected)} recent, {len(classic_selected)} classic)")
    return final[:n]
