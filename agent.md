# Agent Specification — AI Newsroom Assistant

**Version:** 1.0.0
**Model:** Codex AI
**Organization:** Cognizant — CODEX Hackathon | POD 38 — PDP
**Classification:** Production-Ready Agent Specification

---

## 1. Agent Identity

The **AI Newsroom Assistant** is a multi-capability language agent built on Codex AI. It operates as an intelligent backend service within a media technology platform, automating the full content localization pipeline — from raw broadcast ingestion to multilingual, culturally-adapted news publication — with mandatory human editorial oversight before broadcasting.

The agent is not autonomous in its final publishing decision. It surfaces structured AI outputs for human editors to review, edit, approve, or reject. This design preserves editorial accountability while eliminating repetitive manual localization work.

---

## 2. Core Capabilities

| Capability | Function | Output |
|---|---|---|
| Broadcast Transcription | Cleans and structures raw transcripts into publishable articles | Structured JSON with title, content, category, key facts |
| Multilingual Translation | Translates news to 14 regional/global languages | Translated title + content with tone score |
| Cultural Adaptation | Adapts idioms, units, references for target audiences | Adapted content + change log |
| Sensitivity Analysis | Flags content risk across 8 categories | Severity level + per-flag explanations |
| Journalistic Tone Check | Evaluates broadcast readiness of any language version | Score + improvement suggestions |
| Broadcast Summary | Generates 2-sentence broadcast-ready summaries | Plain text summary |

---

## 3. Agent System Prompt

The following system prompt is applied to every Codex AI API call and is cached using `cache_control: ephemeral` to reduce latency and token cost on repeated requests within a session.

```
You are an expert AI Newsroom Assistant specializing in:
1. Journalistic translation preserving formal news tone
2. Cultural adaptation for regional audiences
3. Sensitivity analysis for broadcast content
4. Real-time content localization

Always respond with valid JSON as specified. Never deviate from the output format.
```

**Caching Strategy:** The system prompt is sent with `{"type": "ephemeral"}` cache control. This keeps the prompt warm across multiple API calls within a 5-minute window, reducing repeated prompt token costs during a single article's processing pipeline.

---

## 4. Agent Functions (Tools)

### 4.1 `transcribe_and_clean`

**Purpose:** Converts unstructured broadcast transcript text into a structured, publishable news article.

**Input:**
```
raw_text: str  — Raw broadcast or spoken transcript
```

**Prompt Behavior:** The agent is instructed to identify the headline, restructure the content into inverted-pyramid journalism format, extract key facts, and classify the article category.

**Output Schema:**
```json
{
  "title": "Generated news headline",
  "content": "Cleaned, structured news article text",
  "key_facts": ["fact 1", "fact 2", "fact 3"],
  "estimated_category": "Politics|Business|Sports|Entertainment|Health|Technology|International",
  "confidence": 0.95
}
```

**Fallback:** On JSON parse failure, the function applies regex extraction (`re.search(r'\{.*\}', result, re.DOTALL)`). If extraction fails, it returns the raw text with default metadata.

---

### 4.2 `translate_and_adapt`

**Purpose:** Translates a news article into a target language while preserving journalistic tone and adapting cultural context.

**Input:**
```
title: str            — Original article headline
content: str          — Full article body
target_language: str  — BCP-47 language code (e.g., "hi", "ta")
language_name: str    — Human-readable name (e.g., "Hindi", "Tamil")
```

**Prompt Behavior:** The agent is explicitly instructed to:
1. Use formal journalistic register appropriate for that language's broadcast norms
2. Adapt cultural references, measurement units, and idiomatic expressions
3. Follow regional journalistic conventions (e.g., honorific usage in Tamil, script conventions in Bengali)
4. Document every significant adaptation for the editor's reference

**Output Schema:**
```json
{
  "language_code": "hi",
  "language_name": "Hindi",
  "translated_title": "...",
  "translated_content": "...",
  "cultural_adaptations": ["Description of each adaptation in English"],
  "tone_score": 0.94,
  "notes": "Translator notes for the editor",
  "status": "pending_review"
}
```

**Supported Languages:**

| Code | Language | Code | Language |
|------|----------|------|----------|
| `hi` | Hindi | `ml` | Malayalam |
| `ta` | Tamil | `pa` | Punjabi |
| `te` | Telugu | `or` | Odia |
| `bn` | Bengali | `en` | English |
| `mr` | Marathi | `fr` | French |
| `gu` | Gujarati | `es` | Spanish |
| `kn` | Kannada | `ar` | Arabic |

---

### 4.3 `analyze_sensitivity`

**Purpose:** Evaluates a news article for content that requires editorial review before broadcast.

**Input:**
```
title: str    — Article headline
content: str  — Full article body
```

**Detection Categories:**

| Category | Description |
|---|---|
| Violence / Graphic Content | Explicit descriptions of harm, casualties, or disturbing imagery |
| Political Sensitivity | One-sided political framing, unverified political claims |
| Religious / Cultural Sensitivity | Content that may offend religious communities |
| Privacy Violations | Personally identifiable information, unverified individual allegations |
| Hate Speech / Discrimination | Language targeting identity groups |
| Legal Risk | Defamation, contempt of court, sub judice matters |
| Misinformation | Unverified claims, statistics without sources |
| National Security | Content with potential security implications |

