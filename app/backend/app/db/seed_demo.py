"""
Seed demo data for the application - Retail-realistic scenarios
"""
from datetime import datetime, date, timedelta
from sqlalchemy.orm import Session

from .models import User, ScanEvent, GuardianSnapshot, Conversation, Message
from ..core.security import get_password_hash


def seed_demo_data(db: Session):
    """
    Seed the database with retail-realistic demo data.
    Only works in HACKATHON mode.
    """
    
    # Clear existing data (for fresh demo)
    db.query(Message).delete()
    db.query(Conversation).delete()
    db.query(ScanEvent).delete()
    db.query(GuardianSnapshot).delete()
    db.query(User).delete()
    db.commit()
    
    # Create demo user
    demo_user = User(
        email="demo@sentri-retail.com",
        password_hash=get_password_hash("demo123"),
        full_name="Demo Retail Manager",
        role="retail_manager"
    )
    db.add(demo_user)
    db.commit()
    db.refresh(demo_user)
    
    # Create realistic retail scan events (8-12 events)
    scan_events = [
        # High risk phishing link
        ScanEvent(
            user_id=demo_user.id,
            kind="link",
            input_preview="https://amaz0n-secure-payment.xyz/verify",
            risk_score=92,
            risk_level="high",
            verdict="BLOCK",
            explanation="Detected brand impersonation (amazon typosquat), suspicious TLD (.xyz), and payment verification keyword pattern. This link exhibits multiple phishing characteristics.",
            created_at=datetime.utcnow() - timedelta(hours=2)
        ),
        # Medium risk supplier email
        ScanEvent(
            user_id=demo_user.id,
            kind="email",
            input_preview="From: billing@supp1ier-invoices.com | Subject: URGENT: Invoice #9847 overdue",
            risk_score=68,
            risk_level="medium",
            verdict="REVIEW",
            explanation="Email uses urgency tactics and sender domain contains number substitution (supp1ier). Recommend verifying with known supplier contacts before taking action.",
            created_at=datetime.utcnow() - timedelta(hours=5)
        ),
        # Safe internal link
        ScanEvent(
            user_id=demo_user.id,
            kind="link",
            input_preview="https://corporate.sentri.com/training",
            risk_score=5,
            risk_level="low",
            verdict="ALLOW",
            explanation="Internal corporate domain with valid SSL. No suspicious patterns detected.",
            created_at=datetime.utcnow() - timedelta(hours=8)
        ),
        # High risk credential phishing
        ScanEvent(
            user_id=demo_user.id,
            kind="link",
            input_preview="http://login-retail-portal.tk/auth",
            risk_score=95,
            risk_level="critical",
            verdict="BLOCK",
            explanation="HTTP without encryption, suspicious TLD (.tk), login/credential keywords. High confidence phishing attempt targeting retail credentials.",
            created_at=datetime.utcnow() - timedelta(days=1)
        ),
        # Safe vendor email
        ScanEvent(
            user_id=demo_user.id,
            kind="email",
            input_preview="From: orders@trustedvendor.com | Subject: Order confirmation #45231",
            risk_score=12,
            risk_level="low",
            verdict="ALLOW",
            explanation="Known vendor domain with good reputation. Email content follows standard order confirmation patterns.",
            created_at=datetime.utcnow() - timedelta(days=1, hours=3)
        ),
        # Medium risk log anomaly
        ScanEvent(
            user_id=demo_user.id,
            kind="logs",
            input_preview="[POS-Terminal-7] Multiple failed auth attempts from IP 192.168.1.105",
            risk_score=58,
            risk_level="medium",
            verdict="REVIEW",
            explanation="Multiple authentication failures detected from single IP. Could indicate brute force attempt or user access issues. Recommend monitoring.",
            created_at=datetime.utcnow() - timedelta(days=1, hours=6)
        ),
        # High risk social engineering
        ScanEvent(
            user_id=demo_user.id,
            kind="email",
            input_preview="From: it-support@sentri-helpdesk.net | Subject: Password reset required immediately",
            risk_score=78,
            risk_level="high",
            verdict="BLOCK",
            explanation="Domain impersonates internal IT (sentri-helpdesk.net vs sentri.com). Urgency language and password reset request are social engineering indicators.",
            created_at=datetime.utcnow() - timedelta(days=2)
        ),
        # Safe promotional link
        ScanEvent(
            user_id=demo_user.id,
            kind="link",
            input_preview="https://wholesale.costco.com/business/deals",
            risk_score=8,
            risk_level="low",
            verdict="ALLOW",
            explanation="Legitimate wholesale vendor domain with valid SSL certificate. No suspicious patterns.",
            created_at=datetime.utcnow() - timedelta(days=2, hours=4)
        ),
        # Critical ransomware indicator
        ScanEvent(
            user_id=demo_user.id,
            kind="logs",
            input_preview="[FileServer] Rapid file encryption detected: 847 files modified in 2 minutes",
            risk_score=98,
            risk_level="critical",
            verdict="BLOCK",
            explanation="Pattern matches ransomware behavior - rapid bulk file encryption. IMMEDIATE ACTION REQUIRED: Isolate affected systems.",
            created_at=datetime.utcnow() - timedelta(days=3)
        ),
        # Safe inventory report
        ScanEvent(
            user_id=demo_user.id,
            kind="email",
            input_preview="From: inventory@store-ops.sentri.com | Subject: Weekly stock report",
            risk_score=3,
            risk_level="low",
            verdict="ALLOW",
            explanation="Internal subdomain email with routine operational content. No threats detected.",
            created_at=datetime.utcnow() - timedelta(days=3, hours=5)
        )
    ]
    
    for event in scan_events:
        db.add(event)
    
    # Create Guardian snapshot for today
    guardian_snapshot = GuardianSnapshot(
        date=date.today(),
        protection_level="WATCH",
        items_analyzed=1247,
        high_risk_blocked=23,
        top_threat="Phishing attempts targeting retail credentials",
        summary_text="Elevated phishing activity detected this week. 23 high-risk items blocked including credential harvesting attempts and suspected ransomware indicators. Recommend enhanced email filtering and staff security awareness training."
    )
    db.add(guardian_snapshot)
    
    # Create sample conversation with assistant
    conversation = Conversation(user_id=demo_user.id)
    db.add(conversation)
    db.commit()
    db.refresh(conversation)
    
    messages = [
        Message(
            conversation_id=conversation.id,
            role="user",
            content="What should I do about the phishing emails targeting our store?",
            created_at=datetime.utcnow() - timedelta(hours=1)
        ),
        Message(
            conversation_id=conversation.id,
            role="assistant",
            content="I recommend a multi-layered approach: 1) Enable enhanced email filtering to catch impersonation attempts, 2) Send a security reminder to staff about verifying sender addresses, 3) Implement a vendor verification process for any invoice or payment requests. Would you like me to help draft a staff communication?",
            created_at=datetime.utcnow() - timedelta(hours=1, minutes=1)
        )
    ]
    
    for msg in messages:
        db.add(msg)
    
    db.commit()
    
    return {
        "user_created": demo_user.email,
        "scan_events": len(scan_events),
        "guardian_snapshot": True,
        "conversations": 1
    }
    asyncio.run(seed_demo_data())