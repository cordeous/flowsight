import { useMemo } from 'react'
import { useData } from '../context/DataContext'
import KpiCard from '../components/ui/KpiCard'
import SectionTitle from '../components/ui/SectionTitle'
import DataTable from '../components/ui/DataTable'
import StatusBadge from '../components/ui/StatusBadge'
import ReorderScatterChart from '../components/charts/ReorderScatterChart'
import TurnoverHeatmap from '../components/charts/TurnoverHeatmap'
import StockoutCategoryBar from '../components/charts/StockoutCategoryBar'
import { C, ALERT_COLORS } from '../utils/colors'
import { fmtNum, fmtCurrency } from '../utils/fmt'

const REORDER_COLS = [
  { key: 'ProductName',    label: 'Product',     render: v => <span title={v}>{v?.length > 24 ? v.slice(0,22)+'…' : v}</span> },
  { key: 'Category',       label: 'Category' },
  { key: 'QuantityOnHand', label: 'On Hand',  align: 'right', render: v => fmtNum(v) },
  { key: 'RecommendedROP', label: 'ROP',      align: 'right', render: v => fmtNum(v) },
  { key: 'RecommendedEOQ', label: 'EOQ',      align: 'right', render: v => fmtNum(v) },
  { key: 'LeadTimeDays',   label: 'Lead Days', align: 'right', render: v => v ?? '—' },
  { key: 'AlertStatus',    label: 'Status',   render: v => <StatusBadge value={v} type="alert" /> },
]

const EOQ_COLS = [
  { key: 'ProductName',   label: 'Product',        render: v => <span title={v}>{v?.length > 24 ? v.slice(0,22)+'…' : v}</span> },
  { key: 'Category',      label: 'Category' },
  { key: 'AnnualDemand',  label: 'Annual Demand',  align: 'right', render: v => fmtNum(v) },
  { key: 'UnitCost',      label: 'Unit Cost',      align: 'right', render: v => fmtCurrency(v, false) },
  { key: 'RecommendedEOQ', label: 'EOQ',           align: 'right', render: v => fmtNum(v) },
  { key: 'RecommendedROP', label: 'ROP',           align: 'right', render: v => fmtNum(v) },
  { key: 'SafetyStockQty', label: 'Safety Stock',  align: 'right', render: v => fmtNum(v) },
]

export default function InventoryHealth() {
  const { reorder, stockout, eoq, turnover } = useData()

  const kpis = useMemo(() => {
    if (!reorder || !stockout || !eoq) return null
    const orderNow  = reorder.filter(r => r.AlertStatus === 'ORDER NOW').length
    const orderSoon = reorder.filter(r => r.AlertStatus === 'ORDER SOON').length
    const ok        = reorder.filter(r => r.AlertStatus === 'OK').length
    // get latest month per product for inventory value
    const latestByProduct = {}
    ;(turnover || []).forEach(r => {
      if (!latestByProduct[r.ProductID] || r.YearMonth > latestByProduct[r.ProductID].YearMonth)
        latestByProduct[r.ProductID] = r
    })
    const totalInvValue = Object.values(latestByProduct).reduce((s, r) => s + r.CurrentInventoryValue, 0)
    const belowROP = stockout.filter(r => r.BelowReorderPoint === 1).length
    return { orderNow, orderSoon, ok, totalInvValue, belowROP }
  }, [reorder, stockout, eoq, turnover])

  const rowStyle = (row) => {
    if (row.AlertStatus === 'ORDER NOW')  return `${C.red}10`
    if (row.AlertStatus === 'ORDER SOON') return `${C.orange}10`
    return 'transparent'
  }

  return (
    <div>
      <SectionTitle>Inventory KPIs</SectionTitle>
      <div style={{ display: 'flex', gap: 12, flexWrap: 'wrap', marginBottom: 20 }}>
        <KpiCard label="ORDER NOW" value={kpis?.orderNow ?? '—'} accent={C.red} sub="Need immediate reorder" />
        <KpiCard label="ORDER SOON" value={kpis?.orderSoon ?? '—'} accent={C.orange} sub="Approaching reorder point" />
        <KpiCard label="Stock OK" value={kpis?.ok ?? '—'} accent={C.green} />
        <KpiCard label="Total Inventory Value" value={fmtCurrency(kpis?.totalInvValue)} accent={C.blue} />
        <KpiCard label="Below Reorder Point" value={`${kpis?.belowROP ?? '—'}/${stockout?.length ?? '—'}`}
          accent={C.orange} sub="Products below ROP" />
      </div>

      <SectionTitle>Reorder Alerts</SectionTitle>
      <div style={{ background: C.surface, border: `1px solid ${C.border}`, borderRadius: 10, padding: '16px 20px', marginBottom: 20 }}>
        <DataTable rows={reorder || []} columns={REORDER_COLS} rowStyle={rowStyle} />
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 12, marginBottom: 20 }}>
        <ReorderScatterChart reorder={reorder} />
        <StockoutCategoryBar stockout={stockout} />
      </div>

      <SectionTitle>Turnover Heatmap</SectionTitle>
      <TurnoverHeatmap turnover={turnover} />

      <SectionTitle>EOQ Recommendations</SectionTitle>
      <div style={{ background: C.surface, border: `1px solid ${C.border}`, borderRadius: 10, padding: '16px 20px', marginBottom: 20 }}>
        <DataTable rows={eoq || []} columns={EOQ_COLS} />
      </div>
    </div>
  )
}
