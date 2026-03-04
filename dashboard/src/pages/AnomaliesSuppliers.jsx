import { useMemo, useState } from 'react'
import { useData } from '../context/DataContext'
import KpiCard from '../components/ui/KpiCard'
import SectionTitle from '../components/ui/SectionTitle'
import DataTable from '../components/ui/DataTable'
import StatusBadge from '../components/ui/StatusBadge'
import AnomalyScatterChart from '../components/charts/AnomalyScatterChart'
import AnomalyDetectorDonut from '../components/charts/AnomalyDetectorDonut'
import SupplierOTDBar from '../components/charts/SupplierOTDBar'
import SupplierRatingScatter from '../components/charts/SupplierRatingScatter'
import AnomalyHeatmap from '../components/charts/AnomalyHeatmap'
import { C } from '../utils/colors'
import { fmtPct } from '../utils/fmt'

const ANOMALY_COLS = [
  { key: 'ProductName', label: 'Product', render: v => <span title={v}>{v?.length > 22 ? v.slice(0, 20) + '…' : v}</span> },
  { key: 'Category', label: 'Category' },
  { key: 'DetectorType', label: 'Detector', render: v => v === 'isolation_forest' ? 'IsoForest' : 'Z-Score' },
  { key: 'AnomalyScore', label: 'Score', align: 'right', render: v => <span className="font-mono text-slate-600">{v?.toFixed(3)}</span> },
  { key: 'AnomalyDate', label: 'Date', render: v => <span className="text-slate-500">{v?.slice(0, 10)}</span> },
  { key: 'FeatureName', label: 'Feature' },
  { key: 'FeatureValue', label: 'Value', align: 'right', render: v => <span className="font-mono text-slate-600">{v?.toFixed(2)}</span> },
  { key: 'Severity', label: 'Severity', render: v => <StatusBadge value={v} type="severity" /> },
]

export default function AnomaliesSuppliers() {
  const { anomaly, supplier } = useData()
  const [detectorFilter, setDetectorFilter] = useState('all')
  const [severityFilter, setSeverityFilter] = useState('all')

  const kpis = useMemo(() => {
    if (!anomaly || !supplier) return null
    const total = anomaly.length
    const high = anomaly.filter(r => r.Severity === 'HIGH').length
    const below50 = supplier.filter(r => r.OnTimeDeliveryPct < 50).length
    const worstIdx = supplier.reduce((mi, r, i, a) => r.OnTimeDeliveryPct < a[mi].OnTimeDeliveryPct ? i : mi, 0)
    const worst = supplier[worstIdx]
    return { total, high, below50, worstOTD: worst?.OnTimeDeliveryPct, worstName: worst?.SupplierName }
  }, [anomaly, supplier])

  const filteredAnomalies = useMemo(() => {
    let rows = anomaly || []
    if (detectorFilter !== 'all') rows = rows.filter(r => r.DetectorType === detectorFilter)
    if (severityFilter !== 'all') rows = rows.filter(r => r.Severity === severityFilter)
    return rows.sort((a, b) => (b.AnomalyScore ?? 0) - (a.AnomalyScore ?? 0))
  }, [anomaly, detectorFilter, severityFilter])

  const btnStyle = (active) => `
    px-3 py-1.5 text-xs font-semibold rounded-lg border transition-all duration-200
    ${active
      ? 'bg-indigo-500 border-indigo-600 text-white shadow-md shadow-indigo-500/30'
      : 'bg-transparent border-slate-200 text-slate-500 hover:text-indigo-600 hover:bg-white'
    }
  `

  return (
    <div className="space-y-6">
      <SectionTitle>Anomaly &amp; Supplier KPIs</SectionTitle>

      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <KpiCard icon="⚠️" label="Total Anomalies" value={kpis?.total ?? '—'} accentColor="#fd7e14" />
        <KpiCard icon="🚨" label="HIGH Severity" value={kpis?.high ?? '—'} accentColor="#dc3545" />
        <KpiCard icon="📉" label="Suppliers < 50% OTD" value={kpis?.below50 ?? '—'} accentColor="#fd7e14" />
        <KpiCard icon="💀" label="Worst Supplier OTD" value={fmtPct(kpis?.worstOTD)}
          accentColor="#dc3545" sub={kpis?.worstName} />
      </div>

      {/* Filters */}
      <div className="flex flex-wrap items-center gap-6 bg-white/50 p-4 rounded-xl border border-slate-200 backdrop-blur-md mb-2">
        <div className="flex items-center gap-3">
          <span className="text-slate-500 text-xs font-bold tracking-wider uppercase">Detector:</span>
          <div className="flex gap-1.5 bg-slate-100/80 p-1 rounded-xl">
            {[['all', 'All'], ['zscore', 'Z-Score'], ['isolation_forest', 'Iso Forest']].map(([v, l]) => (
              <button key={v} onClick={() => setDetectorFilter(v)} className={btnStyle(detectorFilter === v)}>{l}</button>
            ))}
          </div>
        </div>

        <div className="flex items-center gap-3">
          <span className="text-slate-500 text-xs font-bold tracking-wider uppercase">Severity:</span>
          <div className="flex gap-1.5 bg-slate-100/80 p-1 rounded-xl">
            {[['all', 'All'], ['HIGH', 'HIGH'], ['MEDIUM', 'MED']].map(([v, l]) => (
              <button key={v} onClick={() => setSeverityFilter(v)} className={btnStyle(severityFilter === v)}>{l}</button>
            ))}
          </div>
        </div>
      </div>

      <SectionTitle>Suppliers</SectionTitle>
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        <SupplierOTDBar supplier={supplier} />
        <SupplierRatingScatter supplier={supplier} />
      </div>

      <SectionTitle>Anomaly Timeline &amp; Distribution</SectionTitle>
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
        <div className="lg:col-span-2">
          <AnomalyScatterChart anomaly={anomaly} detectorFilter={detectorFilter} severityFilter={severityFilter} />
        </div>
        <div>
          <AnomalyDetectorDonut anomaly={anomaly} />
        </div>
      </div>

      <SectionTitle>Anomaly Heatmap</SectionTitle>
      <div className="mb-6">
        <AnomalyHeatmap anomaly={anomaly} />
      </div>

      <SectionTitle>Anomaly Detail Table</SectionTitle>
      <div className="glass-card rounded-2xl p-0 overflow-hidden mb-8">
        <div className="p-4 overflow-x-auto">
          <DataTable rows={filteredAnomalies} columns={ANOMALY_COLS} />
        </div>
      </div>
    </div>
  )
}
