"""
Intent Router
=============

Detects user intent from messages and routes to appropriate handler.

Supported Intents:
- SCAN_LINK: URL/link security scan
- SCAN_EMAIL: Email phishing analysis
- SCAN_LOGS: Security log analysis
- GUARDIAN_STATUS: System status check
- SECURITY_QUESTION: Security-related question
- GENERAL_CHAT: General conversation
- HELP: Help request
- GREETING: Hello/hi messages
"""

import re
import logging
from enum import Enum
from dataclasses import dataclass
from typing import Tuple, List, Optional

logger = logging.getLogger(__name__)


class Intent(Enum):
    """All supported user intents"""
    SCAN_LINK = "scan_link"
    SCAN_EMAIL = "scan_email"
    SCAN_LOGS = "scan_logs"
    GUARDIAN_STATUS = "guardian_status"
    SECURITY_QUESTION = "security_question"
    GENERAL_CHAT = "general_chat"
    HELP = "help"
    GREETING = "greeting"
    UNKNOWN = "unknown"


@dataclass
class IntentResult:
    """Result of intent detection"""
    intent: Intent
    confidence: float
    extracted_data: dict = None
    
    def __post_init__(self):
        if self.extracted_data is None:
            self.extracted_data = {}


class IntentRouter:
    """
    Intent Router - Determines what the user wants
    
    Uses pattern matching and keyword detection to classify intents.
    Future: Can be enhanced with ML-based classification.
    """
    
    # URL pattern for link detection
    URL_PATTERN = re.compile(
        r'https?://[^\s<>"{}|\\^`\[\]]+|'
        r'www\.[^\s<>"{}|\\^`\[\]]+|'
        r'[a-zA-Z0-9][-a-zA-Z0-9]*\.[a-zA-Z]{2,}(?:/[^\s]*)?'
    )
    
    # Intent patterns with keywords
    INTENT_PATTERNS = {
        Intent.SCAN_LINK: [
            r'\bscan\b.*\b(link|url|website|site)\b',
            r'\bcheck\b.*\b(link|url|website|site)\b',
            r'\bis\b.*\b(safe|secure|legit|legitimate)\b',
            r'\bverify\b.*\b(link|url)\b',
        ],
        Intent.SCAN_EMAIL: [
            r'\bscan\b.*\bemail\b',
            r'\bcheck\b.*\bemail\b',
            r'\bphishing\b.*\bemail\b',
            r'\banalyze\b.*\bemail\b',
            r'\bsuspicious\b.*\bemail\b',
            r'\bemail\b.*\bscan\b',
        ],
        Intent.SCAN_LOGS: [
            r'\bscan\b.*\blogs?\b',
            r'\bcheck\b.*\blogs?\b',
            r'\banalyze\b.*\blogs?\b',
            r'\breview\b.*\blogs?\b',
            r'\blogs?\b.*\bscan\b',
        ],
        Intent.GUARDIAN_STATUS: [
            r'\bstatus\b',
            r'\bguardian\b',
            r'\bsystem\b.*\bstatus\b',
            r'\bhow\b.*\bsentri\b',
            r'\bhealth\b.*\bcheck\b',
        ],
        Intent.HELP: [
            r'\bhelp\b',
            r'\bwhat can you\b',
            r'\bwhat do you\b',
            r'\bhow to\b',
            r'\bcommands\b',
            r'\bfeatures\b',
        ],
        Intent.GREETING: [
            r'^(hi|hello|hey|greetings|good morning|good afternoon|good evening)[\s!?.]*$',
            r'^(hi|hello|hey)\s+(there|sentri|bot)[\s!?.]*$',
        ],
        Intent.SECURITY_QUESTION: [
            r'\bwhat\s+is\b.*\b(phishing|malware|ransomware|virus|trojan|security)\b',
            r'\bhow\s+(to|do)\b.*\b(protect|secure|prevent|avoid)\b',
            r'\bexplain\b.*\b(security|attack|threat)\b',
            r'\btips?\b.*\b(security|safety|protection)\b',
            r'\b(password|auth|authentication|2fa|mfa)\b',
            r'\b(cyber|security|threat|attack|vulnerability)\b',
        ],
    }
    
    # Keywords for quick detection (after pattern matching)
    SECURITY_KEYWORDS = [
        'phishing', 'malware', 'ransomware', 'virus', 'trojan', 'hack',
        'security', 'threat', 'attack', 'vulnerability', 'breach',
        'password', 'authentication', '2fa', 'mfa', 'firewall',
        'encryption', 'ssl', 'https', 'certificate', 'scam', 'fraud'
    ]
    
    def __init__(self):
        """Initialize the Intent Router"""
        logger.info("🧭 Intent Router initialized")
    
    def detect_intent(self, message: str) -> IntentResult:
        """
        Detect intent from user message
        
        Args:
            message: User message text
            
        Returns:
            IntentResult with detected intent and confidence
        """
        message_lower = message.lower().strip()
        
        # Check for URLs first - highest priority
        urls = self.extract_urls(message)
        if urls:
            return IntentResult(
                intent=Intent.SCAN_LINK,
                confidence=0.95,
                extracted_data={"urls": urls}
            )
        
        # Check email-like content (headers, from/to)
        if self._looks_like_email(message):
            return IntentResult(
                intent=Intent.SCAN_EMAIL,
                confidence=0.90,
                extracted_data={"email_content": message}
            )
        
        # Check log-like content
        if self._looks_like_logs(message):
            return IntentResult(
                intent=Intent.SCAN_LOGS,
                confidence=0.85,
                extracted_data={"log_content": message}
            )
        
        # Pattern-based detection
        for intent, patterns in self.INTENT_PATTERNS.items():
            for pattern in patterns:
                if re.search(pattern, message_lower, re.IGNORECASE):
                    return IntentResult(
                        intent=intent,
                        confidence=0.85,
                        extracted_data=self._extract_relevant_data(message, intent)
                    )
        
        # Keyword-based fallback for security questions
        for keyword in self.SECURITY_KEYWORDS:
            if re.search(rf'\b{re.escape(keyword)}\b', message_lower):
                return IntentResult(
                    intent=Intent.SECURITY_QUESTION,
                    confidence=0.70,
                    extracted_data={"keyword": keyword}
                )
        
        # Default to general chat
        return IntentResult(
            intent=Intent.GENERAL_CHAT,
            confidence=0.50,
            extracted_data={}
        )
    
    def extract_urls(self, message: str) -> List[str]:
        """
        Extract URLs from message
        
        Args:
            message: Message text
            
        Returns:
            List of extracted URLs
        """
        urls = self.URL_PATTERN.findall(message)
        # Filter out common false positives
        filtered = []
        for url in urls:
            # Skip version numbers like "2.0" or "3.11"
            if re.match(r'^\d+\.\d+$', url):
                continue
            # Skip file extensions
            if url.startswith('.') and len(url) < 6:
                continue
            filtered.append(url)
        return filtered
    
    def _looks_like_email(self, message: str) -> bool:
        """Check if message looks like email content"""
        email_indicators = [
            r'\bfrom:\s*\S+@\S+',
            r'\bto:\s*\S+@\S+',
            r'\bsubject:\s*.+',
            r'\bcc:\s*\S+@\S+',
            r'\bsent:\s*.+\d{4}',
            r'dear\s+(user|customer|sir|madam|valued)',
            r'click\s+(here|the\s+link|below)',
            r'verify\s+your\s+(account|email|identity)',
            r'urgent\s+(action|response|attention)',
        ]
        
        message_lower = message.lower()
        match_count = sum(1 for indicator in email_indicators 
                        if re.search(indicator, message_lower))
        
        return match_count >= 2
    
    def _looks_like_logs(self, message: str) -> bool:
        """Check if message looks like security logs"""
        log_indicators = [
            r'\d{4}[-/]\d{2}[-/]\d{2}',  # Date
            r'\d{2}:\d{2}:\d{2}',  # Time
            r'\b(ERROR|WARN|INFO|DEBUG|CRITICAL)\b',
            r'\b(IP|address):\s*\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}',
            r'\b(failed|denied|blocked|rejected)\b',
            r'\b(login|auth|access)\s+(attempt|failure)',
        ]
        
        match_count = sum(1 for indicator in log_indicators 
                        if re.search(indicator, message, re.IGNORECASE))
        
        return match_count >= 2
    
    def _extract_relevant_data(self, message: str, intent: Intent) -> dict:
        """Extract relevant data based on intent"""
        data = {}
        
        if intent == Intent.SCAN_LINK:
            data["urls"] = self.extract_urls(message)
        elif intent == Intent.SCAN_EMAIL:
            data["email_content"] = message
        elif intent == Intent.SCAN_LOGS:
            data["log_content"] = message
        elif intent == Intent.SECURITY_QUESTION:
            # Extract the main topic
            for keyword in self.SECURITY_KEYWORDS:
                if keyword in message.lower():
                    data["topic"] = keyword
                    break
        
        return data
    
    def get_intent_description(self, intent: Intent) -> str:
        """Get human-readable description of intent"""
        descriptions = {
            Intent.SCAN_LINK: "Scanning URL for security threats",
            Intent.SCAN_EMAIL: "Analyzing email for phishing indicators",
            Intent.SCAN_LOGS: "Reviewing security logs for anomalies",
            Intent.GUARDIAN_STATUS: "Checking Guardian system status",
            Intent.SECURITY_QUESTION: "Answering security question",
            Intent.GENERAL_CHAT: "General conversation",
            Intent.HELP: "Providing help information",
            Intent.GREETING: "Responding to greeting",
            Intent.UNKNOWN: "Processing unknown request",
        }
        return descriptions.get(intent, "Processing request")
