from pydantic import BaseModel
from typing import Optional, List
from enum import Enum


class Language(str, Enum):
    HINDI = "hi"
    TAMIL = "ta"
    TELUGU = "te"
    BENGALI = "bn"
    MARATHI = "mr"
    GUJARATI = "gu"
    KANNADA = "kn"
    MALAYALAM = "ml"
    PUNJABI = "pa"
    ODIA = "or"
    ENGLISH = "en"
    FRENCH = "fr"
    SPANISH = "es"
    ARABIC = "ar"


LANGUAGE_NAMES = {
    "hi": "Hindi", "ta": "Tamil", "te": "Telugu", "bn": "Bengali",
    "mr": "Marathi", "gu": "Gujarati", "kn": "Kannada", "ml": "Malayalam",
    "pa": "Punjabi", "or": "Odia", "en": "English", "fr": "French",
    "es": "Spanish", "ar": "Arabic"
}


class SensitivityLevel(str, Enum):
    SAFE = "safe"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class ContentStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    REVIEW = "review"
    APPROVED = "approved"
    REJECTED = "rejected"
    PUBLISHED = "published"


class NewsArticleInput(BaseModel):
    title: str
    content: str
    source: Optional[str] = "Manual Input"
    category: Optional[str] = "General"
    target_languages: List[str] = ["hi", "ta", "te", "bn"]
    priority: Optional[str] = "normal"


class TranscriptionRequest(BaseModel):
    audio_text: str
    source_language: Optional[str] = "en"


class TranslationResult(BaseModel):
    language_code: str
    language_name: str
    translated_title: str
    translated_content: str
    cultural_adaptations: List[str]
    tone_score: float
    status: str = "pending_review"


class SensitivityFlag(BaseModel):
    category: str
    description: str
    severity: SensitivityLevel
    flagged_text: Optional[str] = None


class SensitivityAnalysis(BaseModel):
    overall_level: SensitivityLevel
    flags: List[SensitivityFlag]
    recommendation: str
    safe_to_publish: bool


class NewsArticle(BaseModel):
    id: str
    title: str
    content: str
    source: str
    category: str
    status: ContentStatus
    sensitivity: Optional[SensitivityAnalysis] = None
    translations: List[TranslationResult] = []
    created_at: str
    updated_at: str


class EditorAction(BaseModel):
    article_id: str
    language_code: Optional[str] = None
    action: str
    editor_note: Optional[str] = None
    modified_content: Optional[str] = None


class ProcessingResponse(BaseModel):
    success: bool
    message: str
    article_id: str
    data: Optional[dict] = None
