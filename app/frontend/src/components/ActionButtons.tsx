'use client';

import { useState } from 'react';
import { Link2, Mail, FileText, Zap, ChevronDown, ChevronUp, Plus, X } from 'lucide-react';
import { ScanKind } from '@/lib/types';
import { demoScenarios } from '@/lib/demoScenarios';

interface ActionButtonsProps {
  onScan: (kind: ScanKind, input: string) => void;
  onDemoScenario: (scenario: keyof typeof demoScenarios) => void;
  loading?: boolean;
}

// Email input structure
interface EmailInput {
  from: string;
  subject: string;
  body: string;
  embeddedLinks: string[];
}

export default function ActionButtons({ onScan, onDemoScenario, loading }: ActionButtonsProps) {
  const [activeAction, setActiveAction] = useState<ScanKind | null>(null);
  const [input, setInput] = useState('');
  const [showDemos, setShowDemos] = useState(false);
  
  // Email-specific state
  const [emailInput, setEmailInput] = useState<EmailInput>({
    from: '',
    subject: '',
    body: '',
    embeddedLinks: [],
  });
  const [newLink, setNewLink] = useState('');

  const actions = [
    {
      kind: 'link' as ScanKind,
      label: 'Scan Link',
      icon: Link2,
      placeholder: 'Paste URL to analyze...',
      color: 'bg-blue-500 hover:bg-blue-600',
    },
    {
      kind: 'email' as ScanKind,
      label: 'Analyze Email',
      icon: Mail,
      placeholder: 'Paste email content or address...',
      color: 'bg-purple-500 hover:bg-purple-600',
    },
    {
      kind: 'logs' as ScanKind,
      label: 'Summarize Logs',
      icon: FileText,
      placeholder: 'Paste security logs...',
      color: 'bg-green-500 hover:bg-green-600',
    },
  ];

  const handleActionClick = (kind: ScanKind) => {
    if (activeAction === kind) {
      setActiveAction(null);
      setInput('');
      setEmailInput({ from: '', subject: '', body: '', embeddedLinks: [] });
    } else {
      setActiveAction(kind);
      setInput('');
      setEmailInput({ from: '', subject: '', body: '', embeddedLinks: [] });
    }
  };

  const addEmbeddedLink = () => {
    if (newLink.trim() && !emailInput.embeddedLinks.includes(newLink.trim())) {
      setEmailInput(prev => ({
        ...prev,
        embeddedLinks: [...prev.embeddedLinks, newLink.trim()]
      }));
      setNewLink('');
    }
  };

  const removeEmbeddedLink = (index: number) => {
    setEmailInput(prev => ({
      ...prev,
      embeddedLinks: prev.embeddedLinks.filter((_, i) => i !== index)
    }));
  };

  const handleSubmit = () => {
    if (activeAction === 'email') {
      // Build email content from structured input
      let emailContent = '';
      if (emailInput.from.trim()) {
        emailContent += `From: ${emailInput.from.trim()}\n`;
      }
      if (emailInput.subject.trim()) {
        emailContent += `Subject: ${emailInput.subject.trim()}\n`;
      }
      emailContent += '\n' + emailInput.body.trim();
      
      // Append embedded links to the body so they get analyzed
      if (emailInput.embeddedLinks.length > 0) {
        emailContent += '\n\nLinks found in email:\n' + emailInput.embeddedLinks.join('\n');
      }
      
      if (emailContent.trim()) {
        onScan('email', emailContent.trim());
        setEmailInput({ from: '', subject: '', body: '', embeddedLinks: [] });
        setActiveAction(null);
      }
    } else if (activeAction && input.trim()) {
      onScan(activeAction, input.trim());
      setInput('');
      setActiveAction(null);
    }
  };

  const isEmailValid = emailInput.from.trim() || emailInput.subject.trim() || emailInput.body.trim();

  return (
    <div className="card space-y-4">
      <h3 className="font-semibold text-slate-800">Security Actions</h3>

      {/* Action Buttons */}
      <div className="grid grid-cols-3 gap-2">
        {actions.map((action) => {
          const Icon = action.icon;
          const isActive = activeAction === action.kind;
          return (
            <button
              key={action.kind}
              onClick={() => handleActionClick(action.kind)}
              disabled={loading}
              className={`flex flex-col items-center gap-1 p-3 rounded-xl transition-all ${
                isActive
                  ? `${action.color} text-white shadow-lg scale-105`
                  : 'bg-slate-100 text-slate-600 hover:bg-slate-200'
              } disabled:opacity-50`}
            >
              <Icon className="w-5 h-5" />
              <span className="text-xs font-medium">{action.label}</span>
            </button>
          );
        })}
      </div>

      {/* Email Input - Structured Form */}
      {activeAction === 'email' && (
        <div className="space-y-3 animate-fade-in">
          {/* From Field */}
          <div>
            <label className="block text-xs font-medium text-slate-600 mb-1">
              From (Sender Email)
            </label>
            <input
              type="text"
              value={emailInput.from}
              onChange={(e) => setEmailInput(prev => ({ ...prev, from: e.target.value }))}
              placeholder="e.g., sender@example.com"
              className="w-full px-3 py-2 border border-slate-300 rounded-lg text-sm focus:ring-2 focus:ring-purple-500 focus:border-purple-500"
            />
          </div>

          {/* Subject Field */}
          <div>
            <label className="block text-xs font-medium text-slate-600 mb-1">
              Subject
            </label>
            <input
              type="text"
              value={emailInput.subject}
              onChange={(e) => setEmailInput(prev => ({ ...prev, subject: e.target.value }))}
              placeholder="e.g., URGENT: Verify your account"
              className="w-full px-3 py-2 border border-slate-300 rounded-lg text-sm focus:ring-2 focus:ring-purple-500 focus:border-purple-500"
            />
          </div>

          {/* Body Field */}
          <div>
            <label className="block text-xs font-medium text-slate-600 mb-1">
              Email Body
            </label>
            <textarea
              value={emailInput.body}
              onChange={(e) => setEmailInput(prev => ({ ...prev, body: e.target.value }))}
              placeholder="Paste the email content here..."
              className="w-full px-3 py-2 border border-slate-300 rounded-lg text-sm resize-none focus:ring-2 focus:ring-purple-500 focus:border-purple-500"
              rows={4}
            />
          </div>

          {/* Embedded Links Field */}
          <div>
            <label className="block text-xs font-medium text-slate-600 mb-1">
              Embedded Links (Optional)
            </label>
            <div className="flex gap-2">
              <input
                type="text"
                value={newLink}
                onChange={(e) => setNewLink(e.target.value)}
                onKeyDown={(e) => e.key === 'Enter' && (e.preventDefault(), addEmbeddedLink())}
                placeholder="Add suspicious URL..."
                className="flex-1 px-3 py-2 border border-slate-300 rounded-lg text-sm focus:ring-2 focus:ring-purple-500 focus:border-purple-500"
              />
              <button
                type="button"
                onClick={addEmbeddedLink}
                disabled={!newLink.trim()}
                className="px-3 py-2 bg-purple-100 text-purple-700 rounded-lg hover:bg-purple-200 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                <Plus className="w-4 h-4" />
              </button>
            </div>
            
            {/* Display added links */}
            {emailInput.embeddedLinks.length > 0 && (
              <div className="mt-2 space-y-1">
                {emailInput.embeddedLinks.map((link, index) => (
                  <div key={index} className="flex items-center gap-2 text-xs bg-slate-100 px-2 py-1 rounded">
                    <span className="flex-1 truncate text-slate-600">{link}</span>
                    <button
                      type="button"
                      onClick={() => removeEmbeddedLink(index)}
                      className="text-red-500 hover:text-red-700"
                    >
                      <X className="w-3 h-3" />
                    </button>
                  </div>
                ))}
                <p className="text-xs text-slate-500 mt-1">
                  {emailInput.embeddedLinks.length} link(s) will be checked for phishing
                </p>
              </div>
            )}
          </div>

          <button
            onClick={handleSubmit}
            disabled={!isEmailValid || loading}
            className="w-full btn-primary disabled:opacity-50 flex items-center justify-center gap-2"
          >
            {loading ? (
              <>
                <div className="spinner border-white border-t-transparent w-4 h-4"></div>
                <span>Analyzing...</span>
              </>
            ) : (
              <>
                <Mail className="w-4 h-4" />
                <span>Analyze Email</span>
              </>
            )}
          </button>
        </div>
      )}

      {/* Standard Input Field for Link and Logs */}
      {activeAction && activeAction !== 'email' && (
        <div className="space-y-2 animate-fade-in">
          <textarea
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder={actions.find((a) => a.kind === activeAction)?.placeholder}
            className="w-full px-3 py-2 border border-slate-300 rounded-lg text-sm resize-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            rows={3}
          />
          <button
            onClick={handleSubmit}
            disabled={!input.trim() || loading}
            className="w-full btn-primary disabled:opacity-50 flex items-center justify-center gap-2"
          >
            {loading ? (
              <>
                <div className="spinner border-white border-t-transparent w-4 h-4"></div>
                <span>Scanning...</span>
              </>
            ) : (
              <>
                <Zap className="w-4 h-4" />
                <span>Analyze Now</span>
              </>
            )}
          </button>
        </div>
      )}

      {/* Demo Scenarios */}
      <div className="pt-2 border-t border-slate-200">
        <button
          onClick={() => setShowDemos(!showDemos)}
          className="w-full flex items-center justify-between text-sm text-slate-500 hover:text-slate-700"
        >
          <span>Demo Scenarios</span>
          {showDemos ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
        </button>

        {showDemos && (
          <div className="mt-3 space-y-2 animate-fade-in">
            {Object.entries(demoScenarios).map(([key, scenario]) => (
              <button
                key={key}
                onClick={() => onDemoScenario(key as keyof typeof demoScenarios)}
                disabled={loading}
                className="w-full text-left text-xs p-2 bg-slate-50 hover:bg-slate-100 rounded-lg transition-colors disabled:opacity-50"
              >
                <span className="font-medium text-slate-700">{scenario.title}</span>
                <p className="text-slate-500 mt-0.5">{scenario.description}</p>
              </button>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
