import { useMemo } from 'react'
import { useData } from '../context/DataContext'
import KpiCard from '../components/ui/KpiCard'
import SectionTitle from '../components/ui/SectionTitle'
import Card from '../components/ui/Card'
import DataTable from '../components/ui/DataTable'
import StatusBadge from '../components/ui/StatusBadge'
import ReorderScatterChart from '../components/charts/ReorderScatterChart'
import TurnoverHeatmap from '../components/charts/TurnoverHeatmap'
import StockoutCategoryBar from '../components/charts/StockoutCategoryBar'
import { fmtNum, fmtCurrency, fmtPct } from '../utils/fmt'

const REORDER_COLS = [
  { key: 'ProductName', label: 'Product', render: v => <span title={v}>{v?.length > 24 ? v.slice(0, 22) + '…' : v}</span> },
  { key: 'Category', label: 'Category' },
  { key: 'QuantityOnHand', label: 'On Hand', align: 'right', render: v => fmtNum(v) },
  { key: 'RecommendedROP', label: 'ROP', align: 'right', render: v => fmtNum(v) },
  { key: 'RecommendedEOQ', label: 'EOQ', align: 'right', render: v => fmtNum(v) },
  { key: 'LeadTimeDays', label: 'Lead Days', align: 'right', render: v => v ?? '—' },
  { key: 'AlertStatus', label: 'Status', render: v => <StatusBadge value={v} type="alert" /> },
]

const EOQ_COLS = [
  { key: 'ProductName', label: 'Product', render: v => <span title={v}>{v?.length > 24 ? v.slice(0, 22) + '…' : v}</span> },
  { key: 'Category', label: 'Category' },
  { key: 'AnnualDemand', label: 'Annual Demand', align: 'right', render: v => fmtNum(v) },
  { key: 'UnitCost', label: 'Unit Cost', align: 'right', render: v => fmtCurrency(v, false) },
  { key: 'RecommendedEOQ', label: 'EOQ', align: 'right', render: v => fmtNum(v) },
  { key: 'RecommendedROP', label: 'ROP', align: 'right', render: v => fmtNum(v) },
  { key: 'SafetyStockQty', label: 'Safety Stock', align: 'right', render: v => fmtNum(v) },
]

export default function InventoryHealth() {
  const { reorder, stockout, eoq, turnover } = useData()

  const kpis = useMemo(() => {
    if (!reorder || !stockout || !eoq) return null
    const orderNow = reorder.filter(r => r.AlertStatus === 'ORDER NOW').length
    const orderSoon = reorder.filter(r => r.AlertStatus === 'ORDER SOON').length
    const ok = reorder.filter(r => r.AlertStatus === 'OK').length
    // get latest month per product for inventory value
    const latestByProduct = {}
      ; (turnover || []).forEach(r => {
        if (!latestByProduct[r.ProductID] || r.YearMonth > latestByProduct[r.ProductID].YearMonth)
          latestByProduct[r.ProductID] = r
      })
    const totalInvValue = Object.values(latestByProduct).reduce((s, r) => s + r.CurrentInventoryValue, 0)
    const belowROP = stockout.filter(r => r.BelowReorderPoint === 1).length
    return { orderNow, orderSoon, ok, totalInvValue, belowROP }
  }, [reorder, stockout, eoq, turnover])

  const rowStyle = (row) => {
    if (row.AlertStatus === 'ORDER NOW') return 'bg-red-500/10'
    if (row.AlertStatus === 'ORDER SOON') return 'bg-orange-500/10'
    return 'transparent'
  }

  return (
    <div className="space-y-6">
      <SectionTitle>Inventory KPIs</SectionTitle>

      <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-5 gap-4">
        <KpiCard icon="🚨" label="ORDER NOW" value={kpis?.orderNow ?? '—'} accentColor="#dc3545" sub="Need immediate reorder" />
        <KpiCard icon="⏳" label="ORDER SOON" value={kpis?.orderSoon ?? '—'} accentColor="#fd7e14" sub="Approaching reorder point" />
        <KpiCard icon="✅" label="Stock OK" value={kpis?.ok ?? '—'} accentColor="#198754" />
        <KpiCard icon="💰" label="Total Inventory Value" value={fmtCurrency(kpis?.totalInvValue)} accentColor="#0d6efd" />
        <KpiCard icon="📉" label="Below Reorder Point" value={`${kpis?.belowROP ?? '—'}/${stockout?.length ?? '—'}`}
          accentColor="#fd7e14" sub="Products below ROP" />
      </div>

      {/* Category Alert Summary */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
        {(() => {
          const categories = [...new Set((reorder || []).map(r => r.Category))].sort()
          return categories.map(cat => {
            const items = (reorder || []).filter(r => r.Category === cat)
            const orderNow = items.filter(r => r.AlertStatus === 'ORDER NOW').length
            const orderSoon = items.filter(r => r.AlertStatus === 'ORDER SOON').length
            const ok = items.filter(r => r.AlertStatus === 'OK').length
            return (
              <Card key={cat} className="!p-4">
                <div className="text-sm font-bold text-slate-700 mb-3 flex items-center gap-2">
                  <span className="text-base">📦</span>{cat}
                </div>
                <div className="flex gap-3">
                  <div className="flex-1 bg-red-50 border border-red-100 rounded-lg p-2 text-center">
                    <div className="text-xl font-extrabold text-rose-600">{orderNow}</div>
                    <div className="text-[10px] text-rose-500 font-semibold uppercase">Order Now</div>
                  </div>
                  <div className="flex-1 bg-orange-50 border border-orange-100 rounded-lg p-2 text-center">
                    <div className="text-xl font-extrabold text-orange-600">{orderSoon}</div>
                    <div className="text-[10px] text-orange-500 font-semibold uppercase">Order Soon</div>
                  </div>
                  <div className="flex-1 bg-emerald-50 border border-emerald-100 rounded-lg p-2 text-center">
                    <div className="text-xl font-extrabold text-emerald-600">{ok}</div>
                    <div className="text-[10px] text-emerald-500 font-semibold uppercase">OK</div>
                  </div>
                </div>
              </Card>
            )
          })
        })()}
      </div>

      <SectionTitle>Reorder Alerts</SectionTitle>
      <div className="glass-card rounded-2xl p-0 overflow-hidden mb-6">
        <div className="p-4 overflow-x-auto">
          <DataTable rows={reorder || []} columns={REORDER_COLS} rowStyle={rowStyle} />
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        <ReorderScatterChart reorder={reorder} />
        <StockoutCategoryBar stockout={stockout} />
      </div>

      <SectionTitle>Turnover Heatmap</SectionTitle>
      <div className="mb-6">
        <TurnoverHeatmap turnover={turnover} />
      </div>

      <SectionTitle>EOQ Recommendations</SectionTitle>
      <div className="glass-card rounded-2xl p-0 overflow-hidden mb-8">
        <div className="p-4 overflow-x-auto">
          <DataTable rows={eoq || []} columns={EOQ_COLS} />
        </div>
      </div>
    </div>
  )
}
