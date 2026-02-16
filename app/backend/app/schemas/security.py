from pydantic import BaseModel
from typing import Optional, Dict, Any

class SecurityScanResult(BaseModel):
    risk_score: int
    risk_level: str
    verdict: str
    explanation: str
    signals: list[str]
    recommended_actions: list[str]
    meta: Optional[Dict[str, Any]] = None
