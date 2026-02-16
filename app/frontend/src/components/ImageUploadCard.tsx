'use client';

import { useState, useRef } from 'react';
import { Upload, X, Shield, AlertTriangle, CheckCircle, FileImage, Loader2 } from 'lucide-react';

interface ImageScanResult {
    exif: {
        present: boolean;
        fields: Record<string, string>;
        note: string;
    };
    heuristics: {
        scores: {
            edge_detail_variance: number;
            repeat_texture_score: number;
            dct_highfreq_energy: number;
        };
        indicators: string[];
        type_guess: string;
    };
    assessment: {
        ai_likelihood_level: 'LOW' | 'MEDIUM' | 'HIGH';
        ai_likelihood_score: number;
        reasons: string[];
        recommended_actions: string[];
    };
    disclaimer: string;
}

interface ScanResponse {
    tool_result: ImageScanResult;
    assistant_explanation: string | null;
}

export default function ImageUploadCard() {
    const [file, setFile] = useState<File | null>(null);
    const [preview, setPreview] = useState<string | null>(null);
    const [result, setResult] = useState<ScanResponse | null>(null);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);
    const [useAI, setUseAI] = useState(false);
    const fileInputRef = useRef<HTMLInputElement>(null);

    const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        const selected = e.target.files?.[0];
        if (selected) {
            if (!selected.type.startsWith('image/')) {
                setError('Please select an image file (JPG, PNG, WebP)');
                return;
            }
            setFile(selected);
            setPreview(URL.createObjectURL(selected));
            setResult(null);
            setError(null);
        }
    };

    const clearFile = () => {
        setFile(null);
        setPreview(null);
        setResult(null);
        setError(null);
        if (fileInputRef.current) {
            fileInputRef.current.value = '';
        }
    };

    const handleScan = async () => {
        if (!file) return;

        setLoading(true);
        setError(null);

        try {
            const formData = new FormData();
            formData.append('file', file);

            // Use query param for use_llm as expected by FastAPI default
            const res = await fetch(`http://localhost:8000/scan/image?use_llm=${useAI}`, {
                method: 'POST',
                body: formData,
            });

            if (!res.ok) {
                throw new Error('Scan failed. Please try again.');
            }

            const data = await res.json();
            if (data.error) {
                throw new Error(data.error);
            }
            setResult(data);
        } catch (err) {
            setError(err instanceof Error ? err.message : 'An error occurred during scanning');
        } finally {
            setLoading(false);
        }
    };

    const getLikelihoodColor = (level: string) => {
        switch (level) {
            case 'LOW': return 'text-green-600 bg-green-50 border-green-200';
            case 'MEDIUM': return 'text-yellow-600 bg-yellow-50 border-yellow-200';
            case 'HIGH': return 'text-red-600 bg-red-50 border-red-200';
            default: return 'text-slate-600 bg-slate-50 border-slate-200';
        }
    };

    return (
        <div className="card p-4 space-y-4">
            <div className="flex items-center justify-between">
                <h3 className="font-semibold text-slate-800 flex items-center gap-2">
                    <FileImage className="w-5 h-5 text-blue-500" />
                    AI Image Scanner
                </h3>
                {file && (
                    <button
                        onClick={clearFile}
                        className="text-slate-400 hover:text-slate-600"
                    >
                        <X className="w-4 h-4" />
                    </button>
                )}
            </div>

            {!file ? (
                <div
                    onClick={() => fileInputRef.current?.click()}
                    className="border-2 border-dashed border-slate-300 rounded-lg p-6 text-center cursor-pointer hover:border-blue-400 hover:bg-blue-50 transition-colors"
                >
                    <Upload className="w-8 h-8 text-slate-400 mx-auto mb-2" />
                    <p className="text-sm font-medium text-slate-600">Click to upload image</p>
                    <p className="text-xs text-slate-400 mt-1">JPG, PNG, WebP supported</p>
                    <input
                        ref={fileInputRef}
                        type="file"
                        accept="image/*"
                        className="hidden"
                        onChange={handleFileChange}
                    />
                </div>
            ) : (
                <div className="space-y-4">
                    <div className="relative rounded-lg overflow-hidden border border-slate-200 bg-slate-50">
                        <img
                            src={preview!}
                            alt="Preview"
                            className="max-h-48 mx-auto object-contain"
                        />
                    </div>

                    {!result && (
                        <div className="space-y-3">
                            <label className="flex items-center gap-2 text-sm text-slate-600 cursor-pointer">
                                <input
                                    type="checkbox"
                                    checked={useAI}
                                    onChange={(e) => setUseAI(e.target.checked)}
                                    className="rounded border-slate-300 text-blue-600 focus:ring-blue-500"
                                />
                                <span>Explain with AI (Slower)</span>
                            </label>

                            <button
                                onClick={handleScan}
                                disabled={loading}
                                className="w-full btn-primary flex items-center justify-center gap-2"
                            >
                                {loading ? (
                                    <>
                                        <Loader2 className="w-4 h-4 animate-spin" />
                                        Scanning...
                                    </>
                                ) : (
                                    <>
                                        <Shield className="w-4 h-4" />
                                        Scan Authenticity
                                    </>
                                )}
                            </button>
                        </div>
                    )}

                    {error && (
                        <div className="p-3 bg-red-50 text-red-700 text-sm rounded-lg flex items-start gap-2">
                            <AlertTriangle className="w-4 h-4 shrink-0 mt-0.5" />
                            {error}
                        </div>
                    )}
                </div>
            )}

            {result && (
                <div className="space-y-4 animate-fadeIn">
                    {/* Result Header */}
                    <div className={`p-4 rounded-lg border flex items-start gap-3 ${getLikelihoodColor(result.tool_result.assessment.ai_likelihood_level)}`}>
                        {result.tool_result.assessment.ai_likelihood_level === 'LOW' ? (
                            <CheckCircle className="w-6 h-6 shrink-0" />
                        ) : (
                            <AlertTriangle className="w-6 h-6 shrink-0" />
                        )}
                        <div>
                            <p className="font-bold text-lg">
                                AI Likelihood: {result.tool_result.assessment.ai_likelihood_level}
                            </p>
                            <p className="text-sm opacity-90 mt-1">
                                {result.tool_result.assessment.reasons.length > 0
                                    ? result.tool_result.assessment.reasons[0]
                                    : 'No strong AI indicators found.'}
                            </p>
                        </div>
                    </div>

                    {/* Assistant Explanation */}
                    {result.assistant_explanation && (
                        <div className="bg-white border border-slate-200 rounded-lg p-3">
                            <p className="text-xs font-semibold text-slate-500 uppercase mb-1">Analysis</p>
                            <p className="text-sm text-slate-700 leading-relaxed">
                                {result.assistant_explanation}
                            </p>
                        </div>
                    )}

                    <div className="text-xs text-slate-400 italic text-center">
                        {result.tool_result.disclaimer}
                    </div>
                </div>
            )}
        </div>
    );
}