**Output Schema:**
```json
{
  "overall_level": "safe|low|medium|high|critical",
  "safe_to_publish": true,
  "flags": [
    {
      "category": "Political Sensitivity",
      "description": "Article presents only one government perspective without opposition comment",
      "severity": "medium",
      "flagged_text": "The exact text that triggered this flag"
    }
  ],
  "recommendation": "Specific editorial guidance for this article"
}
```

**Severity Scale:**

| Level | Meaning | Action |
|---|---|---|
| `safe` | No concerns | Proceed to publication |
| `low` | Minor issues | Note for editor awareness |
| `medium` | Requires review | Editor must review before approval |
| `high` | Significant risk | Senior editor sign-off required |
| `critical` | Do not publish | Legal/compliance review required |

---

### 4.4 `adapt_cultural_references`

**Purpose:** Performs a second-pass deep cultural adaptation on an already-translated article.

**Input:**
```
content: str           — Already-translated content
target_language: str   — BCP-47 code
language_name: str     — Human-readable language name
```

**Adaptation Scope:**
- Currency conversions (USD → INR, GBP → EUR)
- Unit conversions (miles → km, Fahrenheit → Celsius)
- Date/time format normalization per locale
- Name transliterations
- Regional idiom substitution
- Contextual explanations for audiences unfamiliar with the original event's geography

**Output Schema:**
```json
{
  "adapted_content": "Fully adapted content",
  "changes": ["List of specific changes made"],
  "cultural_context_added": ["Context explanations inserted"]
}
```

---

### 4.5 `generate_summary`

**Purpose:** Creates a broadcast-ready 2-sentence summary of the article.

**Input:**
```
title: str         — Article headline
content: str       — Full article body
language: str      — Target language code (default: "en")
```

**Behavior:** This function does **not** use prompt caching (`use_cache=False`) because summaries are short, one-off requests where cache setup overhead would outweigh savings.

**Output:** Plain text string — no JSON wrapper.

---

### 4.6 `check_journalistic_tone`

**Purpose:** Evaluates translated content for broadcast-quality journalistic tone.

**Input:**
```
content: str        — Content to evaluate
language_name: str  — The language of the content
```

**Output Schema:**
```json
{
  "tone_score": 0.91,
  "issues": ["Passive voice overuse in paragraph 2", "Colloquial phrasing in lead sentence"],
  "suggestions": ["Rewrite lead using active voice", "Replace informal expression with formal equivalent"],
  "is_broadcast_ready": true
}
```

---

## 5. Processing Pipeline

When an article is ingested, the agent executes a sequential background pipeline:

```
ARTICLE INGESTED
      │
      ▼
[1] STATUS → "processing"
      │  WebSocket broadcast: status_update
      │
      ▼
[2] analyze_sensitivity(title, content)
      │  Stores: article.sensitivity
      │  WebSocket broadcast: sensitivity_done
      │
      ▼
[3] FOR EACH target_language:
      │  translate_and_adapt(title, content, lang_code, lang_name)
      │  Stores: article.translations[]
      │  WebSocket broadcast: translation_done
      │
      ▼
[4] STATUS → "review"
      │  WebSocket broadcast: ready_for_review
      │
      ▼
EDITOR REVIEW QUEUE
```

**Pipeline is non-blocking:** FastAPI `BackgroundTasks` runs the pipeline asynchronously. The API returns immediately after ingestion. All status updates are pushed to connected clients via WebSocket.

---

## 6. Editor Interaction Model

The agent produces all outputs in **`pending_review`** status. No content is published without an explicit editor action. Supported editor actions:

| Action | Effect |
|---|---|
| `approve` | Sets article status to `approved` |
| `reject` | Sets article status to `rejected` |
| `publish` | Sets article status to `published` (must be approved first) |
| `edit` | Replaces a specific language's translated content; marks it `editor_revised` |
| `request_retranslation` | Triggers a fresh `translate_and_adapt` call for a given language |

All editor actions accept an optional `editor_note` that is stored in the article's audit log.

---

## 7. Data Schemas

### Article Lifecycle States

```
pending → processing → review → approved → published
                              ↘ rejected
```

### Core Article Object

```json
{
  "id": "A3F9C1B2",
  "title": "string",
  "content": "string",
  "source": "string",
  "category": "string",
  "priority": "normal|high|breaking",
  "target_languages": ["hi", "ta", "te"],
  "status": "pending|processing|review|approved|rejected|published",
  "sensitivity": { ... },
  "translations": [ ... ],
  "editor_notes": [{ "action": "string", "note": "string" }],
  "created_at": "ISO 8601",
  "updated_at": "ISO 8601"
}
```

---

## 8. API Reference

