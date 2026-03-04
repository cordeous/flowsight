export default function StatusBadge({ value, type = 'alert' }) {
  // Try to use tailwind semantic colors mapping for better styling
  const getColorClass = (val) => {
    const v = (val || '').toString().toUpperCase();
    if (v === 'HIGH' || v === 'ORDER NOW') return 'bg-red-500/15 text-red-400 border-red-500/30'
    if (v === 'MEDIUM' || v === 'ORDER SOON') return 'bg-orange-500/15 text-orange-400 border-orange-500/30'
    if (v === 'LOW' || v === 'OK') return 'bg-emerald-500/15 text-emerald-400 border-emerald-500/30'
    return 'bg-slate-500/15 text-slate-400 border-slate-500/30'
  }

  return (
    <span className={`inline-flex items-center px-2 py-0.5 rounded text-xs font-bold uppercase tracking-wider border backdrop-blur-sm ${getColorClass(value)}`}>
      {value}
    </span>
  )
}
