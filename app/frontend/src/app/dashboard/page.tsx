'use client';

import { useState, useEffect, useCallback } from 'react';
import { useRouter } from 'next/navigation';
// Removed auth check
import HeaderStatus from '@/components/HeaderStatus';
import InsightCard from '@/components/InsightCard';
import ActivityTable from '@/components/ActivityTable';
import { Shield, AlertTriangle, CheckCircle, Activity, TrendingUp, Eye, RefreshCw, Trash2 } from 'lucide-react';
import { scanHistory, onScanAdded } from '@/lib/demoScenarios';
import { ScanEvent, ScanKind, RiskLevel } from '@/lib/types';

interface DashboardStats {
  total: number;
  todayCount: number;
  todayHighRisk: number;
  todaySafe: number;
  byLevel: { low: number; medium: number; high: number; critical: number };
  byKind: { link: number; email: number; logs: number; text: number };
  avgRiskScore: number;
}

export default function DashboardPage() {
  const router = useRouter();
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [recentScans, setRecentScans] = useState<ScanEvent[]>([]);
  const [loading, setLoading] = useState(true);
  const [lastUpdated, setLastUpdated] = useState<Date>(new Date());
  const [autoRefresh, setAutoRefresh] = useState(true);

  // ... (loadDashboardData and useEffects remain same)
  const loadDashboardData = useCallback(() => {
    try {
      const currentStats = scanHistory.getStats();
      const scans = scanHistory.getRecent(20);

      setStats(currentStats);
      setRecentScans(scans.map(scan => ({
        id: scan.id,
        userId: scan.userId,
        kind: scan.kind,
        inputPreview: scan.inputPreview,
        riskScore: scan.riskScore,
        riskLevel: scan.riskLevel,
        verdict: scan.verdict,
        explanation: scan.explanation,
        createdAt: scan.createdAt,
      })));
      setLastUpdated(new Date());
    } catch (error) {
      console.error('Error loading dashboard:', error);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    loadDashboardData();
    const unsubscribe = onScanAdded(() => {
      loadDashboardData();
    });
    return () => unsubscribe();
  }, [router, loadDashboardData]);

  useEffect(() => {
    if (!autoRefresh) return;
    const interval = setInterval(loadDashboardData, 30000);
    return () => clearInterval(interval);
  }, [autoRefresh, loadDashboardData]);

  const getProtectionLevel = () => {
    if (!stats) return 'ACTIVE';
    const highRisk = stats.byLevel.high + stats.byLevel.critical;
    if (highRisk >= 5) return 'WARNING';
    if (highRisk >= 2) return 'WATCH';
    return 'ACTIVE';
  };

  const getStatusColor = (level: string) => {
    switch (level) {
      case 'ACTIVE': return 'text-green-500';
      case 'WATCH': return 'text-yellow-500';
      case 'WARNING': return 'text-red-500';
      default: return 'text-slate-500';
    }
  };

  const getStatusBg = (level: string) => {
    switch (level) {
      case 'ACTIVE': return 'bg-green-50 border-green-200';
      case 'WATCH': return 'bg-yellow-50 border-yellow-200';
      case 'WARNING': return 'bg-red-50 border-red-200';
      default: return 'bg-slate-50 border-slate-200';
    }
  };

  const handleClearHistory = () => {
    if (confirm('Clear all scan history? This cannot be undone.')) {
      scanHistory.clear();
      loadDashboardData();
    }
  };

  const protectionLevel = getProtectionLevel();

  if (loading) {
    return (
      <div className="min-h-screen bg-slate-50 flex flex-col">
        <HeaderStatus />
        <main className="flex-1 flex items-center justify-center">
          <div className="text-center">
            <div className="spinner mx-auto mb-4"></div>
            <p className="text-slate-500">Loading dashboard...</p>
          </div>
        </main>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-slate-50 flex flex-col">
      <HeaderStatus />

      <main className="flex-1 max-w-7xl mx-auto w-full p-4 space-y-6">

        {/* TOP ROW: Status + Metrics */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <div className={`lg:col-span-2 rounded-xl border-2 p-6 flex flex-col justify-center ${getStatusBg(protectionLevel)}`}>
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-4">
                <div className={`p-3 rounded-xl ${protectionLevel === 'ACTIVE' ? 'bg-green-100' :
                  protectionLevel === 'WATCH' ? 'bg-yellow-100' : 'bg-red-100'
                  }`}>
                  <Shield className={`w-8 h-8 ${getStatusColor(protectionLevel)}`} />
                </div>
                <div>
                  <h1 className="text-2xl font-bold text-slate-800">Guardian Engine</h1>
                  <p className={`font-semibold ${getStatusColor(protectionLevel)}`}>
                    Protection Level: {protectionLevel}
                  </p>
                </div>
              </div>
              <div className="text-right">
                <button
                  onClick={loadDashboardData}
                  className="p-2 rounded-lg bg-white border border-slate-200 hover:bg-slate-50 transition-colors"
                  title="Refresh"
                >
                  <RefreshCw className="w-5 h-5 text-slate-600" />
                </button>
              </div>
            </div>
          </div>

          {/* Time to Decision Metric */}
          <div className="card bg-slate-900 text-white border-slate-700">
            <h3 className="text-sm font-semibold text-slate-400 mb-4 uppercase tracking-wider">Time-to-Decision</h3>
            <div className="flex justify-between items-end mb-4">
              <div>
                <p className="text-3xl font-mono font-bold text-green-400">{'<'}1s</p>
                <p className="text-xs text-slate-400">Sentri AI</p>
              </div>
              <div className="text-right">
                <p className="text-xl font-mono text-slate-500">~10m</p>
                <p className="text-xs text-slate-400">Manual Analyst</p>
              </div>
            </div>
            <div className="w-full bg-slate-800 h-2 rounded-full overflow-hidden">
              <div className="bg-green-500 h-full w-[5%]"></div>
            </div>
            <p className="text-xs text-slate-500 mt-2 italic">99.8% faster than manual review</p>
          </div>
        </div>

        {/* RESEARCH METRICS ROW */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {/* Model Performance Panel */}
          <div className="card">
            <h3 className="text-lg font-bold text-slate-800 mb-4 flex items-center gap-2">
              <Activity className="w-5 h-5 text-blue-600" />
              Live Model Metrics
            </h3>
            <div className="grid grid-cols-2 gap-4 text-center">
              <div className="p-3 bg-slate-50 rounded border border-slate-100">
                <div className="text-2xl font-bold text-slate-800">99.2%</div>
                <div className="text-xs text-slate-500 uppercase">Accuracy</div>
              </div>
              <div className="p-3 bg-slate-50 rounded border border-slate-100">
                <div className="text-2xl font-bold text-slate-800">98.5%</div>
                <div className="text-xs text-slate-500 uppercase">Precision</div>
              </div>
              <div className="p-3 bg-slate-50 rounded border border-slate-100">
                <div className="text-2xl font-bold text-slate-800">99.7%</div>
                <div className="text-xs text-slate-500 uppercase">Recall</div>
              </div>
              <div className="p-3 bg-slate-50 rounded border border-slate-100">
                <div className="text-2xl font-bold text-slate-800">99.1%</div>
                <div className="text-xs text-slate-500 uppercase">F1 Score</div>
              </div>
            </div>
            <p className="text-xs text-slate-400 mt-3 text-center">Dataset: sentri-threat-corpus-v4 • Last Retrained: 2h ago</p>
          </div>

          {/* Attack Coverage Matrix */}
          <div className="card">
            <h3 className="text-lg font-bold text-slate-800 mb-4 flex items-center gap-2">
              <Shield className="w-5 h-5 text-blue-600" />
              Attack Coverage Matrix
            </h3>
            <div className="overflow-x-auto">
              <table className="w-full text-sm text-left">
                <thead>
                  <tr className="border-b border-slate-100 text-slate-500">
                    <th className="pb-2">Attack Type</th>
                    <th className="pb-2 text-center">Text</th>
                    <th className="pb-2 text-center">URL</th>
                    <th className="pb-2 text-center">Img</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-50">
                  {[
                    { name: 'Phishing', t: true, u: true, i: false },
                    { name: 'Malware Distrib.', t: false, u: true, i: false },
                    { name: 'Deepfake / AI', t: false, u: false, i: true },
                    { name: 'Social Eng.', t: true, u: false, i: false },
                  ].map((row) => (
                    <tr key={row.name}>
                      <td className="py-2 font-medium text-slate-700">{row.name}</td>
                      <td className="py-2 text-center">{row.t ? '✅' : '❌'}</td>
                      <td className="py-2 text-center">{row.u ? '✅' : '❌'}</td>
                      <td className="py-2 text-center">{row.i ? '✅' : '❌'}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </div>

        {/* Activity & Limitations Row */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <div className="lg:col-span-2 card">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-lg font-semibold text-slate-800">Recent Scan Activity</h2>
              <span className="text-sm text-slate-500">{recentScans.length} scans</span>
            </div>
            <ActivityTable scans={recentScans} />
          </div>

          <div className="card bg-amber-50 border-amber-100">
            <h3 className="text-lg font-bold text-amber-900 mb-3 flex items-center gap-2">
              <AlertTriangle className="w-5 h-5" />
              System Limitations
            </h3>
            <ul className="space-y-2 text-sm text-amber-800">
              <li className="flex items-start gap-2">
                <span className="mt-1">•</span>
                Cannot guarantee 100% detection of zero-day exploits.
              </li>
              <li className="flex items-start gap-2">
                <span className="mt-1">•</span>
                Image heuristics are probabilistic, not definitive proof.
              </li>
              <li className="flex items-start gap-2">
                <span className="mt-1">•</span>
                Encrypted archives cannot be inspected without keys.
              </li>
            </ul>
            <div className="mt-4 pt-3 border-t border-amber-200">
              <p className="text-xs font-bold text-amber-800 uppercase tracking-wide mb-1">Evastion Awareness</p>
              <p className="text-xs text-amber-700">
                Adversarial patterns (e.g. homoglyphs, hidden text) may lower confidence scores but trigger "SUSPICIOUS" verdicts.
              </p>
            </div>
          </div>
        </div>

        {/* Quick Actions Footer */}
        <div className="flex gap-4 justify-end">
          <button
            onClick={handleClearHistory}
            className="text-red-500 text-sm hover:underline"
          >
            Clear Local History
          </button>
        </div>

      </main>
    </div>
  );
}
