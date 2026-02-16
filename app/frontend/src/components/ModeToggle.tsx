'use client';

import React from 'react';

interface ModeToggleProps {
  mode: string;
  onModeChange: (mode: string) => void;
}

export default function ModeToggle({ mode, onModeChange }: ModeToggleProps) {
  return (
    <div className="mode-toggle">
      <button
        className={`mode-btn active`}
        onClick={() => { }}
        disabled
      >
        <span className="mode-icon">🛡️</span>
        <span className="mode-label">Security Protocol Active</span>
      </button>

      <style jsx>{`
        .mode-toggle {
          display: flex;
          gap: 8px;
          padding: 4px;
          background: rgba(255, 255, 255, 0.05);
          border-radius: 12px;
          border: 1px solid rgba(255, 255, 255, 0.1);
        }
        .mode-btn {
          display: flex;
          align-items: center;
          gap: 6px;
          padding: 8px 16px;
          border: none;
          border-radius: 8px;
          background: transparent;
          color: rgba(255, 255, 255, 0.5);
          cursor: pointer;
          font-size: 0.85rem;
          font-weight: 500;
          transition: all 0.2s ease;
        }
        .mode-btn.active {
          background: linear-gradient(135deg, #6366f1, #8b5cf6);
          color: #fff;
          box-shadow: 0 2px 8px rgba(99, 102, 241, 0.3);
          cursor: default;
        }
        .mode-icon {
          font-size: 1rem;
        }
        .mode-label {
          font-family: 'Inter', sans-serif;
        }
      `}</style>
    </div>
  );
}
