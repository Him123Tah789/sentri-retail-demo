import random
import time

def security_stub_scan(intent: str, text: str):
    t0 = time.time()
    
    # 1. Detection Logic (Mock signals)
    signals = []
    text_lower = text.lower()
    
    # Phishing signals
    if any(x in text_lower for x in ["urgent", "immediately", "account suspended", "verify now"]):
        signals.append("Urgency tactics detected")
    if "http" in text_lower or "www" in text_lower:
        signals.append("Contains external link")
    if any(x in text_lower for x in ["password", "credential", "login"]):
        signals.append("Credential harvesting keywords")
    if "payment" in text_lower or "invoice" in text_lower:
        signals.append("Financial request")

    # 2. Correlation Engine logic
    # "One alert is noise. Multiple agreeing signals is intelligence."
    base_score = 0.0
    if len(signals) == 0:
        base_score = 1.0
    elif len(signals) == 1:
        base_score = 3.5
    elif len(signals) == 2:
        base_score = 6.0
    else:
        base_score = 8.5 + (len(signals) * 0.2)

    # 3. False Positive Control (Safe / Suspicious / Malicious)
    # Tristate verdict logic
    if base_score < 3.0:
        verdict = "SAFE"
        risk_level = "LOW"
    elif base_score < 7.0:
        verdict = "SUSPICIOUS"
        risk_level = "MEDIUM"
    else:
        verdict = "MALICIOUS"
        risk_level = "HIGH"

    # Correlation Status
    correlation = "LOW"
    if len(signals) >= 3:
        correlation = "HIGH"
    elif len(signals) >= 1:
        correlation = "MEDIUM"

    # 4. Evidence Object
    score_final = min(10.0, round(base_score + random.uniform(-0.5, 0.5), 1))
    latency = int((time.time() - t0) * 1000) + random.randint(20, 150) # Simulated ml latency

    evidence = {
        "risk_score": score_final,
        "confidence": round(random.uniform(0.85, 0.99), 2),
        "top_signals": signals[:3],
        "model_version": "sentri_nlp_v4.2.0-HK",
        "latency_ms": latency,
        "threat_correlation": correlation
    }

    return {
        "risk_score": score_final,
        "risk_level": risk_level,
        "verdict": verdict,
        "signals": signals,
        "explanation": f"Analysis based on {len(signals)} detected persistence vectors. Correlation level: {correlation}.",
        "recommended_actions": [
            "Verify sender identity out-of-band" if verdict != "SAFE" else "No action needed",
            "Do not click links" if "link" in str(signals) else None,
            "Flag as false positive to improve model" if verdict == "SUSPICIOUS" else None
        ],
        "evidence": evidence
    }
