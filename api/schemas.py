"""Pydantic request/response models for the chat API."""
from typing import Optional
from datetime import datetime
from pydantic import BaseModel, ConfigDict


class ButtonSchema(BaseModel):
    text: str
    cb: str


class MessageResponse(BaseModel):
    text: str
    buttons: list[ButtonSchema] = []


class StartResponse(BaseModel):
    session_id: str
    message: MessageResponse


class ChatRequest(BaseModel):
    session_id: str
    message: Optional[str] = None
    callback_data: Optional[str] = None


class ChatResponse(BaseModel):
    text: str
    buttons: list[ButtonSchema] = []


class EscalationOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    session_id: str
    category: str
    issue: str
    portal: Optional[str] = None
    assessment_type: Optional[str] = None
    student_name: str
    student_email: str
    bfsi_id: str
    description: Optional[str] = None
    email_sent: bool = False
    status: str = "pending"
    created_at: datetime


class StatsResponse(BaseModel):
    total_sessions: int
    today_sessions: int
    total_messages: int
    total_escalations: int
    pending_escalations: int
    events_this_week: int
