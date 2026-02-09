/**
 * Sentri History & Memory Store
 * Real-time data storage for scans and chat history
 * 
 * Risk Score Scale (1-10):
 * - 1-2: Safe (Low risk) - Green
 * - 3-4: Caution (Medium risk) - Yellow
 * - 5-7: High Risk - Orange
 * - 8-10: Critical/Block - Red
 */

import { ScanResult, ScanEvent, GuardianStatus, GuardianSummary, ChatResponse, ScanKind, RiskLevel, Message } from './types';

// ============================================================
// HISTORY STORES - In-Memory Storage
// ============================================================

export interface StoredScan {
  id: number;
  userId: number;
  kind: ScanKind;
  input: string;
  inputPreview: string;
  riskScore: number;
  riskLevel: RiskLevel;
  verdict: string;
  explanation: string;
  recommendedActions: string[];
  createdAt: string;
}

export interface StoredChatMessage {
  id: string;
  conversationId: number;
  role: 'user' | 'assistant' | 'system';
  content: string;
  toolUsed?: string;
  scanResult?: StoredScan;
  createdAt: string;
}

export interface ConversationHistory {
  id: number;
  userId: number;
  messages: StoredChatMessage[];
  createdAt: string;
  updatedAt: string;
}

// ============================================================
// GLOBAL MEMORY STORES
// ============================================================

class ScanHistoryStore {
  private scans: StoredScan[] = [];
  private nextId = 1;

  add(scan: Omit<StoredScan, 'id' | 'createdAt'>): StoredScan {
    const newScan: StoredScan = {
      ...scan,
      id: this.nextId++,
      createdAt: new Date().toISOString(),
    };
    this.scans.unshift(newScan);
    if (this.scans.length > 100) {
      this.scans = this.scans.slice(0, 100);
    }
    return newScan;
  }

  getAll(): StoredScan[] { return [...this.scans]; }
  getByUserId(userId: number): StoredScan[] { return this.scans.filter(s => s.userId === userId); }
  getRecent(limit: number = 10): StoredScan[] { return this.scans.slice(0, limit); }
  getById(id: number): StoredScan | undefined { return this.scans.find(s => s.id === id); }
  getByRiskLevel(level: RiskLevel): StoredScan[] { return this.scans.filter(s => s.riskLevel === level); }
  getHighRiskScans(): StoredScan[] { return this.scans.filter(s => s.riskScore >= 7); }
  getCriticalScans(): StoredScan[] { return this.scans.filter(s => s.riskScore >= 8); }

  getStats() {
    const total = this.scans.length;
    const byLevel = {
      low: this.scans.filter(s => s.riskLevel === 'low').length,
      medium: this.scans.filter(s => s.riskLevel === 'medium').length,
      high: this.scans.filter(s => s.riskLevel === 'high').length,
      critical: this.scans.filter(s => s.riskLevel === 'critical').length,
    };
    const byKind = {
      link: this.scans.filter(s => s.kind === 'link').length,
      email: this.scans.filter(s => s.kind === 'email').length,
      logs: this.scans.filter(s => s.kind === 'logs').length,
      text: this.scans.filter(s => s.kind === 'text').length,
    };
    const avgRiskScore = total > 0 ? this.scans.reduce((sum, s) => sum + s.riskScore, 0) / total : 0;
    return { total, byLevel, byKind, avgRiskScore: Math.round(avgRiskScore * 10) / 10 };
  }
  clear() { this.scans = []; this.nextId = 1; }
}

class ChatHistoryStore {
  private conversations: Map<number, ConversationHistory> = new Map();
  private nextConversationId = 1;
  private nextMessageId = 1;

  getOrCreateConversation(userId: number): ConversationHistory {
    const existing = Array.from(this.conversations.values()).find(conv => conv.userId === userId);
    if (existing) return existing;
    const newConv: ConversationHistory = {
      id: this.nextConversationId++,
      userId,
      messages: [],
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString(),
    };
    this.conversations.set(newConv.id, newConv);
    return newConv;
  }

