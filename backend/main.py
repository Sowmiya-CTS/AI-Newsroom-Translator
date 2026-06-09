import asyncio
import json
import os
from typing import List, Optional
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, BackgroundTasks, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

load_dotenv()

from models import (
    NewsArticleInput, EditorAction, TranscriptionRequest,
    ProcessingResponse, LANGUAGE_NAMES
)
from database import (
    create_article, get_article, get_all_articles,
    update_article, add_translation, get_stats
)
from services.claude_service import (
    transcribe_and_clean, translate_and_adapt,
    analyze_sensitivity, generate_summary, check_journalistic_tone,
    generate_multi_format, calculate_readiness_score, chat_with_assistant
)

app = FastAPI(
    title="AI Newsroom Assistant",
    description="Real-Time Content Localization Platform powered by Claude AI",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# WebSocket connection manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def broadcast(self, message: dict):
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except Exception:
                pass

manager = ConnectionManager()


async def process_article_pipeline(article_id: str):
    """Full AI processing pipeline for a news article."""
    article = get_article(article_id)
    if not article:
        return

    # Step 1: Update status to processing
    update_article(article_id, {"status": "processing"})
    await manager.broadcast({"event": "status_update", "article_id": article_id, "status": "processing"})

    # Step 2: Sensitivity Analysis
    sensitivity = analyze_sensitivity(article["title"], article["content"])
    update_article(article_id, {"sensitivity": sensitivity})
    await manager.broadcast({
        "event": "sensitivity_done",
        "article_id": article_id,
        "sensitivity": sensitivity
    })

    # Step 3: Translate to all target languages (parallel-style)
    target_languages = article.get("target_languages", ["hi", "ta", "te", "bn"])
    for lang_code in target_languages:
        lang_name = LANGUAGE_NAMES.get(lang_code, lang_code)
        try:
            translation = translate_and_adapt(
                article["title"],
                article["content"],
                lang_code,
                lang_name
            )
            add_translation(article_id, translation)
            await manager.broadcast({
                "event": "translation_done",
                "article_id": article_id,
                "language": lang_name,
                "language_code": lang_code
            })
        except Exception as e:
            await manager.broadcast({
                "event": "translation_error",
                "article_id": article_id,
                "language": lang_name,
                "error": str(e)
            })

    # Step 4: Move to review queue
    update_article(article_id, {"status": "review"})
    await manager.broadcast({
        "event": "ready_for_review",
        "article_id": article_id,
        "status": "review"
    })


# ──────────────────────────────────────────────
# REST Endpoints
# ──────────────────────────────────────────────

@app.get("/")
def root():
    return {"message": "AI Newsroom Assistant API", "version": "1.0.0", "status": "running"}


@app.get("/api/stats")
def get_dashboard_stats():
    return get_stats()


@app.get("/api/articles")
def list_articles(status: Optional[str] = None, category: Optional[str] = None):
    articles = get_all_articles()
    if status:
        articles = [a for a in articles if a["status"] == status]
    if category:
        articles = [a for a in articles if a.get("category") == category]
    return {"articles": articles, "total": len(articles)}


@app.get("/api/articles/{article_id}")
def get_article_by_id(article_id: str):
    article = get_article(article_id)
    if not article:
        raise HTTPException(status_code=404, detail="Article not found")
    return article


@app.post("/api/articles", response_model=ProcessingResponse)
async def ingest_article(data: NewsArticleInput, background_tasks: BackgroundTasks):
    article = create_article(data.model_dump())
    background_tasks.add_task(process_article_pipeline, article["id"])
    return ProcessingResponse(
        success=True,
        message="Article ingested. AI processing started.",
        article_id=article["id"],
        data={"article": article}
    )


@app.post("/api/transcribe")
async def transcribe_content(request: TranscriptionRequest, background_tasks: BackgroundTasks):
    """Transcribe and clean raw broadcast text, then ingest as article."""
    cleaned = transcribe_and_clean(request.audio_text)
    article_data = {
        "title": cleaned.get("title", "Untitled"),
        "content": cleaned.get("content", request.audio_text),
        "source": "Broadcast Transcription",
        "category": cleaned.get("estimated_category", "General"),
        "target_languages": ["hi", "ta", "te", "bn", "mr"],
        "priority": "high"
    }
    article = create_article(article_data)
    background_tasks.add_task(process_article_pipeline, article["id"])
    return {
        "success": True,
        "article_id": article["id"],
        "transcription": cleaned,
        "message": "Transcription complete. Processing pipeline started."
    }


@app.post("/api/articles/{article_id}/action")
async def editor_action(article_id: str, action: EditorAction):
    """Handle editor review actions: approve, reject, edit, publish."""
    article = get_article(article_id)
    if not article:
        raise HTTPException(status_code=404, detail="Article not found")

    updates = {}
    if action.action == "approve":
        updates["status"] = "approved"
    elif action.action == "reject":
        updates["status"] = "rejected"
    elif action.action == "publish":
        updates["status"] = "published"
    elif action.action == "edit" and action.language_code and action.modified_content:
        translations = article.get("translations", [])
        for t in translations:
            if t["language_code"] == action.language_code:
                t["translated_content"] = action.modified_content
                t["status"] = "editor_revised"
                break
        updates["translations"] = translations
    elif action.action == "request_retranslation" and action.language_code:
        lang_name = LANGUAGE_NAMES.get(action.language_code, action.language_code)
        new_translation = translate_and_adapt(
            article["title"], article["content"],
            action.language_code, lang_name
        )
        add_translation(article_id, new_translation)
        return {"success": True, "message": f"Retranslation complete for {lang_name}"}

    if action.editor_note:
        notes = article.get("editor_notes", [])
        notes.append({"note": action.editor_note, "action": action.action})
        updates["editor_notes"] = notes

    updated = update_article(article_id, updates)
    await manager.broadcast({
        "event": "editor_action",
        "article_id": article_id,
        "action": action.action
    })
    return {"success": True, "article": updated}


@app.get("/api/articles/{article_id}/summary")
def get_article_summary(article_id: str, language: str = "en"):
    article = get_article(article_id)
    if not article:
        raise HTTPException(status_code=404, detail="Article not found")
    summary = generate_summary(article["title"], article["content"], language)
    return {"article_id": article_id, "language": language, "summary": summary}


@app.get("/api/articles/{article_id}/tone-check")
def check_tone(article_id: str, language_code: str = "en"):
    article = get_article(article_id)
    if not article:
        raise HTTPException(status_code=404, detail="Article not found")

    if language_code == "en":
        result = check_journalistic_tone(article["content"], "English")
    else:
        translation = next(
            (t for t in article.get("translations", []) if t["language_code"] == language_code), None
        )
        if not translation:
            raise HTTPException(status_code=404, detail="Translation not found")
        lang_name = LANGUAGE_NAMES.get(language_code, language_code)
        result = check_journalistic_tone(translation["translated_content"], lang_name)

    return {"article_id": article_id, "language_code": language_code, "analysis": result}


@app.get("/api/languages")
def get_supported_languages():
    return {"languages": [{"code": k, "name": v} for k, v in LANGUAGE_NAMES.items()]}


@app.get("/api/articles/{article_id}/multi-format")
def get_multi_format(article_id: str, language_code: str = "en"):
    article = get_article(article_id)
    if not article:
        raise HTTPException(status_code=404, detail="Article not found")
    if language_code == "en":
        title, content = article["title"], article["content"]
        lang_name = "English"
    else:
        translation = next(
            (t for t in article.get("translations", []) if t["language_code"] == language_code), None
        )
        if not translation:
            raise HTTPException(status_code=404, detail="Translation not found")
        title, content = translation["translated_title"], translation["translated_content"]
        lang_name = LANGUAGE_NAMES.get(language_code, language_code)
    formats = generate_multi_format(title, content, lang_name)
    return {"article_id": article_id, "language_code": language_code, "formats": formats}


@app.get("/api/articles/{article_id}/readiness")
def get_readiness(article_id: str):
    article = get_article(article_id)
    if not article:
        raise HTTPException(status_code=404, detail="Article not found")
    return {"article_id": article_id, "readiness": calculate_readiness_score(article)}


# ──────────────────────────────────────────────
# WebSocket for real-time updates
# ──────────────────────────────────────────────

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)


