"""
main.py — Research Digest pipeline orchestrator.

Flow:
  1. Load config from environment
  2. Fetch papers from arXiv, Semantic Scholar, OpenAlex
  3. Rank papers (SMART or FREE mode)
  4. Generate email
  5. Send email
"""

import os
import sys
from dotenv import load_dotenv

from agent.fetchers import arxiv, semantic_scholar, openalex
from agent.ranker import free_mode, smart_mode
from agent.email import template, sender


def load_config() -> dict:
    load_dotenv()
    return {
        "about_me": os.getenv("ABOUT_ME", ""),
        "interests": os.getenv("INTERESTS", "machine learning, artificial intelligence"),
        "mode": os.getenv("MODE", "free").lower().strip(),
        "sources": [s.strip() for s in os.getenv("SOURCES", "arxiv,semantic_scholar,openalex").split(",")],
        "papers_per_digest": int(os.getenv("PAPERS_PER_DIGEST", "5")),
    }


def fetch_papers(config: dict) -> tuple[list[dict], list[dict]]:
    """Fetch from all configured sources. Returns (recent, classic)."""
    interests = config["interests"]
    sources = config["sources"]

    all_recent, all_classic = [], []

    fetcher_map = {
        "arxiv": arxiv.fetch_all,
        "semantic_scholar": semantic_scholar.fetch_all,
        "openalex": openalex.fetch_all,
    }

    for source in sources:
        fetcher = fetcher_map.get(source)
        if not fetcher:
            print(f"[MAIN] Unknown source '{source}' — skipping")
            continue
        try:
            result = fetcher(interests)
            all_recent.extend(result.get("recent", []))
            all_classic.extend(result.get("classic", []))
        except Exception as e:
            print(f"[MAIN] Source '{source}' failed: {e} — continuing with other sources")

    print(f"[MAIN] Total fetched: {len(all_recent)} recent, {len(all_classic)} classic papers")

    if not all_recent and not all_classic:
        print("[MAIN] CRITICAL: No papers fetched from any source. Exiting.")
        sys.exit(1)

    return all_recent, all_classic


def run():
    print("=" * 60)
    print("  ISHITA — RESEARCH DIGEST AGENT")
    print("=" * 60)

    config = load_config()
    print(f"[MAIN] Mode: {config['mode'].upper()}")
    print(f"[MAIN] Sources: {', '.join(config['sources'])}")
    print(f"[MAIN] Interests: {config['interests'][:80]}...")

    # ── Fetch ────────────────────────────────────────────────────
    recent_papers, classic_papers = fetch_papers(config)

    # ── Rank ─────────────────────────────────────────────────────
    n = config["papers_per_digest"]
    mode_used = config["mode"]
    fallback_reason = ""

    if config["mode"] == "smart":
        papers, mode_used = smart_mode.rank(
            recent_papers,
            classic_papers,
            about_me=config["about_me"],
            interests=config["interests"],
            n=n,
        )
        if mode_used == "free":
            fallback_reason = "Gemini API failed or returned invalid response."
            mode_used = "fallback"
    else:
        papers = free_mode.rank(recent_papers, classic_papers, config["interests"], n=n)
        mode_used = "free"

    if not papers:
        print("[MAIN] CRITICAL: No papers selected after ranking. Exiting.")
        sys.exit(1)

    print(f"[MAIN] Final selection: {len(papers)} papers (mode: {mode_used})")

    # ── Generate email ────────────────────────────────────────────
    subject, html = template.build_email(
        papers=papers,
        mode=mode_used,
        about_me=config["about_me"],
        interests=config["interests"],
        fallback_reason=fallback_reason,
    )

    # ── Send ──────────────────────────────────────────────────────
    success = sender.send(subject, html)

    if success:
        print("[MAIN] ✓ Digest delivered successfully")
    else:
        print("[MAIN] ✗ Email delivery failed")
        sys.exit(1)

    print("=" * 60)


if __name__ == "__main__":
    run()
