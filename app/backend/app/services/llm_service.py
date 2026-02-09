"""
LLM Service - Gemini AI integration for Sentri AI Assistant
The LLM is used for generating explanations, guidance, and general chat.
Risk decisions are made by the rules engine (risk_engine.py).
"""
import os
import re
import logging
from typing import Optional, Dict, List
import google.generativeai as genai
from .prompts import (
    SYSTEM_PROMPT,
    SCAN_EXPLANATION_PROMPT,
    DAILY_INSIGHT_PROMPT,
    LOG_SUMMARY_PROMPT,
    GENERAL_CHAT_PROMPT,
    FALLBACK_RESPONSES,
    SUMMARY_GENERATION_PROMPT,
    MEMORY_CONTEXT_PROMPT
)

logger = logging.getLogger(__name__)

# Configuration - Gemini API
GEMINI_API_KEY = "AIzaSyAKKF7sUvihCyTBPteCW3ywwFzFmJBoatM"
MODEL = "gemini-2.0-flash"
LLM_ENABLED = True

# Initialize Gemini
genai.configure(api_key=GEMINI_API_KEY)
gemini_model = genai.GenerativeModel(MODEL)


# ============================================
# LOCAL KNOWLEDGE BASE - Comprehensive Q&A
# ============================================

LOCAL_KNOWLEDGE_BASE = {
    # ========== PROGRAMMING LANGUAGES ==========
    "python": "**Python** is a popular, beginner-friendly programming language known for its clean syntax and versatility.\n\n**Used for:** Web development, data science, AI/ML, automation, scripting\n\n**Key Features:**\n• Easy to read and write\n• Huge ecosystem of libraries (NumPy, Pandas, Django, Flask)\n• Great for beginners and experts alike\n• Used by Google, Netflix, Instagram, Spotify\n\n**Example:**\n```python\nprint('Hello, World!')\n```",
    
    "javascript": "**JavaScript** is the language of the web, running in browsers and servers.\n\n**Used for:** Frontend web development, backend (Node.js), mobile apps (React Native)\n\n**Key Features:**\n• Powers interactive websites\n• Runs in every browser\n• Frameworks: React, Vue, Angular\n• Event-driven and asynchronous\n\n**Example:**\n```javascript\nconsole.log('Hello, World!');\n```",
    
    "java": "**Java** is a versatile, object-oriented programming language known for 'write once, run anywhere'.\n\n**Used for:** Enterprise apps, Android development, backend systems\n\n**Key Features:**\n• Platform independent (JVM)\n• Strongly typed and object-oriented\n• Large standard library\n• Used by banks, enterprises, Android apps\n\n**Example:**\n```java\nSystem.out.println(\"Hello, World!\");\n```",
    
    "c++|cpp": "**C++** is a powerful, high-performance programming language based on C.\n\n**Used for:** Game development, system software, embedded systems, competitive programming\n\n**Key Features:**\n• Close to hardware, very fast\n• Object-oriented + procedural\n• Manual memory management\n• Used in games, OS, browsers\n\n**Example:**\n```cpp\ncout << \"Hello, World!\" << endl;\n```",
    
    "rust": "**Rust** is a systems programming language focused on safety and performance.\n\n**Used for:** System software, WebAssembly, command-line tools, game engines\n\n**Key Features:**\n• Memory safety without garbage collection\n• Zero-cost abstractions\n• Concurrent programming support\n• Growing rapidly in popularity",
    
    "typescript": "**TypeScript** is JavaScript with static types, created by Microsoft.\n\n**Used for:** Large-scale web applications, Angular, React projects\n\n**Key Features:**\n• Adds type safety to JavaScript\n• Better IDE support and autocompletion\n• Catches errors at compile time\n• Compiles to plain JavaScript",
    
    "go|golang": "**Go** (Golang) is a simple, efficient language created by Google.\n\n**Used for:** Cloud services, DevOps tools, APIs, microservices\n\n**Key Features:**\n• Fast compilation\n• Built-in concurrency (goroutines)\n• Simple syntax\n• Used by Docker, Kubernetes, Terraform",
    
    "sql": "**SQL** (Structured Query Language) is used to manage and query databases.\n\n**Used for:** Database operations, data analysis, reporting\n\n**Key Commands:**\n• `SELECT` - retrieve data\n• `INSERT` - add data\n• `UPDATE` - modify data\n• `DELETE` - remove data\n• `JOIN` - combine tables\n\n**Example:**\n```sql\nSELECT * FROM users WHERE age > 18;\n```",
    
    "html": "**HTML** (HyperText Markup Language) is the standard language for creating web pages.\n\n**Used for:** Structuring web content, creating web page layouts\n\n**Key Elements:**\n• `<head>` - page metadata\n• `<body>` - visible content\n• `<div>`, `<span>` - containers\n• `<a>` - links\n• `<img>` - images",
    
    "css": "**CSS** (Cascading Style Sheets) is used to style and layout web pages.\n\n**Used for:** Styling HTML elements, responsive design, animations\n\n**Key Concepts:**\n• Selectors (class, ID, element)\n• Box model (margin, padding, border)\n• Flexbox and Grid for layouts\n• Media queries for responsiveness",
    
    "react": "**React** is a JavaScript library for building user interfaces, created by Facebook.\n\n**Used for:** Single-page applications, interactive UIs, mobile apps (React Native)\n\n**Key Concepts:**\n• Components (reusable UI pieces)\n• Virtual DOM for performance\n• JSX syntax\n• Hooks (useState, useEffect)\n• State management",
    
    # ========== TECH CONCEPTS ==========
    "api": "**API** (Application Programming Interface) is how software systems communicate.\n\n**Types:**\n• **REST API** - Uses HTTP methods (GET, POST, PUT, DELETE)\n• **GraphQL** - Flexible queries, single endpoint\n• **WebSocket** - Real-time bidirectional communication\n\n**Example REST API:**\n```\nGET /api/users/123\nPOST /api/users\n```",
    
    "database|db": "**Database** is an organized collection of data stored electronically.\n\n**Types:**\n• **SQL/Relational** - MySQL, PostgreSQL, SQLite (tables with rows)\n• **NoSQL** - MongoDB, Redis (flexible documents/key-value)\n\n**Key Concepts:**\n• Tables, rows, columns\n• Primary keys, foreign keys\n• CRUD operations\n• Indexing for performance",
    
    "cloud|aws|azure|gcp": "**Cloud Computing** provides on-demand computing resources over the internet.\n\n**Major Providers:**\n• **AWS** (Amazon) - Largest, most services\n• **Azure** (Microsoft) - Enterprise integration\n• **GCP** (Google) - AI/ML focused\n\n**Services:**\n• Compute (VMs, containers)\n• Storage (S3, Blob)\n• Databases (RDS, Cosmos)\n• AI/ML tools",
    
    "git|github": "**Git** is a version control system for tracking code changes. **GitHub** is a platform for hosting Git repositories.\n\n**Common Commands:**\n```\ngit clone <repo>    # Download repository\ngit add .           # Stage changes\ngit commit -m 'msg' # Save changes\ngit push            # Upload to GitHub\ngit pull            # Download updates\n```",
    
    "docker|container": "**Docker** is a platform for building and running containerized applications.\n\n**Key Concepts:**\n• **Image** - Blueprint for a container\n• **Container** - Running instance of an image\n• **Dockerfile** - Instructions to build an image\n\n**Benefits:**\n• Consistent across environments\n• Isolated and lightweight\n• Easy deployment",
    
    "machine learning|ml|ai|artificial intelligence": "**Machine Learning (ML)** is AI that learns from data without explicit programming.\n\n**Types:**\n• **Supervised** - Learns from labeled data (classification, regression)\n• **Unsupervised** - Finds patterns in unlabeled data (clustering)\n• **Reinforcement** - Learns by trial and error\n\n**Popular Tools:** TensorFlow, PyTorch, scikit-learn",
    
    "oauth": "**OAuth** (Open Authorization) lets users grant apps limited access without sharing passwords.\n\n**How it works:**\n1. User clicks 'Login with Google'\n2. Google asks user for permission\n3. App receives a token (not password)\n4. App uses token to access allowed data\n\n**OAuth 2.0** is the current standard.",
    
    "encryption|encrypt": "**Encryption** converts data into a coded format to prevent unauthorized access.\n\n**Types:**\n• **Symmetric** - Same key encrypts/decrypts (AES)\n• **Asymmetric** - Public/private key pairs (RSA)\n• **Hashing** - One-way conversion (SHA-256, bcrypt)\n\n**Uses:** HTTPS, passwords, secure messaging",
    
    "vpn": "**VPN** (Virtual Private Network) creates a secure, encrypted connection over the internet.\n\n**Benefits:**\n• Encrypts your traffic\n• Hides your IP address\n• Bypass geo-restrictions\n• Secure public WiFi use\n\n**For business:** Secure remote access to company networks",
    
    "http|https": "**HTTP** (HyperText Transfer Protocol) is how browsers communicate with web servers.\n\n**HTTP Methods:**\n• `GET` - Retrieve data\n• `POST` - Send data\n• `PUT` - Update data\n• `DELETE` - Remove data\n\n**HTTPS** = HTTP + SSL/TLS encryption for security 🔒",
    
    # ========== SECURITY ==========
    "phishing": "**Phishing** is a cyber attack tricking you into revealing sensitive information.\n\n🚨 **Warning Signs:**\n• Urgent language ('Act NOW!')\n• Suspicious sender addresses\n• Links that don't match the company\n• Requests for passwords/payment info\n• Grammar mistakes\n\n✅ **Protection:**\n• Hover over links before clicking\n• Verify sender email addresses\n• Contact companies directly if unsure",
    
    "malware|virus|ransomware": "**Malware** is malicious software designed to harm or exploit systems.\n\n**Types:**\n• **Virus** - Spreads by attaching to files\n• **Ransomware** - Encrypts files, demands payment\n• **Trojan** - Disguised as legitimate software\n• **Spyware** - Secretly monitors activity\n\n✅ **Protection:** Keep software updated, use antivirus, don't click suspicious links",
    
    "password": "**Password Security Best Practices:**\n\n✅ **Do:**\n• Use 12+ characters with mixed types\n• Use unique passwords for each account\n• Enable 2FA (two-factor authentication)\n• Use a password manager\n\n❌ **Don't:**\n• Use personal info (birthdays, pet names)\n• Reuse passwords\n• Share via email/chat\n\n💡 **Tip:** Try passphrases like 'Coffee-Mountain-Blue-42!'",
    
    "firewall": "**Firewall** is a security system that monitors and controls network traffic.\n\n**Types:**\n• **Network firewall** - Protects entire networks\n• **Host firewall** - Protects individual devices\n• **Application firewall** - Filters specific app traffic\n\n**Functions:** Block malicious traffic, control access, log activity",
    
    "2fa|two factor|mfa": "**Two-Factor Authentication (2FA/MFA)** adds an extra security layer beyond passwords.\n\n**Methods:**\n• SMS codes (less secure)\n• Authenticator apps (Google, Microsoft)\n• Hardware keys (YubiKey)\n• Biometrics (fingerprint, face)\n\n✅ **Always enable 2FA** for important accounts (email, banking, social media)",
    
    # ========== RETAIL SECURITY ==========
    "pos|point of sale": "**POS Security** (Point of Sale) protects retail payment systems.\n\n🛡️ **Best Practices:**\n• Keep POS software updated\n• Use EMV chip readers (encrypted)\n• Separate POS from guest WiFi\n• Regular security audits\n• Train staff on skimmer detection\n\n⚠️ **Watch for:** Unusual devices on terminals, unexpected behavior",
    
    "fraud|scam": "**Retail Fraud Prevention:**\n\n🚨 **Common Types:**\n• Fake vendor invoices\n• Return fraud\n• Gift card scams\n• Chargebacks from stolen cards\n\n✅ **Prevention:**\n• Verify vendor contacts before paying\n• Scan suspicious emails with Sentri\n• Train staff on fraud indicators\n• Implement return verification",
    
    # ========== GENERAL KNOWLEDGE ==========
    "capital of france|paris": "The capital of **France** is **Paris**! 🗼\n\nParis is known for:\n• The Eiffel Tower\n• The Louvre Museum\n• Notre-Dame Cathedral\n• Champs-Élysées\n\nPopulation: ~2.1 million (city), ~12 million (metro area)",
    
    "capital": "Here are some world capitals:\n\n🌍 **Major Capitals:**\n• **USA** - Washington, D.C.\n• **UK** - London\n• **France** - Paris\n• **Japan** - Tokyo\n• **Australia** - Canberra\n• **Germany** - Berlin\n• **Canada** - Ottawa\n\nAsk about a specific country for more details!",
    
    "weather": "I can't check live weather, but here are some tips:\n\n☀️ **Check weather at:**\n• weather.com\n• AccuWeather.com\n• Your phone's weather app\n\n**Tip:** Always have a backup plan for outdoor events!",
    
    "time|date": "I don't have access to real-time clock, but:\n\n⏰ **Check time at:**\n• Your device's clock\n• time.is (accurate world clock)\n• worldtimeserver.com",
    
    # ========== MATH & SCIENCE ==========
    "prime number|prime": "**Prime Numbers** are numbers greater than 1 that are only divisible by 1 and themselves.\n\n**First 10 primes:** 2, 3, 5, 7, 11, 13, 17, 19, 23, 29\n\n**Facts:**\n• 2 is the only even prime\n• Prime numbers are infinite\n• Used in cryptography (RSA encryption)",
    
    "fibonacci": "**Fibonacci Sequence** is where each number is the sum of the two before it.\n\n**Sequence:** 0, 1, 1, 2, 3, 5, 8, 13, 21, 34, 55...\n\n**Formula:** F(n) = F(n-1) + F(n-2)\n\n**Fun fact:** Appears in nature (sunflowers, shells, galaxies)!",
    
    "pi": "**Pi (π)** is the ratio of a circle's circumference to its diameter.\n\n**Value:** 3.14159265358979...\n\n**Uses:**\n• Circle calculations (area = πr²)\n• Trigonometry\n• Engineering and physics\n\n**Fun fact:** Pi is irrational - its digits never end or repeat!",
    
    # ========== HELP & GREETINGS ==========
    "help|what can you do": "I'm **Sentri**, your AI assistant! Here's what I can do:\n\n💬 **Chat & Explain:**\n• Answer questions about tech, programming, security\n• Explain concepts in simple terms\n• General knowledge Q&A\n\n🔍 **Security Scans:**\n• Paste a **URL** to check if it's safe\n• Paste an **email** to detect phishing\n• Paste **logs** for security analysis\n\nJust ask naturally or use the action buttons!",
    
    "hello|hi|hey|good morning|good afternoon": "Hello! 👋 I'm **Sentri**, your AI assistant!\n\nI can help you with:\n• 💻 Programming questions\n• 🔒 Security guidance\n• 📚 General knowledge\n• 🔍 Link/email scanning\n\nWhat would you like to know?",
    
    "thanks|thank you|thx": "You're welcome! 😊 Happy to help!\n\nFeel free to ask me anything else - I'm here for you!",
    
    "bye|goodbye|see you": "Goodbye! 👋 Stay safe out there!\n\nCome back anytime you have questions or need to scan something suspicious!",
    
    "who are you|your name": "I'm **Sentri** 🛡️ - your AI assistant for retail security and general knowledge!\n\n**What I do:**\n• Answer questions (tech, programming, security, general)\n• Scan suspicious links and emails\n• Provide security guidance\n• Help with coding concepts\n\n**Built for:** Retail security teams and curious minds!",
}