  addMessage(conversationId: number, role: 'user' | 'assistant' | 'system', content: string, toolUsed?: string, scanResult?: StoredScan): StoredChatMessage {
    const conv = this.conversations.get(conversationId);
    if (!conv) throw new Error(`Conversation ${conversationId} not found`);
    const message: StoredChatMessage = {
      id: `msg_${this.nextMessageId++}`,
      conversationId,
      role,
      content,
      toolUsed,
      scanResult,
      createdAt: new Date().toISOString(),
    };
    conv.messages.push(message);
    conv.updatedAt = new Date().toISOString();
    if (conv.messages.length > 50) conv.messages = conv.messages.slice(-50);
    return message;
  }

  getMessages(conversationId: number): StoredChatMessage[] {
    const conv = this.conversations.get(conversationId);
    return conv ? [...conv.messages] : [];
  }
  getRecentMessages(conversationId: number, limit: number = 10): StoredChatMessage[] {
    return this.getMessages(conversationId).slice(-limit);
  }
  getAllConversations(): ConversationHistory[] { return Array.from(this.conversations.values()); }
  getConversationByUserId(userId: number): ConversationHistory | undefined {
    return Array.from(this.conversations.values()).find(conv => conv.userId === userId);
  }
  clear() { this.conversations.clear(); this.nextConversationId = 1; this.nextMessageId = 1; }
}

// Global store instances
export const scanHistory = new ScanHistoryStore();
export const chatHistory = new ChatHistoryStore();

// ============================================================
// RISK SCORE UTILITIES (1-10 Scale)
// ============================================================

export function getRiskLevelFromScore(score: number): RiskLevel {
  if (score <= 2) return 'low';
  if (score <= 4) return 'medium';
  if (score <= 7) return 'high';
  return 'critical';
}

export function getVerdictFromScore(score: number): string {
  if (score <= 2) return '✅ SAFE - No Risk Detected';
  if (score <= 4) return '⚠️ CAUTION - Review Recommended';
  if (score <= 7) return '🚨 HIGH RISK - Avoid';
  return '🛑 BLOCK - Critical Threat';
}

export function getRiskColor(score: number): string {
  if (score <= 2) return '#22c55e';
  if (score <= 4) return '#eab308';
  if (score <= 7) return '#f97316';
  return '#ef4444';
}

export function getRiskBadgeClass(score: number): string {
  if (score <= 2) return 'bg-green-100 text-green-700';
  if (score <= 4) return 'bg-yellow-100 text-yellow-700';
  if (score <= 7) return 'bg-orange-100 text-orange-700';
  return 'bg-red-100 text-red-700';
}

// ============================================================
// DEMO SCENARIOS
// ============================================================

export const demoScenarios = {
  phishingLink: {
    kind: 'link' as ScanKind,
    title: 'Phishing Link',
    description: 'Suspicious retail promotion URL',
    input: 'https://amaz0n-deals.malicious-site.com/login?redirect=checkout',
  },
  suspiciousEmail: {
    kind: 'email' as ScanKind,
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
    kind: 'logs' as ScanKind,
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
    kind: 'link' as ScanKind,
    title: 'Safe Link',
    description: 'Legitimate retail website',
    input: 'https://www.amazon.com/dp/B09V3KXJPB',
  },
};

// ============================================================
// THREAT ANALYSIS ENGINE
// ============================================================

interface ThreatIndicator {
  pattern: RegExp;
  weight: number;
  description: string;
}

const linkThreatIndicators: ThreatIndicator[] = [
  { pattern: /amaz0n|amazom|amazon-/i, weight: 3, description: 'Brand typosquatting detected' },
  { pattern: /paypa1|paypal-|pay-pal/i, weight: 3, description: 'PayPal impersonation' },
  { pattern: /g00gle|googl3|google-/i, weight: 3, description: 'Google impersonation' },
  { pattern: /malicious|phishing|scam/i, weight: 4, description: 'Known malicious domain' },
  { pattern: /verify.*account|account.*verify/i, weight: 2, description: 'Account verification phishing' },
  { pattern: /login.*redirect|redirect.*login/i, weight: 2, description: 'Suspicious redirect' },
  { pattern: /\.(xyz|tk|ml|ga|cf|gq)$/i, weight: 2, description: 'High-risk TLD' },
  { pattern: /bit\.ly|tinyurl|t\.co/i, weight: 1, description: 'URL shortener' },
  { pattern: /[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}/i, weight: 2, description: 'IP address instead of domain' },
];

