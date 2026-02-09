'use client';

import { AlertTriangle, CheckCircle, AlertCircle, XCircle, Shield } from 'lucide-react';
import { ScanResult } from '@/lib/types';

interface ResultCardProps {
  result: ScanResult;
}

export default function ResultCard({ result }: ResultCardProps) {
  const getRiskConfig = (level: string) => {
    switch (level.toLowerCase()) {
      case 'low':
        return {
          icon: CheckCircle,
          bg: 'bg-green-50',
          border: 'border-green-200',
          iconColor: 'text-green-500',
          textColor: 'text-green-700',
          label: 'Low Risk',
          barColor: 'bg-green-500',
        };
      case 'medium':
        return {
          icon: AlertCircle,
          bg: 'bg-yellow-50',
          border: 'border-yellow-200',
          iconColor: 'text-yellow-500',
          textColor: 'text-yellow-700',
          label: 'Medium Risk',
          barColor: 'bg-yellow-500',
        };
      case 'high':
        return {
          icon: AlertTriangle,
          bg: 'bg-orange-50',
          border: 'border-orange-200',
          iconColor: 'text-orange-500',
          textColor: 'text-orange-700',
          label: 'High Risk',
          barColor: 'bg-orange-500',
        };
      case 'critical':
        return {
          icon: XCircle,
          bg: 'bg-red-50',
          border: 'border-red-200',
          iconColor: 'text-red-500',
          textColor: 'text-red-700',
          label: 'Critical Risk',
          barColor: 'bg-red-500',
        };
      default:
        return {
          icon: Shield,
          bg: 'bg-slate-50',
          border: 'border-slate-200',
          iconColor: 'text-slate-500',
          textColor: 'text-slate-700',
          label: 'Unknown',
          barColor: 'bg-slate-500',
        };
    }
  };

  const config = getRiskConfig(result.riskLevel);
  const Icon = config.icon;

  return (
    <div className={`card ${config.bg} border ${config.border} animate-fade-in`}>
      {/* Header */}
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-3">
          <div className={`p-2 rounded-lg ${config.bg}`}>
            <Icon className={`w-6 h-6 ${config.iconColor}`} />
          </div>
          <div>
            <h3 className="font-semibold text-slate-800">Scan Result</h3>
            <p className={`text-sm font-medium ${config.textColor}`}>{config.label}</p>
          </div>
        </div>
        <div className="text-right">
          <p className="text-2xl font-bold text-slate-800">{result.riskScore}</p>
          <p className="text-xs text-slate-500">/ 10</p>
        </div>
      </div>

      {/* Risk Bar */}
      <div className="mb-4">
        <div className="h-2 bg-slate-200 rounded-full overflow-hidden">
          <div
            className={`h-full ${config.barColor} transition-all duration-500`}
            style={{ width: `${(result.riskScore / 10) * 100}%` }}
          />
        </div>
      </div>

      {/* Verdict */}
      <div className="p-3 bg-white rounded-lg mb-4">
        <p className="text-sm font-medium text-slate-700 mb-1">Verdict</p>
        <p className={`font-semibold ${config.textColor}`}>{result.verdict}</p>
      </div>

      {/* Explanation */}
      <div>
        <p className="text-sm font-medium text-slate-700 mb-2">Analysis</p>
        <p className="text-sm text-slate-600 leading-relaxed">{result.explanation}</p>
      </div>

      {/* Scanned Target */}
      <div className="mt-4 pt-4 border-t border-slate-200">
        <p className="text-xs text-slate-500">Scanned: <span className="font-mono">{result.inputPreview}</span></p>
        <p className="text-xs text-slate-400 mt-1">
          {new Date(result.createdAt).toLocaleString()}
        </p>
      </div>
    </div>
  );
}