@app.get("/api/articles/{article_id}/sensitivity")
def get_sensitivity(article_id: str):
    article = get_article(article_id)
    if not article:
        raise HTTPException(status_code=404, detail="Article not found")
    return {"article_id": article_id, "sensitivity": article.get("sensitivity", {})}


@app.post("/api/articles/{article_id}/approve")
async def approve_translation(article_id: str, body: dict):
    article = get_article(article_id)
    if not article:
        raise HTTPException(status_code=404, detail="Article not found")
    lang_code = body.get("language_code")
    translations = article.get("translations", [])
    for t in translations:
        if t["language_code"] == lang_code:
            t["status"] = "approved"
    update_article(article_id, {"translations": translations})
    return {"success": True, "message": f"{lang_code} approved"}


@app.post("/api/articles/{article_id}/reject")
async def reject_translation(article_id: str, body: dict):
    article = get_article(article_id)
    if not article:
        raise HTTPException(status_code=404, detail="Article not found")
    lang_code = body.get("language_code")
    reason = body.get("reason", "Editorial revision required")
    translations = article.get("translations", [])
    for t in translations:
        if t["language_code"] == lang_code:
            t["status"] = "rejected"
            t["reject_reason"] = reason
    update_article(article_id, {"translations": translations})
    return {"success": True, "message": f"{lang_code} rejected"}


