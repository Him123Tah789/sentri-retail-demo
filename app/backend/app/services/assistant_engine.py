"""
Assistant Engine - HYBRID CHAT + TOOLS for retail security
Combines general AI chat with security scan actions.

Architecture:
- Intent Router: Detects if user wants chat vs. security action
- Rules Engine (risk_engine.py): Calculates risk scores for scans
- LLM Service (llm_service.py): Powers conversations and explanations
- This module: Orchestrates everything
"""
import re
from typing import Optional, Dict, Tuple, List
from dataclasses import dataclass, asdict, field
from enum import Enum
from .risk_engine import analyze_link, analyze_email, analyze_logs, RiskResult
from .llm_service import llm_service


class ToolUsed(str, Enum):
    """Tools that Sentri can use"""
    SCAN_LINK = "scan_link"
    SCAN_EMAIL = "scan_email"
    SCAN_LOGS = "scan_logs"
    NONE = "none"


@dataclass
class RiskSummary:
    """Brief risk summary when a scan is performed"""
    level: str  # HIGH, MEDIUM, LOW
    score: int  # 0-100
    verdict: str  # Short verdict
    action_required: bool  # Whether user needs to take action


@dataclass
class AssistantResponse:
    """Complete assistant response with scan results and explanation"""
    reply: str  # The chat message to show
    tool_used: str = "none"  # Which tool was used
    risk_summary: Optional[Dict] = None  # Brief risk info
    scan_result: Optional[Dict] = None  # Full scan data
    scan_type: Optional[str] = None  # Legacy: 'link', 'email', 'logs', or None


async def generate_response_async(
    message: str, 
    context: Optional[Dict] = None,
    conversation_history: Optional[list] = None,
    memory_summary: str = "",
    topics_covered: str = ""
) -> AssistantResponse:
    """
    Generate AI assistant response - HYBRID CHAT + TOOLS.
    
    Flow:
    1. Detect intent (chat vs security action)
    2. If security content detected → run scan → explain results
    3. If general chat → answer naturally with LLM
    
    Memory Layers:
    - memory_summary: Rolling summary of conversation
    - topics_covered: Topics already discussed (anti-repetition)
    - conversation_history: Last 6-8 messages
    """
    message_lower = message.lower()
    history = conversation_history or []
    
    # --- TOOL DETECTION LAYER ---
    
    # Priority 1: Check for URL (highest priority - always scan if URL present)
    url_pattern = r'https?://[^\s<>"{}|\\^`\[\]]+'
    urls = re.findall(url_pattern, message)
    if urls:
        url = urls[0]
        result = analyze_link(url)
        return await _handle_link_scan(url, result, history)
    
    # Priority 2: Check for log content (explicit log patterns)
    if _contains_log_content(message):
        lines = _extract_log_lines(message)
        if len(lines) >= 2:  # At least 2 lines to be considered logs
            result = analyze_logs("User Submitted", lines)
            return await _handle_log_scan(lines, result, history)
    
    # Priority 3: Check for email content
    if _contains_email_content(message):
        subject, body = _extract_email_parts(message)
        if subject or (body and len(body) > 30):  # Has subject or substantial body
            result = analyze_email(subject, body)
            return await _handle_email_scan(subject, body, result, history)
    
    # Priority 4: Check for scan request without content
    if _wants_to_scan(message_lower):
        return AssistantResponse(
            reply=_get_scan_prompt(message_lower),
            tool_used=ToolUsed.NONE.value
        )
    
    # --- GENERAL CHAT LAYER ---
    # No scannable content - use LLM for natural conversation
    
    llm_response = await llm_service.chat_with_memory(
        message=message, 
        history=history,
        summary=memory_summary,
        topics_covered=topics_covered
    )
    
    return AssistantResponse(
        reply=llm_response,
        tool_used=ToolUsed.NONE.value
    )


