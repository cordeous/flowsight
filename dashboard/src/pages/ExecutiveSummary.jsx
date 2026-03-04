import { useMemo } from 'react'
import { useData } from '../context/DataContext'
import KpiCard from '../components/ui/KpiCard'
import SectionTitle from '../components/ui/SectionTitle'
import Card from '../components/ui/Card'
import RevenueTrendChart from '../components/charts/RevenueTrendChart'
import CategoryDonutChart from '../components/charts/CategoryDonutChart'
import TopProductsBarChart from '../components/charts/TopProductsBarChart'
import { fmtCurrency, fmtPct, fmtNum } from '../utils/fmt'

function MiniStatRow({ label, value, valueClass = '' }) {
  return (
    <div className="flex items-center justify-between py-2 border-b border-slate-100 last:border-0">
      <span className="text-sm text-slate-500">{label}</span>
      <span className={`text-sm font-semibold ${valueClass || 'text-slate-800'}`}>{value}</span>
    </div>
  )
}

export default function ExecutiveSummary() {
  const { sales, stockout, supplier, turnover, reorder } = useData()

  const kpis = useMemo(() => {
    if (!sales || !stockout || !supplier || !turnover || !reorder) return null
    const totalRevenue = sales.reduce((s, r) => s + r.TotalRevenue, 0)
    const totalUnits = sales.reduce((s, r) => s + r.TotalUnitsSold, 0)
    const stockoutRate = stockout.filter(r => r.IsStockout === 1).length / stockout.length * 100
    const fleetOTD = supplier.reduce((s, r) => s + r.OnTimeDeliveryPct, 0) / supplier.length
    const avgTurnover = turnover.reduce((s, r) => s + r.InventoryTurnoverRatio, 0) / turnover.length
    const criticalCount = reorder.filter(r => r.AlertStatus === 'ORDER NOW').length
    return { totalRevenue, totalUnits, stockoutRate, fleetOTD, avgTurnover, criticalCount }
  }, [sales, stockout, supplier, turnover, reorder])

  const momChange = useMemo(() => {
    if (!sales) return null
    const byMonth = {}
    sales.forEach(r => { byMonth[r.YearMonth] = (byMonth[r.YearMonth] || 0) + r.TotalRevenue })
    const months = Object.keys(byMonth).sort()
    if (months.length < 2) return null
    const last = byMonth[months[months.length - 1]]
    const prev = byMonth[months[months.length - 2]]
    return ((last - prev) / prev) * 100
  }, [sales])

  // Top suppliers by OTD
  const topSuppliers = useMemo(() => {
    if (!supplier) return []
    return [...supplier].sort((a, b) => b.OnTimeDeliveryPct - a.OnTimeDeliveryPct).slice(0, 5)
  }, [supplier])

  // Worst suppliers
  const worstSuppliers = useMemo(() => {
    if (!supplier) return []
    return [...supplier].sort((a, b) => a.OnTimeDeliveryPct - b.OnTimeDeliveryPct).slice(0, 5)
  }, [supplier])

  // Recent category revenue breakdown
  const categoryRevenue = useMemo(() => {
    if (!sales) return []
    const map = {}
    sales.forEach(r => { map[r.Category] = (map[r.Category] || 0) + r.TotalRevenue })
    const total = Object.values(map).reduce((s, v) => s + v, 0)
    return Object.entries(map).map(([cat, rev]) => ({ cat, rev, pct: (rev / total) * 100 }))
      .sort((a, b) => b.rev - a.rev)
  }, [sales])

  const ACCENT_COLORS = ['bg-indigo-500', 'bg-blue-400', 'bg-emerald-500', 'bg-orange-400', 'bg-purple-500']

  return (
    <div className="space-y-6">
      <SectionTitle>Key Performance Indicators</SectionTitle>

      <div className="grid grid-cols-2 sm:grid-cols-3 xl:grid-cols-6 gap-4">
        <KpiCard icon="💰" label="Total Revenue (2yr)" value={fmtCurrency(kpis?.totalRevenue)} accentColor="#0d6efd"
          sub={momChange != null ? `${momChange >= 0 ? '+' : ''}${fmtPct(momChange)} MoM` : undefined} />
        <KpiCard icon="🛒" label="Total Units Sold" value={fmtNum(kpis?.totalUnits)} accentColor="#198754" />
        <KpiCard icon="📦" label="Stockout Rate" value={fmtPct(kpis?.stockoutRate)}
          accentColor={kpis?.stockoutRate > 10 ? '#dc3545' : kpis?.stockoutRate > 5 ? '#fd7e14' : '#198754'} />
        <KpiCard icon="🚚" label="Fleet OTD %" value={fmtPct(kpis?.fleetOTD)}
          accentColor={kpis?.fleetOTD > 70 ? '#198754' : kpis?.fleetOTD > 40 ? '#fd7e14' : '#dc3545'} />
        <KpiCard icon="🔄" label="Inventory Turnover" value={`${fmtNum(kpis?.avgTurnover, 2)}x`}
          accentColor={kpis?.avgTurnover > 4 ? '#198754' : '#fd7e14'} />
        <KpiCard icon="🚨" label="Critical Reorders" value={kpis?.criticalCount ?? '—'}
          accentColor={kpis?.criticalCount > 0 ? '#dc3545' : '#198754'}
          sub="Products needing ORDER NOW" />
      </div>

      <SectionTitle>Revenue Trends</SectionTitle>
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
        <div className="lg:col-span-2">
          <RevenueTrendChart sales={sales} />
        </div>
        <div className="flex flex-col gap-4">
          <Card>
            <div className="text-xs font-bold uppercase tracking-wider text-slate-500 mb-3 flex items-center gap-2">
              <span className="w-2 h-2 rounded-full bg-indigo-500"></span>Revenue by Category
            </div>
            {categoryRevenue.map(({ cat, rev, pct }, i) => (
              <div key={cat} className="mb-3">
                <div className="flex items-center justify-between text-sm mb-1">
                  <span className="text-slate-600 font-medium">{cat}</span>
                  <span className="text-slate-800 font-semibold">{fmtCurrency(rev)}</span>
                </div>
                <div className="h-1.5 bg-slate-100 rounded-full overflow-hidden">
                  <div className={`h-full rounded-full transition-all duration-700 ${ACCENT_COLORS[i % ACCENT_COLORS.length]}`}
                    style={{ width: `${pct}%` }} />
                </div>
              </div>
            ))}
          </Card>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        <CategoryDonutChart sales={sales} />

        <Card>
          <div className="text-xs font-bold uppercase tracking-wider text-slate-500 mb-1 flex items-center gap-2">
            <span className="w-2 h-2 rounded-full bg-emerald-500"></span>Top 5 Suppliers by OTD
          </div>
          {topSuppliers.map(s => (
            <div key={s.SupplierID} className="flex items-center justify-between py-2 border-b border-slate-100 last:border-0">
              <span className="text-sm text-slate-600 truncate max-w-[180px]">{s.SupplierName}</span>
              <div className="flex items-center gap-2">
                <div className="w-24 h-1.5 bg-slate-100 rounded-full overflow-hidden hidden sm:block">
                  <div className="h-full bg-emerald-500 rounded-full" style={{ width: `${s.OnTimeDeliveryPct}%` }} />
                </div>
                <span className="text-sm font-bold text-emerald-600">{fmtPct(s.OnTimeDeliveryPct)}</span>
              </div>
            </div>
          ))}
          <div className="mt-4 text-xs font-bold uppercase tracking-wider text-slate-500 mb-1 flex items-center gap-2">
            <span className="w-2 h-2 rounded-full bg-rose-500"></span>Worst 5 Suppliers
          </div>
          {worstSuppliers.map(s => (
            <div key={s.SupplierID} className="flex items-center justify-between py-2 border-b border-slate-100 last:border-0">
              <span className="text-sm text-slate-600 truncate max-w-[180px]">{s.SupplierName}</span>
              <div className="flex items-center gap-2">
                <div className="w-24 h-1.5 bg-slate-100 rounded-full overflow-hidden hidden sm:block">
                  <div className="h-full bg-rose-500 rounded-full" style={{ width: `${s.OnTimeDeliveryPct}%` }} />
                </div>
                <span className="text-sm font-bold text-rose-600">{fmtPct(s.OnTimeDeliveryPct)}</span>
              </div>
            </div>
          ))}
        </Card>
      </div>

      <SectionTitle>Top Products by Revenue</SectionTitle>
      <div className="mb-8">
        <TopProductsBarChart sales={sales} />
      </div>
    </div>
  )
}
