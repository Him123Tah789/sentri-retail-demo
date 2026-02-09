# Tools Layer - Trusted Engines
# These are deterministic, secure, NOT LLM-based

from .risk_link import LinkScanner
from .risk_email import EmailScanner
from .risk_logs import LogsScanner
from .guardian_status import GuardianStatus

__all__ = [
    "LinkScanner",
    "EmailScanner",
    "LogsScanner",
    "GuardianStatus",
    "ToolsManager"
]


class ToolsManager:
    """
    Tools Manager - Unified interface for all risk tools
    
    Gateway calls this to execute scans.
    All tools are deterministic and rule-based (not LLM).
    """
    
    def __init__(self):
        self.link_scanner = LinkScanner()
        self.email_scanner = EmailScanner()
        self.logs_scanner = LogsScanner()
        self.guardian_status = GuardianStatus()
    
    async def scan_link(self, url: str) -> dict:
        """Scan a URL for threats"""
        return await self.link_scanner.scan(url)
    
    async def scan_email(self, content: str) -> dict:
        """Scan email for phishing"""
        return await self.email_scanner.scan(content)
    
    async def scan_logs(self, logs: str) -> dict:
        """Scan security logs for anomalies"""
        return await self.logs_scanner.scan(logs)
    
    async def get_guardian_status(self) -> dict:
        """Get Guardian system status"""
        return await self.guardian_status.get_status()
