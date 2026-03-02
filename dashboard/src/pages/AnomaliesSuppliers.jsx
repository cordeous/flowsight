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
  { key: 'ProductName',   label: 'Product',    render: v => <span title={v}>{v?.length > 22 ? v.slice(0,20)+'…' : v}</span> },
  { key: 'Category',      label: 'Category' },
  { key: 'DetectorType',  label: 'Detector',   render: v => v === 'isolation_forest' ? 'IsoForest' : 'Z-Score' },
  { key: 'AnomalyScore',  label: 'Score', align: 'right', render: v => v?.toFixed(3) },
  { key: 'AnomalyDate',   label: 'Date',       render: v => v?.slice(0, 10) },
  { key: 'FeatureName',   label: 'Feature' },
  { key: 'FeatureValue',  label: 'Value', align: 'right', render: v => v?.toFixed(2) },
  { key: 'Severity',      label: 'Severity',   render: v => <StatusBadge value={v} type="severity" /> },
]

export default function AnomaliesSuppliers() {
  const { anomaly, supplier } = useData()
  const [detectorFilter, setDetectorFilter] = useState('all')
  const [severityFilter, setSeverityFilter] = useState('all')

  const kpis = useMemo(() => {
    if (!anomaly || !supplier) return null
    const total     = anomaly.length
    const high      = anomaly.filter(r => r.Severity === 'HIGH').length
    const below50   = supplier.filter(r => r.OnTimeDeliveryPct < 50).length
    const worstIdx  = supplier.reduce((mi, r, i, a) => r.OnTimeDeliveryPct < a[mi].OnTimeDeliveryPct ? i : mi, 0)
    const worst     = supplier[worstIdx]
    return { total, high, below50, worstOTD: worst?.OnTimeDeliveryPct, worstName: worst?.SupplierName }
  }, [anomaly, supplier])

  const filteredAnomalies = useMemo(() => {
    let rows = anomaly || []
    if (detectorFilter !== 'all') rows = rows.filter(r => r.DetectorType === detectorFilter)
    if (severityFilter !== 'all') rows = rows.filter(r => r.Severity === severityFilter)
    return rows.sort((a, b) => (b.AnomalyScore ?? 0) - (a.AnomalyScore ?? 0))
  }, [anomaly, detectorFilter, severityFilter])

  const btnStyle = (active) => ({
    padding: '5px 12px', fontSize: 11, cursor: 'pointer', borderRadius: 6, border: `1px solid ${C.border}`,
    background: active ? C.blue : 'transparent', color: active ? '#fff' : C.subtle,
  })

  return (
    <div>
      <SectionTitle>Anomaly &amp; Supplier KPIs</SectionTitle>
      <div style={{ display: 'flex', gap: 12, flexWrap: 'wrap', marginBottom: 20 }}>
        <KpiCard label="Total Anomalies" value={kpis?.total ?? '—'} accent={C.orange} />
        <KpiCard label="HIGH Severity" value={kpis?.high ?? '—'} accent={C.red} />
        <KpiCard label="Suppliers < 50% OTD" value={kpis?.below50 ?? '—'} accent={C.orange} />
        <KpiCard label="Worst Supplier OTD" value={fmtPct(kpis?.worstOTD)}
          accent={C.red} sub={kpis?.worstName} />
      </div>

      {/* Filters */}
      <div style={{ display: 'flex', gap: 16, alignItems: 'center', marginBottom: 16, flexWrap: 'wrap' }}>
        <div style={{ display: 'flex', gap: 4 }}>
          <span style={{ color: C.subtle, fontSize: 11, marginRight: 4 }}>Detector:</span>
          {[['all', 'All'], ['zscore', 'Z-Score'], ['isolation_forest', 'Isolation Forest']].map(([v, l]) => (
            <button key={v} onClick={() => setDetectorFilter(v)} style={btnStyle(detectorFilter === v)}>{l}</button>
          ))}
        </div>
        <div style={{ display: 'flex', gap: 4 }}>
          <span style={{ color: C.subtle, fontSize: 11, marginRight: 4 }}>Severity:</span>
          {[['all', 'All'], ['HIGH', 'HIGH'], ['MEDIUM', 'MEDIUM']].map(([v, l]) => (
            <button key={v} onClick={() => setSeverityFilter(v)} style={btnStyle(severityFilter === v)}>{l}</button>
          ))}
        </div>
      </div>

      <SectionTitle>Suppliers</SectionTitle>
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 12, marginBottom: 20 }}>
        <SupplierOTDBar supplier={supplier} />
        <SupplierRatingScatter supplier={supplier} />
      </div>

      <SectionTitle>Anomaly Timeline &amp; Distribution</SectionTitle>
      <div style={{ display: 'grid', gridTemplateColumns: '2fr 1fr', gap: 12, marginBottom: 20 }}>
        <AnomalyScatterChart anomaly={anomaly} detectorFilter={detectorFilter} severityFilter={severityFilter} />
        <AnomalyDetectorDonut anomaly={anomaly} />
      </div>

      <SectionTitle>Anomaly Heatmap</SectionTitle>
      <AnomalyHeatmap anomaly={anomaly} />

      <SectionTitle>Anomaly Detail Table</SectionTitle>
      <div style={{ background: C.surface, border: `1px solid ${C.border}`, borderRadius: 10, padding: '16px 20px', marginBottom: 20 }}>
        <DataTable rows={filteredAnomalies} columns={ANOMALY_COLS} />
      </div>
    </div>
  )
}
