import { ChatResponse, Mode } from './types';

// Use standard API calls without /api/v1 prefix
const API_BASE = 'http://localhost:8000';

export async function sendChatMessage(
  message: string,
  mode: Mode,
  conversationId?: string,
  context?: Record<string, any>
): Promise<ChatResponse> {
  // If we are in demo mode (no backend), we could mock.
  // But for hackathon, we assume backend is running.

  const res = await fetch(`${API_BASE}/assistant/chat`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      message,
      mode,
      conversation_id: conversationId,
      context,
    }),
  });

  if (!res.ok) {
    throw new Error('Failed to send message');
  }

  return res.json();
}

export async function getHealth(): Promise<{ status: string }> {
  const res = await fetch(`${API_BASE}/health`);
  return res.json();
}

export async function getDemoVehicles() {
  const res = await fetch(`${API_BASE}/auto/vehicles`);
  return res.json();
}

// History API
export interface ConversationSummary {
  id: string;
  mode: Mode;
  preview: string;
  timestamp: string;
  message_count: number;
}

export async function getHistory(): Promise<{ conversations: ConversationSummary[] }> {
  const res = await fetch(`${API_BASE}/assistant/history`);
  if (!res.ok) throw new Error('Failed to fetch history');
  return res.json();
}

export async function getConversation(cid: string): Promise<{ messages: any[] }> {
  const res = await fetch(`${API_BASE}/assistant/history/${cid}`);
  if (!res.ok) throw new Error('Failed to fetch conversation');
  return res.json();
}
