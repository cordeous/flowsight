import { useMemo } from 'react'
import { useData } from '../context/DataContext'
import KpiCard from '../components/ui/KpiCard'
import SectionTitle from '../components/ui/SectionTitle'
import RevenueTrendChart from '../components/charts/RevenueTrendChart'
import CategoryDonutChart from '../components/charts/CategoryDonutChart'
import TopProductsBarChart from '../components/charts/TopProductsBarChart'
import { C, ALERT_COLORS } from '../utils/colors'
import { fmtCurrency, fmtPct, fmtNum } from '../utils/fmt'

export default function ExecutiveSummary() {
  const { sales, stockout, supplier, turnover, reorder } = useData()

  const kpis = useMemo(() => {
    if (!sales || !stockout || !supplier || !turnover || !reorder) return null
    const totalRevenue  = sales.reduce((s, r) => s + r.TotalRevenue, 0)
    const totalUnits    = sales.reduce((s, r) => s + r.TotalUnitsSold, 0)
    const stockoutRate  = stockout.filter(r => r.IsStockout === 1).length / stockout.length * 100
    const fleetOTD      = supplier.reduce((s, r) => s + r.OnTimeDeliveryPct, 0) / supplier.length
    const avgTurnover   = turnover.reduce((s, r) => s + r.InventoryTurnoverRatio, 0) / turnover.length
    const criticalCount = reorder.filter(r => r.AlertStatus === 'ORDER NOW').length
    return { totalRevenue, totalUnits, stockoutRate, fleetOTD, avgTurnover, criticalCount }
  }, [sales, stockout, supplier, turnover, reorder])

  // Month-over-month change for last month
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

  return (
    <div>
      <SectionTitle>Key Performance Indicators</SectionTitle>
      <div style={{ display: 'flex', gap: 12, flexWrap: 'wrap', marginBottom: 20 }}>
        <KpiCard label="Total Revenue (2yr)" value={fmtCurrency(kpis?.totalRevenue)} accent={C.blue}
          sub={momChange != null ? `${momChange >= 0 ? '+' : ''}${fmtPct(momChange)} MoM (last month)` : undefined} />
        <KpiCard label="Total Units Sold" value={fmtNum(kpis?.totalUnits)} accent={C.green} />
        <KpiCard label="Stockout Rate" value={fmtPct(kpis?.stockoutRate)}
          accent={kpis?.stockoutRate > 10 ? C.red : kpis?.stockoutRate > 5 ? C.orange : C.green} />
        <KpiCard label="Fleet OTD %" value={fmtPct(kpis?.fleetOTD)}
          accent={kpis?.fleetOTD > 70 ? C.green : kpis?.fleetOTD > 40 ? C.orange : C.red} />
        <KpiCard label="Avg Inventory Turnover" value={`${fmtNum(kpis?.avgTurnover, 2)}x`}
          accent={kpis?.avgTurnover > 4 ? C.green : C.orange} />
        <KpiCard label="Critical Reorders" value={kpis?.criticalCount ?? '—'}
          accent={kpis?.criticalCount > 0 ? C.red : C.green}
          sub="Products needing ORDER NOW" />
      </div>

      <SectionTitle>Revenue Trends</SectionTitle>
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 12, marginBottom: 20 }}>
        <RevenueTrendChart sales={sales} />
        <CategoryDonutChart sales={sales} />
      </div>

      <SectionTitle>Top Products</SectionTitle>
      <TopProductsBarChart sales={sales} />
    </div>
  )
}
