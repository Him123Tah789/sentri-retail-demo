"use client";

import { useEffect, useRef, useState } from "react";
import type { Mode } from "@/lib/types";

type VoiceControlsProps = {
    mode: Mode;
    setMode: (m: Mode) => void;
    onSendText: (text: string) => void;     // send chat message
    onAction: (action: string) => void;     // trigger buttons (tco, scan, sensitivity)
    lastAssistantReply?: string;            // for speak-back
};

declare global {
    interface Window {
        webkitSpeechRecognition?: any;
        SpeechRecognition?: any;
    }
}

export default function VoiceControls({
    mode,
    setMode,
    onSendText,
    onAction,
    lastAssistantReply,
}: VoiceControlsProps) {
    const [supported, setSupported] = useState(false);
    const [listening, setListening] = useState(false);
    const [transcript, setTranscript] = useState("");
    const [autoSpeak, setAutoSpeak] = useState(false);

    const recognitionRef = useRef<any>(null);

    useEffect(() => {
        const SR = window.SpeechRecognition || window.webkitSpeechRecognition;
        if (!SR) {
            setSupported(false);
            return;
        }
        setSupported(true);

        const rec = new SR();
        rec.continuous = false;       // keep simple & reliable
        rec.interimResults = true;    // show live text
        rec.lang = "en-US";           // change if needed (e.g., "bn-BD")

        rec.onstart = () => {
            setListening(true);
            setTranscript("");
        };

        rec.onresult = (event: any) => {
            let finalText = "";
            let interim = "";

            for (let i = event.resultIndex; i < event.results.length; i++) {
                const txt = event.results[i][0].transcript;
                if (event.results[i].isFinal) finalText += txt;
                else interim += txt;
            }

            setTranscript((finalText + interim).trim());
        };

        rec.onerror = () => {
            setListening(false);
        };

        rec.onend = () => {
            setListening(false);
            const text = transcriptRef.current.trim();
            if (text) handleVoiceText(text);
        };

        recognitionRef.current = rec;
    }, []);

    // Keep latest transcript in a ref to avoid stale closure in onend
    const transcriptRef = useRef("");
    useEffect(() => {
        transcriptRef.current = transcript;
    }, [transcript]);

    function startListening() {
        if (!recognitionRef.current) return;
        try {
            recognitionRef.current.start();
        } catch {
            // start() can throw if already started
        }
    }

    function stopListening() {
        if (!recognitionRef.current) return;
        try {
            recognitionRef.current.stop();
        } catch { }
    }

    function speak(text: string) {
        if (!("speechSynthesis" in window)) return;
        const u = new SpeechSynthesisUtterance(text);
        u.rate = 1.0;
        u.pitch = 1.0;
        window.speechSynthesis.cancel();
        window.speechSynthesis.speak(u);
    }

    // Simple voice command parser (extend anytime)
    function handleVoiceText(text: string) {
        const t = text.toLowerCase();

        // Mode switching commands
        if (t.includes("switch to security") || t.includes("security mode")) {
            setMode("security");
            return;
        }
        if (t.includes("switch to automotive") || t.includes("automotive mode") || t.includes("car mode")) {
            setMode("automotive");
            return;
        }

        // Action commands
        if (mode === "security") {
            if (t.includes("scan link")) return onAction("scan_link");
            if (t.includes("analyze email") || t.includes("scan email")) return onAction("scan_email");
            if (t.includes("summarize logs") || t.includes("scan logs")) return onAction("scan_logs");
        } else {
            if (t.includes("calculate tco") || t.includes("tco")) return onAction("auto_tco");
            if (t.includes("fuel sensitivity") || (t.includes("sensitivity") && t.includes("fuel")))
                return onAction("auto_sensitivity_fuel");
            if (t.includes("mileage sensitivity") || (t.includes("sensitivity") && (t.includes("mileage") || t.includes("kilometer"))))
                return onAction("auto_sensitivity_km");
        }

        // Otherwise: send as normal chat message
        onSendText(text);
    }

    // Speak back automatically when reply changes (optional)
    useEffect(() => {
        if (!autoSpeak) return;
        if (lastAssistantReply?.trim()) speak(lastAssistantReply);
    }, [lastAssistantReply, autoSpeak]);

    if (!supported) {
        return (
            <div className="rounded border border-zinc-700 p-3 bg-zinc-950 text-zinc-300 text-sm">
                Voice is not supported in this browser. Use Chrome or Edge for Speech-to-Text.
            </div>
        );
    }

    return (
        <div className="rounded border border-zinc-700 p-3 bg-zinc-950">
            <div className="flex flex-wrap items-center gap-3">
                <button
                    className={`px-3 py-2 rounded ${listening ? "bg-red-500 text-white" : "bg-white text-black"}`}
                    onMouseDown={startListening}
                    onMouseUp={stopListening}
                    onTouchStart={startListening}
                    onTouchEnd={stopListening}
                    title="Hold to talk"
                >
                    🎙️ {listening ? "Listening..." : "Hold to Talk"}
                </button>

                <button
                    className="px-3 py-2 rounded bg-zinc-800"
                    onClick={() => lastAssistantReply && speak(lastAssistantReply)}
                    disabled={!lastAssistantReply}
                    title="Speak last reply"
                >
                    🔊 Speak Reply
                </button>

                <label className="flex items-center gap-2 text-sm text-zinc-300">
                    <input
                        type="checkbox"
                        checked={autoSpeak}
                        onChange={(e) => setAutoSpeak(e.target.checked)}
                    />
                    Auto-speak replies
                </label>

                <div className="text-sm text-zinc-400">
                    Commands: “security mode”, “automotive mode”, “scan link”, “calculate tco”, “fuel sensitivity”
                </div>
            </div>

            <div className="mt-2 text-sm text-zinc-200">
                <span className="text-zinc-400">Transcript:</span>{" "}
                {transcript ? transcript : <span className="text-zinc-500">—</span>}
            </div>
        </div>
    );
}