const emailThreatIndicators: ThreatIndicator[] = [
  { pattern: /urgent|immediately|suspended|locked/i, weight: 2, description: 'Urgency tactics' },
  { pattern: /click here|click below|click now/i, weight: 1, description: 'Suspicious call-to-action' },
  { pattern: /credit card|bank account|social security/i, weight: 3, description: 'Requests financial info' },
  { pattern: /password|credentials|login details/i, weight: 2, description: 'Requests credentials' },
  { pattern: /invoice.*overdue|payment.*required/i, weight: 2, description: 'Fake invoice scam' },
  { pattern: /verify.*account|confirm.*identity/i, weight: 2, description: 'Account verification phishing' },
  { pattern: /suspicious-domain|fake-site|malicious/i, weight: 4, description: 'Known malicious sender' },
  { pattern: /lottery|winner|prize|congratulations/i, weight: 3, description: 'Lottery/prize scam' },
  { pattern: /wire transfer|western union|moneygram/i, weight: 3, description: 'Wire transfer scam' },
];

const logsThreatIndicators: ThreatIndicator[] = [
  { pattern: /failed login|invalid password|authentication failed/i, weight: 1, description: 'Failed login attempt' },
  { pattern: /brute force|attack detected|security alert/i, weight: 4, description: 'Attack detected' },
  { pattern: /account locked|blocked|suspended/i, weight: 2, description: 'Account lockout' },
  { pattern: /unauthorized access|privilege escalation/i, weight: 4, description: 'Unauthorized access' },
  { pattern: /sql injection|xss|script injection/i, weight: 4, description: 'Code injection attempt' },
  { pattern: /multiple.*failed|repeated.*attempt/i, weight: 2, description: 'Repeated failures' },
  { pattern: /root|admin|administrator/i, weight: 1, description: 'Privileged account targeted' },
];

function calculateRiskScore(kind: ScanKind, input: string): { score: number; indicators: string[] } {
  let indicators: ThreatIndicator[] = [];
  switch (kind) {
    case 'link': indicators = linkThreatIndicators; break;
    case 'email': indicators = emailThreatIndicators; break;
    case 'logs': indicators = logsThreatIndicators; break;
  }
  let score = 1;
  const matchedIndicators: string[] = [];
  for (const indicator of indicators) {
    if (indicator.pattern.test(input)) {
      score += indicator.weight;
      matchedIndicators.push(indicator.description);
    }
  }
  return { score: Math.min(score, 10), indicators: matchedIndicators };
}

function generateExplanation(kind: ScanKind, indicators: string[], score: number): string {
  if (indicators.length === 0) {
    const safeMessages: Record<ScanKind, string> = {
      link: 'This URL appears legitimate. No suspicious patterns detected. Safe to proceed.',
      email: 'This email appears legitimate. No phishing indicators detected.',
      logs: 'Log activity appears normal. No security anomalies detected.',
      text: 'Content analysis complete. No security concerns identified.',
    };
    return safeMessages[kind];
  }
  const severity = score >= 8 ? 'CRITICAL' : score >= 5 ? 'WARNING' : 'NOTICE';
  const indicatorList = indicators.map(i => `• ${i}`).join('\n');
  return `**${severity}** - ${indicators.length} threat indicator(s) detected:\n\n${indicatorList}\n\n**Risk Score: ${score}/10**`;
}

function getRecommendedActions(score: number, kind: ScanKind): string[] {
  if (score <= 2) return ['Safe to proceed', 'No action required'];
  if (score <= 4) return ['Verify source before proceeding', 'Exercise caution', 'Report if unusual'];
  if (score <= 7) {
    const actions = ['Do NOT proceed', 'Report to IT security'];
    if (kind === 'link') actions.push('Do NOT click this link');
    if (kind === 'email') actions.push('Mark as spam and delete');
    if (kind === 'logs') actions.push('Investigate source IP');
    return actions;
  }
  return ['🛑 BLOCK IMMEDIATELY', 'Report to IT security NOW', 'Do NOT interact', 'Document for incident report'];
}

