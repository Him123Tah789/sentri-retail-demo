'use client';

import { useState } from 'react';
import ChatBox from '@/components/ChatBox';
import ActionButtons from '@/components/ActionButtons';
import ModeToggle from '@/components/ModeToggle';
import VoiceControls from '@/components/VoiceControls';
import HistorySidebar from '@/components/HistorySidebar';
import { Message, Mode, ScanKind, RiskLevel } from '@/lib/types';
import { sendChatMessage, getConversation } from '@/lib/api';
import { scanHistory } from '@/lib/demoScenarios';

const getWelcomeMessage = (mode: string): Message => {
  if (mode === 'automotive') {
    return {
      id: '1',
      role: 'assistant',
      content: `👋 Hey there!\n\nI'm **Sentri**, your automotive cost and buying advisor.\n\n**Here's what I can do for you:**\n• 📊 **TCO Calculator** — Get a full cost-of-ownership breakdown for any vehicle\n• ⚡ **Compare Fuel Types** — See hybrid vs diesel vs petrol vs EV side-by-side\n• 📋 **Used Car Checklist** — Run a weighted inspection before you buy\n• 🔄 **What-If Analysis** — Simulate how price or cost changes impact you\n\nJust type naturally or tap a quick-action button on the right!`,
      createdAt: new Date().toISOString(),
    };
  }

  return {
    id: '1',
    role: 'assistant',
    content: `👋 Hey there!\n\nI'm **Sentri**, your AI-powered security assistant.\n\n**Here's what I can do for you:**\n• 🔗 **Scan Links** — Paste a URL and I'll check it for phishing, malware, and threats\n• 📧 **Analyze Emails** — Forward suspicious content for deep phishing detection\n• 📋 **Review Logs** — Paste security logs for anomaly and intrusion analysis\n• 💬 **Security Q&A** — Ask anything about cybersecurity best practices\n\nJust type naturally or use the action buttons on the right!`,
    createdAt: new Date().toISOString(),
  };
};

