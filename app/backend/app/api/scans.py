"""
Security scan endpoints
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from pydantic import BaseModel

from ..db.database import get_database
from ..db.models import User, ScanEvent
from ..core.security import get_current_user
from ..services.risk_engine import analyze_link, analyze_email, analyze_logs

router = APIRouter()


# Request models
class LinkScanRequest(BaseModel):
    url: str


class EmailScanRequest(BaseModel):
    subject: str
    body: str


class LogsScanRequest(BaseModel):
    source: str
    lines: List[str]


# Response models
class ScanResponse(BaseModel):
    kind: str
    risk_score: int
    risk_level: str
    verdict: str
    explanation: str
    recommended_actions: List[str]


class ScanEventResponse(BaseModel):
    id: int
    kind: str
    input_preview: str
    risk_score: int
    risk_level: str
    verdict: str
    explanation: Optional[str]
    created_at: str
    
    class Config:
        from_attributes = True


@router.post("/link", response_model=ScanResponse)
async def scan_link(
    request: LinkScanRequest,
    db: Session = Depends(get_database),
    current_user: User = Depends(get_current_user)
):
    """Scan a URL for security risks"""
    result = analyze_link(request.url)
    
    # Store scan event
    scan_event = ScanEvent(
        user_id=current_user.id,
        kind="link",
        input_preview=request.url[:200],
        risk_score=result.score,
        risk_level=result.level,
        verdict=result.verdict,
        explanation=result.explanation
    )
    db.add(scan_event)
    db.commit()
    
    return ScanResponse(
        kind="link",
        risk_score=result.score,
        risk_level=result.level,
        verdict=result.verdict,
        explanation=result.explanation,
        recommended_actions=result.recommended_actions
    )


@router.post("/email", response_model=ScanResponse)
async def scan_email(
    request: EmailScanRequest,
    db: Session = Depends(get_database),
    current_user: User = Depends(get_current_user)
):
    """Analyze email content for phishing/fraud"""
    result = analyze_email(request.subject, request.body)
    
    # Store scan event
    preview = f"Subject: {request.subject[:50]}"
    scan_event = ScanEvent(
        user_id=current_user.id,
        kind="email",
        input_preview=preview[:200],
        risk_score=result.score,
        risk_level=result.level,
        verdict=result.verdict,
        explanation=result.explanation
    )
    db.add(scan_event)
    db.commit()
    
    return ScanResponse(
        kind="email",
        risk_score=result.score,
        risk_level=result.level,
        verdict=result.verdict,
        explanation=result.explanation,
        recommended_actions=result.recommended_actions
    )


@router.post("/logs", response_model=ScanResponse)
async def scan_logs(
    request: LogsScanRequest,
    db: Session = Depends(get_database),
    current_user: User = Depends(get_current_user)
):
    """Analyze security logs for threats"""
    result = analyze_logs(request.source, request.lines)
    
    # Store scan event
    preview = f"Source: {request.source} | {len(request.lines)} lines"
    scan_event = ScanEvent(
        user_id=current_user.id,
        kind="logs",
        input_preview=preview[:200],
        risk_score=result.score,
        risk_level=result.level,
        verdict=result.verdict,
        explanation=result.explanation
    )
    db.add(scan_event)
    db.commit()
    
    return ScanResponse(
        kind="logs",
        risk_score=result.score,
        risk_level=result.level,
        verdict=result.verdict,
        explanation=result.explanation,
        recommended_actions=result.recommended_actions
    )


@router.get("/recent", response_model=List[ScanEventResponse])
async def get_recent_scans(
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_database),
    current_user: User = Depends(get_current_user)
):
    """Get recent scan events for current user"""
    scans = db.query(ScanEvent)\
        .filter(ScanEvent.user_id == current_user.id)\
        .order_by(ScanEvent.created_at.desc())\
        .limit(limit)\
        .all()
    
    return [
        ScanEventResponse(
            id=s.id,
            kind=s.kind,
            input_preview=s.input_preview,
            risk_score=s.risk_score,
            risk_level=s.risk_level,
            verdict=s.verdict,
            explanation=s.explanation,
            created_at=s.created_at.isoformat()
        )
        for s in scans
    ]
