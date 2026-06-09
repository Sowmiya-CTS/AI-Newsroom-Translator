# AI Newsroom Assistant — Real-Time Content Localization

## 1. Derived Ideas

### Core Problem
Breaking news is published in one language and takes hours to reach regional audiences — losing relevance, context, and cultural resonance.

### Derived Solution Pillars
| Idea | Implementation |
|------|----------------|
| Real-time Transcription | Convert broadcast audio/raw text into structured news articles |
| Multilingual Translation | Claude AI translates to 12+ regional languages preserving journalistic tone |
| Cultural Adaptation Engine | Idioms, measurements, references adapted per region |
| Sensitivity Flagging | AI detects violence, political bias, legal risk, hate speech |
| Human-in-the-Loop | Editors review, edit, approve before broadcasting |
| Live Pipeline | WebSocket-powered real-time status updates |

---

## 2. New Implementations (Innovative Features)

- **Regional Dialect Awareness** — prompts differentiate Hindi for North India vs general Hindi
- **Tone Scoring** — each translation gets a journalistic tone quality score (0–100%)
- **Retranslation on Demand** — editors can trigger fresh AI translation with one click
- **Priority Queue** — breaking news marked "high" or "breaking" gets flagged visually
- **Live Activity Feed** — real-time WebSocket stream shows every pipeline event
- **Summary Generation** — one-click broadcast-ready 2-sentence summary
- **Tone Checker** — on-demand journalistic tone analysis per language

---

## 3. Dashboard / Application

### Pages
1. **Dashboard** — Stats overview + recent articles + live activity feed
2. **Ingest** — Submit news articles OR paste raw broadcast transcripts
3. **Review Queue** — Split-screen article list + full detail with sensitivity & translations
4. **Published** — Card grid of all published multilingual articles

### UI Stack
- React 18 + CSS (dark theme, no external UI library — fast loading)
- WebSocket for real-time updates
- Axios for REST API calls

---

## 4. Project Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                        CONTENT INPUT                            │
│   Text Article ──┐                                              │
│                  ├──► Ingest API ──► Article DB (in-memory)     │
│   Raw Transcript─┘         │                                    │
│                            │ Background Task                    │
│                            ▼                                    │
│   ┌──────────────── AI PIPELINE (Claude) ─────────────────┐    │
│   │  Step 1: Sensitivity Analysis                          │    │
│   │     • Detects: violence, political, legal, hate speech │    │
│   │     • Sets overall flag level: safe/low/medium/high   │    │
│   │                                                        │    │
│   │  Step 2: Parallel Translation (per language)           │    │
│   │     • Translate with journalistic tone preservation    │    │
│   │     • Cultural adaptation (idioms, units, context)    │    │
│   │     • Tone quality scoring                             │    │
│   │                                                        │    │
│   │  Step 3: Status → "Review"                             │    │
│   └────────────────────────────────────────────────────────┘    │
│                            │                                    │
│                            ▼ WebSocket broadcast                │
│   ┌──────────────── EDITOR REVIEW ─────────────────────────┐   │
│   │  • View sensitivity flags                               │   │
│   │  • Read each translation                                │   │
│   │  • Edit translated content inline                      │   │
│   │  • Check journalistic tone                              │   │
│   │  • Approve / Reject / Request retranslation            │   │
│   └─────────────────────────────────────────────────────────┘   │
│                            │                                    │
│                            ▼                                    │
│                     PUBLISH / BROADCAST                         │
└─────────────────────────────────────────────────────────────────┘
```

---

## 5. Tech Stack

| Layer | Technology |
|-------|-----------|
| AI Engine | Claude claude-sonnet-4-6 (Anthropic SDK) |
| Backend | Python 3.11 + FastAPI |
| Real-time | WebSockets (FastAPI native) |
| Frontend | React 18 + CSS |
| HTTP Client | Axios |
| Storage | In-memory dict (demo) / PostgreSQL (production) |
| Prompt Caching | Anthropic `cache_control: ephemeral` on system prompt |

---

## Quick Start

### Prerequisites
- Python 3.11+
- Node.js 18+
- Anthropic API Key

### Setup

```bash
# 1. Set API key
cd backend
cp .env.example .env
# Edit .env: ANTHROPIC_API_KEY=sk-ant-...

# 2. Start backend
pip install -r requirements.txt
python main.py

# 3. Start frontend (new terminal)
cd ../frontend
npm install
npm start
```

Or double-click `start.bat` on Windows.

### URLs
- **App**: http://localhost:3000
- **API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs

---

## Sample Demo Flow

1. Open http://localhost:3000
2. Go to **Ingest** tab
3. Paste this text in "Transcribe Broadcast":
   > "Breaking: A 7.2 magnitude earthquake struck off the Japanese coast at 6:42 AM local time. Tsunami warnings have been issued. The government has activated emergency response protocols."
4. Select target languages: Hindi, Tamil, Telugu, Bengali
5. Click **Transcribe & Localize**
6. Watch the **Live Activity Feed** on Dashboard
7. Go to **Review Queue** to see sensitivity analysis + all translations
8. Edit a translation → Approve → Publish

---

## API Reference

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/articles` | GET | List all articles |
| `/api/articles` | POST | Ingest new article |
| `/api/transcribe` | POST | Transcribe + ingest |
| `/api/articles/{id}` | GET | Get article details |
| `/api/articles/{id}/action` | POST | Editor actions |
| `/api/articles/{id}/summary` | GET | Generate summary |
| `/api/articles/{id}/tone-check` | GET | Check tone quality |
| `/api/stats` | GET | Dashboard statistics |
| `/ws` | WS | Real-time events |
