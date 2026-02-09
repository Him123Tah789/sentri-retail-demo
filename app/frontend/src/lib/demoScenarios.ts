import { ScanResult, ScanEvent, GuardianStatus, GuardianSummary, ChatResponse, ScanKind, RiskLevel } from './types';

// Demo scenarios for quick testing
export const demoScenarios = {
  phishingLink: {
    kind: 'link',
    title: 'Phishing Link',
    description: 'Suspicious retail promotion URL',
    input: 'https://amaz0n-deals.malicious-site.com/login?redirect=checkout',
  },
  suspiciousEmail: {
    kind: 'email',
    title: 'Suspicious Email',
    description: 'Fake invoice from unknown vendor',
    input: `From: billing@amaz0n-vendor.com
Subject: URGENT: Invoice #INV-2024-8847 - Payment Required Immediately

Dear Valued Customer,

Your payment of $4,299.99 is overdue. Click here immediately to avoid service suspension:
http://payment-portal.suspicious-domain.net/pay/INV-2024-8847

Please provide your credit card details to process payment.

Regards,
Billing Department`,
  },
  securityLogs: {
    kind: 'logs',
    title: 'Security Logs',
    description: 'POS system failed login attempts',
    input: `2024-01-15 14:23:01 WARN  [AUTH] Failed login attempt for user 'admin' from IP 192.168.1.105
2024-01-15 14:23:15 WARN  [AUTH] Failed login attempt for user 'admin' from IP 192.168.1.105  
2024-01-15 14:23:28 WARN  [AUTH] Failed login attempt for user 'manager' from IP 192.168.1.105
2024-01-15 14:23:45 WARN  [AUTH] Failed login attempt for user 'root' from IP 192.168.1.105
2024-01-15 14:24:02 ERROR [AUTH] Account 'admin' locked after 5 failed attempts
2024-01-15 14:24:15 WARN  [AUTH] Failed login attempt for user 'pos_terminal' from IP 192.168.1.105
2024-01-15 14:24:30 ALERT [SEC] Potential brute force attack detected from IP 192.168.1.105`,
  },
  safeLink: {
    kind: 'link',
    title: 'Safe Link',
    description: 'Legitimate retail website',
    input: 'https://www.amazon.com/dp/B09V3KXJPB',
  },
};

// Generate demo scan result based on input
export function generateDemoScanResult(kind: ScanKind, input: string): ScanResult {
  const now = new Date().toISOString();
  const preview = input.substring(0, 50) + (input.length > 50 ? '...' : '');

  // Check for suspicious patterns
  const suspiciousPatterns = [
    /malicious|phishing|suspicious|fake|amaz0n|paypa1|g00gle/i,
    /urgent|immediately|suspended|locked/i,
    /Failed login|brute force|attack/i,
  ];

  const hasSuspiciousContent = suspiciousPatterns.some((pattern) => pattern.test(input));

  if (hasSuspiciousContent) {
    // High/Critical risk scenarios
    const isCritical = /brute force|attack|malicious/i.test(input);
    return {
      id: Date.now(),
      scanType: kind,
      inputPreview: preview,
      riskScore: isCritical ? 9.2 : 7.5,
      riskLevel: isCritical ? 'critical' : 'high',
      verdict: isCritical ? 'BLOCK IMMEDIATELY' : 'HIGH RISK - AVOID',
      explanation: generateExplanation(kind, input, isCritical ? 'critical' : 'high'),
      recommendedActions: [],
      createdAt: now,
    };
  }

  // Check for medium risk patterns
  const mediumRiskPatterns = [/redirect|external|unknown/i];
  const isMediumRisk = mediumRiskPatterns.some((pattern) => pattern.test(input));

  if (isMediumRisk) {
    return {
      id: Date.now(),
      scanType: kind,
      inputPreview: preview,
      riskScore: 5.2,
      riskLevel: 'medium',
      verdict: 'PROCEED WITH CAUTION',
      explanation: generateExplanation(kind, input, 'medium'),
      recommendedActions: [],
      createdAt: now,
    };
  }

  // Low risk (safe)
  return {
    id: Date.now(),
    scanType: kind,
    inputPreview: preview,
    riskScore: 1.5,
    riskLevel: 'low',
    verdict: 'SAFE TO PROCEED',
    explanation: generateExplanation(kind, input, 'low'),
    recommendedActions: [],
    createdAt: now,
  };
}