def _wants_to_scan(message: str) -> bool:
    """Check if user is asking to scan something but hasn't provided content"""
    scan_keywords = ['scan', 'check', 'analyze', 'verify', 'is.*safe', 'review']
    target_keywords = ['link', 'url', 'email', 'message', 'logs', 'website']
    
    has_scan_intent = any(re.search(kw, message) for kw in scan_keywords)
    has_target = any(word in message for word in target_keywords)
    
    # User wants to scan but hasn't provided the content
    has_content = 'http' in message or len(message) > 200  # URLs or substantial content
    
    return has_scan_intent and has_target and not has_content


def _get_scan_prompt(message: str) -> str:
    """Return appropriate prompt based on what user wants to scan"""
    if 'link' in message or 'url' in message or 'website' in message:
        return "I can scan that link for you. Just paste the URL and I'll analyze it for security risks."
    elif 'email' in message or 'message' in message:
        return "I can analyze that email for phishing indicators. Please paste the email content (subject and body) and I'll check it."
    elif 'log' in message:
        return "I can review those logs for security events. Paste the log entries and I'll summarize any concerns."
    else:
        return "I can scan links, emails, or logs for security threats. What would you like me to analyze?"


def generate_response(message: str, context: Optional[Dict] = None) -> str:
    """
    Synchronous wrapper for backward compatibility.
    Returns just the reply text (no structured data).
    """
    import asyncio
    try:
        loop = asyncio.get_event_loop()
        if loop.is_running():
            # If already in async context, use nest_asyncio or return sync fallback
            return _generate_response_sync(message, context)
        result = loop.run_until_complete(generate_response_async(message, context))
        return result.reply
    except RuntimeError:
        # No event loop, create one
        result = asyncio.run(generate_response_async(message, context))
        return result.reply


def _generate_response_sync(message: str, context: Optional[Dict] = None) -> str:
    """Synchronous fallback when async isn't available"""
    message_lower = message.lower()
    
    # Check for URL
    url_pattern = r'https?://[^\s<>"{}|\\^`\[\]]+'
    urls = re.findall(url_pattern, message)
    if urls:
        url = urls[0]
        result = analyze_link(url)
        return _format_link_analysis_sync(url, result)
    
    # Check for email content
    if _contains_email_content(message):
        subject, body = _extract_email_parts(message)
        result = analyze_email(subject, body)
        return _format_email_analysis_sync(result)
    
    # Topic responses
    return _get_topic_response(message_lower)


async def _handle_link_scan(url: str, result: RiskResult, history: list = None) -> AssistantResponse:
    """Handle link scan with LLM explanation"""
    
    # Get LLM explanation with conversation context
    explanation = await llm_service.explain_scan_result(
        scan_type="Link/URL",
        input_preview=url[:100],
        risk_score=result.score,
        risk_level=result.level,
        verdict=result.verdict,
        signals=result.explanation,
        recommended_actions=" | ".join(result.recommended_actions),
        history=history
    )
    
    # Build the reply
    emoji = "🔴" if result.level == "HIGH" else "🟡" if result.level == "MEDIUM" else "🟢"
    
    reply = f"""{emoji} **Link Scan Complete**

**URL:** `{url[:60]}{'...' if len(url) > 60 else ''}`
**Risk Level:** {result.level} ({result.score}/100)
**Verdict:** {result.verdict}

---

{explanation}"""
    
    # Structured scan data
    scan_data = {
        "kind": "link",
        "input_preview": url[:100],
        "risk_score": result.score,
        "risk_level": result.level,
        "verdict": result.verdict,
        "explanation": result.explanation,
        "recommended_actions": result.recommended_actions
    }
    
    # Risk summary for quick display
    risk_summary = {
        "level": result.level,
        "score": result.score,
        "verdict": result.verdict,
        "action_required": result.level in ["HIGH", "MEDIUM"]
    }
    
    return AssistantResponse(
        reply=reply,
        tool_used=ToolUsed.SCAN_LINK.value,
        risk_summary=risk_summary,
        scan_result=scan_data,
        scan_type="link"
    )


