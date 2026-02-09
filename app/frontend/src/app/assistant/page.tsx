'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { isAuthenticated, getUser } from '@/lib/auth';
import HeaderStatus from '@/components/HeaderStatus';
import ChatBox from '@/components/ChatBox';
import ActionButtons from '@/components/ActionButtons';
import ResultCard from '@/components/ResultCard';
import { Message, ScanResult, ScanKind, ChatResponse } from '@/lib/types';
import { sendChatMessage, scanLink, scanEmail, scanLogs } from '@/lib/api';
import { demoScenarios } from '@/lib/demoScenarios';

// Tool badges for visual feedback
const ToolBadge = ({ tool }: { tool: string }) => {
  if (tool === 'none') return null;
  
  const badges: Record<string, { label: string; color: string }> = {
    scan_link: { label: '🔗 Link Scanned', color: 'bg-blue-100 text-blue-700' },
    scan_email: { label: '📧 Email Analyzed', color: 'bg-purple-100 text-purple-700' },
    scan_logs: { label: '📋 Logs Reviewed', color: 'bg-orange-100 text-orange-700' },
  };
  
  const badge = badges[tool];
  if (!badge) return null;
  
  return (
    <span className={`inline-block px-2 py-0.5 text-xs rounded-full ${badge.color} mr-2`}>
      {badge.label}
    </span>
  );
};

// Risk badge for visual feedback
const RiskBadge = ({ level, score }: { level: string; score: number }) => {
  const colors: Record<string, string> = {
    HIGH: 'bg-red-100 text-red-700 border-red-200',
    MEDIUM: 'bg-yellow-100 text-yellow-700 border-yellow-200',
    LOW: 'bg-green-100 text-green-700 border-green-200',
  };
  
  return (
    <span className={`inline-block px-2 py-0.5 text-xs rounded-full border ${colors[level] || colors.LOW}`}>
      Risk: {level} ({score}/100)
    </span>
  );
};

