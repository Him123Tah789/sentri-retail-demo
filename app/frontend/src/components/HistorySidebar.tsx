"use client";

import { useEffect, useState } from "react";
import { getHistory, ConversationSummary } from "@/lib/api";
import { Mode } from "@/lib/types";

type HistorySidebarProps = {
    onSelect: (cid: string) => void;
    isOpen: boolean;
    setIsOpen: (o: boolean) => void;
};

export default function HistorySidebar({ onSelect, isOpen, setIsOpen }: HistorySidebarProps) {
    const [history, setHistory] = useState<ConversationSummary[]>([]);
    const [loading, setLoading] = useState(false);

    // Poll for history updates every time drawer opens or mount
    useEffect(() => {
        if (isOpen) {
            loadHistory();
        }
    }, [isOpen]);

    async function loadHistory() {
        setLoading(true);
        try {
            const res = await getHistory();
            setHistory(res.conversations);
        } catch (e) {
            console.error(e);
        } finally {
            setLoading(false);
        }
    }

    return (
        <>
            {/* Toggle Button (visible when closed) */}
            {!isOpen && (
                <button
                    onClick={() => setIsOpen(true)}
                    className="fixed left-4 top-20 z-20 p-2 bg-white border border-slate-200 rounded-lg shadow-sm hover:shadow-md transition-shadow"
                    title="Open History"
                >
                    📜
                </button>
            )}

            {/* Sidebar Overlay */}
            {isOpen && (
                <div
                    className="fixed inset-0 z-30 bg-black/20"
                    onClick={() => setIsOpen(false)}
                />
            )}

            {/* Sidebar Panel */}
            <div
                className={`fixed inset-y-0 left-0 z-40 w-64 bg-white border-r border-slate-200 shadow-xl transform transition-transform duration-200 ${isOpen ? 'translate-x-0' : '-translate-x-full'}`}
            >
                <div className="p-4 border-b border-slate-200 flex justify-between items-center">
                    <h2 className="font-bold text-slate-800">History</h2>
                    <button onClick={() => setIsOpen(false)} className="text-slate-400 hover:text-slate-600">✕</button>
                </div>

                <div className="overflow-y-auto h-[calc(100vh-60px)] p-2 space-y-2">
                    {loading && <div className="text-center p-4 text-slate-400 text-sm">Loading...</div>}

                    {!loading && history.length === 0 && (
                        <div className="text-center p-4 text-slate-400 text-sm">No history yet.</div>
                    )}

                    {history.map((h) => (
                        <div
                            key={h.id}
                            onClick={() => {
                                onSelect(h.id);
                                setIsOpen(false);
                            }}
                            className="p-3 bg-slate-50 hover:bg-slate-100 rounded-lg cursor-pointer border border-transparent hover:border-slate-200 transition-colors"
                        >
                            <div className="flex items-center justify-between mb-1">
                                <span className={`text-xs px-2 py-0.5 rounded-full ${h.mode === 'security' ? 'bg-blue-100 text-blue-700' : 'bg-emerald-100 text-emerald-700'}`}>
                                    {h.mode}
                                </span>
                                <span className="text-xs text-slate-400">
                                    {new Date(h.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                                </span>
                            </div>
                            <p className="text-sm text-slate-700 font-medium truncate">
                                {h.preview}
                            </p>
                            <p className="text-xs text-slate-400 mt-1">
                                {h.message_count} messages
                            </p>
                        </div>
                    ))}

                    <button
                        onClick={loadHistory}
                        className="w-full text-center text-xs text-slate-400 py-2 hover:text-slate-600"
                    >
                        Refresh List
                    </button>
                </div>
            </div>
        </>
    );
}
