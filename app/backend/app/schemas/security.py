from pydantic import BaseModel
from typing import Optional, Dict, Any, List

class Evidence(BaseModel):
    risk_score: float
    confidence: float
    top_signals: List[str]
    model_version: str
    latency_ms: int
    threat_correlation: Optional[str] = None  # HIGH, MEDIUM, LOW

class SecurityScanResult(BaseModel):
    risk_score: float
    risk_level: str
    verdict: str  # SAFE, SUSPICIOUS, MALICIOUS
    explanation: str
    signals: list[str]
    recommended_actions: list[str]
    evidence: Optional[Evidence] = None
    meta: Optional[Dict[str, Any]] = None