async def _handle_email_scan(subject: str, body: str, result: RiskResult, history: list = None) -> AssistantResponse:
    """Handle email scan with LLM explanation"""
    
    preview = f"Subject: {subject[:50]}" if subject else body[:50]
    
    # Get LLM explanation with conversation context
    explanation = await llm_service.explain_scan_result(
        scan_type="Email",
        input_preview=preview,
        risk_score=result.score,
        risk_level=result.level,
        verdict=result.verdict,
        signals=result.explanation,
        recommended_actions=" | ".join(result.recommended_actions),
        history=history
    )
    
    emoji = "🔴" if result.level == "HIGH" else "🟡" if result.level == "MEDIUM" else "🟢"
    
    reply = f"""{emoji} **Email Analysis Complete**

**Subject:** {subject[:60] if subject else '(Not provided)'}
**Risk Level:** {result.level} ({result.score}/100)
**Verdict:** {result.verdict}

---

{explanation}"""
    
    # Risk summary for quick display
    risk_summary = {
        "level": result.level,
        "score": result.score,
        "verdict": result.verdict,
        "action_required": result.level in ["HIGH", "MEDIUM"]
    }
    
    scan_data = {
        "kind": "email",
        "input_preview": preview,
        "risk_score": result.score,
        "risk_level": result.level,
        "verdict": result.verdict,
        "explanation": result.explanation,
        "recommended_actions": result.recommended_actions
    }
    
    return AssistantResponse(
        reply=reply,
        tool_used=ToolUsed.SCAN_EMAIL.value,
        risk_summary=risk_summary,
        scan_result=scan_data,
        scan_type="email"
    )


async def _handle_log_scan(lines: list, result: RiskResult, history: list = None) -> AssistantResponse:
    """Handle log scan with LLM summary"""
    
    # Get LLM summary
    summary = await llm_service.summarize_logs(
        source="Security Logs",
        log_entries=lines[:20]  # Limit entries
    )
    
    emoji = "🔴" if result.level == "HIGH" else "🟡" if result.level == "MEDIUM" else "🟢"
    
    reply = f"""{emoji} **Log Analysis Complete**

**Entries Analyzed:** {len(lines)}
**Risk Level:** {result.level} ({result.score}/100)
**Verdict:** {result.verdict}

---

{summary}"""
    
    # Risk summary for quick display
    risk_summary = {
        "level": result.level,
        "score": result.score,
        "verdict": result.verdict,
        "action_required": result.level in ["HIGH", "MEDIUM"]
    }
    
    scan_data = {
        "kind": "logs",
        "input_preview": f"{len(lines)} log entries",
        "risk_score": result.score,
        "risk_level": result.level,
        "verdict": result.verdict,
        "explanation": result.explanation,
        "recommended_actions": result.recommended_actions
    }
    
    return AssistantResponse(
        reply=reply,
        tool_used=ToolUsed.SCAN_LOGS.value,
        risk_summary=risk_summary,
        scan_result=scan_data,
        scan_type="logs"
    )


def _contains_email_content(message: str) -> bool:
    """Check if message contains email content to analyze"""
    message_lower = message.lower()
    indicators = [
        "subject:" in message_lower,
        "from:" in message_lower,
        "dear customer" in message_lower,
        "dear user" in message_lower,
        "click here" in message_lower and len(message) > 100,
        message_lower.count('\n') >= 3 and any(kw in message_lower for kw in ["urgent", "invoice", "payment", "verify"])
    ]
    return any(indicators)


def _extract_email_parts(message: str) -> Tuple[str, str]:
    """Extract subject and body from email content"""
    subject = ""
    body = message
    
    lines = message.split('\n')
    for i, line in enumerate(lines):
        line_lower = line.lower()
        if line_lower.startswith("subject:"):
            subject = line[8:].strip()
        elif line_lower.startswith("from:"):
            continue  # Skip from line
        else:
            # Rest is body
            body = '\n'.join(lines[i:])
            break
    
    if not subject:
        # No subject found, use first line
        subject = lines[0][:50] if lines else ""
        body = message
    
    return subject, body


def _contains_log_content(message: str) -> bool:
    """Check if message contains log-like content"""
    log_indicators = [
        r"\d{4}-\d{2}-\d{2}",  # Date format
        r"\d{2}:\d{2}:\d{2}",  # Time format
        r"\[ERROR\]|\[WARN\]|\[INFO\]",  # Log levels
        r"failed|denied|error|unauthorized",  # Common log keywords
    ]
    
    # Must have multiple lines and match log patterns
    if message.count('\n') < 2:
        return False
    
    match_count = sum(1 for pattern in log_indicators if re.search(pattern, message, re.IGNORECASE))
    return match_count >= 2


