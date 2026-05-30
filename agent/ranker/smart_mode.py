"""
SMART MODE ranker — uses Gemini 2.0 Flash to curate and summarize papers.
Falls back to FREE MODE on any failure.
"""

import json
import os
from google import genai
from google.genai import types
from agent.ranker import free_mode


GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.0-flash")


def build_prompt(about_me: str, interests: str, papers: list[dict]) -> str:
    seen = set()
    selected = []

    for p in papers[:5] + papers[-5:]:
        key = p["title"]
        if key not in seen:
            selected.append(p)
            seen.add(key)
    papers_json = json.dumps([
        {
            "title": p["title"],
            "abstract": p.get("abstract", "")[:400],
        }
        for p in selected
    ], indent=2)

    return f"""You are a research paper curator. Your job is to select the 5 most relevant and valuable papers for this user.

USER PROFILE:
About me: {about_me}
Interests: {interests}

CANDIDATE PAPERS:
{papers_json}

INSTRUCTIONS:
1. Infer the user's intent dynamically from their profile — do NOT assume a fixed domain
2. Select the 5 best papers from the candidates
3. Provide a concise summary and explain why each paper matters to this specific user
4. Return ONLY a valid JSON object — no markdown, no backticks, no preamble

REQUIRED OUTPUT FORMAT (strict JSON):
{{
  "papers": [
    {{
      "title": "exact title from candidates",
      "summary": "2-3 sentence summary of the paper",
      "url": "exact url from candidates"
    }}
  ]
}}"""


def rank(
    recent_papers: list[dict],
    classic_papers: list[dict],
    about_me: str,
    interests: str,
    n: int = 5,
) -> tuple[list[dict], str]:
    """
    Run SMART MODE ranking via Gemini.

    Returns:
        (papers, mode_used) where mode_used is "smart" or "free"
    """
    api_key = os.getenv("GEMINI_API_KEY", "").strip()
    if not api_key:
        print("[SMART MODE] No GEMINI_API_KEY found — falling back to FREE MODE")
        return free_mode.rank(recent_papers, classic_papers, interests, n), "free"

    all_papers = recent_papers + classic_papers

    if not all_papers:
        print("[SMART MODE] No papers to rank — falling back to FREE MODE")
        return free_mode.rank(recent_papers, classic_papers, interests, n), "free"

    try:
        client = genai.Client(api_key=api_key)
        prompt = build_prompt(about_me, interests, all_papers)

        response = client.models.generate_content(
            model=GEMINI_MODEL,
            contents=prompt,
            config=types.GenerateContentConfig(
                temperature=0.4,
                max_output_tokens=8000,
                response_mime_type="application/json"
            ),
        )
        print("[SMART MODE] RAW RESPONSE:", response)
        raw = response.text.strip()

        # Strip markdown fences if present
        if raw.startswith("```"):
            raw = raw.split("```")[1]
            if raw.startswith("json"):
                raw = raw[4:]
            raw = raw.strip()

        parsed = json.loads(raw)
        papers = parsed.get("papers", [])

        if not papers or len(papers) == 0:
            raise ValueError("Gemini returned empty papers list")

        # Enrich with source info by matching titles back to originals
        title_map = {p["title"].lower().strip(): p for p in all_papers}
        enriched = []
        for gp in papers[:n]:
            original = title_map.get(gp["title"].lower().strip(), {})
            enriched.append({
                "title": gp["title"],
                "summary": gp.get("summary", ""),
                "why_it_matters": gp.get("why_it_matters", ""),
                "url": gp.get("url") or original.get("url", ""),
                "source": original.get("source", "unknown"),
                "mode": "smart",
            })

        print(f"[SMART MODE] Gemini selected {len(enriched)} papers")
        return enriched, "smart"

    except json.JSONDecodeError as e:
        print(f"[SMART MODE] JSON parse error: {e} — falling back to FREE MODE")
    except Exception as e:
        print(f"[SMART MODE] Gemini error: {e} — falling back to FREE MODE")

    return free_mode.rank(recent_papers, classic_papers, interests, n), "free"
