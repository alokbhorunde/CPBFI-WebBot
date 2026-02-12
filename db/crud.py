"""All database CRUD operations."""
import logging
from datetime import datetime, timezone, timedelta
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from db.models import Session, Message, Escalation, AnalyticsEvent

logger = logging.getLogger(__name__)


# --- Sessions ---

async def create_session(db: AsyncSession, session_id: str, state: dict,
                         ip: str = None, ua: str = None):
    """Create a new chat session."""
    s = Session(id=session_id, state=state, ip_address=ip, user_agent=ua)
    db.add(s)
    await db.flush()
    return s


async def get_session(db: AsyncSession, session_id: str):
    """Get a session by ID."""
    result = await db.execute(select(Session).where(Session.id == session_id))
    return result.scalar_one_or_none()


async def update_session_state(db: AsyncSession, session_id: str, state: dict):
    """Update a session's state JSON."""
    session = await get_session(db, session_id)
    if session:
        session.state = state
        session.updated_at = datetime.now(timezone.utc)
        await db.flush()


# --- Messages ---

async def save_message(db: AsyncSession, session_id: str, role: str,
                       content: str, buttons: list = None, callback: str = None):
    """Save a message to the conversation log."""
    msg = Message(
        session_id=session_id,
        role=role,
        content=content,
        buttons=buttons,
        callback=callback
    )
    db.add(msg)
    await db.flush()
    return msg


async def get_messages(db: AsyncSession, session_id: str, limit: int = 50):
    """Get recent messages for a session."""
    result = await db.execute(
        select(Message)
        .where(Message.session_id == session_id)
        .order_by(Message.created_at.desc())
        .limit(limit)
    )
    messages = result.scalars().all()
    return list(reversed(messages))


# --- Escalations ---

async def save_escalation(db: AsyncSession, session_id: str, category: str,
                          issue: str, portal: str, assessment_type: str,
                          name: str, email: str, bfsi_id: str,
                          description: str = "", email_sent: bool = False):
    """Save an escalation ticket."""
    esc = Escalation(
        session_id=session_id,
        category=category,
        issue=issue,
        portal=portal or None,
        assessment_type=assessment_type or None,
        student_name=name,
        student_email=email,
        bfsi_id=bfsi_id,
        description=description or None,
        email_sent=email_sent,
        status="sent" if email_sent else "failed"
    )
    db.add(esc)
    await db.flush()
    return esc


async def get_escalations(db: AsyncSession, status: str = None, limit: int = 50):
    """Get escalation tickets, optionally filtered by status."""
    query = select(Escalation).order_by(Escalation.created_at.desc()).limit(limit)
    if status:
        query = query.where(Escalation.status == status)
    result = await db.execute(query)
    return result.scalars().all()


# --- Analytics ---

async def log_event(db: AsyncSession, event: str, session_id: str = None,
                    category: str = None, detail: str = None):
    """Log an analytics event."""
    evt = AnalyticsEvent(
        event=event, session_id=session_id,
        category=category, detail=detail
    )
    db.add(evt)
    await db.flush()


async def get_stats(db: AsyncSession):
    """Get summary stats for the admin dashboard."""
    now = datetime.now(timezone.utc)
    today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    week_ago = now - timedelta(days=7)

    # Total sessions
    total_sessions = await db.execute(select(func.count(Session.id)))
    total_sessions = total_sessions.scalar() or 0

    # Today's sessions
    today_sessions = await db.execute(
        select(func.count(Session.id)).where(Session.created_at >= today_start)
    )
    today_sessions = today_sessions.scalar() or 0

    # Total messages
    total_messages = await db.execute(select(func.count(Message.id)))
    total_messages = total_messages.scalar() or 0

    # Total escalations
    total_escalations = await db.execute(select(func.count(Escalation.id)))
    total_escalations = total_escalations.scalar() or 0

    # Pending escalations
    pending = await db.execute(
        select(func.count(Escalation.id)).where(Escalation.status.in_(["pending", "failed"]))
    )
    pending = pending.scalar() or 0

    # Events this week
    week_events = await db.execute(
        select(func.count(AnalyticsEvent.id)).where(AnalyticsEvent.created_at >= week_ago)
    )
    week_events = week_events.scalar() or 0

    return {
        "total_sessions": total_sessions,
        "today_sessions": today_sessions,
        "total_messages": total_messages,
        "total_escalations": total_escalations,
        "pending_escalations": pending,
        "events_this_week": week_events
    }