def get_local_response(message: str) -> Optional[str]:
    """
    Get a response from local knowledge base when API is unavailable.
    Returns None if no match found.
    Uses word boundary matching to avoid false positives.
    """
    message_lower = message.lower().strip()
    
    # Define priority order - longer/more specific phrases first
    priority_keywords = [
        # Specific phrases (check these first)
        "capital of france", "paris",
        "capital",
        "machine learning", "artificial intelligence",
        "two factor", "mfa", "2fa",
        "point of sale",
        "who are you", "your name", "what can you do",
        "good morning", "good afternoon",
        "thank you", "thanks", "thx",
        "goodbye", "bye", "see you",
        # Single words
        "hello", "hi", "hey",
    ]
    
    # First check priority keywords in order
    for pkey in priority_keywords:
        if pkey in message_lower:
            for keywords, response in LOCAL_KNOWLEDGE_BASE.items():
                keyword_list = keywords.split("|")
                if pkey in keyword_list or any(pkey in k for k in keyword_list):
                    return response
    
    # Handle "what is X" or "explain X" patterns
    what_is_match = re.search(r'(?:what is|what\'s|explain|tell me about|define|how does)\s+(\w+)', message_lower)
    if what_is_match:
        topic = what_is_match.group(1)
        for keywords, response in LOCAL_KNOWLEDGE_BASE.items():
            keyword_list = keywords.split("|")
            for keyword in keyword_list:
                # Use word boundary regex for accurate matching
                if re.search(rf'\b{re.escape(topic)}\b', keyword):
                    return response
    
    # General keyword matching with word boundaries
    for keywords, response in LOCAL_KNOWLEDGE_BASE.items():
        keyword_list = keywords.split("|")
        for keyword in keyword_list:
            # Skip very short keywords to avoid false positives
            if len(keyword) < 3:
                continue
            # Use word boundary matching
            if re.search(rf'\b{re.escape(keyword)}\b', message_lower):
                return response
    
    return None