**Base URL:** `http://127.0.0.1:8000`

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/stats` | Dashboard statistics |
| `GET` | `/api/articles` | List articles (filter: `?status=review`) |
| `POST` | `/api/articles` | Ingest structured news article |
| `POST` | `/api/transcribe` | Ingest raw broadcast transcript |
| `GET` | `/api/articles/{id}` | Full article with translations and sensitivity |
| `POST` | `/api/articles/{id}/action` | Editor action (approve/reject/edit/publish) |
| `GET` | `/api/articles/{id}/summary` | Generate broadcast summary |
| `GET` | `/api/articles/{id}/tone-check` | Tone quality analysis |
| `GET` | `/api/languages` | List all supported languages |
| `WS` | `/ws` | WebSocket connection for real-time events |

**Interactive Docs:** `http://127.0.0.1:8000/docs`

---

## 9. WebSocket Event Reference

All pipeline events are broadcast to every connected WebSocket client.

| Event | Payload Fields | Description |
|-------|---------------|-------------|
| `status_update` | `article_id`, `status` | Article status changed |
| `sensitivity_done` | `article_id`, `sensitivity` | Sensitivity analysis completed |
| `translation_done` | `article_id`, `language`, `language_code` | One language translation completed |
| `translation_error` | `article_id`, `language`, `error` | Translation failed for a language |
| `ready_for_review` | `article_id`, `status` | Full pipeline complete, in editor queue |
| `editor_action` | `article_id`, `action` | Editor performed an action |

---

## 10. Configuration

### Environment Variables

```
GEMINI_API_KEY=your_api_key_here
```

### Model Configuration

| Parameter | Value | Notes |
|-----------|-------|-------|
| Model | `gemini-2.0-flash` | Balanced speed + quality for newsroom SLAs |
| Max Tokens | `4096` | Sufficient for full article translations |
| System Prompt Caching | `ephemeral` | Reduces cost on multi-language pipelines |

---

## 11. Error Handling

All Codex AI API response parsing uses a two-stage fallback:

```python
# Stage 1: Direct JSON parse
try:
    return json.loads(result)
except json.JSONDecodeError:
    # Stage 2: Regex extraction of JSON block
    match = re.search(r'\{.*\}', result, re.DOTALL)
    if match:
        return json.loads(match.group())
    # Stage 3: Return safe defaults
    return default_response
```

Translation failures are caught per-language and broadcast as `translation_error` events — a failure in one language does not halt the pipeline for remaining languages.

---

## 12. Security Considerations

- **No content is auto-published.** Every article requires explicit editor approval before status advances to `published`.
- **Sensitivity flags are advisory.** The agent recommends; the editor decides.
- **CORS is open (`allow_origins=["*"]`)** in this hackathon build. Production deployments must restrict to known frontend origins.
- **API keys** are loaded from `.env` and never exposed through any API endpoint.
- **In-memory storage** means data is lost on server restart. Production deployments must use a persistent database (PostgreSQL recommended).

---

## 13. Extending the Agent

### Adding a New Language
1. Add the language code and name to `LANGUAGE_NAMES` in [backend/models.py](backend/models.py)
2. Add it to the `Language` enum
3. It will automatically appear in the frontend language selector

### Adding a New AI Capability
1. Add a new function to [backend/services/codex_service.py](backend/services/codex_service.py) following the existing pattern
2. Add a new API endpoint in [backend/main.py](backend/main.py)
3. Wire up the UI call in [frontend/app.html](frontend/app.html)

### Replacing In-Memory Storage with PostgreSQL
Replace [backend/database.py](backend/database.py) with SQLAlchemy async session calls. All function signatures (`create_article`, `get_article`, `update_article`, `add_translation`, `get_stats`) remain unchanged — the rest of the codebase requires no modification.

---

## 14. Project Structure

```
ai-newsroom/
├── agent.md                          ← This file
├── PROJECT_OVERVIEW.md               ← Hackathon documentation
├── start.bat                         ← Windows one-click startup
│
├── backend/
│   ├── main.py                       ← FastAPI app, routes, WebSocket manager, pipeline
│   ├── models.py                     ← Pydantic schemas, enums, language registry
│   ├── database.py                   ← In-memory article store (CRUD)
│   ├── requirements.txt              ← Python dependencies
│   ├── .env.example                  ← Environment variable template
│   └── services/
│       └── codex_service.py          ← All Codex AI functions (agent core)
│
└── frontend/
    └── app.html                      ← Single-file React app (CDN, no build step)
```

---

## 15. Dependencies

### Backend
| Package | Version | Purpose |
|---------|---------|---------|
| `google-genai` | 2.8.0 | Codex AI API client |
| `fastapi` | 0.115.0 | REST API + WebSocket framework |
| `uvicorn` | 0.32.0 | ASGI server |
| `pydantic` | 2.10.0 | Data validation and serialization |
| `python-dotenv` | 1.0.1 | Environment variable loading |
| `python-multipart` | 0.0.12 | Form data parsing |

### Frontend
| Package | CDN | Purpose |
|---------|-----|---------|
| `react` | unpkg.com | UI framework |
| `@babel/standalone` | unpkg.com | JSX transpilation |
| `responsivevoice` | responsivevoice.org | Multilingual TTS (14 languages) |

---

*Agent specification authored for CODEX Hackathon — Cognizant POD 38 PDP | Byte Break Team | June 2026*
