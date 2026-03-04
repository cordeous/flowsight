import { NavLink } from 'react-router-dom'

const NAV = [
  { to: '/', label: 'Executive', icon: '📊' },
  { to: '/inventory', label: 'Inventory', icon: '📦' },
  { to: '/forecast', label: 'Forecast', icon: '📈' },
  { to: '/anomalies', label: 'Anomalies', icon: '⚠️' },
]

export default function Sidebar({ mobileMenuOpen, setMobileMenuOpen }) {
  return (
    <>
      {/* Mobile Backdrop */}
      {mobileMenuOpen && (
        <div
          className="fixed inset-0 bg-slate-900/50 backdrop-blur-sm z-30 md:hidden transition-opacity"
          onClick={() => setMobileMenuOpen(false)}
        />
      )}

      {/* Sidebar Content */}
      <aside id="sidebar-export-exclude" className={`
        fixed md:sticky top-0 left-0 h-screen z-40
        w-64 bg-zinc-900 border-r border-zinc-800 shadow-xl
        flex flex-col flex-shrink-0 transition-transform duration-300 ease-in-out
        ${mobileMenuOpen ? 'translate-x-0' : '-translate-x-full md:translate-x-0'}
      `}>
        <div className="p-6">
          <div className="flex items-center justify-between">
            <div className="text-xl font-bold tracking-tight text-white flex items-center gap-2">
              <span className="w-7 h-7 rounded bg-indigo-500 flex items-center justify-center text-xs shadow-md shadow-indigo-500/30">FS</span>
              FlowSight
            </div>
            <button
              className="md:hidden text-zinc-400 hover:text-white transition-colors"
              onClick={() => setMobileMenuOpen(false)}
            >
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M6 18L18 6M6 6l12 12"></path></svg>
            </button>
          </div>
          <div className="text-xs text-zinc-400 mt-2 font-medium tracking-wide uppercase pl-9">Supply Chain Analytics</div>
        </div>

        <nav className="flex-1 px-3 py-6 overflow-y-auto space-y-1">
          {NAV.map(({ to, label, icon }) => (
            <NavLink key={to} to={to} end={to === '/'}
              onClick={() => setMobileMenuOpen(false)}
              className={({ isActive }) => `
                group flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-semibold transition-all duration-200
                ${isActive
                  ? 'bg-zinc-800 text-white border-l-4 border-indigo-500 shadow-sm shadow-black/20'
                  : 'text-zinc-400 border-l-4 border-transparent hover:text-zinc-200 hover:bg-zinc-800 hover:border-zinc-600'
                }
              `}
            >
              <span className="text-lg opacity-90 transition-transform duration-300 group-hover:scale-110">{icon}</span>
              {label}
            </NavLink>
          ))}
        </nav>

        <div className="p-5 border-t border-zinc-800 text-xs text-zinc-500 bg-zinc-950/30">
          <div className="font-mono bg-zinc-900 rounded p-2 mb-2 text-[10px] leading-relaxed text-zinc-400 border border-zinc-800 shadow-inner">
            python scripts/run_all.py<br />
            npm run build
          </div>
          <p className="font-medium">System v2.2.0</p>
        </div>
      </aside>
    </>
  )
}
