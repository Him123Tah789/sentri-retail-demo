// ─── Types for Sentri Hackathon ───

export type Mode = 'security' | 'automotive';

// Chat
export interface Message {
  id: string;
  role: 'user' | 'assistant' | 'system';
  content: string;
  createdAt: string;
}

export interface ChatRequest {
  conversation_id?: string;
  mode: Mode;
  message: string;
  context?: Record<string, unknown>;
}

export interface ChatResponse {
  conversation_id: string;
  mode: Mode;
  intent: string;
  reply: string;
  tool_result?: Record<string, unknown>;
}

// Automotive
export type FuelType = 'petrol' | 'diesel' | 'hybrid' | 'ev';

export interface VehicleNormalized {
  vehicle_id: string;
  make: string;
  model: string;
  year: number;
  fuel_type: FuelType;
  msrp: number;
  efficiency_value: number;
  efficiency_unit: 'L_PER_100KM' | 'KWH_PER_100KM';
  notes?: string;
}

export interface TcoAssumptions {
  purchase_price: number;
  down_payment?: number;
  interest_rate_apr?: number;
  loan_term_months?: number;
  annual_km?: number;
  fuel_price_per_liter?: number;
  electricity_price_per_kwh?: number;
  insurance_per_year?: number;
  tax_per_year?: number;
  maintenance_per_year?: number;
  fees_one_time?: number;
  tires_cost_per_set?: number;
  tires_replace_km?: number;
  years?: number;
}

export interface TcoBreakdown {
  depreciation: number;
  financing: number;
  fuel_or_energy: number;
  insurance: number;
  tax: number;
  maintenance: number;
  tires: number;
  fees: number;
}

export interface TcoResult {
  total: number;
  per_year: number;
  per_month: number;
  breakdown: TcoBreakdown;
  assumptions: TcoAssumptions;
}

export interface SensitivityPoint {
  x: number;
  total: number;
  per_month: number;
}

export interface SensitivityResult {
  slider: string;
  points: SensitivityPoint[];
}

// Security
// Security
export interface Evidence {
  risk_score: number;
  confidence: number;
  top_signals: string[];
  model_version: string;
  latency_ms: number;
  threat_correlation?: string;
}

export interface SecurityScanResult {
  risk_score: number;
  risk_level: string;
  verdict: string;
  explanation: string;
  signals: string[];
  recommended_actions: string[];
  evidence?: Evidence;
}

export interface ApiError {
  detail: string;
  code?: string;
}

// Dashboard & History Types
export type ScanKind = 'link' | 'email' | 'logs' | 'text';
export type RiskLevel = 'low' | 'medium' | 'high' | 'critical';

export interface ScanResult {
  id: number;
  scanType: ScanKind;
  inputPreview: string;
  riskScore: number;
  riskLevel: RiskLevel;
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
  protectionLevel: 'ACTIVE' | 'WATCH' | 'WARNING';
  lastUpdated: string;
  systemsProtected: number;
  activeAlerts: number;
}

export interface GuardianSummary {
  id: number;
  date: string;
  protectionLevel: 'ACTIVE' | 'WATCH' | 'WARNING';
  itemsAnalyzed: number;
  highRiskBlocked: number;
  topThreat: string | null;
  summaryText: string;
}

export interface User {
  id: number;
  email: string;
  fullName: string;
  role: 'admin' | 'staff' | 'analyst' | 'hq_it';
}

export interface AuthResponse {
  accessToken: string;
  tokenType: string;
  user: User;
}
