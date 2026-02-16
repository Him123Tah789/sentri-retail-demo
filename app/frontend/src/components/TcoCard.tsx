'use client';

import React from 'react';

interface TcoBreakdown {
    depreciation: number;
    financing: number;
    fuel_or_energy: number;
    insurance: number;
    tax: number;
    maintenance: number;
    tires: number;
    fees: number;
}

interface TcoResult {
    total: number;
    per_year: number;
    per_month: number;
    breakdown: TcoBreakdown;
}

interface TcoCardProps {
    result: TcoResult;
    vehicleName?: string;
}

export default function TcoCard({ result, vehicleName }: TcoCardProps) {
    const b = result.breakdown;
    const items = [
        { label: 'Depreciation', value: b.depreciation, color: '#ef4444' },
        { label: 'Fuel / Energy', value: b.fuel_or_energy, color: '#f59e0b' },
        { label: 'Insurance', value: b.insurance, color: '#3b82f6' },
        { label: 'Tax', value: b.tax, color: '#8b5cf6' },
        { label: 'Maintenance', value: b.maintenance, color: '#10b981' },
        { label: 'Tires', value: b.tires, color: '#6366f1' },
        { label: 'Financing', value: b.financing, color: '#ec4899' },
        { label: 'Fees', value: b.fees, color: '#64748b' },
    ];

    const max = Math.max(...items.map((i) => i.value), 1);

    return (
        <div className="tco-card">
            <div className="tco-header">
                <h3>{vehicleName ? `TCO — ${vehicleName}` : 'TCO Breakdown'}</h3>
                <div className="tco-totals">
                    <div className="total-item">
                        <span className="total-label">Total</span>
                        <span className="total-value">${result.total.toLocaleString()}</span>
                    </div>
                    <div className="total-item">
                        <span className="total-label">Per Year</span>
                        <span className="total-value">${result.per_year.toLocaleString()}</span>
                    </div>
                    <div className="total-item">
                        <span className="total-label">Per Month</span>
                        <span className="total-value">${result.per_month.toLocaleString()}</span>
                    </div>
                </div>
            </div>

            <div className="tco-bars">
                {items.map((item) => (
                    <div key={item.label} className="bar-row">
                        <span className="bar-label">{item.label}</span>
                        <div className="bar-track">
                            <div
                                className="bar-fill"
                                style={{
                                    width: `${(item.value / max) * 100}%`,
                                    background: item.color,
                                }}
                            />
                        </div>
                        <span className="bar-value">${item.value.toLocaleString()}</span>
                    </div>
                ))}
            </div>

            <style jsx>{`
        .tco-card {
          background: rgba(255, 255, 255, 0.03);
          border: 1px solid rgba(255, 255, 255, 0.08);
          border-radius: 16px;
          padding: 24px;
          margin: 12px 0;
        }
        .tco-header h3 {
          font-size: 1rem;
          font-weight: 600;
          color: #e2e8f0;
          margin: 0 0 16px 0;
        }
        .tco-totals {
          display: flex;
          gap: 24px;
          margin-bottom: 20px;
          padding-bottom: 16px;
          border-bottom: 1px solid rgba(255, 255, 255, 0.06);
        }
        .total-item {
          display: flex;
          flex-direction: column;
          gap: 4px;
        }
        .total-label {
          font-size: 0.75rem;
          color: rgba(255, 255, 255, 0.4);
          text-transform: uppercase;
          letter-spacing: 0.05em;
        }
        .total-value {
          font-size: 1.15rem;
          font-weight: 700;
          color: #f1f5f9;
        }
        .tco-bars {
          display: flex;
          flex-direction: column;
          gap: 10px;
        }
        .bar-row {
          display: flex;
          align-items: center;
          gap: 12px;
        }
        .bar-label {
          width: 100px;
          font-size: 0.8rem;
          color: rgba(255, 255, 255, 0.6);
          flex-shrink: 0;
        }
        .bar-track {
          flex: 1;
          height: 8px;
          background: rgba(255, 255, 255, 0.05);
          border-radius: 4px;
          overflow: hidden;
        }
        .bar-fill {
          height: 100%;
          border-radius: 4px;
          transition: width 0.5s ease;
        }
        .bar-value {
          width: 80px;
          text-align: right;
          font-size: 0.8rem;
          color: rgba(255, 255, 255, 0.7);
          font-weight: 500;
          flex-shrink: 0;
        }
      `}</style>
        </div>
    );
}
