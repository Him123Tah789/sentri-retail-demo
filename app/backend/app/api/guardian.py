"""
Guardian Engine endpoints
"""
from datetime import date
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional

from ..db.database import get_database
from ..db.models import GuardianSnapshot
from ..core.security import get_current_user

router = APIRouter()


class GuardianStatusResponse(BaseModel):
    protection_level: str
    badge_text: str


class GuardianSummaryResponse(BaseModel):
    date: str
    protection_level: str
    items_analyzed: int
    high_risk_blocked: int
    top_threat: Optional[str]
    summary_text: str


@router.get("/status", response_model=GuardianStatusResponse)
async def get_guardian_status(db: Session = Depends(get_database)):
    """Get current Guardian protection status"""
    # Get today's snapshot or latest
    today = date.today()
    snapshot = db.query(GuardianSnapshot)\
        .filter(GuardianSnapshot.date == today)\
        .first()
    
    if snapshot:
        protection_level = snapshot.protection_level
    else:
        # Default status if no snapshot
        protection_level = "ACTIVE"
    
    return GuardianStatusResponse(
        protection_level=protection_level,
        badge_text=f"Retail Protection: {protection_level}"
    )


@router.get("/summary/today", response_model=GuardianSummaryResponse)
async def get_today_summary(db: Session = Depends(get_database)):
    """Get today's Guardian security summary"""
    today = date.today()
    snapshot = db.query(GuardianSnapshot)\
        .filter(GuardianSnapshot.date == today)\
        .first()
    
    if snapshot:
        return GuardianSummaryResponse(
            date=snapshot.date.isoformat(),
            protection_level=snapshot.protection_level,
            items_analyzed=snapshot.items_analyzed,
            high_risk_blocked=snapshot.high_risk_blocked,
            top_threat=snapshot.top_threat,
            summary_text=snapshot.summary_text
        )
    
    # Return default summary if no data for today
    return GuardianSummaryResponse(
        date=today.isoformat(),
        protection_level="ACTIVE",
        items_analyzed=0,
        high_risk_blocked=0,
        top_threat=None,
        summary_text="No activity recorded today. Guardian is actively monitoring all retail systems."
    )
