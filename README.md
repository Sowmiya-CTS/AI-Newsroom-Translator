# 📡 AI Newsroom Assistant — Real-Time Content Localization

> **Cognizant CODEX Hackathon 2025 | POD 38 PDP | Byte Break Team**

An AI-powered multilingual news broadcasting platform that automates the full content localization pipeline — from raw broadcast ingestion to culturally-adapted, sensitivity-checked news publication across **14 languages** with live voice broadcast.

---

## 🌍 Why This Exists

Every day, breaking news reaches only a fraction of its potential audience because it exists in one language. Regional broadcasters spend hours manually translating, culturally adapting, and sensitivity-checking content before it can air. This platform eliminates that bottleneck — ingesting a single English news story and producing broadcast-ready content in Hindi, Tamil, Telugu, Bengali, Marathi, Gujarati, Kannada, Malayalam, Punjabi, Odia, French, Spanish, Arabic, and more — in seconds.

---

## ✨ Key Features

| Feature | Description |
|---|---|
| 🎙 **Live Broadcast Studio** | AI news presenter with animated avatar, multilingual voice (TTS), lip-sync animation |
| 🌐 **14-Language Translation** | Culturally-adapted translations with journalistic tone preservation |
| 🛡 **Sensitivity Analysis** | 8-category content risk detection before any article goes live |
| 📋 **Editorial Review Queue** | Human-in-the-loop approval workflow — no auto-publishing |
| 📤 **Multi-Format Publishing** | Teleprompter script, push alert, SMS, social caption, radio intro, ticker |
| 🔴 **Real-Time Pipeline** | WebSocket live updates as articles process through the AI pipeline |
| 🤖 **AI Chatbot** | Context-aware newsroom assistant for platform guidance |
| 🔐 **Secure Access** | Login-gated platform — authorized team members only |
| 📊 **Analytics Dashboard** | Pipeline stats, translation coverage, sensitivity distribution |
| 🔌 **MCP Integration** | Model Context Protocol endpoints for AI agent tool-use |

---

## 🛠 Tech Stack

### Backend
| Layer | Technology | Version |
|---|---|---|
| API Framework | **FastAPI** | 0.115.0 |
| ASGI Server | **Uvicorn** | 0.32.0 |
| AI Model | **Google Gemini 2.0 Flash** | via `google-genai` 2.8.0 |
| Data Validation | **Pydantic** | 2.10.0 |
| Real-Time Events | **WebSocket** (FastAPI native) | — |
| Environment Config | **python-dotenv** | 1.0.1 |
| Language | **Python** | 3.10+ |

### Frontend
| Layer | Technology |
|---|---|
| UI Framework | **React 18** (CDN, no build step) |
| JSX Transpiler | **Babel Standalone** (CDN) |
| Styling | Vanilla CSS (dark theme, CSS variables) |
| TTS Engine | **Web Speech API** + **ResponsiveVoice.js** fallback |
| Canvas Animation | **HTML5 Canvas API** (AI avatar lip-sync) |
| Charts | Vanilla CSS + SVG |

### Architecture
```
Browser (React SPA)
       │  HTTP / WebSocket
       ▼
FastAPI Backend (:8000)
       │
       ├── Google Gemini AI  ──► Translation, Sensitivity, Summarization
       ├── In-Memory DB      ──► Articles, Translations, Audit Log
       └── WebSocket Manager ──► Real-time pipeline events
```

---

## 🚀 Getting Started

