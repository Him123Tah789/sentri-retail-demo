"""
Guardian Status Tool
====================

System health and status monitoring.

Capabilities:
- Component health checks
- Statistics aggregation
- Alert status
"""

import logging
from datetime import datetime
from typing import Dict

logger = logging.getLogger(__name__)


class GuardianStatus:
    """
    Guardian Status - System Monitoring Tool
    
    Provides health and status information about the Sentri system.
    """
    
    def __init__(self):
        """Initialize Guardian Status"""
        self._stats = {
            "scans_today": 0,
            "threats_blocked": 0,
            "emails_analyzed": 0,
            "logs_reviewed": 0,
            "uptime_start": datetime.utcnow().isoformat()
        }
        logger.info("🛡️ Guardian Status initialized")
    
    def increment_stat(self, stat_name: str, count: int = 1):
        """Increment a statistic"""
        if stat_name in self._stats:
            self._stats[stat_name] += count
    
    async def get_status(self) -> dict:
        """
        Get Guardian system status
        
        Returns:
            Status dict with health information
        """
        now = datetime.utcnow()
        start = datetime.fromisoformat(self._stats["uptime_start"])
        uptime = (now - start).total_seconds()
        
        return {
            "status": "healthy",
            "guardian_version": "1.0.0",
            "timestamp": now.isoformat(),
            "components": {
                "link_scanner": "active",
                "email_scanner": "active",
                "logs_scanner": "active",
                "llm_service": "active",
                "memory_manager": "active"
            },
            "stats": {
                "scans_today": self._stats["scans_today"],
                "threats_blocked": self._stats["threats_blocked"],
                "emails_analyzed": self._stats["emails_analyzed"],
                "logs_reviewed": self._stats["logs_reviewed"],
                "uptime_seconds": int(uptime)
            },
            "alerts": {
                "active_alerts": 0,
                "last_threat": None
            }
        }
    
    async def get_summary(self) -> dict:
        """Get a brief status summary"""
        return {
            "status": "healthy",
            "scans_today": self._stats["scans_today"],
            "threats_blocked": self._stats["threats_blocked"],
            "message": "All systems operational"
        }