function generateExplanation(kind: ScanKind, input: string, riskLevel: RiskLevel): string {
  const explanations: Record<ScanKind, Record<RiskLevel, string>> = {
    link: {
      low: 'This URL appears to be from a legitimate source. The domain is verified and no malicious content was detected. Safe to click.',
      medium: 'This URL contains some unusual parameters or redirects. Verify the destination before entering any sensitive information.',
      high: 'WARNING: This URL shows signs of phishing. The domain mimics a legitimate brand but uses character substitution (e.g., 0 instead of o). Do NOT enter credentials.',
      critical: 'CRITICAL: Known malicious domain detected. This site has been flagged for credential theft and malware distribution. Access blocked.',
    },
    email: {
      low: 'This email appears to be legitimate. Sender reputation is good and content matches expected patterns.',
      medium: 'Email contains some suspicious elements but sender appears valid. Verify any links or attachments before clicking.',
      high: 'This email shows classic phishing indicators: urgency tactics, suspicious sender domain, and requests for sensitive information. Mark as spam.',
      critical: 'CRITICAL: This email is a confirmed phishing attempt. Contains malicious links and fake invoice scam. Delete immediately and report to IT.',
    },
    logs: {
      low: 'Log activity appears normal. No security incidents or anomalies detected in this time period.',
      medium: 'Some unusual activity detected in logs. A few failed authentications but within normal thresholds. Continue monitoring.',
      high: 'Multiple failed login attempts detected suggesting password spraying attack. Consider implementing additional authentication measures.',
      critical: 'CRITICAL: Active brute force attack detected. Multiple failed logins across different accounts from same IP. Block IP immediately and review compromised accounts.',
    },
    text: {
      low: 'Content analysis complete. No security concerns identified.',
      medium: 'Some potentially sensitive information detected. Review before sharing.',
      high: 'Content contains suspicious patterns that may indicate social engineering or fraud.',
      critical: 'Critical security threat detected in content. Do not proceed.',
    },
  };

  return explanations[kind][riskLevel];
}

// Generate demo Guardian status
export function generateDemoGuardianStatus(): GuardianStatus {
  return {
    protectionLevel: 'ACTIVE',
    lastUpdated: new Date().toISOString(),
    systemsProtected: 24,
    activeAlerts: 3,
  };
}

// Generate demo Guardian summary
export function generateDemoGuardianSummary(): GuardianSummary {
  return {
    id: 1,
    date: new Date().toISOString().split('T')[0],
    protectionLevel: 'ACTIVE',
    itemsAnalyzed: 1247,
    highRiskBlocked: 23,
    topThreat: 'Phishing campaign targeting retail staff credentials detected and blocked',
    summaryText: `Today's security posture remains strong. Guardian analyzed 1,247 items across your retail network, blocking 23 high-risk threats before they could reach employees. The most significant threat was a coordinated phishing campaign mimicking vendor invoices. All POS systems are secure and operating normally. Recommended action: remind staff about verifying unexpected invoice emails.`,
  };
}

// Generate demo recent scans
export function generateDemoRecentScans(limit: number): ScanEvent[] {
  const scans: ScanEvent[] = [
    {
      id: 1,
      userId: 1,
      kind: 'link',
      inputPreview: 'https://amaz0n-deals.fake-site.com...',
      riskScore: 8.7,
      riskLevel: 'high',
      verdict: 'HIGH RISK - AVOID',
      explanation: 'Phishing site detected',
      createdAt: new Date(Date.now() - 1000 * 60 * 5).toISOString(),
    },
    {
      id: 2,
      userId: 1,
      kind: 'email',
      inputPreview: 'From: billing@suspicious-vendor...',
      riskScore: 9.1,
      riskLevel: 'critical',
      verdict: 'BLOCK IMMEDIATELY',
      explanation: 'Invoice phishing scam',
      createdAt: new Date(Date.now() - 1000 * 60 * 15).toISOString(),
    },
    {
      id: 3,
      userId: 2,
      kind: 'link',
      inputPreview: 'https://www.amazon.com/dp/B09V3...',
      riskScore: 1.2,
      riskLevel: 'low',
      verdict: 'SAFE TO PROCEED',
      explanation: 'Legitimate retailer',
      createdAt: new Date(Date.now() - 1000 * 60 * 30).toISOString(),
    },
    {
      id: 4,
      userId: 1,
      kind: 'logs',
      inputPreview: '2024-01-15 Failed login attempts...',
      riskScore: 7.8,
      riskLevel: 'high',
      verdict: 'INVESTIGATE',
      explanation: 'Brute force attempt detected',
      createdAt: new Date(Date.now() - 1000 * 60 * 45).toISOString(),
    },
    {
      id: 5,
      userId: 2,
      kind: 'email',
      inputPreview: 'From: support@microsoft.com...',
      riskScore: 2.1,
      riskLevel: 'low',
      verdict: 'SAFE TO PROCEED',
      explanation: 'Legitimate support email',
      createdAt: new Date(Date.now() - 1000 * 60 * 60).toISOString(),
    },
    {
      id: 6,
      userId: 1,
      kind: 'link',
      inputPreview: 'https://retailportal.company.com...',
      riskScore: 1.0,
      riskLevel: 'low',
      verdict: 'SAFE TO PROCEED',
      explanation: 'Internal company portal',
      createdAt: new Date(Date.now() - 1000 * 60 * 90).toISOString(),
    },
    {
      id: 7,
      userId: 3,
      kind: 'email',
      inputPreview: 'From: rewards@target-promo.net...',
      riskScore: 6.5,
      riskLevel: 'medium',
      verdict: 'PROCEED WITH CAUTION',
      explanation: 'Unverified promotion email',
      createdAt: new Date(Date.now() - 1000 * 60 * 120).toISOString(),
    },
  ];

  return scans.slice(0, limit);
}

