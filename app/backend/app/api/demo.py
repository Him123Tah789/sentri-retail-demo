"""
Demo seed endpoint - only available in HACKATHON mode
"""
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel

from ..core.config import settings
from ..db.database import get_database
from ..db.seed_demo import seed_demo_data

router = APIRouter()


class SeedResponse(BaseModel):
    success: bool
    message: str


@router.post("/seed", response_model=SeedResponse)
async def seed_demo(db: Session = Depends(get_database)):
    """
    Seed demo data - only works in HACKATHON mode
    """
    if not settings.is_hackathon_mode:
        raise HTTPException(
            status_code=403,
            detail="Demo seeding only available in HACKATHON mode"
        )
    
    try:
        seed_demo_data(db)
        return SeedResponse(
            success=True,
            message="Demo data seeded successfully"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to seed demo data: {str(e)}"
        )
