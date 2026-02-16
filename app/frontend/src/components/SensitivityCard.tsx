'use client';

import React from 'react';

interface SensitivityPoint {
    x: number;
    total: number;
    per_month: number;
}

interface SensitivityResult {
    slider: string;
    points: SensitivityPoint[];
}

interface SensitivityCardProps {
    result: SensitivityResult;
}

export default function SensitivityCard({ result }: SensitivityCardProps) {
    const pts = result.points;
    if (!pts || pts.length === 0) return null;

    const minTotal = Math.min(...pts.map((p) => p.total));
    const maxTotal = Math.max(...pts.map((p) => p.total));
    const range = maxTotal - minTotal || 1;

    const sliderLabels: Record<string, string> = {
        fuel_price: 'Fuel Price ($/L)',
        annual_km: 'Annual Distance (km)',
        interest_rate: 'Interest Rate',
    };

    const formatX = (x: number) => {
        if (result.slider === 'interest_rate') return `${(x * 100).toFixed(1)}%`;
        if (result.slider === 'annual_km') return `${(x / 1000).toFixed(0)}k km`;
        return `$${x.toFixed(2)}`;
    };

    // SVG chart dimensions
    const W = 400;
    const H = 180;
    const PAD = 40;
    const chartW = W - PAD * 2;
    const chartH = H - PAD * 2;

    const points = pts.map((p, i) => {
        const x = PAD + (i / (pts.length - 1)) * chartW;
        const y = PAD + chartH - ((p.total - minTotal) / range) * chartH;
        return { x, y, data: p };
    });

    const pathD = points.map((p, i) => `${i === 0 ? 'M' : 'L'} ${p.x} ${p.y}`).join(' ');
    const areaD = pathD + ` L ${points[points.length - 1].x} ${PAD + chartH} L ${points[0].x} ${PAD + chartH} Z`;

    return (
        <div className="sensitivity-card">
            <h3>🔄 What-If: {sliderLabels[result.slider] || result.slider}</h3>

            <svg viewBox={`0 0 ${W} ${H}`} className="chart">
                <defs>
                    <linearGradient id="areaGrad" x1="0" y1="0" x2="0" y2="1">
                        <stop offset="0%" stopColor="#6366f1" stopOpacity="0.3" />
                        <stop offset="100%" stopColor="#6366f1" stopOpacity="0.02" />
                    </linearGradient>
                </defs>

                {/* Grid lines */}
                {[0, 0.25, 0.5, 0.75, 1].map((f) => (
                    <line
                        key={f}
                        x1={PAD}
                        y1={PAD + chartH * (1 - f)}
                        x2={PAD + chartW}
                        y2={PAD + chartH * (1 - f)}
                        stroke="rgba(255,255,255,0.06)"
                        strokeDasharray="4"
                    />
                ))}

                {/* Area */}
                <path d={areaD} fill="url(#areaGrad)" />

                {/* Line */}
                <path d={pathD} fill="none" stroke="#6366f1" strokeWidth="2.5" strokeLinecap="round" />

                {/* Points */}
                {points.map((p, i) => (
                    <circle key={i} cx={p.x} cy={p.y} r="4" fill="#6366f1" stroke="#1e1b4b" strokeWidth="2" />
                ))}

                {/* X labels */}
                {points.map((p, i) => (
                    <text key={`xl-${i}`} x={p.x} y={H - 4} textAnchor="middle" fill="rgba(255,255,255,0.5)" fontSize="9">
                        {formatX(p.data.x)}
                    </text>
                ))}

                {/* Y labels */}
                {[0, 0.5, 1].map((f) => (
                    <text key={`yl-${f}`} x={PAD - 6} y={PAD + chartH * (1 - f) + 3} textAnchor="end" fill="rgba(255,255,255,0.4)" fontSize="8">
                        ${Math.round(minTotal + range * f).toLocaleString()}
                    </text>
                ))}
            </svg>

            <div className="sensitivity-summary">
                <span>
                    Range: <strong>${minTotal.toLocaleString()}</strong> — <strong>${maxTotal.toLocaleString()}</strong>
                </span>
                <span>Δ ${(maxTotal - minTotal).toLocaleString()}</span>
            </div>

            <style jsx>{`
        .sensitivity-card {
          background: rgba(255, 255, 255, 0.03);
          border: 1px solid rgba(255, 255, 255, 0.08);
          border-radius: 16px;
          padding: 24px;
          margin: 12px 0;
        }
        .sensitivity-card h3 {
          font-size: 1rem;
          font-weight: 600;
          color: #e2e8f0;
          margin: 0 0 16px 0;
        }
        .chart {
          width: 100%;
          max-width: 460px;
        }
        .sensitivity-summary {
          display: flex;
          justify-content: space-between;
          margin-top: 12px;
          padding-top: 12px;
          border-top: 1px solid rgba(255, 255, 255, 0.06);
          font-size: 0.8rem;
          color: rgba(255, 255, 255, 0.5);
        }
        .sensitivity-summary strong {
          color: #c4b5fd;
        }
      `}</style>
        </div>
    );
}
