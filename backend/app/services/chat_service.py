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
    SCHEME_INTENT_WORDS = (
        "scheme", "yojana", "government benefit", "benefit", "benefits", "welfare", "eligibility", "eligible",
        "apply", "application", "documents", "subsidy", "pension", "scholarship",
        "ration", "lpg", "ujjwala", "ayushman", "pm-kisan", "loan", "financial assistance",
        "सरकारी योजना", "योजना", "पात्रता", "आवेदन", "दस्तावेज"
    )
    LGBTQ_TERMS = ("gay", "lesbian", "bisexual", "transgender", "lgbt", "same-sex", "homosexual")

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
        is_greeting = any(w == text_lower or text_lower.startswith(w + " ") for w in cls.GREETING_WORDS)

        name_question_patterns = ("what's my name", "whats my name", "what is my name", "do you know my name", "tell me my name")
        if any(pattern in text_lower for pattern in name_question_patterns):
            answer = (
                f"Your account name is **{user.full_name}**."
                if user and user.full_name
                else "I don’t have a name for this chat. Sign in to let me use the name on your account."
            )
            return {
                "message": answer,
                "intent": "personal_information",
                "detected_entities": {},
                "recommended_schemes": [],
                "follow_up_suggestions": [],
                "reasoning_summary": "Answered from the signed-in account name; no scheme lookup was performed.",
                "citations": [],
                "grounded_sources": []
            }

        # Recognize meta-questions before looking for scheme keywords: users may
        # paste a prior scheme answer while asking why it was produced.
        meta_patterns = (
            "what has the user asked", "what did the user ask", "what is the user asking",
            "give details about what has the user asked", "why did it give this answer",
            "why did you give this answer", "why is it giving this"
        )
        if any(pattern in text_lower for pattern in meta_patterns):
            return {
                "message": (
                    "You’re asking me to explain or summarize the user’s question. The scheme text "
                    "you pasted is context from a previous answer; it isn’t itself a request for "
                    "scheme eligibility details."
                ),
                "intent": "meta_question",
                "detected_entities": {},
                "recommended_schemes": [],
                "follow_up_suggestions": [],
                "reasoning_summary": "Recognized a question about the conversation rather than a scheme lookup.",
                "citations": [],
                "grounded_sources": []
            }

        # Personal or general questions must not be sent to scheme retrieval. The
        # retriever can find weak keyword overlaps and then confidently attach an
        # unrelated scheme, so only explicit welfare questions reach the RAG path.
        asks_about_schemes = any(term in text_lower for term in cls.SCHEME_INTENT_WORDS)
        if not asks_about_schemes and not is_greeting:
            if any(term in text_lower for term in cls.LGBTQ_TERMS):
                answer = (
                    "Being gay (or another LGBTQ+ identity) is a normal part of human diversity; "
                    "there is nothing wrong with you. If you mean a particular concern—such as "
                    "safety, family acceptance, relationships, or whether a government benefit "
                    "applies to you—tell me a little more and I’ll respond to that directly."
                )
                intent = "personal_support"
            else:
                answer = (
                    "I’m JanSahay, focused on Indian government schemes and welfare benefits. "
                    "I couldn’t identify a scheme-related question in your message. If you’re "
                    "asking about a benefit, tell me the scheme or what support you need."
                )
                intent = "out_of_scope"
            return {
                "message": answer,
                "intent": intent,
                "detected_entities": {},
                "recommended_schemes": [],
                "follow_up_suggestions": [],
                "reasoning_summary": "No scheme lookup was performed because the message was not a welfare-scheme question.",
                "citations": [],
                "grounded_sources": []
            }

        # Handle basic greetings gracefully
        if is_greeting:
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
