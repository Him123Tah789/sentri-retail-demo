import re

def has_url(text: str) -> bool:
    return bool(re.search(r"https?://|hxxp://|hxxps://", text.lower()))

def looks_like_logs(text: str) -> bool:
    keywords = ["failed login", "error", "auth", "ip", "token", "pos", "branch", "ssh"]
    t = text.lower()
    return any(k in t for k in keywords) and ("\n" in text or len(text) > 120)

def looks_like_email(text: str) -> bool:
    t = text.lower()
    return ("subject:" in t and "from:" in t) or ("invoice" in t and "dear" in t)

def detect_intent(mode: str, text: str) -> str:
    t = text.lower()

    if mode == "security":
        if has_url(text): return "scan_link"
        if looks_like_email(text): return "scan_email"
        if looks_like_logs(text): return "scan_logs"
        return "security_chat"

    return "chat"