### Prerequisites
- Python 3.10 or higher
- A valid **Gemini API key** from [aistudio.google.com](https://aistudio.google.com) *(optional — platform runs in demo mode without it)*

### 1. Clone the Repository
```bash
git clone https://github.com/YOUR_USERNAME/ai-newsroom.git
cd ai-newsroom
```

### 2. Install Backend Dependencies
```bash
cd backend
pip install -r requirements.txt
```

### 3. Configure API Key *(optional)*
```bash
# backend/.env
GEMINI_API_KEY=AIzaXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
```
> Without a valid key the platform runs in **Demo Mode** — all AI functions return realistic pre-built responses so the full workflow is demonstrable.

### 4. Start the Backend
```bash
cd backend
python main.py
```
Backend starts at `http://127.0.0.1:8000`
Interactive API docs at `http://127.0.0.1:8000/docs`

### 5. Open the Frontend
Open `frontend/app.html` directly in your browser — no build step, no npm install required.

### 6. Login
Enter your name on the login screen. Authorized members: **Sowmiya, Admin, Editor, Newsroom, Cognizant**

---

## 📖 How to Use — Newsroom Translator Workflow

### Step 1 — Ingest Content
Navigate to **Ingest Content** in the sidebar.

**Option A — Structured Article:**
- Enter headline, article body, source, category
- Select target languages (Hindi, Tamil, Telugu, etc.)
- Set priority: Normal / High / Breaking
- Click **Submit Article**

**Option B — Raw Broadcast Transcript:**
- Paste raw spoken transcript text
- AI automatically cleans, structures, and extracts a headline
- Click **Transcribe & Ingest**

### Step 2 — AI Processing Pipeline
After ingestion, watch the live pipeline in the Dashboard:
```
Ingested → Sensitivity Analysis → Translation (×N languages) → Review Queue
```
Real-time WebSocket events show each step completing. Toast notifications alert on translation completions and sensitivity flags.

### Step 3 — Editorial Review
Navigate to **Review Queue**.
- View sensitivity flags (safe / low / medium / high / critical)
- Read each translated version side by side
- Actions: **Approve**, **Reject**, **Edit translation**, **Request re-translation**
- All actions are logged with optional editor notes

### Step 4 — Broadcast Studio
Navigate to **Broadcast Studio**.
1. Select an approved article from the left panel
2. Choose your target language using the **language chips** (Hindi, Tamil, Telugu, Bengali, Marathi, Gujarati, Kannada, Malayalam, Punjabi, Odia, French, Spanish, Arabic, English)
3. Click **Generate Formats** to produce teleprompter script, push alert, SMS, social caption, radio intro
4. Click **▶ Broadcast in [Language]** — the AI news presenter reads the story in the selected language with animated lip-sync

### Step 5 — Publish & Monitor
- Navigate to **Published Articles**
- Click the ▶ play button on any article card to open the live broadcast modal
- Select language chips in the modal to hear the story in any available language
- The broadcast modal shows: live ticker, lower-third caption, audio bars animation

---

## 🌐 Supported Languages

| Code | Language | Script |
|------|----------|--------|
| `hi` | Hindi | Devanagari |
| `ta` | Tamil | Tamil |
| `te` | Telugu | Telugu |
| `bn` | Bengali | Bengali |
| `mr` | Marathi | Devanagari |
| `gu` | Gujarati | Gujarati |
| `kn` | Kannada | Kannada |
| `ml` | Malayalam | Malayalam |
| `pa` | Punjabi | Gurmukhi |
| `or` | Odia | Odia |
| `fr` | French | Latin |
| `es` | Spanish | Latin |
| `ar` | Arabic | Arabic |
| `en` | English | Latin |

---

## 🔌 API Reference

Base URL: `http://127.0.0.1:8000`

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/stats` | Dashboard statistics |
| `GET` | `/api/articles` | List articles (filter: `?status=review`) |
| `POST` | `/api/articles` | Ingest structured article |
| `POST` | `/api/transcribe` | Ingest raw transcript |
| `GET` | `/api/articles/{id}` | Full article with translations |
| `POST` | `/api/articles/{id}/action` | Approve / Reject / Edit / Publish |
| `GET` | `/api/articles/{id}/multi-format?language_code=hi` | Generate broadcast formats |
| `GET` | `/api/articles/{id}/sensitivity` | Sensitivity analysis result |
| `GET` | `/api/languages` | All supported languages |
| `WS` | `/ws` | WebSocket for real-time pipeline events |
| `GET` | `/mcp/tools` | MCP tool list |
| `POST` | `/mcp/execute` | MCP tool execution |
| `POST` | `/api/chat` | AI chatbot |

---

## 📁 Project Structure

```
ai-newsroom/
├── README.md
├── agent.md                        ← Agent specification
├── frontend/
│   └── app.html                    ← Complete single-file React app (CDN)
└── backend/
    ├── main.py                     ← FastAPI app, routes, WebSocket manager
    ├── models.py                   ← Pydantic schemas, language registry
    ├── database.py                 ← In-memory article store with seed data
    ├── requirements.txt
    ├── .env                        ← API keys (not committed)
    ├── .env.example
    └── services/
        └── claude_service.py       ← All AI functions (translation, sensitivity, etc.)
```

---

## 🏗 Production Upgrade Path

| Current (Demo) | Production |
|---|---|
| In-memory dict store | PostgreSQL with SQLAlchemy |
| Single process | Kubernetes + horizontal scaling |
| Demo mode fallback | Live Gemini 2.0 Flash API |
| File-based frontend | React + Vite build pipeline |
| Web Speech API TTS | D-ID / HeyGen lip-sync video API |
| Open CORS | Restricted origins + JWT auth |

---

## 👥 Team

**Byte Break Team — Cognizant CODEX Hackathon 2025, POD 38 PDP**

---

## 📄 License

MIT License — built for the Cognizant CODEX Hackathon 2025.
