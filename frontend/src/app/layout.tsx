import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";
import Link from "next/link";

const inter = Inter({ subsets: ["latin"] });

export const metadata: Metadata = {
  title: "Smart Job Assistant",
  description: "AI-Powered Job Application Manager",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" className="dark">
      <body className={`${inter.className} flex h-screen overflow-hidden text-slate-200 antialiased`}>
        {/* Sidebar */}
        <aside className="w-64 glass-panel border-r border-white/5 flex flex-col p-6 z-10 relative">
          <div className="flex items-center gap-3 mb-10">
            <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-indigo-500 to-purple-600 flex items-center justify-center font-bold text-white shadow-lg shadow-indigo-500/30">
              JA
            </div>
            <h1 className="text-xl font-semibold bg-clip-text text-transparent bg-gradient-to-r from-indigo-300 to-purple-300">Job Assistant</h1>
          </div>
          
          <nav className="flex flex-col gap-2 flex-1">
            <NavItem href="/" icon="❖" label="Dashboard" />
            <NavItem href="/profile" icon="👤" label="Profile" />
            <NavItem href="/jobs" icon="💼" label="Job Tracker" />
            <NavItem href="/interview-prep" icon="🎯" label="Interview Prep" />
          </nav>
        </aside>

        {/* Main Content */}
        <main className="flex-1 overflow-y-auto p-8 relative">
          <div className="absolute inset-0 bg-center opacity-20 pointer-events-none" style={{ backgroundImage: 'radial-gradient(circle at 1px 1px, rgba(255,255,255,0.15) 1px, transparent 0)', backgroundSize: '40px 40px' }}></div>
          <div className="relative z-10 max-w-6xl mx-auto">
            {children}
          </div>
        </main>
      </body>
    </html>
  );
}

function NavItem({ href, icon, label }: { href: string; icon: string; label: string }) {
  return (
    <Link 
      href={href} 
      className="flex items-center gap-3 px-4 py-3 rounded-xl hover:bg-white/5 transition-all duration-200 group"
    >
      <span className="text-xl opacity-70 group-hover:opacity-100 group-hover:scale-110 transition-all">{icon}</span>
      <span className="font-medium text-slate-400 group-hover:text-white transition-colors">{label}</span>
    </Link>
  );
}
