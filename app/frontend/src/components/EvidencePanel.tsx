'use client';

import { useState } from 'react';
import { ChevronDown, ChevronUp, Activity, Zap, Layers, AlertCircle, Check, ThumbsUp, ThumbsDown } from 'lucide-react';
import { Evidence } from '@/lib/types';

interface EvidencePanelProps {
    evidence: Evidence;
}

export default function EvidencePanel({ evidence }: EvidencePanelProps) {
    const [isOpen, setIsOpen] = useState(false);
    const [feedback, setFeedback] = useState<'positive' | 'negative' | null>(null);

    const getScoreColor = (score: number) => {
        if (score < 4) return 'text-green-600';
        if (score < 7) return 'text-yellow-600';
        return 'text-red-600';
    };

    const getConfColor = (conf: number) => {
        if (conf > 0.8) return 'text-green-600';
        if (conf > 0.5) return 'text-yellow-600';
        return 'text-red-600';
    };

    return (
        <div className="mt-3 border border-slate-200 rounded-lg overflow-hidden bg-slate-50">
            <button
                onClick={() => setIsOpen(!isOpen)}
                className="w-full flex items-center justify-between p-3 bg-slate-100 hover:bg-slate-200 transition-colors text-xs font-medium text-slate-600 uppercase tracking-wider"
            >
                <div className="flex items-center gap-2">
                    <Activity className="w-4 h-4" />
                    <span>AI Evidence & Analysis</span>
                </div>
                {isOpen ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
            </button>

            {isOpen && (
                <div className="p-4 space-y-4 text-sm animate-fadeIn">
                    {/* Top Row: Score, Confidence, Latency */}
                    <div className="grid grid-cols-3 gap-2 text-center">
                        <div className="p-2 bg-white rounded border border-slate-200">
                            <div className="text-xs text-slate-400 mb-1">Risk Score</div>
                            <div className={`font-mono font-bold text-lg ${getScoreColor(evidence.risk_score)}`}>
                                {evidence.risk_score}/10
                            </div>
                        </div>
                        <div className="p-2 bg-white rounded border border-slate-200">
                            <div className="text-xs text-slate-400 mb-1">Confidence</div>
                            <div className={`font-mono font-bold text-lg ${getConfColor(evidence.confidence)}`}>
                                {Math.round(evidence.confidence * 100)}%
                            </div>
                        </div>
                        <div className="p-2 bg-white rounded border border-slate-200">
                            <div className="text-xs text-slate-400 mb-1">Latency</div>
                            <div className="font-mono font-bold text-lg text-slate-700">
                                {evidence.latency_ms}ms
                            </div>
                        </div>
                    </div>

                    {/* Model & Correlation */}
                    <div className="flex flex-col gap-2">
                        <div className="flex justify-between items-center text-xs text-slate-500">
                            <span className="flex items-center gap-1">
                                <Layers className="w-3 h-3" /> Model:
                            </span>
                            <span className="font-mono">{evidence.model_version}</span>
                        </div>

                        {evidence.threat_correlation && (
                            <div className="flex justify-between items-center text-xs text-slate-500">
                                <span className="flex items-center gap-1">
                                    <Zap className="w-3 h-3" /> Correlation:
                                </span>
                                <span className={`font-bold px-1.5 py-0.5 rounded text-[10px] ${evidence.threat_correlation === 'HIGH' ? 'bg-red-100 text-red-700' :
                                        evidence.threat_correlation === 'MEDIUM' ? 'bg-yellow-100 text-yellow-700' :
                                            'bg-green-100 text-green-700'
                                    }`}>
                                    {evidence.threat_correlation}
                                </span>
                            </div>
                        )}
                    </div>

                    {/* Top Signals */}
                    <div>
                        <div className="text-xs font-semibold text-slate-600 mb-2 flex items-center gap-1">
                            <AlertCircle className="w-3 h-3" /> Top Contributing Signals
                        </div>
                        <ul className="space-y-1">
                            {evidence.top_signals.map((sig, i) => (
                                <li key={i} className="flex items-start gap-2 text-xs text-slate-600 bg-white p-1.5 rounded border border-slate-100">
                                    <span className="text-slate-400 mt-0.5">•</span>
                                    {sig}
                                </li>
                            ))}
                            {evidence.top_signals.length === 0 && (
                                <li className="text-xs text-slate-400 italic">No specific signals detected.</li>
                            )}
                        </ul>
                    </div>

                    {/* Feedback Loop */}
                    <div className="pt-2 border-t border-slate-200">
                        <div className="text-[10px] text-slate-400 uppercase tracking-widest mb-2 text-center">
                            Analyst Feedback Loop
                        </div>
                        <div className="flex gap-2 justify-center">
                            <button
                                onClick={() => setFeedback('positive')}
                                className={`flex-1 flex items-center justify-center gap-1 py-1.5 px-3 rounded text-xs transition-colors ${feedback === 'positive'
                                        ? 'bg-blue-600 text-white'
                                        : 'bg-white border border-slate-200 text-slate-600 hover:bg-slate-50'
                                    }`}
                            >
                                <ThumbsUp className="w-3 h-3" /> Confirm
                            </button>
                            <button
                                onClick={() => setFeedback('negative')}
                                className={`flex-1 flex items-center justify-center gap-1 py-1.5 px-3 rounded text-xs transition-colors ${feedback === 'negative'
                                        ? 'bg-slate-600 text-white'
                                        : 'bg-white border border-slate-200 text-slate-600 hover:bg-slate-50'
                                    }`}
                            >
                                <ThumbsDown className="w-3 h-3" /> False Pos.
                            </button>
                        </div>
                        {feedback && (
                            <p className="text-center text-[10px] text-green-600 mt-2 flex items-center justify-center gap-1">
                                <Check className="w-3 h-3" /> Feedback recorded for retraining
                            </p>
                        )}
                    </div>
                </div>
            )}
        </div>
    );
}