def _extract_log_lines(message: str) -> list:
    """Extract log lines from message"""
    lines = [line.strip() for line in message.split('\n') if line.strip()]
    return lines


def _get_topic_response(message_lower: str) -> str:
    """Get topic-specific response for common questions"""
    
    if any(kw in message_lower for kw in ["phishing", "suspicious link", "fake"]):
        return _get_phishing_guidance()
    
    if any(kw in message_lower for kw in ["invoice", "payment", "vendor"]):
        return _get_invoice_fraud_guidance()
    
    if any(kw in message_lower for kw in ["password", "login", "credential"]):
        return _get_credential_guidance()
    
    if any(kw in message_lower for kw in ["pos", "terminal", "register"]):
        return _get_pos_security_guidance()
    
    if any(kw in message_lower for kw in ["report", "incident", "breach"]):
        return _get_incident_reporting_guidance()
    
    if any(kw in message_lower for kw in ["help", "what can you", "how do"]):
        return _get_help_response()
    
    return _get_default_response()


def _format_link_analysis_sync(url: str, result: RiskResult) -> str:
    """Format link analysis result as chat response (sync fallback)"""
    emoji = "🔴" if result.level == "HIGH" else "🟡" if result.level == "MEDIUM" else "🟢"
    
    response = f"""{emoji} **Link Analysis Complete**

**URL:** `{url[:60]}{'...' if len(url) > 60 else ''}`

**Risk Level:** {result.level}
**Risk Score:** {result.score}/100
**Verdict:** {result.verdict}

**Analysis:**
{result.explanation}

**Recommended Actions:**
"""
    for action in result.recommended_actions:
        response += f"• {action}\n"
    
    return response


def _format_email_analysis_sync(result: RiskResult) -> str:
    """Format email analysis result as chat response (sync fallback)"""
    emoji = "🔴" if result.level == "HIGH" else "🟡" if result.level == "MEDIUM" else "🟢"
    
    response = f"""{emoji} **Email Analysis Complete**

**Risk Level:** {result.level}
**Risk Score:** {result.score}/100
**Verdict:** {result.verdict}

**Analysis:**
{result.explanation}

**Recommended Actions:**
"""
    for action in result.recommended_actions:
        response += f"• {action}\n"
    
    return response


def _get_email_analysis_prompt() -> str:
    return """I can analyze email content for phishing and fraud indicators.

**To analyze an email, please provide:**
1. The subject line
2. The sender address
3. The email body content

Or simply paste the full email text and I'll identify:
• Urgency tactics
• Payment/invoice fraud indicators
• Suspicious links
• Social engineering patterns

**Example format:**
```
Subject: URGENT: Invoice Payment Required
From: accounts@vendor-portal.com
Body: Dear Customer, please pay immediately...
```"""


def _get_phishing_guidance() -> str:
    return """**🎣 Phishing Detection Guide for Retail**

**Red Flags to Watch:**
1. **Lookalike domains** - amaz0n, paypa1, g00gle
2. **Urgency language** - "Act now", "Account suspended"
3. **Generic greetings** - "Dear Customer" instead of your name
4. **Suspicious links** - Hover to preview before clicking
5. **Request for credentials** - Legitimate companies don't ask via email

**Retail-Specific Threats:**
• Fake vendor invoices
• Fraudulent shipping notifications
• Gift card scam emails
• POS system update phishing

**What to Do:**
1. Don't click any links
2. Verify sender via official channels
3. Report to IT security
4. Use Sentri's Scan Link feature

Would you like me to analyze a specific link or email?"""


