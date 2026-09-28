import AgentChat from "@/components/AgentChat";
import { promises as fs } from "fs";
import path from "path";

async function getStats() {
  const dataDir = path.join(process.cwd(), "..", "data");
  
  let jobsCount = 0;
  let appsCount = 0;
  let skillsCount = 0;
  
  try {
    const jobsData = await fs.readFile(path.join(dataDir, "jobs.json"), "utf8");
    jobsCount = JSON.parse(jobsData).filter((j: any) => j.title).length; // Only count jobs with titles
  } catch (e) {}
  
  try {
    const appsData = await fs.readFile(path.join(dataDir, "applications.json"), "utf8");
    appsCount = JSON.parse(appsData).filter((a: any) => a.job_id).length;
  } catch (e) {}
  
  try {
    const skillsData = await fs.readFile(path.join(dataDir, "skills.json"), "utf8");
    skillsCount = JSON.parse(skillsData).filter((s: any) => s.name).length;
  } catch (e) {}
  
  return { jobsCount, appsCount, skillsCount };
}

export default async function Dashboard() {
  const stats = await getStats();

  return (
    <div className="space-y-8 animate-in fade-in slide-in-from-bottom-4 duration-700">
      <header>
        <h1 className="text-4xl font-bold mb-2">Welcome Back</h1>
        <p className="text-slate-400">Here's an overview of your job application pipeline.</p>
      </header>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <StatCard title="Saved Jobs" value={stats.jobsCount.toString()} trend="In your database" color="from-blue-500/20 to-blue-600/5" border="border-blue-500/20" />
        <StatCard title="Active Applications" value={stats.appsCount.toString()} trend="Pending status" color="from-purple-500/20 to-purple-600/5" border="border-purple-500/20" />
        <StatCard title="Total Skills" value={stats.skillsCount.toString()} trend="Extracted from profile" color="from-emerald-500/20 to-emerald-600/5" border="border-emerald-500/20" />
      </div>

      <div className="glass-panel p-8 rounded-2xl relative overflow-hidden group">
        <div className="absolute top-0 right-0 -mr-20 -mt-20 w-64 h-64 bg-indigo-500/10 rounded-full blur-3xl group-hover:bg-indigo-500/20 transition-all duration-500 pointer-events-none"></div>
        <h2 className="text-2xl font-semibold mb-6 flex items-center gap-2">
          <span className="text-purple-400">✦</span> Ask Assistant
        </h2>
        <AgentChat />
      </div>
    </div>
  );
}

function StatCard({ title, value, trend, color, border }: any) {
  return (
    <div className={`glass-panel p-6 rounded-2xl border ${border} bg-gradient-to-br ${color} hover:scale-[1.02] transition-transform duration-300 cursor-default relative overflow-hidden`}>
      <div className="relative z-10">
        <h3 className="text-slate-400 font-medium mb-2">{title}</h3>
        <div className="text-4xl font-bold text-white mb-2">{value}</div>
        <div className="text-sm text-slate-300/80">{trend}</div>
      </div>
    </div>
  );
}
