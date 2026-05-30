#!/usr/bin/env python3
"""
run.py — Local test runner for the Research Digest agent.

Usage:
    python run.py              # Full run (fetches real papers, sends real email)
    python run.py --dry-run    # Fetch + rank + preview email, do NOT send
    python run.py --mode free  # Override mode for this run
    python run.py --mode smart # Override mode for this run
"""

import argparse
import os
import sys

# Ensure project root is in path
sys.path.insert(0, os.path.dirname(__file__))

from dotenv import load_dotenv
load_dotenv()

from agent.fetchers import arxiv, semantic_scholar, openalex
from agent.ranker import free_mode, smart_mode
from agent.email import template, sender


def parse_args():
    parser = argparse.ArgumentParser(description="Ishita — Local Runner")
    parser.add_argument("--dry-run", action="store_true", help="Preview email without sending")
    parser.add_argument("--mode", choices=["smart", "free"], help="Override MODE from .env")
    parser.add_argument("--output", default="preview.html", help="HTML preview output file (dry-run only)")
    return parser.parse_args()


def main():
    args = parse_args()

    about_me = os.getenv("ABOUT_ME", "")
    interests = os.getenv("INTERESTS", "machine learning, artificial intelligence")
    mode = args.mode or os.getenv("MODE", "free").lower().strip()
    sources = [s.strip() for s in os.getenv("SOURCES", "arxiv,semantic_scholar,openalex").split(",")]
    n = int(os.getenv("PAPERS_PER_DIGEST", "5"))

    print("=" * 60)
    print("  ISHITA — LOCAL TEST RUNNER")
    if args.dry_run:
        print("  [DRY RUN — email will NOT be sent]")
    print("=" * 60)
    print(f"Mode     : {mode.upper()}")
    print(f"Sources  : {', '.join(sources)}")
    print(f"Interests: {interests[:80]}")
    print()

    # ── Fetch ────────────────────────────────────────────────────
    all_recent, all_classic = [], []
    fetcher_map = {
        "arxiv": arxiv.fetch_all,
        "semantic_scholar": semantic_scholar.fetch_all,
        "openalex": openalex.fetch_all,
    }

    for source in sources:
        fetcher = fetcher_map.get(source)
        if not fetcher:
            continue
        try:
            result = fetcher(interests)
            all_recent.extend(result.get("recent", []))
            all_classic.extend(result.get("classic", []))
        except Exception as e:
            print(f"[{source}] Failed: {e}")

    print(f"\nFetched: {len(all_recent)} recent, {len(all_classic)} classic papers total\n")

    if not all_recent and not all_classic:
        print("ERROR: No papers fetched. Check your internet connection or interests config.")
        sys.exit(1)

    # ── Rank ─────────────────────────────────────────────────────
    mode_used = mode
    fallback_reason = ""

    if mode == "smart":
        papers, mode_used = smart_mode.rank(all_recent, all_classic, about_me, interests, n)
        if mode_used == "free":
            fallback_reason = "Gemini API failed or returned invalid response."
            mode_used = "fallback"
    else:
        papers = free_mode.rank(all_recent, all_classic, interests, n)

    print(f"\nSelected {len(papers)} papers (mode: {mode_used})\n")
    for i, p in enumerate(papers, 1):
        print(f"  {i}. {p['title'][:80]}")
        print(f"     Source: {p.get('source', 'unknown')} | URL: {p.get('url', '')[:60]}")
        print()

    # ── Build email ───────────────────────────────────────────────
    subject, html = template.build_email(
        papers=papers,
        mode=mode_used,
        about_me=about_me,
        interests=interests,
        fallback_reason=fallback_reason,
    )

    print(f"Subject: {subject}\n")

    if args.dry_run:
        # Save HTML preview
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(html)
        print(f"✓ Email preview saved to: {args.output}")
        print("  Open it in your browser to review before going live.")
    else:
        print("Sending email...")
        success = sender.send(subject, html)
        if success:
            print("✓ Email sent successfully!")
        else:
            print("✗ Email failed — check SMTP credentials in .env")
            sys.exit(1)

    print("=" * 60)


if __name__ == "__main__":
    main()
