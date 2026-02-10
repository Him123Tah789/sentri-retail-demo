'use client';

import { useState, useEffect, useCallback } from 'react';
import { useRouter } from 'next/navigation';
import { isAuthenticated } from '@/lib/auth';
import HeaderStatus from '@/components/HeaderStatus';
import InsightCard from '@/components/InsightCard';
import ActivityTable from '@/components/ActivityTable';
import { Shield, AlertTriangle, CheckCircle, Activity, TrendingUp, Eye, RefreshCw, Trash2 } from 'lucide-react';
import { scanHistory, onScanAdded, getRiskColor, StoredScan } from '@/lib/demoScenarios';
import { ScanEvent } from '@/lib/types';

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
    if (!isAuthenticated()) {
      router.push('/login');
      return;
    }
    loadDashboardData();
    
    // Subscribe to new scans for real-time updates
    const unsubscribe = onScanAdded(() => {
      loadDashboardData();
    });

    return () => unsubscribe();
  }, [router, loadDashboardData]);

  // Auto-refresh every 30 seconds
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
        {/* Guardian Status Banner */}
        <div className={`rounded-xl border-2 p-6 ${getStatusBg(protectionLevel)}`}>
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              <div className={`p-3 rounded-xl ${
                protectionLevel === 'ACTIVE' ? 'bg-green-100' :
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
            <div className="text-right flex items-center gap-4">
              <div>
                <p className="text-sm text-slate-500">Last Updated</p>
                <p className="font-medium text-slate-700">
                  {lastUpdated.toLocaleTimeString()}
                </p>
              </div>
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

        {/* Stats Grid - Real Dynamic Data */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          <InsightCard
            icon={<Eye className="w-6 h-6" />}
            title="Items Analyzed"
            value={stats?.todayCount || 0}
            subtitle={`${stats?.total || 0} total`}
            color="blue"
          />
          <InsightCard
            icon={<AlertTriangle className="w-6 h-6" />}
            title="High Risk Blocked"
            value={stats?.todayHighRisk || 0}
            subtitle="Today"
            color="red"
          />
          <InsightCard
            icon={<CheckCircle className="w-6 h-6" />}
            title="Safe Scans"
            value={stats?.todaySafe || 0}
            subtitle="Low risk today"
            color="green"
          />
          <InsightCard
            icon={<TrendingUp className="w-6 h-6" />}
            title="Avg Risk Score"
            value={stats?.avgRiskScore?.toFixed(1) || '0.0'}
            subtitle="Out of 10"
            color="purple"
          />
        </div>

        {/* Main Content Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Risk Distribution */}
          <div className="lg:col-span-2 card">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-lg font-semibold text-slate-800">Risk Distribution</h2>
              <Activity className="w-5 h-5 text-slate-400" />
            </div>
            
            <div className="grid grid-cols-4 gap-4">
              <div className="p-4 bg-green-50 rounded-lg text-center">
                <p className="text-2xl font-bold text-green-600">{stats?.byLevel.low || 0}</p>
                <p className="text-sm text-green-700">Safe</p>
                <p className="text-xs text-green-500">Score 1-3</p>
              </div>
              <div className="p-4 bg-yellow-50 rounded-lg text-center">
                <p className="text-2xl font-bold text-yellow-600">{stats?.byLevel.medium || 0}</p>
                <p className="text-sm text-yellow-700">Caution</p>
                <p className="text-xs text-yellow-500">Score 4-6</p>
              </div>
              <div className="p-4 bg-orange-50 rounded-lg text-center">
                <p className="text-2xl font-bold text-orange-600">{stats?.byLevel.high || 0}</p>
                <p className="text-sm text-orange-700">High Risk</p>
                <p className="text-xs text-orange-500">Score 7-8</p>
              </div>
              <div className="p-4 bg-red-50 rounded-lg text-center">
                <p className="text-2xl font-bold text-red-600">{stats?.byLevel.critical || 0}</p>
                <p className="text-sm text-red-700">Critical</p>
                <p className="text-xs text-red-500">Score 9-10</p>
              </div>
            </div>

            {/* Scan Types */}
            <div className="mt-6 pt-4 border-t border-slate-200">
              <h3 className="text-sm font-medium text-slate-600 mb-3">Scans by Type</h3>
              <div className="flex gap-4">
                <div className="flex items-center gap-2">
                  <span className="w-3 h-3 rounded-full bg-blue-500"></span>
                  <span className="text-sm text-slate-600">Links: {stats?.byKind.link || 0}</span>
                </div>
                <div className="flex items-center gap-2">
                  <span className="w-3 h-3 rounded-full bg-purple-500"></span>
                  <span className="text-sm text-slate-600">Emails: {stats?.byKind.email || 0}</span>
                </div>
                <div className="flex items-center gap-2">
                  <span className="w-3 h-3 rounded-full bg-orange-500"></span>
                  <span className="text-sm text-slate-600">Logs: {stats?.byKind.logs || 0}</span>
                </div>
              </div>
            </div>
          </div>

          {/* Quick Actions */}
          <div className="card">
            <h2 className="text-lg font-semibold text-slate-800 mb-4">Quick Actions</h2>
            <div className="space-y-3">
              <button
                onClick={() => router.push('/assistant')}
                className="w-full btn-primary text-left flex items-center gap-3"
              >
                <Shield className="w-5 h-5" />
                <span>Open AI Assistant</span>
              </button>
              <button
                onClick={loadDashboardData}
                className="w-full btn-secondary text-left flex items-center gap-3"
              >
                <RefreshCw className="w-5 h-5" />
                <span>Refresh Data</span>
              </button>
              <button
                onClick={handleClearHistory}
                className="w-full px-4 py-2 border border-red-200 text-red-600 rounded-lg hover:bg-red-50 text-left flex items-center gap-3 transition-colors"
              >
                <Trash2 className="w-5 h-5" />
                <span>Clear History</span>
              </button>
            </div>

            {/* Auto-refresh Toggle */}
            <div className="mt-4 pt-4 border-t border-slate-200">
              <label className="flex items-center gap-2 cursor-pointer">
                <input
                  type="checkbox"
                  checked={autoRefresh}
                  onChange={(e) => setAutoRefresh(e.target.checked)}
                  className="w-4 h-4 rounded border-slate-300"
                />
                <span className="text-sm text-slate-600">Auto-refresh (30s)</span>
              </label>
            </div>
          </div>
        </div>

        {/* Recent Activity */}
        <div className="card">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-lg font-semibold text-slate-800">Recent Scan Activity</h2>
            <span className="text-sm text-slate-500">
              {recentScans.length} {recentScans.length === 1 ? 'scan' : 'scans'}
            </span>
          </div>
          <ActivityTable scans={recentScans} />
        </div>
      </main>
    </div>
  );
}
