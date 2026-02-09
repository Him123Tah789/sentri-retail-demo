"""
Risk Engine - Transparent scoring system for retail security
Explainable AI-style risk assessment
"""
import re
from typing import List, Dict, Tuple
from dataclasses import dataclass


@dataclass
class RiskResult:
    """Risk assessment result"""
    score: int  # 0-100
    level: str  # LOW, MEDIUM, HIGH
    verdict: str  # Short verdict
    explanation: str  # Detailed explanation
    recommended_actions: List[str]  # Action items


# Suspicious patterns for different scan types
LINK_PATTERNS = {
    "lookalike_domains": [
        r"amaz[o0]n", r"paypa[l1]", r"g[o0][o0]gle", r"micr[o0]s[o0]ft",
        r"app[l1]e", r"netf[l1]ix", r"faceb[o0][o0]k", r"[l1]inkedin"
    ],
    "suspicious_keywords": [
        r"login", r"verify", r"account", r"secure", r"update",
        r"confirm", r"suspend", r"unlock", r"password", r"credential"
    ],
    "suspicious_tlds": [
        r"\.xyz$", r"\.top$", r"\.work$", r"\.click$", r"\.loan$",
        r"\.racing$", r"\.win$", r"\.bid$", r"\.stream$"
    ],
    "suspicious_paths": [
        r"/login", r"/signin", r"/verify", r"/secure", r"/account",
        r"/bank", r"/payment", r"/invoice"
    ]
}

EMAIL_PATTERNS = {
    "urgency_words": [
        r"urgent", r"immediately", r"asap", r"right away", r"within 24",
        r"account will be", r"suspended", r"terminated", r"locked"
    ],
    "payment_keywords": [
        r"invoice", r"payment", r"wire transfer", r"bank account",
        r"credit card", r"billing", r"overdue", r"outstanding"
    ],
    "phishing_phrases": [
        r"click here", r"verify your", r"confirm your", r"update your",
        r"dear customer", r"dear user", r"act now"
    ],
    "suspicious_senders": [
        r"@.*-.*\.com$",  # hyphenated domains
        r"@.*\d{3,}.*\.com$",  # numbers in domain
        r"noreply@(?!amazon|google|microsoft|apple)"
    ]
}

LOG_PATTERNS = {
    "failed_auth": [
        r"failed login", r"authentication failed", r"invalid password",
        r"access denied", r"unauthorized", r"login attempt"
    ],
    "privilege_escalation": [
        r"admin token", r"root access", r"privilege", r"sudo",
        r"elevated", r"permission change"
    ],
    "anomaly_indicators": [
        r"new ip", r"unusual location", r"odd hour", r"brute force",
        r"multiple attempts", r"rate limit"
    ]
}


def analyze_link(url: str) -> RiskResult:
    """Analyze a URL for security risks"""
    score = 0
    findings = []
    actions = []
    
    url_lower = url.lower()
    
    # Check for lookalike domains
    for pattern in LINK_PATTERNS["lookalike_domains"]:
        if re.search(pattern, url_lower):
            score += 40
            findings.append("Lookalike domain detected (brand impersonation)")
            actions.append("Do not enter credentials")
            break
    
    # Check for suspicious keywords in URL
    keyword_count = 0
    for pattern in LINK_PATTERNS["suspicious_keywords"]:
        if re.search(pattern, url_lower):
            keyword_count += 1
    if keyword_count >= 2:
        score += 25
        findings.append(f"Multiple suspicious keywords in URL ({keyword_count} found)")
        actions.append("Verify via official website directly")
    elif keyword_count == 1:
        score += 10
        findings.append("Suspicious keyword in URL path")
    
    # Check for suspicious TLDs
    for pattern in LINK_PATTERNS["suspicious_tlds"]:
        if re.search(pattern, url_lower):
            score += 20
            findings.append("Suspicious top-level domain")
            actions.append("Avoid entering sensitive information")
            break
    
    # Check URL structure
    if url_lower.count('.') > 3:
        score += 15
        findings.append("Excessive subdomains (obfuscation technique)")
    
    if len(url) > 100:
        score += 10
        findings.append("Unusually long URL")
    
    # Check for suspicious paths
    for pattern in LINK_PATTERNS["suspicious_paths"]:
        if re.search(pattern, url_lower):
            score += 15
            findings.append("Suspicious URL path pattern")
            break
    
    # HTTP vs HTTPS
    if url_lower.startswith("http://"):
        score += 15
        findings.append("Insecure HTTP connection (no HTTPS)")
        actions.append("Never enter credentials on HTTP pages")
    
    # Determine level and verdict
    score = min(score, 100)
    level, verdict = _get_level_verdict(score, "link")
    
    if not actions:
        if score < 30:
            actions.append("Link appears safe to visit")
        else:
            actions.append("Verify vendor via official contact")
            actions.append("Report to IT security if suspicious")
    
    explanation = " | ".join(findings) if findings else "No significant risk indicators found"
    
    return RiskResult(
        score=score,
        level=level,
        verdict=verdict,
        explanation=explanation,
        recommended_actions=actions
    )


