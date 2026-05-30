"""
Email HTML template — light, minimal, editorial design.
Clean typography, generous whitespace, premium feel.
"""

from datetime import datetime


SOURCE_LABELS = {
    "arxiv": "arXiv",
    "semantic_scholar": "Semantic Scholar",
    "openalex": "OpenAlex",
    "unknown": "Research",
}

MODE_CONFIGS = {
    "smart": {
        "badge": "✦ SMART MODE",
        "badge_color": "#1a1a1a",
        "subject_prefix": "✦ Ishita · Research Digest",
    },
    "free": {
        "badge": "◈ FREE MODE",
        "badge_color": "#555555",
        "subject_prefix": "◈ Ishita · Research Digest",
    },
    "fallback": {
        "badge": "⚠ FALLBACK MODE",
        "badge_color": "#b45309",
        "subject_prefix": "⚠ Ishita · Research Digest",
    },
}


def render_paper_smart(index: int, paper: dict) -> str:
    source = SOURCE_LABELS.get(paper.get("source", ""), "Research")
    url = paper.get("url", "#")
    return f"""
    <tr>
      <td style="padding: 0 0 48px 0;">
        <table width="100%" cellpadding="0" cellspacing="0" border="0">
          <tr>
            <td style="padding-bottom: 8px;">
              <span style="font-family: 'Georgia', serif; font-size: 11px; letter-spacing: 0.12em; text-transform: uppercase; color: #999999;">
                {str(index).zfill(2)} &nbsp;·&nbsp; {source}
              </span>
            </td>
          </tr>
          <tr>
            <td style="padding-bottom: 14px; border-top: 1px solid #e8e8e8; padding-top: 16px;">
              <a href="{url}" style="text-decoration: none; color: #1a1a1a;">
                <span style="font-family: 'Georgia', serif; font-size: 20px; line-height: 1.4; color: #1a1a1a; font-weight: normal; letter-spacing: -0.02em;">
                  {paper.get('title', '')}
                </span>
              </a>
            </td>
          </tr>
          <tr>
            <td style="padding-bottom: 12px;">
              <p style="margin: 0; font-family: -apple-system, 'Helvetica Neue', sans-serif; font-size: 14px; line-height: 1.7; color: #555555;">
                {paper.get('summary', '')}
              </p>
            </td>
          </tr>
          <tr>
            <td style="padding-bottom: 16px;">
              <table cellpadding="0" cellspacing="0" border="0">
                <tr>
                  <td style="background: #f5f5f0; border-left: 2px solid #1a1a1a; padding: 10px 14px;">
                    <p style="margin: 0; font-family: -apple-system, 'Helvetica Neue', sans-serif; font-size: 13px; line-height: 1.6; color: #444444; font-style: italic;">
                      {paper.get('why_it_matters', '')}
                    </p>
                  </td>
                </tr>
              </table>
            </td>
          </tr>
          <tr>
            <td>
              <a href="{url}" style="font-family: -apple-system, 'Helvetica Neue', sans-serif; font-size: 11px; letter-spacing: 0.1em; text-transform: uppercase; color: #1a1a1a; text-decoration: none; border-bottom: 1px solid #1a1a1a; padding-bottom: 1px;">
                Read Paper →
              </a>
            </td>
          </tr>
        </table>
      </td>
    </tr>
    """


def render_paper_free(index: int, paper: dict) -> str:
    source = SOURCE_LABELS.get(paper.get("source", ""), "Research")
    url = paper.get("url", "#")
    abstract = paper.get("abstract", "No abstract available.")[:400]
    if len(paper.get("abstract", "")) > 400:
        abstract += "…"
    return f"""
    <tr>
      <td style="padding: 0 0 48px 0;">
        <table width="100%" cellpadding="0" cellspacing="0" border="0">
          <tr>
            <td style="padding-bottom: 8px;">
              <span style="font-family: 'Georgia', serif; font-size: 11px; letter-spacing: 0.12em; text-transform: uppercase; color: #999999;">
                {str(index).zfill(2)} &nbsp;·&nbsp; {source}
              </span>
            </td>
          </tr>
          <tr>
            <td style="padding-bottom: 14px; border-top: 1px solid #e8e8e8; padding-top: 16px;">
              <a href="{url}" style="text-decoration: none; color: #1a1a1a;">
                <span style="font-family: 'Georgia', serif; font-size: 20px; line-height: 1.4; color: #1a1a1a; font-weight: normal; letter-spacing: -0.02em;">
                  {paper.get('title', '')}
                </span>
              </a>
            </td>
          </tr>
          <tr>
            <td style="padding-bottom: 16px;">
              <p style="margin: 0; font-family: -apple-system, 'Helvetica Neue', sans-serif; font-size: 14px; line-height: 1.7; color: #555555;">
                {abstract}
              </p>
            </td>
          </tr>
          <tr>
            <td>
              <a href="{url}" style="font-family: -apple-system, 'Helvetica Neue', sans-serif; font-size: 11px; letter-spacing: 0.1em; text-transform: uppercase; color: #1a1a1a; text-decoration: none; border-bottom: 1px solid #1a1a1a; padding-bottom: 1px;">
                Read Paper →
              </a>
            </td>
          </tr>
        </table>
      </td>
    </tr>
    """


