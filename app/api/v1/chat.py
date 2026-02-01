from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from app.api import deps
from app.models.user import User
from app.models.chat import ChatMessage
from app.core.config import settings
from app.core.ratelimit import rate_limiter
from google import genai

router = APIRouter()

# Инициализация клиента Gemini
client = genai.Client(api_key=settings.GEMINI_API_KEY)

class ChatRequest(BaseModel):
    message: str
    context_topic: str = "General Programming"

class ChatResponse(BaseModel):
    reply: str
    message_id: int # ID сообщения AI для лайка

@router.post("/ask", response_model=ChatResponse, dependencies=[Depends(rate_limiter)])
def ask_ai_mentor(
    request: ChatRequest,
    current_user: User = Depends(deps.get_current_user),
    db: Session = Depends(deps.get_db)
):
    """
    Отвечает на вопросы пользователя в контексте текущей темы обучения.
    """
    # 1. Сохраняем вопрос пользователя
    user_msg = ChatMessage(
        user_id=current_user.id,
        role="user",
        content=request.message,
        context_topic=request.context_topic
    )
    db.add(user_msg)
    db.commit()

    try:
        # 2. Формируем промпт
        prompt = f"""
        You are an expert AI Tech Mentor for a student named {current_user.username}.
        The student is currently studying the topic: "{request.context_topic}".
        
        The student asks: "{request.message}"
        
        Provide a helpful, concise, and encouraging answer. 
        If the question is technical, give a short code example if applicable.
        Keep the tone friendly and professional.
        """

        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=prompt
        )
        
        reply_text = response.text

        # 3. Сохраняем ответ AI
        ai_msg = ChatMessage(
            user_id=current_user.id,
            role="ai",
            content=reply_text,
            context_topic=request.context_topic
        )
        db.add(ai_msg)
        db.commit()
        db.refresh(ai_msg)
        
        return {"reply": reply_text, "message_id": ai_msg.id}

    except Exception as e:
        print(f"AI Chat Error: {e}")
        if "429" in str(e):
             raise HTTPException(status_code=429, detail="AI Service is busy. Please try again later.")
        raise HTTPException(status_code=500, detail="AI Mentor is currently unavailable.")


@router.post("/{message_id}/like")
def like_message(
    message_id: int,
    is_liked: bool = True,
    current_user: User = Depends(deps.get_current_user),
    db: Session = Depends(deps.get_db)
):
    msg = db.query(ChatMessage).filter(ChatMessage.id == message_id, ChatMessage.user_id == current_user.id).first()
    if not msg:
        raise HTTPException(status_code=404, detail="Message not found")
    
    msg.is_liked = is_liked
    db.commit()
    return {"status": "ok"}
