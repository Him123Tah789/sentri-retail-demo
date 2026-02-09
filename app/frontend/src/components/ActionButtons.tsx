'use client';

import { useState } from 'react';
import { Link2, Mail, FileText, Zap, ChevronDown, ChevronUp } from 'lucide-react';
import { ScanKind } from '@/lib/types';
import { demoScenarios } from '@/lib/demoScenarios';

interface ActionButtonsProps {
  onScan: (kind: ScanKind, input: string) => void;
  onDemoScenario: (scenario: keyof typeof demoScenarios) => void;
  loading?: boolean;
}

export default function ActionButtons({ onScan, onDemoScenario, loading }: ActionButtonsProps) {
  const [activeAction, setActiveAction] = useState<ScanKind | null>(null);
  const [input, setInput] = useState('');
  const [showDemos, setShowDemos] = useState(false);

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
    } else {
      setActiveAction(kind);
      setInput('');
    }
  };

  const handleSubmit = () => {
    if (activeAction && input.trim()) {
      onScan(activeAction, input.trim());
      setInput('');
      setActiveAction(null);
    }
  };

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

      {/* Input Field */}
      {activeAction && (
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
