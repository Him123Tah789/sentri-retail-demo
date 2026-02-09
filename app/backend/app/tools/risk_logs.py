"""
Logs Scanner Tool
=================

Deterministic security log analysis.
NOT LLM-based - uses rules and patterns.

Capabilities:
- Failed login detection
- Brute force pattern recognition
- Anomaly detection
- Threat indicator extraction
"""

import re
import logging
from datetime import datetime
from typing import List, Dict
from collections import Counter

logger = logging.getLogger(__name__)


class LogsScanner:
    """
    Logs Scanner - Security Log Analysis Tool
    
    This is a TRUSTED tool that uses deterministic rules.
    Gateway calls this for log analysis.
    """
    
    # Log patterns indicating security issues
    THREAT_PATTERNS = [
        # Authentication failures
        (r'(failed|invalid)\s*(login|auth|password|authentication)', 'auth_failure', 15),
        (r'(access\s*)?denied', 'access_denied', 10),
        (r'unauthorized\s*(access|attempt)', 'unauthorized', 20),
        
        # Attack patterns
        (r'sql\s*injection', 'sql_injection', 30),
        (r'xss|cross.site.script', 'xss_attack', 25),
        (r'(brute\s*force|multiple\s*failed)', 'brute_force', 25),
        (r'(ddos|dos\s*attack)', 'dos_attack', 30),
        
        # Malware indicators
        (r'(malware|virus|trojan|ransomware)', 'malware', 35),
        (r'(suspicious|malicious)\s*(file|activity|process)', 'suspicious_activity', 20),
        
        # Network threats
        (r'port\s*scan', 'port_scan', 20),
        (r'(intrusion|breach)\s*(detected|attempt)', 'intrusion', 30),
        
        # System issues
        (r'(critical|severe)\s*error', 'critical_error', 15),
        (r'(service|system)\s*(crash|failure)', 'system_failure', 15),
    ]
    
    # IP pattern for extraction
    IP_PATTERN = re.compile(r'\b(?:\d{1,3}\.){3}\d{1,3}\b')
    
    # Timestamp patterns
    TIMESTAMP_PATTERNS = [
        r'\d{4}[-/]\d{2}[-/]\d{2}[T\s]\d{2}:\d{2}:\d{2}',
        r'\d{2}[-/]\d{2}[-/]\d{4}\s\d{2}:\d{2}:\d{2}',
        r'\w{3}\s+\d{1,2}\s+\d{2}:\d{2}:\d{2}',
    ]
    
    def __init__(self):
        """Initialize Logs Scanner"""
        logger.info("📋 Logs Scanner initialized")
    
    async def scan(self, logs: str) -> dict:
        """
        Scan security logs for threats and anomalies
        
        Args:
            logs: Log content to analyze
            
        Returns:
            Scan result dict with threat assessment
        """
        logger.info("🔍 Scanning security logs...")
        
        lines = logs.strip().split('\n')
        total_lines = len(lines)
        
        signals = []
        risk_score = 0
        threat_types = Counter()
        ips_detected = []
        
        # Analyze each line
        for line in lines:
            line_lower = line.lower()
            
            # Check threat patterns
            for pattern, threat_type, score in self.THREAT_PATTERNS:
                if re.search(pattern, line_lower, re.IGNORECASE):
                    threat_types[threat_type] += 1
                    if threat_types[threat_type] == 1:  # Only add signal once per type
                        signals.append(f"{threat_type.replace('_', ' ').title()} detected")
                    risk_score += score
            
            # Extract IPs
            ips = self.IP_PATTERN.findall(line)
            ips_detected.extend(ips)
        
        # Analyze patterns
        ip_counts = Counter(ips_detected)
        
        # Check for brute force (many attempts from same IP)
        for ip, count in ip_counts.most_common(5):
            if count >= 5:
                signals.append(f"Multiple events from IP: {ip} ({count} occurrences)")
                risk_score += 20
        
        # Check for failed login patterns
        failed_logins = threat_types.get('auth_failure', 0)
        if failed_logins >= 5:
            signals.append(f"High failed login count: {failed_logins}")
            risk_score += 15
        if failed_logins >= 10:
            signals.append("Possible brute force attack detected")
            risk_score += 25
        
        # Cap the score
        risk_score = min(100, risk_score)
        
        # Calculate risk level
        risk_level = self._calculate_risk_level(risk_score)
        verdict = self._generate_verdict(risk_level, threat_types)
        
        # Get top suspicious IPs
        suspicious_ips = [ip for ip, count in ip_counts.most_common(5) if count >= 3]
        
        return {
            "type": "logs",
            "lines_analyzed": total_lines,
            "risk_score": risk_score,
            "risk_level": risk_level,
            "verdict": verdict,
            "signals": signals[:10],
            "threat_summary": dict(threat_types),
            "suspicious_ips": suspicious_ips,
            "recommended_action": self._get_recommended_action(risk_level, threat_types)
        }
    
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
    
    def _generate_verdict(self, risk_level: str, threats: Counter) -> str:
        """Generate human-readable verdict"""
        total_threats = sum(threats.values())
        
        if risk_level == "CRITICAL":
            return f"🚨 CRITICAL THREATS - {total_threats} security events requiring immediate attention"
        elif risk_level == "HIGH":
            return f"⚠️ HIGH RISK - {total_threats} concerning security events detected"
        elif risk_level == "MEDIUM":
            return f"⚡ MODERATE - {total_threats} events warrant investigation"
        elif risk_level == "LOW":
            return f"⚠️ LOW RISK - {total_threats} minor events detected"
        return "✅ CLEAN - No significant security events found"
    
    def _get_recommended_action(self, risk_level: str, threats: Counter) -> str:
        """Get recommended action based on threats found"""
        if 'intrusion' in threats or 'malware' in threats:
            return "IMMEDIATE: Isolate affected systems, initiate incident response."
        if 'brute_force' in threats or 'sql_injection' in threats:
            return "HIGH: Block suspicious IPs, review access controls, check for compromise."
        if 'auth_failure' in threats:
            return "Review failed login attempts, consider account lockout policies."
        if risk_level in ["CRITICAL", "HIGH"]:
            return "Investigate flagged events immediately, consider security team escalation."
        if risk_level == "MEDIUM":
            return "Monitor situation, investigate if pattern continues."
        return "Continue normal monitoring - no immediate action required."
