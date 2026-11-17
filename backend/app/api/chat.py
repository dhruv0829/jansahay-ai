import json
from typing import Optional
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.models.models import User, ChatHistory
from app.schemas.chat import ChatRequest, ChatResponse
from app.services.auth_service import get_current_user, get_optional_current_user
from app.services.chat_service import ChatService

router = APIRouter(prefix="/chat", tags=["AI Scheme Assistant"])

@router.post("", response_model=ChatResponse)
def handle_chat_message(
    req: ChatRequest,
    current_user: Optional[User] = Depends(get_optional_current_user),
    db: Session = Depends(get_db)
):
    # Process message via Grounded Civic RAG Engine
    response = ChatService.generate_response(
        db=db,
        message=req.message,
        user=current_user,
        session_id=req.session_id or "default-session",
        language=req.language or "en"
    )

    # Persist chats only for signed-in users. Anonymous chat text may contain
    # personal details and must not be stored under a shared predictable ID.
    if current_user:
        try:
            user_msg = ChatHistory(
                user_id=current_user.id,
                session_id=req.session_id or "default-session",
                role="user",
                content=req.message
            )
            db.add(user_msg)

            ai_msg = ChatHistory(
                user_id=current_user.id,
                session_id=req.session_id or "default-session",
                role="assistant",
                content=response["message"],
                structured_json=json.dumps({
                    "citations": response.get("citations", []),
                    "intent": response.get("intent")
                })
            )
            db.add(ai_msg)
            db.commit()
        except Exception:
            db.rollback()

    return response

@router.get("/history/{session_id}")
def get_chat_history(
    session_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    history = db.query(ChatHistory).filter(
        ChatHistory.session_id == session_id,
        ChatHistory.user_id == current_user.id,
    ).order_by(ChatHistory.created_at.asc()).all()
    return [
        {
            "id": h.id,
            "role": h.role,
            "content": h.content,
            "created_at": h.created_at.isoformat()
        }
        for h in history
    ]
