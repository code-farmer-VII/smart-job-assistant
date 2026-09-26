export default function Profile() {
  return (
    <div className="space-y-8 animate-in fade-in slide-in-from-bottom-4 duration-700">
      <header>
        <h1 className="text-4xl font-bold mb-2">My Profile</h1>
        <p className="text-slate-400">Manage your skills, experience, and projects.</p>
      </header>
      
      <div className="glass-panel p-8 rounded-2xl flex items-center justify-center min-h-[400px]">
        <p className="text-slate-500">Profile data will be populated from data/profile.json</p>
      </div>
    </div>
  );
}
