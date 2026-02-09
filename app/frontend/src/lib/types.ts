// Type definitions for Sentri Retail Demo

export type ScanKind = 'link' | 'email' | 'logs' | 'text';

export type RiskLevel = 'low' | 'medium' | 'high' | 'critical';

export type ProtectionLevel = 'ACTIVE' | 'WATCH' | 'WARNING';

export interface User {
  id: number;
  email: string;
  fullName: string;
  role: 'staff' | 'hq_it' | 'admin';
}

export interface AuthResponse {
  accessToken: string;
  tokenType: string;
  user: User;
}

export interface Message {
  id: string;
  role: 'user' | 'assistant' | 'system';
  content: string;
  createdAt: string;
}

export interface Conversation {
  id: number;
  userId: number;
  createdAt: string;
  messages: Message[];
}

export interface ScanResult {
  id: number;
  scanType: string;
  inputPreview: string;
  riskScore: number;
  riskLevel: 'low' | 'medium' | 'high' | 'critical';
  verdict: string;
  explanation: string;
  recommendedActions: string[];
  createdAt: string;
}

export interface ScanEvent {
  id: number;
  userId: number;
  kind: ScanKind;
  inputPreview: string;
  riskScore: number;
  riskLevel: RiskLevel;
  verdict: string;
  explanation: string;
  createdAt: string;
}

export interface GuardianStatus {
  protectionLevel: ProtectionLevel;
  lastUpdated: string;
  systemsProtected: number;
  activeAlerts: number;
}

export interface GuardianSummary {
  id: number;
  date: string;
  protectionLevel: ProtectionLevel;
  itemsAnalyzed: number;
  highRiskBlocked: number;
  topThreat: string | null;
  summaryText: string;
}

export interface ApiError {
  detail: string;
  code?: string;
}

// Tool types for hybrid chat + tools system
export type ToolUsed = 'scan_link' | 'scan_email' | 'scan_logs' | 'none';

export interface RiskSummary {
  level: string;  // HIGH, MEDIUM, LOW
  score: number;  // 0-100
  verdict: string;
  action_required: boolean;
}

export interface ChatScanResult {
  kind: string;
  input_preview: string;
  risk_score: number;
  risk_level: string;
  verdict: string;
  explanation: string;
  recommended_actions: string[];
}

export interface ChatResponse {
  conversation_id: number;
  reply: string;
  tool_used: ToolUsed;
  risk_summary?: RiskSummary;
  scan_result?: ChatScanResult;
  scan_type?: string;
}
