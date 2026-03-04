import { useData } from '../../context/DataContext'
import { useMemo } from 'react'

export default function TopBar() {
  const { reorder, stockout, anomaly } = useData()

  const stats = useMemo(() => {
    if (!reorder || !stockout || !anomaly) return null
    return {
      orderNow: reorder.filter(r => r.AlertStatus === 'ORDER NOW').length,
      belowROP: stockout.filter(r => r.BelowReorderPoint === 1).length,
      total: stockout.length,
      anomalies: anomaly.length,
      high: anomaly.filter(r => r.Severity === 'HIGH').length,
    }
  }, [reorder, stockout, anomaly])

  if (!stats) return null

  return (
    <div className="glass-card p-3.5 flex flex-wrap items-center gap-5 mb-6 text-sm">
      <div className="flex items-center gap-2">
        <span className="text-lg animate-[pulse_2s_ease-in-out_infinite]">🔴</span>
        <span className="text-slate-600">
          <strong className="text-rose-600 font-bold tracking-wide">{stats.orderNow} ORDER NOW</strong>
        </span>
      </div>

      <div className="hidden sm:block w-px h-5 bg-slate-200"></div>

      <div className="flex items-center gap-2 text-slate-600">
        <svg className="w-4 h-4 text-orange-500" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M20 7l-8-4-8 4m16 0l-8 4m8-4v10l-8 4m0-10L4 7m8 4v10" /></svg>
        <span><strong className="text-slate-800 font-bold">{stats.belowROP}/{stats.total}</strong> items below ROP</span>
      </div>

      <div className="hidden md:block w-px h-5 bg-slate-200"></div>

      <div className="flex items-center gap-2 text-slate-600">
        <svg className="w-4 h-4 text-amber-500" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" /></svg>
        <span><strong className="text-slate-800 font-bold">{stats.anomalies}</strong> anomalies (<strong className="text-rose-600 font-bold">{stats.high} HIGH</strong>)</span>
      </div>
    </div>
  )
}
