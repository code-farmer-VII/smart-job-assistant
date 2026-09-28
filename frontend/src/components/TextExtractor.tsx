"use client";
import { useState } from "react";

export default function TextExtractor() {
  const [text, setText] = useState("");
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<string | null>(null);

  const handleExtractText = async () => {
    if (!text.trim()) return;
    setLoading(true);
    setResult(null);

    try {
      const res = await fetch("http://localhost:8000/api/extract", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ text })
      });
      const data = await res.json();
      setResult(data.result || data.error);
    } catch (err) {
      setResult("Failed to process text.");
    } finally {
      setLoading(false);
      setText("");
    }
  };

  const handleFileUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;
    
    setLoading(true);
    setResult(null);
    
    const formData = new FormData();
    formData.append("file", file);
    
    try {
      const res = await fetch("http://localhost:8000/api/extract", {
        method: "POST",
        body: formData
      });
      const data = await res.json();
      setResult(data.result || data.error);
    } catch (err) {
      setResult("Failed to upload file.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="glass-panel p-6 rounded-2xl border-indigo-500/20 flex flex-col gap-4">
      <h3 className="font-semibold text-lg flex items-center gap-2">
        <span className="text-indigo-400">⚡</span> Smart Extraction
      </h3>
      <p className="text-sm text-slate-400">
        Upload a file (.pdf, .docx, .txt) or paste your CV/Job Description here. The AI will automatically extract the details and save them to your database.
      </p>
      
      <div className="flex justify-between items-center bg-white/5 p-3 rounded-xl border border-white/10">
        <span className="text-sm text-slate-300 ml-2">Upload Document:</span>
        <input 
          type="file" 
          onChange={handleFileUpload} 
          accept=".txt,.pdf,.docx" 
          disabled={loading}
          className="text-sm text-slate-400 file:mr-4 file:py-2 file:px-4 file:rounded-lg file:border-0 file:text-sm file:font-semibold file:bg-indigo-600 file:text-white hover:file:bg-indigo-500 cursor-pointer"
        />
      </div>

      <div className="flex items-center gap-4 my-2">
        <div className="flex-1 h-px bg-white/10"></div>
        <span className="text-xs text-slate-500 font-semibold uppercase">OR PASTE TEXT</span>
        <div className="flex-1 h-px bg-white/10"></div>
      </div>
      
      <textarea 
        value={text}
        onChange={(e) => setText(e.target.value)}
        placeholder="Paste text here..."
        className="w-full h-32 bg-white/5 border border-white/10 rounded-xl p-4 focus:outline-none focus:ring-2 focus:ring-indigo-500 transition-all text-white placeholder-slate-500 resize-none"
      />
      
      <div className="flex justify-between items-center">
        <div className="text-sm text-emerald-400 max-h-32 overflow-y-auto w-3/4">
          {result && <pre className="whitespace-pre-wrap font-sans">{result}</pre>}
        </div>
        <button 
          onClick={handleExtractText}
          disabled={loading || !text.trim()}
          className="bg-gradient-to-r from-indigo-500 to-purple-600 hover:from-indigo-400 hover:to-purple-500 text-white font-medium py-2 px-6 rounded-lg transition-all duration-300 shadow-[0_0_15px_rgba(99,102,241,0.3)] disabled:opacity-50 disabled:cursor-not-allowed whitespace-nowrap"
        >
          {loading ? 'Processing...' : 'Extract & Save'}
        </button>
      </div>
    </div>
  );
}
