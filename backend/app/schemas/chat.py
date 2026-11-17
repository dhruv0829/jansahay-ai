from typing import Optional, List, Any, Dict
from pydantic import BaseModel

class ChatMessage(BaseModel):
    role: str # "user" or "assistant"
    content: str
    structured_data: Optional[Any] = None

class ChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = "default-session"
    language: Optional[str] = "en"
    context: Optional[dict] = None

class CitationItem(BaseModel):
    scheme_name: str
    short_name: Optional[str] = None
    category: Optional[str] = None
    official_url: str
    source: str

class ChatResponse(BaseModel):
    message: str
    intent: str
    detected_entities: dict = {}
    recommended_schemes: List[Any] = []
    follow_up_suggestions: List[str] = []
    reasoning_summary: Optional[str] = None
    citations: List[CitationItem] = []
    grounded_sources: List[Dict[str, Any]] = []
