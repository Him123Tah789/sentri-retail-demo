'use client';

import { Link2, Mail, FileText, Clock } from 'lucide-react';
import { ScanEvent } from '@/lib/types';

interface ActivityTableProps {
  scans: ScanEvent[];
}

export default function ActivityTable({ scans }: ActivityTableProps) {
  const getKindIcon = (kind: string) => {
    switch (kind) {
      case 'link':
        return <Link2 className="w-4 h-4" />;
      case 'email':
        return <Mail className="w-4 h-4" />;
      case 'logs':
        return <FileText className="w-4 h-4" />;
      default:
        return <FileText className="w-4 h-4" />;
    }
  };

  const getRiskBadge = (level: string) => {
    switch (level.toLowerCase()) {
      case 'low':
        return <span className="badge-low">Low</span>;
      case 'medium':
        return <span className="badge-medium">Medium</span>;
      case 'high':
        return <span className="badge-high">High</span>;
      case 'critical':
        return <span className="badge-critical">Critical</span>;
      default:
        return <span className="badge-low">Unknown</span>;
    }
  };

  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    const now = new Date();
    const diff = now.getTime() - date.getTime();
    const minutes = Math.floor(diff / 60000);
    const hours = Math.floor(diff / 3600000);
    const days = Math.floor(diff / 86400000);

    if (minutes < 60) return `${minutes}m ago`;
    if (hours < 24) return `${hours}h ago`;
    if (days < 7) return `${days}d ago`;
    return date.toLocaleDateString();
  };

  if (scans.length === 0) {
    return (
      <div className="text-center py-8 text-slate-500">
        <Clock className="w-8 h-8 mx-auto mb-2 opacity-50" />
        <p>No recent scan activity</p>
      </div>
    );
  }

  return (
    <div className="overflow-x-auto">
      <table className="w-full">
        <thead>
          <tr className="border-b border-slate-200">
            <th className="text-left py-3 px-2 text-xs font-medium text-slate-500 uppercase">Type</th>
            <th className="text-left py-3 px-2 text-xs font-medium text-slate-500 uppercase">Target</th>
            <th className="text-left py-3 px-2 text-xs font-medium text-slate-500 uppercase">Risk</th>
            <th className="text-left py-3 px-2 text-xs font-medium text-slate-500 uppercase">Score</th>
            <th className="text-left py-3 px-2 text-xs font-medium text-slate-500 uppercase">Verdict</th>
            <th className="text-right py-3 px-2 text-xs font-medium text-slate-500 uppercase">Time</th>
          </tr>
        </thead>
        <tbody>
          {scans.map((scan) => (
            <tr key={scan.id} className="border-b border-slate-100 hover:bg-slate-50 transition-colors">
              <td className="py-3 px-2">
                <div className="flex items-center gap-2">
                  <div className="w-8 h-8 bg-slate-100 rounded-lg flex items-center justify-center text-slate-500">
                    {getKindIcon(scan.kind)}
                  </div>
                  <span className="text-sm font-medium text-slate-700 capitalize">{scan.kind}</span>
                </div>
              </td>
              <td className="py-3 px-2">
                <span className="text-sm text-slate-600 font-mono truncate max-w-[200px] block">
                  {scan.inputPreview}
                </span>
              </td>
              <td className="py-3 px-2">
                {getRiskBadge(scan.riskLevel)}
              </td>
              <td className="py-3 px-2">
                <span className="text-sm font-semibold text-slate-700">{scan.riskScore}</span>
                <span className="text-xs text-slate-400">/10</span>
              </td>
              <td className="py-3 px-2">
                <span className="text-sm text-slate-600">{scan.verdict}</span>
              </td>
              <td className="py-3 px-2 text-right">
                <span className="text-xs text-slate-400">{formatDate(scan.createdAt)}</span>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
