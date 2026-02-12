"""Database models — 4 tables for the web chatbot."""
import json
from datetime import datetime, timezone
from sqlalchemy import Column, String, Text, Boolean, Integer, DateTime, ForeignKey, Index
from sqlalchemy.types import TypeDecorator
from db.database import Base


class JSONType(TypeDecorator):
    """Store Python dicts/lists as JSON strings (SQLite-compatible JSONB replacement)."""
    impl = Text
    cache_ok = True

    def process_bind_param(self, value, dialect):
        if value is not None:
            return json.dumps(value)
        return None

    def process_result_value(self, value, dialect):
        if value is not None:
            return json.loads(value)
        return None


def utcnow():
    return datetime.now(timezone.utc)


class Session(Base):
    """Chat sessions — replaces all in-memory dicts."""
    __tablename__ = "sessions"

    id = Column(String, primary_key=True)
    created_at = Column(DateTime, default=utcnow, nullable=False)
    updated_at = Column(DateTime, default=utcnow, onupdate=utcnow, nullable=False)
    is_active = Column(Boolean, default=True)
    state = Column(JSONType, default=dict, nullable=False)
    ip_address = Column(String, nullable=True)
    user_agent = Column(String(256), nullable=True)


class Message(Base):
    """Every message (user + bot) — full conversation log."""
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True, autoincrement=True)
    session_id = Column(String, ForeignKey("sessions.id"), nullable=False, index=True)
    role = Column(String, nullable=False)  # 'user' or 'bot'
    content = Column(Text, nullable=False)
    buttons = Column(JSONType, nullable=True)
    callback = Column(String, nullable=True)
    created_at = Column(DateTime, default=utcnow, nullable=False)


class Escalation(Base):
    """Escalation tickets — replaces fire-and-forget emails."""
    __tablename__ = "escalations"

    id = Column(Integer, primary_key=True, autoincrement=True)
    session_id = Column(String, ForeignKey("sessions.id"), nullable=False)
    category = Column(String, nullable=False)
    issue = Column(String, nullable=False)
    portal = Column(String, nullable=True)
    assessment_type = Column(String, nullable=True)
    student_name = Column(String, nullable=False)
    student_email = Column(String, nullable=False)
    bfsi_id = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    email_sent = Column(Boolean, default=False)
    email_error = Column(Text, nullable=True)
    status = Column(String, default="pending")
    created_at = Column(DateTime, default=utcnow, nullable=False)
    resolved_at = Column(DateTime, nullable=True)

    __table_args__ = (
        Index("idx_escalations_status", "status"),
    )


class AnalyticsEvent(Base):
    """Event log for analytics."""
    __tablename__ = "analytics"

    id = Column(Integer, primary_key=True, autoincrement=True)
    event = Column(String, nullable=False)
    session_id = Column(String, ForeignKey("sessions.id"), nullable=True)
    category = Column(String, nullable=True)
    detail = Column(Text, nullable=True)
    created_at = Column(DateTime, default=utcnow, nullable=False)

    __table_args__ = (
        Index("idx_analytics_event", "event"),
        Index("idx_analytics_date", "created_at"),
    )
