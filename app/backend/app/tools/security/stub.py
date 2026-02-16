def security_stub_scan(intent: str, text: str):
    # Replace this with your real scan engines (link/email/logs)
    # This stub keeps the skeleton runnable.
    score = 3
    verdict = "SUSPICIOUS - VERIFY" if score >= 3 else "SAFE"
    return {
        "risk_score": score,
        "risk_level": "LOW" if score <= 3 else "MEDIUM",
        "verdict": verdict,
        "signals": ["Urgency tactics"] if "urgent" in text.lower() else [],
        "explanation": "Hackathon stub scan result.",
        "recommended_actions": ["Verify via official channel", "Do not share credentials"]
    }
