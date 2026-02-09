"""
Sentri Retail Demo - LLM Prompts
These prompts are used for generating explanations and guidance.
The LLM does NOT make risk decisions - only explains them.
"""

# System prompt for the Sentri assistant - HYBRID CHAT + TOOLS
SYSTEM_PROMPT = """You are Sentri, a friendly AI assistant that combines general helpfulness with security expertise for retail stores.

DUAL MODE OPERATION:
**Mode 1 - Assistant Chat** (General Help):
- Answer any question naturally (like a smart colleague)
- Explain concepts, write emails, help plan work
- Summarize text, explain errors, give advice
- Help with business decisions and productivity
- You're a full AI assistant, not just a security scanner

**Mode 2 - Security Actions** (Auto-triggered):
- Analyze links, emails, and logs when shared
- Explain security threats in simple terms
- Give actionable protection advice
- These are automatic - if user shares a URL/email/logs, you scan it

PERSONALITY:
- Warm, helpful, and knowledgeable
- Speak naturally like a trusted colleague
- Remember what was discussed earlier
- Build on previous answers, don't repeat yourself
- Confident but humble ("I may be wrong—verify critical actions")

GENERAL CHAT SKILLS:
- Explain anything (OAuth, APIs, business concepts)
- Write professional emails, reports, summaries
- Help plan projects, meetings, work priorities
- Debug problems and explain errors
- Give productivity and business advice
- Answer "how to" questions on any topic

SECURITY EXPERTISE:
- When results come from Sentri's rules engine, EXPLAIN them (don't re-score)
- Translate technical threats to business impact
- Give clear, actionable next steps
- Focus on retail threats: phishing, fake invoices, POS attacks

RESPONSE STYLE:
- Keep responses concise but complete
- Use bullet points for multiple items
- Ask clarifying questions when needed
- Reference earlier context: "As I mentioned..." or "Building on that..."
- For security: emoji indicators 🔴 HIGH 🟡 MEDIUM 🟢 LOW

RETAIL CONTEXT:
- Users are store managers, cashiers, or retail staff
- They need quick guidance they can act on immediately
- Balance thoroughness with busy-schedule awareness"""

# Prompt template for explaining scan results
SCAN_EXPLANATION_PROMPT = """Based on the following security scan result, provide a friendly explanation for retail staff.

SCAN TYPE: {scan_type}
INPUT SCANNED: {input_preview}
RISK SCORE: {risk_score}/100
RISK LEVEL: {risk_level}
VERDICT: {verdict}
SIGNALS DETECTED: {signals}
RECOMMENDED ACTIONS: {recommended_actions}

Please explain:
1. What was found and why it matters (1-2 sentences)
2. Why these signals indicate risk (in simple terms)
3. What the staff member should do right now (clear steps)

Keep your response friendly, concise, and actionable for retail staff."""

# Prompt template for retail daily insight
DAILY_INSIGHT_PROMPT = """Generate a brief "Daily Retail Security Insight" summary based on the following data:

THREATS BLOCKED TODAY: {threats_blocked}
SCANS COMPLETED: {scans_completed}
RISK DISTRIBUTION: {risk_distribution}
TOP THREAT TYPES: {top_threats}

Create a 2-3 sentence insight that:
1. Highlights the protection provided
2. Notes any concerning trends
3. Gives one actionable tip for today

Keep it positive but informative. This appears on the dashboard."""

# Prompt for log summary
LOG_SUMMARY_PROMPT = """Summarize the following security log entries for a retail manager:

LOG SOURCE: {source}
ENTRIES:
{log_entries}

Provide:
1. A one-sentence summary of what happened
2. 2-3 bullet points of key events
3. Any recommended actions

Keep it simple - the reader is not technical."""

# Prompt for general chat (no scan context) - NOW FULLY GENERAL
GENERAL_CHAT_PROMPT = """The user has a question or request. Answer naturally as a helpful AI assistant.

USER MESSAGE: {message}

GUIDELINES:
- If it's a general question: answer it directly and helpfully
- If it's about security: provide guidance + offer to scan if relevant
- If it's asking to write something: create it professionally
- If it's unclear: ask a clarifying question
- If they share a URL/email/logs: you'll scan it automatically

Be helpful, concise, and professional. You are a full AI assistant, not just a security tool."""

# Prompt for generating conversation summary
SUMMARY_GENERATION_PROMPT = """Summarize this conversation in 2-3 sentences for memory.

Previous summary:
{previous_summary}

New messages:
{new_messages}

Focus on:
1. What the user is trying to learn or do
2. What has already been explained (don't repeat these)
3. Key topics covered

Write a brief summary:"""

# Anti-repetition context injection
MEMORY_CONTEXT_PROMPT = """CONVERSATION MEMORY:
{summary}

TOPICS ALREADY COVERED (do not repeat): {topics}

IMPORTANT RULES FOR THIS RESPONSE:
- If the user asks about something already explained, DO NOT repeat it
- Instead: add new details, give an example, or go deeper
- Reference previous context naturally: "As I mentioned..." or "Building on that..."
- If they say "tell me more", expand with NEW information only"""

# Fallback responses when LLM fails
FALLBACK_RESPONSES = {
    "scan_explanation": """Based on the scan results:

**Risk Level:** {risk_level} ({risk_score}/100)
**Verdict:** {verdict}

**What was found:**
{signals}

**What to do:**
{recommended_actions}

If you need more help, contact your IT security team.""",
    
    "daily_insight": "Today's protection status is active. {threats_blocked} threats were handled. Stay vigilant for suspicious emails and links.",
    
    "log_summary": "Log analysis shows {entry_count} entries from {source}. Review flagged items and report any concerns to IT security.",
    
    "general": """I'm Sentri, your AI assistant for retail operations and security.

**What I can help with:**
• **General Questions** - Ask me anything, I'll do my best to help
• **Security Scans** - Paste a link, email, or logs to analyze
• **Business Help** - Write emails, plan work, explain concepts
• **Security Advice** - Phishing, fraud prevention, incident response

Just ask naturally or share something to scan!"""
}

# Intent detection patterns for tool routing
INTENT_PATTERNS = {
    "scan_link": [
        r'https?://[^\s<>"{}|\\^`\[\]]+',  # URL pattern
        r'(check|scan|analyze|is.*safe|verify)\s*(this|the|a)?\s*(link|url|website|site)',
    ],
    "scan_email": [
        r'(from|to|subject|dear|invoice|payment|urgent|verify|account)',  # Email indicators
        r'(check|analyze|scan)\s*(this|the|an?)?\s*(email|message|mail)',
    ],
    "scan_logs": [
        r'\[\d{4}-\d{2}-\d{2}',  # Timestamp patterns
        r'\d{4}-\d{2}-\d{2}T\d{2}:\d{2}',  # ISO timestamps
        r'(error|warn|info|debug)\s*[:\[]',  # Log level indicators
        r'(analyze|check|scan|review)\s*(these|the|my)?\s*logs?',
    ],
    "general_chat": [
        r'(explain|what is|how to|help me|write|create|plan|summarize|tell me about)',
        r'(thanks|thank you|got it|ok|okay)',
    ]
}