@app.post("/api/articles/{article_id}/publish")
async def publish_article(article_id: str):
    article = get_article(article_id)
    if not article:
        raise HTTPException(status_code=404, detail="Article not found")
    update_article(article_id, {"status": "published"})
    await manager.broadcast({"event": "article_published", "article_id": article_id})
    return {"success": True, "message": "Article published"}


@app.post("/api/demo/ingest")
async def demo_ingest(background_tasks: BackgroundTasks):
    demo_data = {
        "raw_transcript": "BREAKING: A 6.8 magnitude earthquake struck Visakhapatnam at 3:42 AM. The National Disaster Response Force deployed 12 teams. Over 200 buildings damaged. State government declared red alert. Tsunami warning issued for coastal areas within 50km.",
        "source": "PTI Wire",
        "category": "Breaking News",
        "target_languages": ["hi", "ta", "te", "bn", "mr"]
    }
    from models import NewsArticleInput
    cleaned = transcribe_and_clean(demo_data["raw_transcript"])
    article_data = {
        "title": cleaned.get("title", "Breaking: Earthquake Strikes Visakhapatnam"),
        "content": cleaned.get("content", demo_data["raw_transcript"]),
        "source": demo_data["source"],
        "category": demo_data["category"],
        "target_languages": demo_data["target_languages"],
        "key_facts": cleaned.get("key_facts", []),
    }
    article = create_article(article_data)
    background_tasks.add_task(process_article_pipeline, article["id"])
    return {"success": True, "article_id": article["id"], "message": "Demo article ingested"}


# ──────────────────────────────────────────────
# AI Chatbot Endpoint
# ──────────────────────────────────────────────

@app.post("/api/chat")
async def chat_endpoint(body: dict):
    message = body.get("message", "").strip()
    context = body.get("context", "")
    if not message:
        raise HTTPException(status_code=400, detail="Message required")
    try:
        response = chat_with_assistant(message, context)
        return {"reply": response, "success": True}
    except Exception as e:
        return {"reply": f"I encountered an error: {str(e)}. Please check if the backend is configured correctly.", "success": False}