def get_smart_fallback(message: str) -> str:
    """
    Generate a contextual fallback response when API is down.
    """
    message_lower = message.lower()
    
    # Try local knowledge base first
    local_response = get_local_response(message)
    if local_response:
        return local_response
    
    # Contextual fallbacks based on message type
    if any(q in message_lower for q in ['what', 'how', 'why', 'explain', 'tell me']):
        return f"""I'd love to explain that for you! Unfortunately, my AI connection is temporarily limited.

**What I can still do:**
• Scan links, emails, or logs for security threats (just paste them!)
• Answer security questions (try asking about phishing, passwords, or malware)
• Explain basic tech concepts

**Your question:** "{message[:50]}{'...' if len(message) > 50 else ''}"

Try rephrasing, or paste a link/email for me to scan!"""
    
    if any(word in message_lower for word in ['write', 'create', 'draft', 'compose']):
        return """I can help with writing, but my AI connection is currently limited.

**For now, try:**
• Being more specific about what you need
• Pasting content for me to analyze/improve
• Using the action buttons to scan security content

I'll do my best to help!"""
    
    # Default smart fallback
    return f"""Thanks for your message! I'm having trouble connecting to my full AI capabilities right now.

**What still works:**
• 🔗 **Scan links** - Paste any URL to check safety
• 📧 **Analyze emails** - Paste suspicious email content
• 📋 **Review logs** - Paste security logs
• 🔒 **Security Q&A** - Ask about phishing, passwords, malware

Your message: "{message[:40]}{'...' if len(message) > 40 else ''}"

Try one of the above, or ask a security question!"""


