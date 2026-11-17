import re
import os
from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session
from app.models.models import Scheme, UserProfile, User
from app.services.rag_service import JanSahayRAGService

class ChatService:
    """
    Unified Chat Interface routing citizen requests through the Grounded RAG Pipeline.
    Supports English, Hindi, and Marathi query inputs with source citations.
    """

    GREETING_WORDS = ["hi", "hello", "namaste", "hey", "good morning", "good evening", "help", "नमस्ते", "नमस्कार"]

    @classmethod
    def generate_response(
        cls,
        db: Session,
        message: str,
        user: Optional[User] = None,
        session_id: str = "default-session",
        language: str = "en"
    ) -> Dict[str, Any]:
        text = message.strip()
        text_lower = text.lower()

        # Handle basic greetings gracefully
        if any(w == text_lower or text_lower.startswith(w + " ") for w in cls.GREETING_WORDS):
            user_greeting = f"Namaste {user.full_name.split()[0]}!" if user else "Namaste!"
            welcome_msg = (
                f"{user_greeting} I am **JanSahay AI (जनसहाय)**, your dedicated citizen welfare advisor.\n\n"
                f"I am grounded in **73 official Government of India welfare schemes** and over **3,400 verified Q&A guidelines** across "
                f"Healthcare, Agriculture, Education, Housing, Social Security, and MSME.\n\n"
                f"How can I assist you today? You can ask about eligibility, benefits, application procedures, or required documents."
            )
            # Fetch 3 featured schemes
            featured = db.query(Scheme).filter(Scheme.is_active == True).limit(3).all()
            from app.recommendation.engine import RecommendationEngine
            from app.schemas.scheme import SchemeDetailOut
            profile = user.profile if user else None
            scored = [RecommendationEngine.score_scheme(s, profile) for s in featured]
            serialized_scored = []
            for r in scored:
                sc = r["scheme"]
                if hasattr(sc, "__table__") or not isinstance(sc, dict):
                    sc_dict = SchemeDetailOut.model_validate(sc).model_dump()
                else:
                    sc_dict = sc
                serialized_scored.append({
                    **r,
                    "scheme": sc_dict
                })

            return {
                "message": welcome_msg,
                "intent": "greeting",
                "detected_entities": {},
                "recommended_schemes": serialized_scored,
                "follow_up_suggestions": [
                    "What schemes are available for farmers in Maharashtra?",
                    "Which healthcare schemes provide ₹5 Lakh cashless cover?",
                    "What scholarships are available for students?",
                    "How do I apply for PM SVANidhi as a street vendor?"
                ],
                "reasoning_summary": "Initial citizen greeting with featured central welfare programs.",
                "citations": [
                    {
                        "scheme_name": s.name,
                        "short_name": s.short_name,
                        "category": s.category,
                        "official_url": s.official_url or "https://www.india.gov.in",
                        "source": f"Government of India / {s.department}"
                    }
                    for s in featured
                ],
                "grounded_sources": []
            }

        # Route query through Grounded RAG Engine
        rag_result = JanSahayRAGService.answer_query(
            db=db,
            query=text,
            user=user,
            language=language
        )

        return {
            "message": rag_result["message"],
            "intent": rag_result.get("intent", "scheme_query"),
            "detected_entities": {},
            "recommended_schemes": rag_result.get("recommended_schemes", []),
            "follow_up_suggestions": rag_result.get("follow_up_suggestions", []),
            "reasoning_summary": f"Grounded RAG retrieval matching {len(rag_result.get('recommended_schemes', []))} schemes with official citations.",
            "citations": rag_result.get("citations", []),
            "grounded_sources": rag_result.get("grounded_sources", [])
        }
