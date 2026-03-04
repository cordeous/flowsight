export default function KpiCard({ label, value, sub, accentColor = 'indigo', icon }) {
  // We'll map accent colors to specific tailwind gradient classes for a glow effect
  const colorMap = {
    '#0d6efd': 'from-blue-500 to-indigo-500 shadow-blue-500/10 border-blue-500/30',
    '#198754': 'from-emerald-400 to-green-500 shadow-emerald-500/10 border-emerald-500/30',
    '#dc3545': 'from-rose-500 to-red-500 shadow-rose-500/10 border-rose-500/30',
    '#fd7e14': 'from-orange-400 to-amber-500 shadow-orange-500/10 border-orange-500/30',
    'indigo': 'from-indigo-400 to-violet-500 shadow-indigo-500/10 border-indigo-500/30',
  }

  // Default to indigo if we can't map the color (since old code passed raw hex)
  const theme = colorMap[accentColor] || colorMap['#0d6efd'] || colorMap['indigo'];

  return (
    <div className={`glass-card relative overflow-hidden group hover:-translate-y-2 hover:shadow-[0_10px_40px_-10px_rgba(0,0,0,0.1)] transition-all duration-300 rounded-2xl p-5 flex-1 min-w-[200px] cursor-pointer`}>
      {/* Top Gradient Bar */}
      <div className={`absolute top-0 left-0 w-full h-1 bg-gradient-to-r ${theme}`} />

      {/* Background glow on hover */}
      <div className={`absolute -inset-0 bg-gradient-to-br ${theme} opacity-0 group-hover:opacity-[0.05] transition-opacity duration-300`} />

      <div className="text-slate-500 text-xs font-bold tracking-wider uppercase mb-2 flex items-center gap-2 group-hover:text-indigo-600 transition-colors">
        {icon && <span className="group-hover:scale-110 transition-transform duration-300">{icon}</span>}
        {label}
      </div>

      <div className="text-3xl font-extrabold text-slate-800 tracking-tight">
        {value}
      </div>

      {sub && (
        <div className="text-slate-600 text-xs mt-3 bg-slate-100/80 backdrop-blur rounded px-2 py-1 inline-block border border-slate-200">
          {sub}
        </div>
      )}
    </div>
  )
}
