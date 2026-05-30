# 📚 Ishita — Research Digest Agent

A fully automated, stateless research paper digest system. Every Monday at **7:00 AM IST**, it fetches the 5 most relevant papers from arXiv, Semantic Scholar, and OpenAlex — curated for your interests — and delivers them to your inbox.

---

## How It Works

```
GitHub Actions (cron: Monday 7am IST)
        ↓
Fetch papers (arXiv + Semantic Scholar + OpenAlex)
        ↓
Rank: FREE heuristic  OR  SMART (Gemini 2.0 Flash)
        ↓
Select top 5  (3 recent · 2 classic high-citation)
        ↓
Generate premium HTML email
        ↓
Send via Gmail SMTP
```

---

## Two Modes

| | FREE MODE | SMART MODE |
|---|---|---|
| AI | None | Gemini 2.0 Flash |
| Cost | Free forever | Free (Gemini free tier) |
| Paper selection | Keyword heuristics | AI-curated |
| Summaries | Raw abstracts | AI-written summaries + why it matters |
| Fallback | — | Auto-falls back to FREE if Gemini fails |

---

## Setup Guide

### Step 1 — Fork this repository

Click **Fork** at the top right of this repo. All workflows run inside your own GitHub account.

---

### Step 2 — Get a Gmail App Password

Gmail requires an **App Password** (not your account password) for SMTP access.

1. Go to your Google Account → **Security**
2. Enable **2-Step Verification** (required)
3. Go to **App Passwords** → Select app: `Mail` → Select device: `Other`
4. Name it `Research Digest` → Click **Generate**
5. Copy the 16-character password — you'll use it as `SMTP_PASS`

---

### Step 3 — Get a Gemini API Key (SMART MODE only)

> Skip this step if you want to run in FREE MODE only.

1. Go to [aistudio.google.com/app/apikey](https://aistudio.google.com/app/apikey)
2. Click **Create API Key**
3. Copy the key — you'll use it as `GEMINI_API_KEY`

The Gemini free tier is sufficient for weekly digest runs.

---

### Step 4 — Configure GitHub Secrets

Go to your forked repo → **Settings** → **Secrets and variables** → **Actions** → **New repository secret**

Add each of the following:

#### Required secrets

| Secret | Description | Example |
|---|---|---|
| `ABOUT_ME` | Free-form description of who you are | `"I'm a PhD student in NLP focused on reasoning"` |
| `INTERESTS` | Keywords or topics you care about | `"chain of thought, RLHF, multimodal LLMs"` |
| `SMTP_USER` | Your Gmail address | `you@gmail.com` |
| `SMTP_PASS` | Gmail App Password (Step 2) | `abcd efgh ijkl mnop` |
| `FROM_EMAIL` | Display name + email | `"Research Digest <you@gmail.com>"` |
| `TO_EMAIL` | Where to send the digest | `you@gmail.com` |

#### Optional secrets (have sensible defaults)

| Secret | Default | Description |
|---|---|---|
| `MODE` | `free` | `smart` or `free` |
| `GEMINI_API_KEY` | _(none)_ | Required for SMART mode |
| `GEMINI_MODEL` | `gemini-2.0-flash` | Gemini model to use |
| `PAPERS_PER_DIGEST` | `5` | Number of papers per digest |
| `SOURCES` | `arxiv,semantic_scholar,openalex` | Paper sources to use |
| `INCLUDE_PREPRINTS` | `true` | Include preprints from arXiv |

---

### Step 5 — Enable GitHub Actions

1. Go to your forked repo → **Actions** tab
2. Click **"I understand my workflows, go ahead and enable them"**
3. The digest will now run automatically every Monday at 7:00 AM IST

---

### Step 6 — Test it manually

Don't wait for Monday — trigger it now:

1. Go to **Actions** → **Ishita**
2. Click **Run workflow**
3. Optionally set **Dry run** to `true` to preview without sending
4. Click the green **Run workflow** button
5. Check your inbox in ~60 seconds

---

## Local Development

### Setup

```bash
git clone https://github.com/YOUR_USERNAME/research-digest
cd research-digest

python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt

cp .env.example .env
# Edit .env with your config
```

### Run locally

```bash
# Full run (fetches papers + sends email)
python run.py

# Dry run — preview email in browser, no send
python run.py --dry-run

# Force a specific mode
python run.py --mode smart
python run.py --mode free

# Dry run + specific mode + custom output file
python run.py --dry-run --mode smart --output my_preview.html
```

The dry run saves a `preview.html` file you can open in your browser to see exactly what the email looks like before going live.

---

## Project Structure

```
research-digest/
├── .github/
│   └── workflows/
│       └── digest.yml          ← GitHub Actions workflow
├── agent/
│   ├── fetchers/
│   │   ├── arxiv.py            ← arXiv API fetcher
│   │   ├── semantic_scholar.py ← Semantic Scholar API fetcher
│   │   └── openalex.py         ← OpenAlex API fetcher
│   ├── ranker/
│   │   ├── free_mode.py        ← Heuristic bucket ranker
│   │   └── smart_mode.py       ← Gemini-powered ranker
│   ├── email/
│   │   ├── template.py         ← HTML email template
│   │   └── sender.py           ← Gmail SMTP sender
│   └── main.py                 ← Pipeline orchestrator
├── run.py                      ← Local test runner
├── .env.example                ← Config template
├── requirements.txt
└── README.md
```

---

## Customizing Your Interests

Edit `ABOUT_ME` and `INTERESTS` in your GitHub Secrets (or `.env` locally).

**Tips for better results:**
- Be specific: `"transformer attention mechanisms, KV cache optimization"` beats `"AI"`
- Mix topics: `"protein folding, drug discovery, molecular dynamics"`
- Update anytime — changes take effect on the next run

---

## Updating the Schedule

The default schedule is **Monday 7:00 AM IST** (`30 1 * * 1` UTC).

To change it, edit `.github/workflows/digest.yml`:

```yaml
schedule:
  - cron: "30 1 * * 1"   # Monday 7am IST
```

Common alternatives:
```yaml
"30 1 * * 1"    # Monday 7am IST (default)
"30 1 * * 1,4"  # Monday + Thursday 7am IST
"30 1 * * *"    # Daily 7am IST
```

---

## Troubleshooting

**Email not arriving?**
- Check your spam folder
- Verify `SMTP_PASS` is the App Password, not your Google account password
- Make sure 2-Step Verification is enabled on your Google account

**SMART mode falling back to FREE?**
- Check that `GEMINI_API_KEY` is set correctly in GitHub Secrets
- Verify the key is active at [aistudio.google.com](https://aistudio.google.com)
- The fallback is intentional — your digest always arrives, even if Gemini fails

**No papers found?**
- Broaden your `INTERESTS` — very niche topics may return few results
- Check that `SOURCES` includes at least one valid source

**Workflow not triggering?**
- GitHub Actions schedules can be delayed by up to 15 minutes
- Make sure Actions are enabled in your forked repo (Step 5)

---

## License

MIT — fork, modify, share freely.
