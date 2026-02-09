'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { isAuthenticated } from '@/lib/auth';
import HeaderStatus from '@/components/HeaderStatus';
import InsightCard from '@/components/InsightCard';
import ActivityTable from '@/components/ActivityTable';
import { Shield, AlertTriangle, CheckCircle, Activity, TrendingUp, Eye } from 'lucide-react';
import { getGuardianStatus, getGuardianSummary, getRecentScans } from '@/lib/api';
import { GuardianStatus, GuardianSummary, ScanEvent } from '@/lib/types';

export default function DashboardPage() {
  const router = useRouter();
  const [guardianStatus, setGuardianStatus] = useState<GuardianStatus | null>(null);
  const [guardianSummary, setGuardianSummary] = useState<GuardianSummary | null>(null);
  const [recentScans, setRecentScans] = useState<ScanEvent[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!isAuthenticated()) {
      router.push('/login');
      return;
    }
    loadDashboardData();
  }, [router]);

  const loadDashboardData = async () => {
    try {
      const [status, summary, scans] = await Promise.all([
        getGuardianStatus(),
        getGuardianSummary(),
        getRecentScans(10),
      ]);
      setGuardianStatus(status);
      setGuardianSummary(summary);
      setRecentScans(scans);
    } catch (error) {
      console.error('Error loading dashboard:', error);
    } finally {
      setLoading(false);
    }
  };

  const getStatusColor = (level: string) => {
    switch (level) {
      case 'ACTIVE':
        return 'text-green-500';
      case 'WATCH':
        return 'text-yellow-500';
      case 'WARNING':
        return 'text-red-500';
      default:
        return 'text-slate-500';
    }
  };

  const getStatusBg = (level: string) => {
    switch (level) {
      case 'ACTIVE':
        return 'bg-green-50 border-green-200';
      case 'WATCH':
        return 'bg-yellow-50 border-yellow-200';
      case 'WARNING':
        return 'bg-red-50 border-red-200';
      default:
        return 'bg-slate-50 border-slate-200';
    }
  };

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
        {guardianStatus && (
          <div className={`rounded-xl border-2 p-6 ${getStatusBg(guardianStatus.protectionLevel)}`}>
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-4">
                <div className={`p-3 rounded-xl ${
                  guardianStatus.protectionLevel === 'ACTIVE' ? 'bg-green-100' :
                  guardianStatus.protectionLevel === 'WATCH' ? 'bg-yellow-100' : 'bg-red-100'
                }`}>
                  <Shield className={`w-8 h-8 ${getStatusColor(guardianStatus.protectionLevel)}`} />
                </div>
                <div>
                  <h1 className="text-2xl font-bold text-slate-800">Guardian Engine</h1>
                  <p className={`font-semibold ${getStatusColor(guardianStatus.protectionLevel)}`}>
                    Protection Level: {guardianStatus.protectionLevel}
                  </p>
                </div>
              </div>
              <div className="text-right">
                <p className="text-sm text-slate-500">Last Updated</p>
                <p className="font-medium text-slate-700">
                  {new Date().toLocaleTimeString()}
                </p>
              </div>
            </div>
          </div>
        )}

        {/* Stats Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          <InsightCard
            icon={<Eye className="w-6 h-6" />}
            title="Items Analyzed"
            value={guardianSummary?.itemsAnalyzed || 0}
            subtitle="Today"
            color="blue"
          />
          <InsightCard
            icon={<AlertTriangle className="w-6 h-6" />}
            title="High Risk Blocked"
            value={guardianSummary?.highRiskBlocked || 0}
            subtitle="Threats stopped"
            color="red"
          />
          <InsightCard
            icon={<CheckCircle className="w-6 h-6" />}
            title="Safe Scans"
            value={recentScans.filter(s => s.riskLevel === 'low').length}
            subtitle="Low risk"
            color="green"
          />
          <InsightCard
            icon={<TrendingUp className="w-6 h-6" />}
            title="Scan Accuracy"
            value="99.2%"
            subtitle="Detection rate"
            color="purple"
          />
        </div>

        {/* Main Content Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Today's Summary */}
          <div className="lg:col-span-2 card">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-lg font-semibold text-slate-800">Today's Security Summary</h2>
              <Activity className="w-5 h-5 text-slate-400" />
            </div>
            
            {guardianSummary && (
              <div className="space-y-4">
                <div className="p-4 bg-slate-50 rounded-lg">
                  <p className="text-slate-700 leading-relaxed">
                    {guardianSummary.summaryText}
                  </p>
                </div>
                
                {guardianSummary.topThreat && (
                  <div className="p-4 bg-red-50 border border-red-200 rounded-lg">
                    <h3 className="font-semibold text-red-800 mb-1">Top Threat Detected</h3>
                    <p className="text-red-700 text-sm">{guardianSummary.topThreat}</p>
                  </div>
                )}
              </div>
            )}
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
                <Activity className="w-5 h-5" />
                <span>Refresh Data</span>
              </button>
            </div>
          </div>
        </div>

        {/* Recent Activity */}
        <div className="card">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-lg font-semibold text-slate-800">Recent Scan Activity</h2>
            <span className="text-sm text-slate-500">{recentScans.length} scans</span>
          </div>
          <ActivityTable scans={recentScans} />
        </div>
      </main>
    </div>
  );
}