def ask_llm(user_message: str, context: str = "") -> str:
    """
    Simple synchronous LLM call using Gemini.
    Returns fallback on failure.
    """
    if not LLM_ENABLED:
        return FALLBACK_RESPONSES.get("general", "Sentri is analyzing your request.")
    
    try:
        full_message = f"{SYSTEM_PROMPT}\n\n{context}\n\nUser Message:\n{user_message}" if context else f"{SYSTEM_PROMPT}\n\nUser Message:\n{user_message}"
        response = gemini_model.generate_content(full_message)
        return response.text
    except Exception as e:
        logger.error(f"Gemini LLM error: {str(e)}")
        return get_smart_fallback(user_message)


class LLMService:
    """Service for LLM-powered explanations using Gemini"""
    
    def __init__(self):
        self.model = MODEL
        self.enabled = LLM_ENABLED
    
    async def _call_llm(self, messages: List[dict], max_tokens: int = 500) -> Optional[str]:
        """Make a call to the Gemini API"""
        if not self.enabled:
            return None
        
        try:
            # Convert OpenAI-style messages to Gemini prompt
            prompt_parts = []
            for msg in messages:
                role = msg.get("role", "user")
                content = msg.get("content", "")
                if role == "system":
                    prompt_parts.append(f"[System Instructions]: {content}")
                elif role == "assistant":
                    prompt_parts.append(f"Assistant: {content}")
                else:
                    prompt_parts.append(f"User: {content}")
            
            full_prompt = "\n\n".join(prompt_parts)
            response = gemini_model.generate_content(full_prompt)
            return response.text
        except Exception as e:
            logger.error(f"Gemini API error: {str(e)}")
            return None
    
    async def explain_scan_result(
        self,
        scan_type: str,
        input_preview: str,
        risk_score: int,
        risk_level: str,
        verdict: str,
        signals: str,
        recommended_actions: str,
        history: List[dict] = None
    ) -> str:
        """Generate a friendly explanation of scan results with conversation context"""
        
        prompt = SCAN_EXPLANATION_PROMPT.format(
            scan_type=scan_type,
            input_preview=input_preview[:100],
            risk_score=risk_score,
            risk_level=risk_level,
            verdict=verdict,
            signals=signals,
            recommended_actions=recommended_actions
        )
        
        # Build messages with history for context
        messages = [{"role": "system", "content": SYSTEM_PROMPT}]
        
        # Add conversation history (limited to last 6 messages)
        if history:
            for msg in history[-6:]:
                messages.append({"role": msg["role"], "content": msg["content"]})
        
        messages.append({"role": "user", "content": prompt})
        
        result = await self._call_llm(messages)
        
        if result:
            return result
        
        # Fallback if LLM fails
        return FALLBACK_RESPONSES["scan_explanation"].format(
            risk_level=risk_level,
            risk_score=risk_score,
            verdict=verdict,
            signals=signals,
            recommended_actions=recommended_actions
        )
    
    async def generate_daily_insight(
        self,
        threats_blocked: int,
        scans_completed: int,
        risk_distribution: Dict[str, int],
        top_threats: list
    ) -> str:
        """Generate daily retail security insight"""
        
        prompt = DAILY_INSIGHT_PROMPT.format(
            threats_blocked=threats_blocked,
            scans_completed=scans_completed,
            risk_distribution=str(risk_distribution),
            top_threats=", ".join(top_threats) if top_threats else "None"
        )
        
        messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": prompt}
        ]
        
        result = await self._call_llm(messages, max_tokens=150)
        
        if result:
            return result
        
        # Fallback
        return FALLBACK_RESPONSES["daily_insight"].format(
            threats_blocked=threats_blocked
        )
    
    async def summarize_logs(
        self,
        source: str,
        log_entries: list
    ) -> str:
        """Summarize security logs for non-technical users"""
        
        # Limit entries for token efficiency
        entries_text = "\n".join(log_entries[:20])
        
        prompt = LOG_SUMMARY_PROMPT.format(
            source=source,
            log_entries=entries_text
        )
        
        messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": prompt}
        ]
        
        result = await self._call_llm(messages, max_tokens=300)
        
        if result:
            return result
        
        # Fallback
        return FALLBACK_RESPONSES["log_summary"].format(
            entry_count=len(log_entries),
            source=source
        )
    
    async def general_chat(self, message: str) -> str:
        """Handle general security questions"""
        
        prompt = GENERAL_CHAT_PROMPT.format(message=message)
        
        messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": prompt}
        ]
        
        result = await self._call_llm(messages, max_tokens=250)
        
        if result:
            return result
        
        # Fallback
        return FALLBACK_RESPONSES["general"]
    
    async def chat_with_history(self, message: str, history: List[dict] = None) -> str:
        """
        Natural conversation with full history context.
        This makes Sentri feel like a real AI assistant.
        """
        # Build messages with conversation history
        messages = [{"role": "system", "content": SYSTEM_PROMPT}]
        
        # Add conversation history (last 8 messages for good context)
        if history:
            for msg in history[-8:]:
                messages.append({"role": msg["role"], "content": msg["content"]})
        
        # Add current message
        messages.append({"role": "user", "content": message})
        
        result = await self._call_llm(messages, max_tokens=400)
        
        if result:
            return result
        
        # Smart fallback based on user's message
        return get_smart_fallback(message)
    
    async def chat_with_memory(
        self, 
        message: str, 
        history: List[dict] = None,
        summary: str = "",
        topics_covered: str = ""
    ) -> str:
        """
        Advanced conversation with memory layers:
        1. Conversation summary (compressed understanding)
        2. Recent chat history (last 6 messages)
        3. Topics already covered (anti-repetition)
        """
        messages = [{"role": "system", "content": SYSTEM_PROMPT}]
        
        # Inject memory context if we have a summary
        if summary or topics_covered:
            memory_context = MEMORY_CONTEXT_PROMPT.format(
                summary=summary or "New conversation, no previous context.",
                topics=topics_covered or "None yet"
            )
            messages.append({"role": "system", "content": memory_context})
        
        # Add recent chat history (last 6 for efficiency)
        if history:
            for msg in history[-6:]:
                messages.append({"role": msg["role"], "content": msg["content"]})
        
        # Add current message
        messages.append({"role": "user", "content": message})
        
        result = await self._call_llm(messages, max_tokens=400)
        
        if result:
            return result
        
        # Smart fallback based on user's message
        return get_smart_fallback(message)
    
    async def generate_summary(
        self,
        previous_summary: str,
        new_messages: List[dict]
    ) -> str:
        """
        Generate updated conversation summary for memory layer.
        Called after each exchange to keep memory fresh.
        """
        # Format new messages for summary
        messages_text = "\n".join([
            f"{m['role'].upper()}: {m['content'][:200]}"
            for m in new_messages[-4:]  # Last 4 messages
        ])
        
        prompt = SUMMARY_GENERATION_PROMPT.format(
            previous_summary=previous_summary or "No previous summary.",
            new_messages=messages_text
        )
        
        messages = [
            {"role": "system", "content": "You are a helpful assistant that summarizes conversations briefly."},
            {"role": "user", "content": prompt}
        ]
        
        result = await self._call_llm(messages, max_tokens=150)
        
        return result or previous_summary or ""
    
    def extract_topics(self, summary: str, user_message: str) -> str:
        """
        Extract key topics from conversation for anti-repetition.
        Simple keyword extraction - no LLM needed.
        """
        topics = []
        keywords = [
            "phishing", "email", "link", "url", "invoice", "fraud",
            "security", "password", "scam", "suspicious", "safe",
            "malware", "virus", "attack", "threat", "risk",
            "pos", "payment", "card", "data", "breach"
        ]
        
        text = (summary + " " + user_message).lower()
        for keyword in keywords:
            if keyword in text:
                topics.append(keyword)
        
        return ", ".join(topics[:8])  # Limit to 8 topics


# Global instance
llm_service = LLMService()