# ──────────────────────────────────────────────
# MCP (Model Context Protocol) Connector
# ──────────────────────────────────────────────

MCP_TOOLS = [
    {
        "name": "list_articles",
        "description": "List all news articles in the newsroom with their status",
        "inputSchema": {"type": "object", "properties": {"status": {"type": "string", "description": "Filter by status: processing, review, published"}}, "required": []}
    },
    {
        "name": "get_article",
        "description": "Get full details of a specific news article including translations and sensitivity analysis",
        "inputSchema": {"type": "object", "properties": {"article_id": {"type": "string", "description": "The article ID"}}, "required": ["article_id"]}
    },
    {
        "name": "analyze_article_sensitivity",
        "description": "Run sensitivity analysis on a news article for editorial review",
        "inputSchema": {"type": "object", "properties": {"article_id": {"type": "string"}}, "required": ["article_id"]}
    },
    {
        "name": "get_pipeline_stats",
        "description": "Get current newsroom pipeline statistics",
        "inputSchema": {"type": "object", "properties": {}, "required": []}
    },
    {
        "name": "ingest_article",
        "description": "Ingest a new news article into the AI processing pipeline",
        "inputSchema": {
            "type": "object",
            "properties": {
                "raw_transcript": {"type": "string", "description": "Raw broadcast transcript text"},
                "source": {"type": "string", "description": "News source/wire service"},
                "target_languages": {"type": "array", "items": {"type": "string"}, "description": "Language codes to translate to"}
            },
            "required": ["raw_transcript"]
        }
    },
    {
        "name": "get_translations",
        "description": "Get all translations for a specific article",
        "inputSchema": {"type": "object", "properties": {"article_id": {"type": "string"}}, "required": ["article_id"]}
    }
]


@app.get("/mcp/tools")
def list_mcp_tools():
    return {"tools": MCP_TOOLS, "protocol": "MCP-1.0", "server": "ai-newsroom-mcp"}


@app.post("/mcp/execute")
async def execute_mcp_tool(body: dict, background_tasks: BackgroundTasks):
    tool_name = body.get("tool")
    params = body.get("params", {})

    if tool_name == "list_articles":
        articles = get_all_articles()
        status_filter = params.get("status")
        if status_filter:
            articles = [a for a in articles if a.get("status") == status_filter]
        return {"result": {"articles": articles, "count": len(articles)}}

    elif tool_name == "get_article":
        article = get_article(params.get("article_id", ""))
        if not article:
            return {"error": "Article not found"}
        return {"result": article}

    elif tool_name == "analyze_article_sensitivity":
        article = get_article(params.get("article_id", ""))
        if not article:
            return {"error": "Article not found"}
        sensitivity = analyze_sensitivity(article["title"], article["content"])
        update_article(article["id"], {"sensitivity": sensitivity})
        return {"result": sensitivity}

    elif tool_name == "get_pipeline_stats":
        return {"result": get_stats()}

    elif tool_name == "ingest_article":
        cleaned = transcribe_and_clean(params.get("raw_transcript", ""))
        article_data = {
            "title": cleaned.get("title", "Untitled"),
            "content": cleaned.get("content", params.get("raw_transcript", "")),
            "source": params.get("source", "MCP Client"),
            "category": cleaned.get("estimated_category", "General"),
            "target_languages": params.get("target_languages", ["hi", "ta", "te"]),
            "key_facts": cleaned.get("key_facts", [])
        }
        article = create_article(article_data)
        background_tasks.add_task(process_article_pipeline, article["id"])
        return {"result": {"article_id": article["id"], "message": "Article ingested via MCP"}}

    elif tool_name == "get_translations":
        article = get_article(params.get("article_id", ""))
        if not article:
            return {"error": "Article not found"}
        return {"result": {"translations": article.get("translations", [])}}

    else:
        return {"error": f"Unknown tool: {tool_name}"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
