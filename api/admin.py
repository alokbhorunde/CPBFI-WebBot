"""Admin API — stats and escalation management."""
import logging
from fastapi import APIRouter, Depends, Header, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from api.schemas import StatsResponse, EscalationOut
from db.database import get_db
from db import crud
from config import settings

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/admin", tags=["Admin"])


def verify_admin(x_admin_key: str = Header(None)):
    """Simple API key auth for admin endpoints."""
    if not x_admin_key or x_admin_key != settings.ADMIN_KEY:
        raise HTTPException(status_code=403, detail="Invalid admin key")


@router.get("/stats", response_model=StatsResponse)
async def get_stats(db: AsyncSession = Depends(get_db), _=Depends(verify_admin)):
    """Dashboard analytics."""
    stats = await crud.get_stats(db)
    return StatsResponse(**stats)


@router.get("/escalations", response_model=list[EscalationOut])
async def get_escalations(
    status: str = None,
    limit: int = 50,
    db: AsyncSession = Depends(get_db),
    _=Depends(verify_admin)
):
    """List escalation tickets."""
    escalations = await crud.get_escalations(db, status=status, limit=limit)
    return [
        EscalationOut(
            id=e.id,
            session_id=e.session_id,
            category=e.category,
            issue=e.issue,
            portal=e.portal,
            assessment_type=e.assessment_type,
            student_name=e.student_name,
            student_email=e.student_email,
            bfsi_id=e.bfsi_id,
            description=e.description,
            email_sent=e.email_sent,
            status=e.status,
            created_at=e.created_at.isoformat() if e.created_at else ""
        )
        for e in escalations
    ]
