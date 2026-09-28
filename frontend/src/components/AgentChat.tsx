"use client";
import { useState } from "react";
import ReactMarkdown from "react-markdown";

export default function AgentChat({ endpoint = "http://localhost:8000/api/orchestrator" }: { endpoint?: string }) {
  const [prompt, setPrompt] = useState("");
  const [messages, setMessages] = useState<{role: 'user'|'assistant', text: string}[]>([]);
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!prompt.trim() || loading) return;

    const userMsg = prompt.trim();
    setPrompt("");
    setMessages(prev => [...prev, { role: 'user', text: userMsg }]);
    setLoading(true);

    try {
      const res = await fetch(endpoint, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ prompt: userMsg })
      });
      const data = await res.json();
      
      setMessages(prev => [...prev, { 
        role: 'assistant', 
        text: data.result || data.error || "An error occurred." 
      }]);
    } catch (err) {
      setMessages(prev => [...prev, { role: 'assistant', text: "Failed to connect to agent." }]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex flex-col h-[400px]">
      <div className="flex-1 overflow-y-auto space-y-4 mb-4 pr-2">
        {messages.length === 0 && (
          <div className="text-center text-slate-500 mt-20 flex flex-col items-center">
            <span className="text-4xl mb-4 opacity-50">✨</span>
            <p>Try asking: &quot;Add a new skill: Next.js (Advanced)&quot;</p>
            <p className="text-sm mt-2 opacity-70">or &quot;Update my profile name to John&quot;</p>
          </div>
        )}
        {messages.map((msg, i) => (
          <div key={i} className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'} animate-in fade-in slide-in-from-bottom-2 duration-300`}>
            <div className={`max-w-[80%] p-4 rounded-2xl ${msg.role === 'user' ? 'bg-indigo-600 text-white rounded-br-none shadow-[0_4px_20px_rgba(79,70,229,0.3)]' : 'glass-panel rounded-bl-none shadow-[0_4px_20px_rgba(0,0,0,0.1)]'}`}>
              {msg.role === 'assistant' ? (
                <div className="prose prose-invert prose-sm max-w-none text-slate-200
                  prose-headings:text-slate-100 prose-headings:font-semibold
                  prose-p:text-slate-200 prose-p:leading-relaxed
                  prose-li:text-slate-200
                  prose-strong:text-white
                  prose-code:text-emerald-300 prose-code:bg-slate-800/60 prose-code:px-1 prose-code:rounded
                  prose-hr:border-slate-600">
                  <ReactMarkdown>{msg.text}</ReactMarkdown>
                </div>
              ) : (
                <p className="font-sans whitespace-pre-wrap">{msg.text}</p>
              )}
            </div>
          </div>
        ))}
        {loading && (
          <div className="flex justify-start animate-in fade-in">
            <div className="glass-panel p-4 rounded-2xl rounded-bl-none flex gap-2 shadow-[0_4px_20px_rgba(0,0,0,0.1)]">
              <div className="w-2 h-2 rounded-full bg-indigo-400 animate-bounce"></div>
              <div className="w-2 h-2 rounded-full bg-indigo-400 animate-bounce [animation-delay:0.2s]"></div>
              <div className="w-2 h-2 rounded-full bg-indigo-400 animate-bounce [animation-delay:0.4s]"></div>
            </div>
          </div>
        )}
      </div>
      
      <form onSubmit={handleSubmit} className="relative mt-auto">
        <input 
          type="text" 
          value={prompt}
          onChange={(e) => setPrompt(e.target.value)}
          placeholder="Command the AI assistant..." 
          className="w-full bg-white/5 border border-white/10 rounded-xl px-6 py-4 focus:outline-none focus:ring-2 focus:ring-indigo-500 transition-all text-white placeholder-slate-400 shadow-inner"
        />
        <button 
          type="submit" 
          disabled={loading}
          className="absolute right-2 top-2 bottom-2 bg-gradient-to-r from-indigo-500 to-purple-600 hover:from-indigo-400 hover:to-purple-500 text-white font-medium rounded-lg transition-all duration-300 shadow-[0_0_15px_rgba(99,102,241,0.3)] hover:shadow-[0_0_25px_rgba(99,102,241,0.5)] flex items-center justify-center min-w-[100px]"
        >
          {loading ? 'Thinking...' : 'Send'}
        </button>
      </form>
    </div>
  );
}
