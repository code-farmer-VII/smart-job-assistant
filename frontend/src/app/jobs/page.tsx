export default function Jobs() {
  return (
    <div className="space-y-8 animate-in fade-in slide-in-from-bottom-4 duration-700">
      <header>
        <h1 className="text-4xl font-bold mb-2">Job Tracker</h1>
        <p className="text-slate-400">Track and analyze your job applications.</p>
      </header>
      
      <div className="glass-panel p-8 rounded-2xl flex items-center justify-center min-h-[400px]">
        <p className="text-slate-500">Job data will be populated from data/jobs.json</p>
      </div>
    </div>
  );
}