// ============================================================
// MAIN SCAN FUNCTION - STORES TO HISTORY
// ============================================================

export function generateDemoScanResult(kind: ScanKind, input: string, userId: number = 1): ScanResult {
  const { score, indicators } = calculateRiskScore(kind, input);
  const riskLevel = getRiskLevelFromScore(score);
  const verdict = getVerdictFromScore(score);
  const explanation = generateExplanation(kind, indicators, score);
  const recommendedActions = getRecommendedActions(score, kind);
  const preview = input.substring(0, 50) + (input.length > 50 ? '...' : '');

  const storedScan = scanHistory.add({
    userId,
    kind,
    input,
    inputPreview: preview,
    riskScore: score,
    riskLevel,
    verdict,
    explanation,
    recommendedActions,
  });

  return {
    id: storedScan.id,
    scanType: kind,
    inputPreview: preview,
    riskScore: score,
    riskLevel,
    verdict,
    explanation,
    recommendedActions,
    createdAt: storedScan.createdAt,
  };
}

// ============================================================
// GUARDIAN STATUS & SUMMARY
// ============================================================

export function generateDemoGuardianStatus(): GuardianStatus {
  const stats = scanHistory.getStats();
  const activeAlerts = stats.byLevel.high + stats.byLevel.critical;
  let protectionLevel: 'ACTIVE' | 'WATCH' | 'WARNING' = 'ACTIVE';
  if (activeAlerts >= 5) protectionLevel = 'WARNING';
  else if (activeAlerts >= 2) protectionLevel = 'WATCH';

  return {
    protectionLevel,
    lastUpdated: new Date().toISOString(),
    systemsProtected: 24,
    activeAlerts,
  };
}

export function generateDemoGuardianSummary(): GuardianSummary {
  const stats = scanHistory.getStats();
  const recentScans = scanHistory.getRecent(5);
  const topThreat = recentScans.find(s => s.riskScore >= 7);
  const topThreatText = topThreat ? `${topThreat.kind.toUpperCase()}: ${topThreat.verdict}` : null;
  
  let protectionLevel: 'ACTIVE' | 'WATCH' | 'WARNING' = 'ACTIVE';
  if (stats.byLevel.critical > 0) protectionLevel = 'WARNING';
  else if (stats.byLevel.high > 0) protectionLevel = 'WATCH';

  const summaryText = `Security analysis: ${stats.total} items scanned. ` +
    `${stats.byLevel.high + stats.byLevel.critical} high-risk threats flagged. ` +
    `Average risk score: ${stats.avgRiskScore}/10. ` +
    (topThreat ? `Latest critical: ${topThreat.inputPreview}` : 'No critical threats.');

  return {
    id: 1,
    date: new Date().toISOString().split('T')[0],
    protectionLevel,
    itemsAnalyzed: stats.total,
    highRiskBlocked: stats.byLevel.high + stats.byLevel.critical,
    topThreat: topThreatText,
    summaryText,
  };
}

// ============================================================
// GET RECENT SCANS FROM HISTORY
// ============================================================

export function generateDemoRecentScans(limit: number): ScanEvent[] {
  const scans = scanHistory.getRecent(limit);
  return scans.map(scan => ({
    id: scan.id,
    userId: scan.userId,
    kind: scan.kind,
    inputPreview: scan.inputPreview,
    riskScore: scan.riskScore,
    riskLevel: scan.riskLevel,
    verdict: scan.verdict,
    explanation: scan.explanation,
    createdAt: scan.createdAt,
  }));
}

// ============================================================
// CHAT RESPONSE WITH HISTORY
// ============================================================