export default function AssistantPage() {
  const [mode, setMode] = useState<Mode>('security');
  const [messages, setMessages] = useState<Message[]>([getWelcomeMessage('security')]);
  const [loading, setLoading] = useState(false);
  const [conversationId, setConversationId] = useState<string | undefined>(undefined);
  const [historyOpen, setHistoryOpen] = useState(false);

  // Mode switch handler — reset chat
  const handleModeChange = (newMode: Mode) => {
    setMode(newMode);
    setMessages([getWelcomeMessage(newMode)]);
    setConversationId(undefined);
  };

  // Clear chat
  const handleClearChat = () => {
    setConversationId(undefined);
    setMessages([getWelcomeMessage(mode)]);
  };

  // Load old conversation from history
  const handleLoadHistory = async (cid: string) => {
    try {
      setLoading(true);
      const res = await getConversation(cid);
      if (res.messages && res.messages.length > 0) {
        // Find mode from last message or first
        const msgs = res.messages;
        const lastMode = msgs[msgs.length - 1].mode as Mode;

        // Update state
        setMode(lastMode || 'security');
        setConversationId(cid);

        // Map messages
        const mapped: Message[] = msgs.map((m: any, i: number) => ({
          id: i.toString(),
          role: m.role,
          content: m.content,
          createdAt: m.timestamp || new Date().toISOString()
        }));

        setMessages(mapped);
      }
    } catch (e) {
      console.error(e);
      alert("Failed to load conversation");
    } finally {
      setLoading(false);
    }
  };

  // Send message via chat API
  const handleSendMessage = async (content: string) => {
    const userMessage: Message = {
      id: Date.now().toString(),
      role: 'user',
      content,
      createdAt: new Date().toISOString(),
    };
    setMessages((prev) => [...prev, userMessage]);
    setLoading(true);

    try {
      const response = await sendChatMessage(content, mode, conversationId);

      if (response.conversation_id) {
        setConversationId(response.conversation_id);
      }

      const assistantMessage: Message = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: response.reply,
        createdAt: new Date().toISOString(),
      };
      setMessages((prev) => [...prev, assistantMessage]);

      // If it was a scan, add to dashboard history
      if (mode === 'security' && response.tool_result) {
        const tr = response.tool_result as any;
        let kind: ScanKind = 'text';
        if (response.intent === 'scan_link') kind = 'link';
        if (response.intent === 'scan_email') kind = 'email';
        if (response.intent === 'scan_logs') kind = 'logs';

        if (['link', 'email', 'logs'].includes(kind)) {
          scanHistory.add({
            userId: 1,
            kind: kind,
            input: content,
            inputPreview: content.substring(0, 50) + (content.length > 50 ? '...' : ''),
            riskScore: tr.risk_score || 0,
            riskLevel: (tr.risk_level?.toLowerCase() || 'low') as RiskLevel,
            verdict: tr.verdict || 'Unknown',
            explanation: tr.explanation || '',
            recommendedActions: tr.recommended_actions || []
          });
        }
      }

    } catch (error) {
      const errorMessage: Message = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: '⚠️ Something went wrong. Please try again.',
        createdAt: new Date().toISOString(),
      };
      setMessages((prev) => [...prev, errorMessage]);
    } finally {
      setLoading(false);
    }
  };

  // Scan handler — sends through chat
  const handleScan = async (_kind: string, input: string) => {
    await handleSendMessage(input);
  };

  // Voice action logic
  const handleVoiceAction = (action: string) => {
    switch (action) {
      case 'scan_link': handleSendMessage("Scan a link for me"); break;
      case 'scan_email': handleSendMessage("Analyze this email"); break;
      case 'scan_logs': handleSendMessage("Review these security logs"); break;
      case 'auto_tco': handleSendMessage("Calculate TCO for a standard sedan"); break;
      case 'auto_sensitivity_fuel': handleSendMessage("Run fuel price sensitivity analysis"); break;
      case 'auto_sensitivity_km': handleSendMessage("Run mileage sensitivity analysis"); break;
      default: handleSendMessage(action.replace(/_/g, " "));
    }
  };

  const lastAssistantReply = messages.length > 0 && messages[messages.length - 1].role === 'assistant'
    ? messages[messages.length - 1].content
    : undefined;

  return (
    <div className="min-h-screen bg-slate-50 flex flex-col">
      {/* History Sidebar */}
      <HistorySidebar
        isOpen={historyOpen}
        setIsOpen={setHistoryOpen}
        onSelect={handleLoadHistory}
      />

      {/* Top Bar */}
      <header className="bg-white border-b border-slate-200 px-6 py-3 flex items-center justify-between pl-16">
        <div className="flex items-center gap-4">
          <h1 className="text-lg font-bold text-slate-800">Sentri</h1>
          <ModeToggle mode={mode} onModeChange={handleModeChange} />
        </div>
        <div className="flex items-center gap-4">
          {/* Link to Dashboard */}
          {/* Link to Dashboard */}
          <a
            href="/dashboard"
            className="flex items-center gap-2 px-3 py-1.5 text-sm font-medium text-blue-700 bg-blue-50 hover:bg-blue-100 rounded-lg transition-colors border border-blue-200"
          >
            <svg
              xmlns="http://www.w3.org/2000/svg"
              width="16"
              height="16"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              strokeWidth="2"
              strokeLinecap="round"
              strokeLinejoin="round"
            >
              <rect width="7" height="9" x="3" y="3" rx="1" />
              <rect width="7" height="5" x="14" y="3" rx="1" />
              <rect width="7" height="9" x="14" y="12" rx="1" />
              <rect width="7" height="5" x="3" y="16" rx="1" />
            </svg>
            Dashboard
          </a>
          <button
            onClick={handleClearChat}
            className="text-sm text-slate-500 hover:text-red-500 transition-colors"
          >
            Clear Chat
          </button>
        </div>
      </header>

      <main className="flex-1 max-w-6xl mx-auto w-full p-4 flex flex-col lg:flex-row gap-6">
        {/* Chat Section */}
        <div className="flex-1 flex flex-col">
          <div className="card flex-1 flex flex-col min-h-[500px]">
            <ChatBox
              messages={messages}
              onSendMessage={handleSendMessage}
              loading={loading}
            />
          </div>
        </div>

        {/* Actions & Tips Section */}
        <div className="lg:w-96 space-y-4">
          {/* Voice Controls */}
          <VoiceControls
            mode={mode}
            setMode={handleModeChange}
            onSendText={handleSendMessage}
            onAction={handleVoiceAction}
            lastAssistantReply={lastAssistantReply}
          />

          <ActionButtons
            onScan={handleScan}
            onSendMessage={handleSendMessage}
            loading={loading}
            mode={mode}
          />

          {/* Quick Tips */}
          <div className="card">
            <h3 className="font-semibold text-slate-800 mb-3">
              {mode === 'automotive' ? 'Automotive Features' : 'Security Features'}
            </h3>
            {mode === 'automotive' ? (
              <ul className="space-y-2 text-sm text-slate-600">
                <li className="flex items-start gap-2">
                  <span className="text-emerald-500">📊</span>
                  <span><strong>TCO Calculator</strong> — Full cost of ownership analysis</span>
                </li>
                <li className="flex items-start gap-2">
                  <span className="text-sky-500">⚡</span>
                  <span><strong>Compare Fuels</strong> — Hybrid vs diesel vs electric</span>
                </li>
                <li className="flex items-start gap-2">
                  <span className="text-amber-500">📋</span>
                  <span><strong>Used Car Check</strong> — Pre-purchase checklist</span>
                </li>
                <li className="flex items-start gap-2">
                  <span className="text-violet-500">🔄</span>
                  <span><strong>What-If Analysis</strong> — See cost impact of changes</span>
                </li>
              </ul>
            ) : (
              <ul className="space-y-2 text-sm text-slate-600">
                <li className="flex items-start gap-2">
                  <span className="text-blue-500">🔗</span>
                  <span><strong>Scan Links</strong> — Paste a URL to check if it&apos;s safe</span>
                </li>
                <li className="flex items-start gap-2">
                  <span className="text-blue-500">📧</span>
                  <span><strong>Analyze Emails</strong> — Paste email content to detect phishing</span>
                </li>
                <li className="flex items-start gap-2">
                  <span className="text-blue-500">📋</span>
                  <span><strong>Review Logs</strong> — Paste log entries for security analysis</span>
                </li>
                <li className="flex items-start gap-2">
                  <span className="text-blue-500">💬</span>
                  <span><strong>Ask Questions</strong> — Get security advice and insights</span>
                </li>
              </ul>
            )}
            <p className="mt-3 text-xs text-slate-400 italic">
              ⚠️ Always verify critical security decisions
            </p>
          </div>
        </div>
      </main>
    </div>
  );
}
