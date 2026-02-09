"""
Local LLM - Knowledge Base Fallback
===================================

When external APIs are unavailable, this provides
responses from a curated local knowledge base.

This is the ultimate fallback - always available.
"""

import re
import logging
from typing import Optional

logger = logging.getLogger(__name__)


class LocalLLM:
    """
    Local LLM - Curated Knowledge Base
    
    Provides responses when external LLM APIs are unavailable.
    Uses pattern matching and a curated knowledge base.
    """
    
    # Curated knowledge base for security topics
    KNOWLEDGE_BASE = {
        # Phishing
        "phishing": """**Phishing** is a cyber attack tricking you into revealing sensitive information.

🚨 **Warning Signs:**
• Urgent language ('Act NOW!')
• Suspicious sender addresses
• Links that don't match the company
• Requests for passwords/payment info
• Grammar mistakes

✅ **Protection:**
• Hover over links before clicking
• Verify sender through official channels
• Never share passwords via email
• Use 2FA on all accounts
• Report suspicious emails""",
        
        # Malware
        "malware": """**Malware** is malicious software designed to harm your device or steal data.

🦠 **Common Types:**
• **Viruses** - Infect files and spread
• **Ransomware** - Encrypts files for ransom
• **Trojans** - Hidden in legitimate software
• **Spyware** - Steals information secretly
• **Worms** - Self-replicating across networks

✅ **Protection:**
• Keep antivirus updated
• Don't download from untrusted sources
• Update all software regularly
• Be careful with email attachments
• Backup important files""",
        
        # Password
        "password": """**Strong Password Tips:**

🔐 **Create Strong Passwords:**
• At least 12+ characters
• Mix uppercase, lowercase, numbers, symbols
• Avoid personal info (birthdays, names)
• Use passphrases: "Coffee$Morning#2024!"

✅ **Best Practices:**
• Unique password for each account
• Use a password manager
• Enable 2FA/MFA everywhere
• Change passwords if breached
• Never share passwords

🚫 **Avoid:**
• "password123", "qwerty"
• Pet names, birthdates
• Same password everywhere""",
        
        # Two-Factor Authentication
        "2fa|mfa|authentication": """**Two-Factor Authentication (2FA/MFA)**

🛡️ **What It Is:**
Extra security beyond just a password. Requires something you:
• **Know** (password)
• **Have** (phone, security key)
• **Are** (fingerprint, face)

✅ **Best 2FA Methods:**
1. **Hardware Keys** (YubiKey) - Most secure
2. **Authenticator Apps** (Google Auth) - Very secure
3. **SMS Codes** - Better than nothing, but can be intercepted

⚡ **Enable 2FA On:**
• Email accounts
• Banking and financial
• Social media
• Work accounts
• Anywhere that offers it""",
        
        # Ransomware
        "ransomware": """**Ransomware** encrypts your files and demands payment to unlock them.

🚨 **How It Spreads:**
• Phishing emails with attachments
• Malicious downloads
• Exploited vulnerabilities
• Infected USB drives

✅ **Protection:**
• Regular offline backups (3-2-1 rule)
• Keep systems updated
• Employee security training
• Use anti-ransomware tools
• Disable macros in documents

⚠️ **If Infected:**
• Disconnect from network immediately
• Don't pay the ransom
• Report to authorities
• Restore from clean backups""",
        
        # VPN
        "vpn": """**VPN (Virtual Private Network)**

🔒 **What It Does:**
• Encrypts your internet traffic
• Hides your IP address
• Protects on public WiFi
• Bypasses geographic restrictions

✅ **When to Use:**
• Public WiFi (coffee shops, airports)
• Accessing sensitive data remotely
• Privacy-conscious browsing

⚠️ **Limitations:**
• Doesn't make you anonymous
• Free VPNs may log your data
• Won't protect from malware
• Choose reputable providers""",
        
        # Social Engineering
        "social engineering": """**Social Engineering** manipulates people into revealing information.

🎭 **Common Tactics:**
• **Phishing** - Fake emails/websites
• **Pretexting** - Fake scenarios
• **Baiting** - Free offers/downloads
• **Tailgating** - Following into buildings
• **Vishing** - Phone scams

✅ **Defense:**
• Verify identities independently
• Don't trust unsolicited contacts
• Think before clicking/sharing
• Report suspicious requests
• Security awareness training""",
    }
    
    # Fallback responses by topic type
    FALLBACKS = {
        "question": """I'd love to help with that! My full AI capabilities are temporarily limited.

**What I can still do:**
• Scan links for security threats
• Analyze suspicious emails
• Review security logs
• Answer basic security questions

Try asking about phishing, passwords, or malware!""",
        
        "chat": """Thanks for chatting! I'm here to help with security.

**Quick Actions:**
• Paste a URL to scan it
• Share suspicious email content
• Ask about security topics

How can I help protect you today?""",
        
        "scan": """I'll analyze that for you using my security tools.

The scan is running - I'll provide risk assessment shortly."""
    }
    
    def __init__(self):
        """Initialize Local LLM"""
        logger.info("📚 Local LLM (Knowledge Base) initialized")
    
    async def generate(self, prompt: str, context: str = None) -> str:
        """
        Generate response from knowledge base
        
        Args:
            prompt: User message/question
            context: Optional conversation context
            
        Returns:
            Response from knowledge base
        """
        prompt_lower = prompt.lower()
        
        # Search knowledge base
        for keywords, response in self.KNOWLEDGE_BASE.items():
            keyword_list = keywords.split("|")
            for keyword in keyword_list:
                if len(keyword) < 3:
                    continue
                if re.search(rf'\b{re.escape(keyword)}\b', prompt_lower):
                    logger.info(f"📚 Knowledge base match: {keyword}")
                    return response
        
        # Determine fallback type
        if any(q in prompt_lower for q in ['what', 'how', 'why', 'explain', 'tell']):
            return self.FALLBACKS["question"]
        
        return self.FALLBACKS["chat"]
    
    async def chat(self, message: str, context: str = None) -> str:
        """Chat using knowledge base"""
        return await self.generate(message, context)
    
    async def answer_security_question(self, question: str, context: str = None) -> str:
        """Answer security question"""
        return await self.generate(question, context)
    
    async def explain_scan(self, scan_type: str, scan_result: dict, context: str = None) -> Optional[str]:
        """
        Explain scan result (simplified for local LLM)
        
        Returns None to let the tool result speak for itself.
        """
        # For local LLM, we don't add extra explanation
        # The tool's result is sufficient
        return None
    
    def is_available(self) -> bool:
        """Local LLM is always available"""
        return True
