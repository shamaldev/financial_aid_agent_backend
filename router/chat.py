from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func
from sqlalchemy.orm import Session
from uuid import uuid4, UUID
import json
from app.oauth2 import get_current_user
from app.redis_client import get_redis
from app import models, schemas
from app.database import get_db
from chatbot.llm import ChatbotAgents
 
agent = ChatbotAgents()
 
router = APIRouter(
    prefix="",
    tags=["Chat"])
 
# GET /api/v1/chats
@router.get(
    "/",
    response_model=schemas.ChatListResponse
)
def list_chat_sessions(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """List all chat sessions for the current user"""
    sessions = (
        db.query(models.ChatSession)
          .filter(models.ChatSession.user_id == current_user.id)
          .order_by(models.ChatSession.last_updated.desc())
          .all()
    )
 
    return schemas.ChatListResponse(
        sessions=[
            schemas.ChatSessionMeta(
                chat_id=s.chat_id,
                created_at=s.created_at,
                last_updated=s.last_updated,
            )
            for s in sessions
        ]
    )
 
 # GET /api/v1/chats/{chat_id}/messages
@router.get(
    "/{chat_id}/messages",
    response_model=schemas.ChatHistoryResponse
)
def get_chat_history(
    chat_id: UUID,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    """Retrieve full message history for a chat session"""
    # verify session
    session = (
        db.query(models.ChatSession)
          .filter_by(chat_id=chat_id, user_id=current_user.id)
          .first()
    )
    if not session:
        raise HTTPException(status_code=404, detail="Chat session not found")
 
    messages = (
        db.query(models.ChatMessage)
          .filter_by(chat_id=chat_id)
          .order_by(models.ChatMessage.created_at)
          .all()
    )
    return schemas.ChatHistoryResponse(
        chat_id=chat_id,
        messages=[
            schemas.ChatMessageOut(
                content=m.message,
                role="user" if m.is_user else "assistant",
                created_at=m.created_at
            )
            for m in messages
        ],
    )
 
 # POST /api/v1/chats/
@router.post(
    "/",
    response_model=schemas.ChatResponse,
    status_code=status.HTTP_200_OK
)
async def send_message(
    payload: schemas.ChatRequest,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
    redis=Depends(get_redis)
):
    """Send a message: starts a new session if chat_id not provided, or continues existing"""
    # ─── 1) Determine / create chat session ─────────────────────────
    if payload.chat_id:
        chat_id = payload.chat_id
        session = (
            db.query(models.ChatSession)
              .filter_by(chat_id=chat_id, user_id=current_user.id)
              .first()
        )
        if not session:
            raise HTTPException(status_code=404, detail="Chat session not found")
    else:
        chat_id = uuid4()
        session = models.ChatSession(
            chat_id=chat_id,
            user_id=current_user.id,
        )
        db.add(session)
        db.commit()
        db.refresh(session)

    cache_key = f"chat:{current_user.id}:{chat_id}"

    # ─── 2) Backfill Redis if empty ────────────────────────────────
    if await redis.exists(cache_key) == 0:
        past = (
            db.query(models.ChatMessage)
              .filter_by(user_id=current_user.id, chat_id=chat_id)
              .order_by(models.ChatMessage.created_at)
              .all()
        )
        for m in past:
            await redis.rpush(cache_key, json.dumps({
                "is_user": m.is_user,
                "message": m.message
            }))
        await redis.expire(cache_key, 86_400)

    # ─── 3) Push & persist user message ────────────────────────────
    await redis.rpush(cache_key, json.dumps({
        "is_user": True,
        "message": payload.message
    }))
    await redis.expire(cache_key, 86_400)

    db.add(models.ChatMessage(
        user_id=current_user.id,
        chat_id=chat_id,
        message=payload.message,
        is_user=True
    ))
    db.commit()

    # ─── 4) Assemble recent context & call LLM ─────────────────────
    all_messages = await redis.lrange(cache_key, 0, -1)
    current_question = payload.message
    previous_messages = all_messages[:-1]  # Exclude the current user message

    # Take up to the last 4 messages (2 pairs)
    if len(previous_messages) > 4:
        history_messages = previous_messages[-4:]
    else:
        history_messages = previous_messages

    # Format history as a list of "user: question\nassistant: response" strings
    history_list = []
    for i in range(0, len(history_messages), 2):
        if i + 1 < len(history_messages):  # Ensure we have a pair
            user_msg = json.loads(history_messages[i])["message"]
            assistant_msg = json.loads(history_messages[i + 1])["message"]
            history_list.append(f"user: {user_msg}\nassistant: {assistant_msg}")

    # Limit to top 3 recent pairs
    history_list = history_list[-3:]

    # Generate bot response with separate question and history
    try:
        bot_resp = agent.generate_answer(current_question, history_list)
    except Exception as e:
        raise e

    # ─── 5) Push & persist bot response ────────────────────────────
    await redis.rpush(cache_key, json.dumps({
        "is_user": False,
        "message": bot_resp
    }))
    await redis.expire(cache_key, 86_400)

    db.add(models.ChatMessage(
        user_id=current_user.id,
        chat_id=chat_id,
        message=bot_resp,
        is_user=False
    ))

    # ─── 6) Bump session.last_updated & commit ────────────────────
    session.last_updated = func.now()
    db.add(session)
    db.commit()

    return schemas.ChatResponse(response=bot_resp, chat_id=chat_id)