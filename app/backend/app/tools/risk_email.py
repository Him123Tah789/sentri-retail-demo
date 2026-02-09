"""
Email Scanner Tool
==================

Deterministic email phishing analysis.
NOT LLM-based - uses rules and patterns.

Capabilities:
- Phishing phrase detection
- Urgency language analysis
- Suspicious sender patterns
- Social engineering detection
"""

import re
import logging
from typing import List, Dict

logger = logging.getLogger(__name__)


class EmailScanner:
    """
    Email Scanner - Phishing Detection Tool
    
    This is a TRUSTED tool that uses deterministic rules.
    Gateway calls this for email analysis.
    """
    
    # Phishing phrases commonly used
    PHISHING_PHRASES = [
        # Urgency
        r'urgent\s*(action|response|attention)',
        r'immediate\s*(action|response)',
        r'act\s*now',
        r'limited\s*time',
        r'expires?\s*(today|soon|immediately)',
        r'your\s*account\s*will\s*be\s*(suspended|closed|locked)',
        
        # Authority impersonation
        r'security\s*department',
        r'technical\s*support',
        r'account\s*verification',
        r'verify\s*your\s*(account|identity|email)',
        
        # Fear/Threat
        r'unusual\s*(activity|login|access)',
        r'unauthorized\s*(access|login|activity)',
        r'suspicious\s*(activity|login)',
        r'your\s*account\s*has\s*been\s*compromised',
        
        # Action requests
        r'click\s*(here|the\s*link|below)',
        r'update\s*your\s*(information|password|details)',
        r'confirm\s*your\s*(identity|account)',
        r'reset\s*your\s*password',
        
        # Prize/Reward
        r'(won|winner|selected)\s*(prize|lottery|reward)',
        r'claim\s*your\s*(prize|reward|gift)',
        r'congratulations.*\$([\d,]+)',
        
        # Financial
        r'wire\s*transfer',
        r'bank\s*account\s*details',
        r'payment\s*failed',
        r'invoice\s*attached',
    ]
    
    # Suspicious sender patterns
    SUSPICIOUS_SENDER_PATTERNS = [
        r'noreply@.*\.(xyz|tk|ml|ga)',
        r'support@.*random',
        r'admin@(?!.*\.(com|org|edu|gov))',
        r'\d{5,}@',  # Many numbers in email
    ]
    
    # Social engineering keywords
    SOCIAL_ENGINEERING_KEYWORDS = [
        'dear valued customer',
        'dear user',
        'dear sir/madam',
        'dear account holder',
        'your recent transaction',
        'we have noticed',
        'we have detected',
        'as a security measure',
        'failure to comply',
        'within 24 hours',
        'within 48 hours',
    ]
    
    def __init__(self):
        """Initialize Email Scanner"""
        logger.info("📧 Email Scanner initialized")
    
    async def scan(self, content: str) -> dict:
        """
        Scan email content for phishing indicators
        
        Args:
            content: Email content (headers + body)
            
        Returns:
            Scan result dict with risk assessment
        """
        logger.info("🔍 Scanning email content...")
        
        content_lower = content.lower()
        signals = []
        risk_score = 0
        
        # Check 1: Phishing phrases
        for pattern in self.PHISHING_PHRASES:
            if re.search(pattern, content_lower, re.IGNORECASE):
                phrase = re.search(pattern, content_lower, re.IGNORECASE).group()
                signals.append(f"Phishing phrase: '{phrase}'")
                risk_score += 15
        
        # Check 2: Social engineering keywords
        for keyword in self.SOCIAL_ENGINEERING_KEYWORDS:
            if keyword in content_lower:
                signals.append(f"Social engineering: '{keyword}'")
                risk_score += 10
        
        # Check 3: Suspicious URLs in content
        urls = re.findall(r'https?://[^\s<>"{}|\\^`\[\]]+', content)
        for url in urls:
            if any(tld in url for tld in ['.xyz', '.tk', '.ml', '.ga', '.cf']):
                signals.append(f"Suspicious URL: {url[:50]}")
                risk_score += 20
        
        # Check 4: Urgency indicators
        urgency_patterns = [
            r'!\s*!+',  # Multiple exclamation marks
            r'(URGENT|IMPORTANT|CRITICAL|ALERT)',
            r'within\s*\d+\s*(hour|day)',
        ]
        for pattern in urgency_patterns:
            if re.search(pattern, content, re.IGNORECASE):
                signals.append("High urgency language detected")
                risk_score += 15
                break
        
        # Check 5: Mismatched sender (if headers present)
        from_match = re.search(r'from:\s*([^\n]+)', content_lower)
        if from_match:
            from_address = from_match.group(1)
            # Check for spoofed domains
            if any(brand in from_address for brand in ['paypal', 'amazon', 'google', 'microsoft']):
                if not any(domain in from_address for domain in ['paypal.com', 'amazon.com', 'google.com', 'microsoft.com']):
                    signals.append("Potentially spoofed sender domain")
                    risk_score += 30
        
        # Check 6: Attachment mentions (common in malware)
        attachment_patterns = [
            r'attached\s*(file|document|invoice)',
            r'see\s*attach',
            r'\.zip\b',
            r'\.exe\b',
            r'\.scr\b',
        ]
        for pattern in attachment_patterns:
            if re.search(pattern, content_lower):
                signals.append("Suspicious attachment reference")
                risk_score += 15
                break
        
        # Check 7: Request for sensitive info
        sensitive_patterns = [
            r'(password|ssn|social\s*security|credit\s*card)',
            r'(bank\s*account|routing\s*number)',
            r'(login\s*credentials|username\s*and\s*password)',
        ]
        for pattern in sensitive_patterns:
            if re.search(pattern, content_lower):
                signals.append("Request for sensitive information")
                risk_score += 25
                break
        
        # Check 8: Grammatical errors (common in phishing)
        grammar_patterns = [
            r'kindly\s+do\s+the\s+needful',
            r'please\s+to\s+verify',
            r'you\s+have\s+been\s+select',
        ]
        for pattern in grammar_patterns:
            if re.search(pattern, content_lower):
                signals.append("Grammatical errors typical of phishing")
                risk_score += 10
                break
        
        # Cap scores from duplicate patterns
        risk_score = min(100, risk_score)
        
        # Calculate risk level
        risk_level = self._calculate_risk_level(risk_score)
        verdict = self._generate_verdict(risk_level, len(signals))
        
        return {
            "type": "email",
            "risk_score": risk_score,
            "risk_level": risk_level,
            "verdict": verdict,
            "signals": signals[:10],  # Limit to top 10
            "indicators_found": len(signals),
            "recommended_action": self._get_recommended_action(risk_level)
        }
    
    def _calculate_risk_level(self, score: int) -> str:
        """Calculate risk level from score"""
        if score >= 60:
            return "CRITICAL"
        elif score >= 40:
            return "HIGH"
        elif score >= 20:
            return "MEDIUM"
        elif score > 0:
            return "LOW"
        return "SAFE"
    
    def _generate_verdict(self, risk_level: str, signal_count: int) -> str:
        """Generate human-readable verdict"""
        verdicts = {
            "CRITICAL": f"🚨 PHISHING DETECTED - {signal_count} red flags found",
            "HIGH": f"⚠️ LIKELY PHISHING - {signal_count} suspicious indicators",
            "MEDIUM": f"⚡ SUSPICIOUS - {signal_count} concerning elements",
            "LOW": f"⚠️ MINOR CONCERNS - {signal_count} small issues",
            "SAFE": "✅ APPEARS LEGITIMATE - No phishing indicators found"
        }
        return verdicts.get(risk_level, "Unable to assess")
    
    def _get_recommended_action(self, risk_level: str) -> str:
        """Get recommended action based on risk"""
        actions = {
            "CRITICAL": "Do NOT click any links. Report as phishing and delete.",
            "HIGH": "Do not interact. Verify sender through official channels.",
            "MEDIUM": "Exercise caution. Verify before clicking any links.",
            "LOW": "Probably safe but verify sender if unexpected.",
            "SAFE": "Email appears legitimate - no action needed."
        }
        return actions.get(risk_level, "Proceed with caution")
