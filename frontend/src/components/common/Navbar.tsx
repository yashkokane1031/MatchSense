import Link from "next/link";
import { HealthBadge } from "./HealthBadge";

export function Navbar() {
  return (
    <nav className="border-b border-white/10 bg-[#0a0d14]/80 backdrop-blur-md sticky top-0 z-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
        <div className="flex items-center gap-8">
          <Link href="/" className="text-xl font-bold tracking-tight text-white flex items-center gap-2">
            <span className="w-2.5 h-2.5 rounded-full bg-cyan-400" />
            Match<span className="text-cyan-400">Sense</span>
          </Link>
          <div className="hidden md:flex items-center gap-6 text-sm font-medium text-slate-300">
            <Link href="/" className="hover:text-white transition-colors">Fixtures</Link>
            <Link href="/simulator" className="hover:text-white transition-colors">H2H Simulator</Link>
            <Link href="/teams" className="hover:text-white transition-colors">Teams</Link>
            <Link href="/models" className="hover:text-white transition-colors">Evaluation & Models</Link>
          </div>
        </div>
        <HealthBadge />
      </div>
    </nav>
  );
}