def render_fallback_notice(reason: str = "") -> str:
    msg = reason or "Gemini API unavailable or returned an invalid response."
    return f"""
    <tr>
      <td style="padding: 0 0 40px 0;">
        <table width="100%" cellpadding="0" cellspacing="0" border="0">
          <tr>
            <td style="background: #fffbeb; border: 1px solid #fde68a; padding: 16px 20px;">
              <p style="margin: 0 0 4px 0; font-family: -apple-system, 'Helvetica Neue', sans-serif; font-size: 12px; font-weight: 600; color: #92400e; letter-spacing: 0.05em; text-transform: uppercase;">
                ⚠ Smart Mode Unavailable
              </p>
              <p style="margin: 0; font-family: -apple-system, 'Helvetica Neue', sans-serif; font-size: 13px; color: #78350f;">
                {msg} Results generated using FREE mode heuristic ranking.
              </p>
            </td>
          </tr>
        </table>
      </td>
    </tr>
    """


def build_email(
    papers: list[dict],
    mode: str,
    about_me: str = "",
    interests: str = "",
    fallback_reason: str = "",
) -> tuple[str, str]:
    """
    Build HTML email and subject line.

    Returns:
        (subject, html_body)
    """
    now = datetime.utcnow()
    date_str = now.strftime("%B %d, %Y")
    week_num = now.isocalendar()[1]

    is_fallback = mode == "fallback"
    display_mode = "fallback" if is_fallback else mode
    cfg = MODE_CONFIGS.get(display_mode, MODE_CONFIGS["free"])

    subject = f"{cfg['subject_prefix']} — Week {week_num}, {now.year}"

    # Build papers HTML
    papers_html = ""
    for i, paper in enumerate(papers, start=1):
        if mode == "smart":
            papers_html += render_paper_smart(i, paper)
        else:
            papers_html += render_paper_free(i, paper)

    fallback_html = render_fallback_notice(fallback_reason) if is_fallback else ""

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Ishita</title>
</head>
<body style="margin: 0; padding: 0; background-color: #fafaf8; font-family: -apple-system, 'Helvetica Neue', sans-serif;">

  <table width="100%" cellpadding="0" cellspacing="0" border="0" style="background-color: #fafaf8;">
    <tr>
      <td align="center" style="padding: 48px 24px;">

        <!-- Container -->
        <table width="600" cellpadding="0" cellspacing="0" border="0" style="max-width: 600px; width: 100%;">

          <!-- Header -->
          <tr>
            <td style="padding: 0 0 48px 0;">
              <table width="100%" cellpadding="0" cellspacing="0" border="0">
                <tr>
                  <td style="border-bottom: 2px solid #1a1a1a; padding-bottom: 20px;">
                    <table width="100%" cellpadding="0" cellspacing="0" border="0">
                      <tr>
                        <td>
                          <span style="font-family: 'Georgia', serif; font-size: 28px; letter-spacing: -0.03em; color: #1a1a1a; font-weight: normal;">
                            Ishita
                          </span>
                        </td>
                        <td align="right" style="vertical-align: middle;">
                          <span style="font-family: -apple-system, 'Helvetica Neue', sans-serif; font-size: 10px; letter-spacing: 0.15em; text-transform: uppercase; color: #ffffff; background-color: {cfg['badge_color']}; padding: 4px 10px;">
                            {cfg['badge']}
                          </span>
                        </td>
                      </tr>
                    </table>
                  </td>
                </tr>
                <tr>
                  <td style="padding-top: 12px;">
                    <span style="font-family: -apple-system, 'Helvetica Neue', sans-serif; font-size: 12px; letter-spacing: 0.08em; text-transform: uppercase; color: #999999;">
                      Week {week_num} &nbsp;·&nbsp; {date_str} &nbsp;·&nbsp; 5 Papers
                    </span>
                  </td>
                </tr>
              </table>
            </td>
          </tr>

          <!-- Intro -->
          <tr>
            <td style="padding: 0 0 48px 0;">
              <p style="margin: 0; font-family: 'Georgia', serif; font-size: 16px; line-height: 1.8; color: #444444; font-style: italic;">
                Your curated reading list for the week — handpicked from arXiv, Semantic Scholar, and OpenAlex based on your interests in <strong style="font-style: normal; font-weight: normal; color: #1a1a1a;">{interests}</strong>.
              </p>
            </td>
          </tr>

          <!-- Fallback notice if needed -->
          {fallback_html}

          <!-- Papers -->
          <tr>
            <td>
              <table width="100%" cellpadding="0" cellspacing="0" border="0">
                {papers_html}
              </table>
            </td>
          </tr>

          <!-- Divider -->
          <tr>
            <td style="padding: 0 0 32px 0; border-top: 1px solid #e8e8e8;"></td>
          </tr>

          <!-- Footer -->
          <tr>
            <td style="padding: 0 0 48px 0;">
              <table width="100%" cellpadding="0" cellspacing="0" border="0">
                <tr>
                  <td>
                    <p style="margin: 0 0 6px 0; font-family: -apple-system, 'Helvetica Neue', sans-serif; font-size: 11px; color: #bbbbbb; letter-spacing: 0.05em; text-transform: uppercase;">
                      Ishita &nbsp;·&nbsp; Automated Research Digest
                    </p>
                    <p style="margin: 0; font-family: -apple-system, 'Helvetica Neue', sans-serif; font-size: 11px; color: #cccccc; line-height: 1.6;">
                      Ishita runs automatically every Monday at 7:00 AM IST.<br>
                      To update your interests, edit your <code style="background: #f0f0ee; padding: 1px 4px; font-size: 10px;">.env</code> file and push to your repository.
                    </p>
                  </td>
                </tr>
              </table>
            </td>
          </tr>

        </table>
      </td>
    </tr>
  </table>

</body>
</html>"""

    return subject, html