def analyze_email(subject: str, body: str) -> RiskResult:
    """Analyze email content for security risks"""
    score = 0
    findings = []
    actions = []
    
    combined = f"{subject} {body}".lower()
    
    # Check urgency language
    urgency_count = 0
    for pattern in EMAIL_PATTERNS["urgency_words"]:
        if re.search(pattern, combined):
            urgency_count += 1
    if urgency_count >= 2:
        score += 30
        findings.append(f"High urgency language ({urgency_count} indicators)")
        actions.append("Do not rush - verify independently")
    elif urgency_count == 1:
        score += 15
        findings.append("Urgency tactics detected")
    
    # Check payment/invoice keywords
    payment_count = 0
    for pattern in EMAIL_PATTERNS["payment_keywords"]:
        if re.search(pattern, combined):
            payment_count += 1
    if payment_count >= 2:
        score += 35
        findings.append(f"Payment/invoice fraud indicators ({payment_count} found)")
        actions.append("Verify invoice via known vendor phone number")
        actions.append("Do not click payment links")
    elif payment_count == 1:
        score += 15
        findings.append("Financial keywords present")
    
    # Check phishing phrases
    phishing_count = 0
    for pattern in EMAIL_PATTERNS["phishing_phrases"]:
        if re.search(pattern, combined):
            phishing_count += 1
    if phishing_count >= 2:
        score += 25
        findings.append("Classic phishing phrases detected")
        actions.append("Do not click any links")
    elif phishing_count == 1:
        score += 10
        findings.append("Potential phishing phrase")
    
    # Check for external links
    link_pattern = r'https?://[^\s<>"{}|\\^`\[\]]+'
    links = re.findall(link_pattern, body)
    if links:
        score += 10
        findings.append(f"Contains {len(links)} external link(s)")
        for link in links[:3]:  # Check first 3 links
            link_result = analyze_link(link)
            if link_result.level == "HIGH":
                score += 20
                findings.append(f"HIGH risk link embedded: {link[:50]}...")
                break
    
    # Check for attachment mentions
    if re.search(r"attachment|attached|enclosed|.pdf|.doc|.xls", combined):
        score += 10
        findings.append("References attachments")
        actions.append("Scan attachments before opening")
    
    # Determine level and verdict
    score = min(score, 100)
    level, verdict = _get_level_verdict(score, "email")
    
    if not actions:
        if score < 30:
            actions.append("Email appears legitimate")
        else:
            actions.append("Forward to IT security for review")
    
    explanation = " | ".join(findings) if findings else "No significant risk indicators found"
    
    return RiskResult(
        score=score,
        level=level,
        verdict=verdict,
        explanation=explanation,
        recommended_actions=actions
    )


def analyze_logs(source: str, lines: List[str]) -> RiskResult:
    """Analyze security logs for threats"""
    score = 0
    findings = []
    actions = []
    
    combined = " ".join(lines).lower()
    
    # Count failed authentication attempts
    failed_count = 0
    for pattern in LOG_PATTERNS["failed_auth"]:
        failed_count += len(re.findall(pattern, combined))
    
    if failed_count >= 5:
        score += 45
        findings.append(f"Multiple failed auth attempts ({failed_count} detected)")
        actions.append("Block source IP immediately")
        actions.append("Check for compromised accounts")
    elif failed_count >= 2:
        score += 25
        findings.append(f"Failed authentication attempts ({failed_count})")
        actions.append("Monitor for continued attempts")
    elif failed_count == 1:
        score += 10
        findings.append("Single failed authentication")
    
    # Check for privilege escalation
    priv_count = 0
    for pattern in LOG_PATTERNS["privilege_escalation"]:
        if re.search(pattern, combined):
            priv_count += 1
    if priv_count >= 2:
        score += 40
        findings.append("Privilege escalation indicators detected")
        actions.append("Review admin account activity")
        actions.append("Verify token creation was authorized")
    elif priv_count == 1:
        score += 20
        findings.append("Potential privilege-related activity")
    
    # Check for anomaly indicators
    anomaly_count = 0
    for pattern in LOG_PATTERNS["anomaly_indicators"]:
        if re.search(pattern, combined):
            anomaly_count += 1
    if anomaly_count >= 2:
        score += 30
        findings.append("Multiple anomaly indicators")
        actions.append("Investigate unusual access patterns")
    elif anomaly_count == 1:
        score += 15
        findings.append("Anomaly indicator present")
    
    # Check for brute force patterns
    if re.search(r"brute.?force|rate.?limit|too many attempts", combined):
        score += 35
        findings.append("Brute force attack pattern detected")
        actions.append("Implement IP-based rate limiting")
        actions.append("Enable account lockout policy")
    
    # Check source context
    if source and re.search(r"pos|terminal|register", source.lower()):
        score += 5
        findings.append(f"Activity from POS system: {source}")
        actions.append("Verify POS terminal physical security")
    
    # Determine level and verdict
    score = min(score, 100)
    level, verdict = _get_level_verdict(score, "logs")
    
    if not actions:
        if score < 30:
            actions.append("Log activity appears normal")
        else:
            actions.append("Escalate to security team")
    
    explanation = " | ".join(findings) if findings else "No significant anomalies detected"
    
    return RiskResult(
        score=score,
        level=level,
        verdict=verdict,
        explanation=explanation,
        recommended_actions=actions
    )


def _get_level_verdict(score: int, scan_type: str) -> Tuple[str, str]:
    """Determine risk level and verdict based on score"""
    if score >= 70:
        level = "HIGH"
        verdicts = {
            "link": "Phishing / Credential Harvesting",
            "email": "Invoice Fraud / Phishing Attack",
            "logs": "Active Security Incident"
        }
    elif score >= 40:
        level = "MEDIUM"
        verdicts = {
            "link": "Suspicious - Verify Before Proceeding",
            "email": "Potential Social Engineering",
            "logs": "Anomaly - Investigation Recommended"
        }
    else:
        level = "LOW"
        verdicts = {
            "link": "No Significant Risk Detected",
            "email": "Appears Legitimate",
            "logs": "Normal Activity"
        }
    
    return level, verdicts.get(scan_type, "Risk Assessment Complete")