def _get_invoice_fraud_guidance() -> str:
    return """**💰 Vendor Invoice Fraud Protection**

This is the #1 threat to retail businesses. Here's how to protect yourself:

**Warning Signs:**
• Invoice from unknown vendor
• Changed payment details
• Urgency to pay "immediately"
• Slight variations in vendor email domain
• Request to use different bank account

**Verification Steps:**
1. **Call the vendor** using a known phone number (not from the email)
2. **Check purchase orders** against your records
3. **Verify banking changes** through established contacts
4. **Review email headers** for sender authentication

**Sentri Protection:**
Use "Analyze Email" to automatically detect:
• Spoofed sender addresses
• Urgency manipulation tactics
• Fraudulent payment links
• Impersonation indicators

Want me to analyze a suspicious invoice email?"""


def _get_credential_guidance() -> str:
    return """**🔐 Credential Security for Retail Staff**

**Password Best Practices:**
• Minimum 12 characters
• Mix of uppercase, lowercase, numbers, symbols
• Different password for each system
• Never share credentials with anyone

**When to Be Suspicious:**
• Unexpected password reset emails
• Login pages that look slightly different
• Requests to "verify" your account
• Pop-ups asking for credentials

**POS Terminal Security:**
• Log out between transactions
• Never leave terminal unattended while logged in
• Report any unusual login screens
• Don't use personal accounts on work systems

**If You Suspect Compromise:**
1. Change password immediately
2. Report to IT security
3. Review recent account activity
4. Enable MFA if available

Need help analyzing a suspicious login page?"""


def _get_pos_security_guidance() -> str:
    return """**🖥️ POS & Terminal Security**

**Daily Security Checks:**
1. Inspect card reader for tampering
2. Check for unauthorized USB devices
3. Verify secure network indicator
4. Report any physical damage

**Suspicious Activity Indicators:**
• Unexpected system updates
• Slow transaction processing
• Unknown processes running
• Login prompts at unusual times

**Skimmer Detection:**
• Loose card slot
• Extra attachments on reader
• Keyboard overlay
• Hidden cameras near PIN pad

**Network Security:**
• Never connect personal devices
• Report unknown WiFi networks
• Don't access personal sites
• Log all unusual network behavior

**Guardian monitors your POS systems 24/7** for:
• Failed login attempts
• Unusual transaction patterns
• Network anomalies
• Privilege escalation attempts

Report any concerns to IT security immediately."""


def _get_incident_reporting_guidance() -> str:
    return """**🚨 Security Incident Reporting**

**Immediate Steps:**
1. Don't panic - document everything
2. Don't delete suspicious items
3. Disconnect compromised system (if instructed)
4. Contact IT security hotline

**What to Report:**
• What happened and when
• Systems/accounts affected
• Any actions you took
• Screenshots if possible

**Reporting Channels:**
• IT Security Hotline: [Your hotline]
• Email: security@yourcompany.com
• Sentri Platform: Use scan features
• Manager escalation for urgent issues

**You Won't Get in Trouble for Reporting**
We'd rather investigate 100 false alarms than miss one real incident.

**Common Reportable Events:**
• Clicked a suspicious link
• Received phishing email
• Noticed unusual POS behavior
• Found unauthorized device
• Saw tampering on equipment

Is there a specific incident you need help with?"""


def _get_help_response() -> str:
    return """**👋 How I Can Help You**

I'm Sentri's AI security assistant specialized in retail protection.

**Security Analysis:**
• 🔗 **Scan Link** - Paste any URL for risk assessment
• 📧 **Analyze Email** - Check emails for phishing/fraud
• 📋 **Review Logs** - Identify security anomalies

**Security Guidance:**
• Ask about phishing detection
• Invoice fraud prevention
• Password & credential security
• POS terminal protection
• Incident reporting

**Try asking:**
• "Analyze this email from a vendor"
• "Is this link safe?" + paste URL
• "How do I report a security incident?"
• "What are signs of POS tampering?"

**Quick Actions:**
Use the buttons below the chat to quickly:
1. Scan a suspicious link
2. Analyze an email
3. Review security logs

How can I help protect your retail operations today?"""


def _get_default_response() -> str:
    return """I'm here to help with retail security concerns.

**I can assist with:**
• Analyzing suspicious links or emails
• Security best practices guidance
• Incident reporting procedures
• POS/terminal security

**Try:**
• Pasting a URL for me to analyze
• Asking about phishing detection
• Describing a security concern

What would you like help with?"""