export function generateDemoChatResponse(message: string, userId: number = 1): ChatResponse {
  const lowerMessage = message.toLowerCase();
  const conversation = chatHistory.getOrCreateConversation(userId);
  chatHistory.addMessage(conversation.id, 'user', message);

  let reply: string;
  let toolUsed: 'scan_link' | 'scan_email' | 'scan_logs' | 'none' = 'none';

  if (lowerMessage.includes('phishing') || lowerMessage.includes('suspicious')) {
    reply = `Great question about phishing! Here's the risk score guide:

**Risk Score Scale (1-10):**
• 1-2: ✅ Safe - No threats
• 3-4: ⚠️ Caution - Review needed
• 5-7: 🚨 High Risk - Avoid
• 8-10: 🛑 BLOCK - Critical threat

**Common Phishing Red Flags:**
• Urgent language demanding action
• Misspelled brand names (amaz0n, paypa1)
• Requests for credentials/payment

Use the scan buttons to analyze suspicious content!`;
  }
  else if (lowerMessage.includes('password') || lowerMessage.includes('login')) {
    reply = `Authentication security best practices:

**Password Guidelines:**
• Minimum 12 characters
• Mix of upper/lower/numbers/symbols
• Never reuse passwords

**Log Analysis Risk Scores:**
• Few failed logins = Score 2-4
• Multiple failures = Score 5-7
• Brute force pattern = Score 8-10

Use the Logs scan to analyze security events.`;
  }
  else if (lowerMessage.includes('history') || lowerMessage.includes('recent')) {
    const stats = scanHistory.getStats();
    const recent = scanHistory.getRecent(3);
    const recentList = recent.map(s => `• ${s.kind}: Score ${s.riskScore}/10 - ${s.verdict}`).join('\n');

    reply = `**📊 Scan History Summary:**

Total Scans: ${stats.total}
Avg Risk Score: ${stats.avgRiskScore}/10

**By Risk Level:**
• Safe (1-2): ${stats.byLevel.low}
• Caution (3-4): ${stats.byLevel.medium}
• High Risk (5-7): ${stats.byLevel.high}
• Critical (8-10): ${stats.byLevel.critical}

**Recent Scans:**
${recentList || 'No scans yet - try scanning a link!'}`;
  }
  else if (lowerMessage.includes('score') || lowerMessage.includes('risk')) {
    reply = `**Sentri Risk Score Guide (1-10):**

🟢 **1-2: SAFE** - No threats detected
🟡 **3-4: CAUTION** - Minor concerns  
🟠 **5-7: HIGH RISK** - Avoid interaction
🔴 **8-10: BLOCK** - Critical threat

**Quick Actions:**
• Scan Link → Phishing detection
• Scan Email → Social engineering
• Scan Logs → Attack patterns`;
  }
  else if (lowerMessage.includes('report') || lowerMessage.includes('incident')) {
    reply = `**Security Incident Reporting:**

**Risk-Based Response:**
• Score 1-4: Log for reference
• Score 5-7: Escalate to IT (24h)
• Score 8-10: URGENT - Report NOW

**Steps:**
1. Don't click suspicious content
2. Screenshot the issue
3. Use scan feature to analyze
4. Report based on risk score

All scans are automatically stored in history.`;
  }
  else {
    const stats = scanHistory.getStats();
    reply = `I'm your Sentri AI security assistant!

**What I can do:**
• 🔗 Scan links for phishing
• 📧 Check emails for threats
• 📋 Analyze security logs

**Current Stats:**
• Total Scans: ${stats.total}
• High Risk Found: ${stats.byLevel.high + stats.byLevel.critical}

**Risk Score Scale:**
1-2 = Safe | 3-4 = Caution | 5-7 = High | 8-10 = Block

How can I help you today?`;
  }

  chatHistory.addMessage(conversation.id, 'assistant', reply, toolUsed);
  return { conversation_id: conversation.id, reply, tool_used: toolUsed };
}

// ============================================================
// UTILITY FUNCTIONS
// ============================================================

export function getScanHistory() { return scanHistory.getAll(); }
export function getScanStats() { return scanHistory.getStats(); }
export function getChatHistory(userId: number) {
  const conv = chatHistory.getConversationByUserId(userId);
  return conv ? conv.messages : [];
}
export function clearAllHistory() { scanHistory.clear(); chatHistory.clear(); }

// Initialize with demo data
export function initializeDemoData() {
  generateDemoScanResult('link', 'https://amaz0n-deals.fake-site.com/login', 1);
  generateDemoScanResult('email', 'From: billing@suspicious-vendor.com - URGENT Payment', 1);
  generateDemoScanResult('link', 'https://www.amazon.com/dp/B09V3KXJPB', 2);
  generateDemoScanResult('logs', 'Failed login attempt for admin from IP 192.168.1.105', 1);
}
