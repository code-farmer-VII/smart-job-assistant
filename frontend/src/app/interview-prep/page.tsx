import AgentChat from "@/components/AgentChat";

export default function InterviewPrep() {
  return (
    <div className="space-y-8 animate-in fade-in slide-in-from-bottom-4 duration-700">
      <header>
        <h1 className="text-4xl font-bold mb-2 bg-clip-text text-transparent bg-gradient-to-r from-emerald-400 to-cyan-400">Interview Simulator</h1>
        <p className="text-slate-400">Chat with the RAG agent to prepare for your upcoming interviews.</p>
      </header>

      <div className="glass-panel p-8 rounded-2xl border-emerald-500/20 shadow-[0_0_50px_rgba(16,185,129,0.1)] relative overflow-hidden group">
        <div className="absolute top-0 right-0 -mr-20 -mt-20 w-64 h-64 bg-emerald-500/10 rounded-full blur-3xl group-hover:bg-emerald-500/20 transition-all duration-500 pointer-events-none"></div>
        <AgentChat endpoint="/api/rag" />
      </div>
    </div>
  );
}
