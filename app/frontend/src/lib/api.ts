import { getAuthHeaders } from './auth';
import { ScanResult, GuardianStatus, GuardianSummary, ScanEvent, ChatResponse } from './types';
import { generateDemoScanResult, generateDemoGuardianStatus, generateDemoGuardianSummary, generateDemoRecentScans, generateDemoChatResponse } from './demoScenarios';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8003';
const API_PREFIX = '/api/v1';

// Map backend snake_case response to frontend camelCase
function mapScanResult(data: Record<string, unknown>): ScanResult {
  return {
    id: data.id as number,
    scanType: (data.scan_type || data.scanType) as string,
    inputPreview: (data.input_preview || data.inputPreview) as string,
    riskScore: (data.risk_score ?? data.riskScore) as number,
    riskLevel: (data.risk_level || data.riskLevel) as 'low' | 'medium' | 'high' | 'critical',
    verdict: data.verdict as string,
    explanation: data.explanation as string,
    recommendedActions: (data.recommended_actions || data.recommendedActions || []) as string[],
    createdAt: (data.created_at || data.createdAt) as string,
  };
}

async function apiRequest<T>(endpoint: string, options: RequestInit = {}): Promise<T> {
  const headers = {
    'Content-Type': 'application/json',
    ...getAuthHeaders(),
    ...options.headers,
  };

  try {
    const response = await fetch(`${API_URL}${API_PREFIX}${endpoint}`, {
      ...options,
      headers,
    });

    if (!response.ok) {
      const error = await response.json().catch(() => ({ detail: 'Request failed' }));
      throw new Error(error.detail || 'API request failed');
    }

    return response.json();
  } catch (error: unknown) {
    const err = error as Error;
    // If network error, we're in demo mode
    if (err.name === 'TypeError' && err.message.includes('fetch')) {
      throw new Error('DEMO_MODE');
    }
    throw error;
  }
}

// Health check (without API prefix)
export async function checkHealth(): Promise<{ status: string }> {
  try {
    const response = await fetch(`${API_URL}/health`);
    return response.json();
  } catch {
    return { status: 'demo' };
  }
}

// Scan endpoints
export async function scanLink(url: string): Promise<ScanResult> {
  try {
    const response = await apiRequest<Record<string, unknown>>('/scan/link', {
      method: 'POST',
      body: JSON.stringify({ url }),
    });
    return mapScanResult(response);
  } catch {
    // Demo mode fallback
    return generateDemoScanResult('link', url);
  }
}

export async function scanEmail(content: string): Promise<ScanResult> {
  try {
    // Parse content to extract subject and body
    const lines = content.split('\n');
    const subjectLine = lines.find(l => l.toLowerCase().startsWith('subject:'));
    const subject = subjectLine ? subjectLine.replace(/^subject:\s*/i, '').trim() : 'No Subject';
    const body = lines.filter(l => !l.toLowerCase().startsWith('subject:') && !l.toLowerCase().startsWith('from:')).join('\n').trim() || content;
    
    const response = await apiRequest<Record<string, unknown>>('/scan/email', {
      method: 'POST',
      body: JSON.stringify({ subject, body }),
    });
    return mapScanResult(response);
  } catch {
    // Demo mode fallback
    return generateDemoScanResult('email', content);
  }
}

export async function scanLogs(logs: string): Promise<ScanResult> {
  try {
    // Parse logs into lines
    const lines = logs.split('\n').filter(l => l.trim());
    const response = await apiRequest<Record<string, unknown>>('/scan/logs', {
      method: 'POST',
      body: JSON.stringify({ source: 'User Submitted', lines }),
    });
    return mapScanResult(response);
  } catch {
    // Demo mode fallback
    return generateDemoScanResult('logs', logs);
  }
}

export async function getRecentScans(limit: number = 20): Promise<ScanEvent[]> {
  try {
    return await apiRequest(`/scan/recent?limit=${limit}`);
  } catch {
    // Demo mode fallback
    return generateDemoRecentScans(limit);
  }
}

// Guardian endpoints
export async function getGuardianStatus(): Promise<GuardianStatus> {
  try {
    return await apiRequest('/guardian/status');
  } catch {
    // Demo mode fallback
    return generateDemoGuardianStatus();
  }
}

export async function getGuardianSummary(): Promise<GuardianSummary> {
  try {
    return await apiRequest('/guardian/summary/today');
  } catch {
    // Demo mode fallback
    return generateDemoGuardianSummary();
  }
}

// Assistant endpoints
export async function sendChatMessage(
  message: string, 
  conversationId?: number
): Promise<ChatResponse> {
  try {
    return await apiRequest('/assistant/chat', {
      method: 'POST',
      body: JSON.stringify({ 
        message, 
        conversation_id: conversationId || null,
        context: {} 
      }),
    });
  } catch {
    // Demo mode fallback
    return generateDemoChatResponse(message);
  }
}

// Demo seed endpoint (only works in HACKATHON mode)
export async function seedDemoData(): Promise<{ success: boolean; message: string }> {
  try {
    return await apiRequest('/demo/seed', {
      method: 'POST',
    });
  } catch {
    return { success: true, message: 'Demo data already loaded (client-side mode)' };
  }
}

// Get conversation history
export async function getConversationHistory(conversationId: number): Promise<{
  conversation_id: number;
  messages: Array<{ role: string; content: string; created_at: string }>;
}> {
  return await apiRequest(`/assistant/conversation/${conversationId}`);
}
