"""
Link Scanner Tool
=================

Deterministic URL risk analysis.
NOT LLM-based - uses rules and patterns.

Capabilities:
- Domain reputation check
- URL pattern analysis
- Phishing indicator detection
- SSL/HTTPS verification
"""

import re
import logging
from urllib.parse import urlparse
from typing import List, Dict

logger = logging.getLogger(__name__)


class LinkScanner:
    """
    Link Scanner - URL Security Tool
    
    This is a TRUSTED tool that uses deterministic rules.
    Gateway calls this for URL analysis.
    """
    
    # Known malicious TLDs
    SUSPICIOUS_TLDS = ['.xyz', '.tk', '.ml', '.ga', '.cf', '.gq', '.top', '.buzz', '.club']
    
    # Phishing patterns in URLs
    PHISHING_PATTERNS = [
        r'(login|signin|verify|account|secure|update|confirm)\.',
        r'\.(com|net|org)-[a-z]+\.',
        r'(paypal|amazon|google|microsoft|apple|netflix|bank).*\.(xyz|tk|ml)',
        r'[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}',  # IP addresses
        r'(free|win|gift|prize|claim|urgent|limited)',
    ]
    
    # Known trusted domains
    TRUSTED_DOMAINS = [
        'google.com', 'microsoft.com', 'apple.com', 'amazon.com',
        'github.com', 'linkedin.com', 'facebook.com', 'twitter.com',
        'youtube.com', 'netflix.com', 'paypal.com', 'stripe.com'
    ]
    
    # Typosquatting patterns (brand impersonation)
    BRAND_TYPOS = {
        'google': ['g00gle', 'googel', 'gogle', 'googIe'],
        'paypal': ['paypai', 'paypa1', 'paypol', 'paypall'],
        'amazon': ['amaz0n', 'amazom', 'arnazon', 'amazonn'],
        'microsoft': ['micros0ft', 'mircosoft', 'microsft'],
        'apple': ['appIe', 'app1e', 'aple'],
    }
    
    def __init__(self):
        """Initialize Link Scanner"""
        logger.info("🔗 Link Scanner initialized")
    
    async def scan(self, url: str) -> dict:
        """
        Scan a URL for security threats
        
        Args:
            url: URL to scan
            
        Returns:
            Scan result dict with risk assessment
        """
        logger.info(f"🔍 Scanning URL: {url[:50]}...")
        
        # Normalize URL
        if not url.startswith(('http://', 'https://')):
            url = 'http://' + url
        
        signals = []
        risk_score = 0
        
        try:
            parsed = urlparse(url)
            domain = parsed.netloc.lower()
            path = parsed.path.lower()
            
            # Check 1: HTTPS
            if not url.startswith('https://'):
                signals.append("No HTTPS (unencrypted connection)")
                risk_score += 15
            
            # Check 2: Suspicious TLD
            for tld in self.SUSPICIOUS_TLDS:
                if domain.endswith(tld):
                    signals.append(f"Suspicious TLD: {tld}")
                    risk_score += 25
                    break
            
            # Check 3: Phishing patterns
            for pattern in self.PHISHING_PATTERNS:
                if re.search(pattern, url, re.IGNORECASE):
                    signals.append(f"Phishing pattern detected")
                    risk_score += 30
                    break
            
            # Check 4: Typosquatting
            typosquat = self._check_typosquatting(domain)
            if typosquat:
                signals.append(f"Possible typosquatting of: {typosquat}")
                risk_score += 40
            
            # Check 5: IP address as domain
            if re.match(r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}', domain):
                signals.append("IP address used as domain")
                risk_score += 35
            
            # Check 6: Suspicious keywords in path
            suspicious_path_keywords = ['login', 'verify', 'secure', 'account', 'update', 'confirm', 'password']
            for keyword in suspicious_path_keywords:
                if keyword in path:
                    signals.append(f"Suspicious keyword in path: {keyword}")
                    risk_score += 10
                    break
            
            # Check 7: Excessive subdomains
            subdomain_count = domain.count('.') - 1
            if subdomain_count > 2:
                signals.append(f"Excessive subdomains ({subdomain_count})")
                risk_score += 15
            
            # Check 8: Trusted domain (reduces risk)
            for trusted in self.TRUSTED_DOMAINS:
                if domain == trusted or domain.endswith('.' + trusted):
                    signals.append(f"Trusted domain: {trusted}")
                    risk_score = max(0, risk_score - 30)
                    break
            
        except Exception as e:
            logger.error(f"URL parsing error: {e}")
            signals.append("URL parsing error")
            risk_score += 20
        
        # Calculate risk level
        risk_level = self._calculate_risk_level(risk_score)
        verdict = self._generate_verdict(risk_level, signals)
        
        return {
            "url": url,
            "risk_score": min(100, risk_score),
            "risk_level": risk_level,
            "verdict": verdict,
            "signals": signals,
            "recommended_action": self._get_recommended_action(risk_level)
        }
    
    def _check_typosquatting(self, domain: str) -> str:
        """Check for typosquatting of known brands"""
        for brand, typos in self.BRAND_TYPOS.items():
            for typo in typos:
                if typo in domain:
                    return brand
        return None
    
    def _calculate_risk_level(self, score: int) -> str:
        """Calculate risk level from score"""
        if score >= 70:
            return "CRITICAL"
        elif score >= 50:
            return "HIGH"
        elif score >= 30:
            return "MEDIUM"
        elif score > 0:
            return "LOW"
        return "SAFE"
    
    def _generate_verdict(self, risk_level: str, signals: List[str]) -> str:
        """Generate human-readable verdict"""
        verdicts = {
            "CRITICAL": "🚨 DANGEROUS - Do NOT visit this URL",
            "HIGH": "⚠️ SUSPICIOUS - High risk of phishing/malware",
            "MEDIUM": "⚡ CAUTION - Some concerning indicators detected",
            "LOW": "⚠️ MINOR CONCERNS - Proceed with caution",
            "SAFE": "✅ APPEARS SAFE - No major threats detected"
        }
        return verdicts.get(risk_level, "Unable to assess")
    
    def _get_recommended_action(self, risk_level: str) -> str:
        """Get recommended action based on risk"""
        actions = {
            "CRITICAL": "Do NOT click or visit. Report as phishing.",
            "HIGH": "Avoid visiting. Verify through official channels.",
            "MEDIUM": "Exercise caution. Verify the sender if received via message.",
            "LOW": "Safe to visit but stay alert for suspicious activity.",
            "SAFE": "No action needed - URL appears legitimate."
        }
        return actions.get(risk_level, "Proceed with caution")