export default function AssistantPage() {
  const router = useRouter();
  const [messages, setMessages] = useState<Message[]>([]);
  const [scanResult, setScanResult] = useState<ScanResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [scanLoading, setScanLoading] = useState(false);
  const [conversationId, setConversationId] = useState<number | undefined>(undefined);
  const [lastToolUsed, setLastToolUsed] = useState<string>('none');
  const [lastRiskSummary, setLastRiskSummary] = useState<{ level: string; score: number } | null>(null);

  // Load chat from localStorage on mount
  useEffect(() => {
    if (!isAuthenticated()) {
      router.push('/login');
      return;
    }
    
    // Try to restore chat history from localStorage
    const savedConversationId = localStorage.getItem('sentri_conversation_id');
    const savedMessages = localStorage.getItem('sentri_chat_messages');
    
    if (savedConversationId && savedMessages) {
      try {
        setConversationId(parseInt(savedConversationId, 10));
        setMessages(JSON.parse(savedMessages));
        return;
      } catch (e) {
        console.error('Failed to restore chat history:', e);
      }
    }
    
    // Welcome message for new conversation
    setMessages([
      {
        id: '1',
        role: 'assistant',
        content: `Hello! I'm Sentri, your AI assistant for retail operations and security.\n\n**I can help with:**\n• **General Questions** - Ask me anything, like "explain OAuth" or "help me write an email"\n• **Security Scans** - Paste a link, email, or logs and I'll analyze them automatically\n• **Business Advice** - Planning, productivity, and decision support\n\nJust type naturally - I'll figure out if you need a chat response or a security scan!`,
        createdAt: new Date().toISOString(),
      },
    ]);
  }, [router]);
  
  // Save chat to localStorage whenever messages change
  useEffect(() => {
    if (messages.length > 0) {
      localStorage.setItem('sentri_chat_messages', JSON.stringify(messages));
    }
    if (conversationId) {
      localStorage.setItem('sentri_conversation_id', conversationId.toString());
    }
  }, [messages, conversationId]);

  // Clear chat history and start fresh
  const handleClearChat = () => {
    localStorage.removeItem('sentri_conversation_id');
    localStorage.removeItem('sentri_chat_messages');
    setConversationId(undefined);
    setLastToolUsed('none');
    setLastRiskSummary(null);
    setMessages([
      {
        id: '1',
        role: 'assistant',
        content: `Hello! I'm Sentri, your AI assistant for retail operations and security.\n\n**I can help with:**\n• **General Questions** - Ask me anything, like "explain OAuth" or "help me write an email"\n• **Security Scans** - Paste a link, email, or logs and I'll analyze them automatically\n• **Business Advice** - Planning, productivity, and decision support\n\nJust type naturally - I'll figure out if you need a chat response or a security scan!`,
        createdAt: new Date().toISOString(),
      },
    ]);
  };

  const handleSendMessage = async (content: string) => {
    const userMessage: Message = {
      id: Date.now().toString(),
      role: 'user',
      content,
      createdAt: new Date().toISOString(),
    };
    setMessages((prev) => [...prev, userMessage]);
    setLoading(true);
    setLastToolUsed('none');
    setLastRiskSummary(null);

    try {
      // Pass conversation_id to maintain memory across messages
      const response = await sendChatMessage(content, conversationId);
      
      // Store conversation_id for subsequent messages (always update)
      if (response.conversation_id) {
        setConversationId(response.conversation_id);
      }
      
      // Track tool usage for visual feedback
      if (response.tool_used && response.tool_used !== 'none') {
        setLastToolUsed(response.tool_used);
      }
      
      // Track risk summary if a scan was performed
      if (response.risk_summary) {
        setLastRiskSummary({
          level: response.risk_summary.level,
          score: response.risk_summary.score
        });
      }
      
      const assistantMessage: Message = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: response.reply,
        createdAt: new Date().toISOString(),
      };
      setMessages((prev) => [...prev, assistantMessage]);
    } catch (error) {
      const errorMessage: Message = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: 'Sorry, I encountered an error. Please try again.',
        createdAt: new Date().toISOString(),
      };
      setMessages((prev) => [...prev, errorMessage]);
    } finally {
      setLoading(false);
    }
  };

  const handleScan = async (kind: ScanKind, input: string) => {
    setScanLoading(true);
    setScanResult(null);

    try {
      let result: ScanResult;
      switch (kind) {
        case 'link':
          result = await scanLink(input);
          break;
        case 'email':
          result = await scanEmail(input);
          break;
        case 'logs':
          result = await scanLogs(input);
          break;
        default:
          throw new Error('Unknown scan type');
      }
      setScanResult(result);

      // Add to chat
      const summaryMessage: Message = {
        id: Date.now().toString(),
        role: 'assistant',
        content: `**Scan Complete** (${kind.toUpperCase()})\n\n**Risk Level:** ${result.riskLevel.toUpperCase()}\n**Score:** ${result.riskScore}/10\n\n${result.explanation}`,
        createdAt: new Date().toISOString(),
      };
      setMessages((prev) => [...prev, summaryMessage]);
    } catch (error) {
      console.error('Scan error:', error);
    } finally {
      setScanLoading(false);
    }
  };

  const handleDemoScenario = (scenario: keyof typeof demoScenarios) => {
    const demo = demoScenarios[scenario];
    handleScan(demo.kind as ScanKind, demo.input);
  };

  return (
    <div className="min-h-screen bg-slate-50 flex flex-col">
      <HeaderStatus />

      <main className="flex-1 max-w-6xl mx-auto w-full p-4 flex flex-col lg:flex-row gap-6">
        {/* Chat Section */}
        <div className="flex-1 flex flex-col">
          <div className="card flex-1 flex flex-col min-h-[500px]">
            <div className="flex justify-between items-center mb-4">
              <div className="flex items-center gap-2">
                <h2 className="text-lg font-semibold text-slate-800">AI Assistant</h2>
                {lastToolUsed !== 'none' && <ToolBadge tool={lastToolUsed} />}
                {lastRiskSummary && <RiskBadge level={lastRiskSummary.level} score={lastRiskSummary.score} />}
              </div>
              <button
                onClick={handleClearChat}
                className="text-sm text-slate-500 hover:text-red-500 transition-colors"
                title="Clear chat history"
              >
                Clear Chat
              </button>
            </div>
            <ChatBox
              messages={messages}
              onSendMessage={handleSendMessage}
              loading={loading}
            />
          </div>
        </div>

        {/* Actions & Results Section */}
        <div className="lg:w-96 space-y-4">
          <ActionButtons
            onScan={handleScan}
            onDemoScenario={handleDemoScenario}
            loading={scanLoading}
          />

          {scanResult && (
            <ResultCard result={scanResult} />
          )}

          {/* Quick Tips */}
          <div className="card">
            <h3 className="font-semibold text-slate-800 mb-3">What Sentri Can Do</h3>
            <ul className="space-y-2 text-sm text-slate-600">
              <li className="flex items-start gap-2">
                <span className="text-blue-500">💬</span>
                <span><strong>General Chat</strong> - Ask anything, get explanations, write emails</span>
              </li>
              <li className="flex items-start gap-2">
                <span className="text-blue-500">🔗</span>
                <span><strong>Scan Links</strong> - Paste a URL to check if it's safe</span>
              </li>
              <li className="flex items-start gap-2">
                <span className="text-blue-500">📧</span>
                <span><strong>Analyze Emails</strong> - Paste email content to detect phishing</span>
              </li>
              <li className="flex items-start gap-2">
                <span className="text-blue-500">📋</span>
                <span><strong>Review Logs</strong> - Paste log entries for security analysis</span>
              </li>
            </ul>
            <p className="mt-3 text-xs text-slate-400 italic">
              ⚠️ I may be wrong—verify critical security decisions
            </p>
          </div>
        </div>
      </main>
    </div>
  );
}