// Generate demo chat response
export function generateDemoChatResponse(message: string): ChatResponse {
  const lowerMessage = message.toLowerCase();

  // Pattern matching for different types of questions
  if (lowerMessage.includes('phishing') || lowerMessage.includes('suspicious')) {
    return {
      conversation_id: 1001,
      reply: `Great question about phishing! Here are key indicators to watch for in retail environments:

**Red Flags:**
• Urgent language demanding immediate action
• Sender email doesn't match the company domain
• Links with misspelled brand names (amaz0n, paypa1)
• Requests for credentials or payment info
• Unexpected invoices or shipping notifications

**Best Practices:**
1. Always verify sender addresses carefully
2. Hover over links before clicking to preview URLs
3. When in doubt, access accounts directly via official websites
4. Report suspicious emails to IT immediately

Would you like me to scan a specific email or link for you?`,
    };
  }

  if (lowerMessage.includes('password') || lowerMessage.includes('login')) {
    return {
      conversation_id: 1001,
      reply: `Here are security best practices for authentication in retail systems:

**Password Guidelines:**
• Minimum 12 characters with mixed case, numbers, and symbols
• Never reuse passwords across systems
• Change passwords every 90 days
• Never share credentials, even with managers

**Suspicious Login Activity:**
If you notice failed login attempts or account lockouts:
1. Report to IT security immediately
2. Check recent access logs
3. Verify no unauthorized changes were made
4. Consider enabling MFA if not already active

The Guardian engine monitors all login attempts across your retail network and will alert on anomalies.`,
    };
  }

  if (lowerMessage.includes('report') || lowerMessage.includes('incident')) {
    return {
      conversation_id: 1001,
      reply: `To report a security incident:

**Immediate Steps:**
1. Don't click any suspicious links
2. Don't delete the suspicious content yet
3. Take a screenshot if possible
4. Note the time and any details

**Reporting Channels:**
• Use the scan feature above to analyze links/emails
• Forward suspicious emails to security@company.com
• Call IT hotline for urgent matters
• Log incident in the security portal

**What happens next:**
Our security team reviews all reports within 4 hours. Critical threats trigger immediate response. You'll receive follow-up guidance within 24 hours.`,
    };
  }

  if (lowerMessage.includes('pos') || lowerMessage.includes('terminal') || lowerMessage.includes('payment')) {
    return {
      conversation_id: 1001,
      reply: `POS and payment terminal security is critical for retail operations:

**Daily Security Checks:**
• Inspect terminals for tampering devices (skimmers)
• Verify secure network connection indicator
• Check for unauthorized USB devices
• Report any physical damage immediately

**Payment Security:**
• Never key in card numbers manually unless necessary
• Verify chip reader is functioning
• Watch for card switching attempts
• Process refunds only through authorized channels

**Current Guardian Status:**
All 24 POS terminals are secure and operating normally. Last security scan: 15 minutes ago.`,
    };
  }

  // Default response
  return {
    conversation_id: 1001,
    reply: `I'm your Sentri AI security assistant, here to help protect your retail operations. I can help you:

**Security Scanning:**
• Analyze suspicious links before clicking
• Check emails for phishing indicators
• Review security logs for threats

**Security Guidance:**
• Best practices for password security
• How to identify social engineering
• POS terminal security protocols
• Incident reporting procedures

**Dashboard Insights:**
• Real-time threat monitoring
• Daily security summaries
• Risk trend analysis

How can I assist you today? You can also use the action buttons to scan a specific link, email, or log file.`,
  };
}
