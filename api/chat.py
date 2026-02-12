"""Chat API — called by the widget embedded in your portal."""
import re
import uuid
import logging
from fastapi import APIRouter, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from api.schemas import StartResponse, ChatRequest, ChatResponse, MessageResponse
from db.database import get_db
from db import crud
from core.state import UserState
from core.router import route_callback, route_text
from utils.rate_limiter import RateLimiter

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api", tags=["Chat"])
limiter = RateLimiter(max_requests=10, window_seconds=30)


@router.post("/session/start", response_model=StartResponse)
async def start_session(request: Request, db: AsyncSession = Depends(get_db)):
    """Called once when user opens the chat widget."""
    session_id = str(uuid.uuid4())
    state = UserState()

    ip = request.client.host if request.client else None
    ua = (request.headers.get("user-agent") or "")[:256]

    await crud.create_session(db, session_id, state.to_dict(), ip, ua)
    await crud.log_event(db, "session_start", session_id)

    from core.flows.menu import get_menu
    welcome = get_menu()

    welcome_text = "👋 Welcome to CPBFI Helpdesk!\n\nHow can I assist you today?"

    await crud.save_message(db, session_id, "bot", welcome_text, buttons=welcome["buttons"])

    return StartResponse(
        session_id=session_id,
        message=MessageResponse(text=welcome_text, buttons=welcome["buttons"])
    )


@router.post("/chat", response_model=ChatResponse)
async def chat(req: ChatRequest, db: AsyncSession = Depends(get_db)):
    """Called for every user action (text message or button click)."""

    # Rate limit
    if not limiter.is_allowed(req.session_id):
        return ChatResponse(text="⚠️ Too many messages. Please wait a moment.", buttons=[])

    # Load session from DB
    session = await crud.get_session(db, req.session_id)
    if not session:
        return ChatResponse(text="Session expired. Please refresh the page.", buttons=[])

    state = UserState.from_dict(session.state)

    # Log user input
    message_text = req.message
    callback_data = req.callback_data
    
    # Sanitize inputs
    if message_text:
        message_text = message_text.strip()[:2000]  # Limit to 2000 chars
        await crud.save_message(db, req.session_id, "user", message_text)
        await crud.log_event(db, "message", req.session_id)
    if callback_data:
        # Validate callback_data against allowed pattern (alphanumeric, underscore, dash)
        callback_data = callback_data.strip()
        if not callback_data or len(callback_data) > 100 or not re.match(r'^[a-zA-Z0-9_-]+$', callback_data):
            return ChatResponse(text="Invalid action.", buttons=[])
        
        await crud.save_message(db, req.session_id, "user",
            f"[clicked: {callback_data}]", callback=callback_data)
        await crud.log_event(db, "button_click", req.session_id, detail=callback_data)

    # Route to correct flow
    if callback_data:
        response = route_callback(state, callback_data)
    elif message_text:
        response = await route_text(state, message_text, db=db, session_id=req.session_id)
    else:
        return ChatResponse(text="Send a message or click a button.", buttons=[])

    # If escalation just completed, save to escalations table
    if state.detail_collection and state.detail_collection.get("_complete"):
        d = state.detail_collection
        await crud.save_escalation(db,
            session_id=req.session_id,
            category=d["category"],
            issue=d["issue"],
            portal=d.get("portal", ""),
            assessment_type=d.get("assessment_type", ""),
            name=d["name"],
            email=d["email"],
            bfsi_id=d["bfsi"],
            description=d.get("description", ""),
            email_sent=d.get("_email_sent", False)
        )
        state.detail_collection = None
        # Reset escalation counter for this category
        if d["category"] == "login":
            state.login_escalation = {"count": 0, "portal": "", "issue": ""}
        elif d["category"] == "assessment":
            state.assessment_escalation = {"count": 0, "issue": "", "type": ""}
        elif d["category"] == "lms":
            state.lms_escalation = {"count": 0, "issue": ""}
        await crud.log_event(db, "escalation", req.session_id, category=d["category"])

    # Save bot response
    await crud.save_message(db, req.session_id, "bot",
        response["text"], buttons=response.get("buttons"))

    # Persist updated state back to DB
    await crud.update_session_state(db, req.session_id, state.to_dict())

    return ChatResponse(text=response["text"], buttons=response.get("buttons", []))
