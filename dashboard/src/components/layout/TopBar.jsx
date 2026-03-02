import { useData } from '../../context/DataContext'
import { C } from '../../utils/colors'
import { useMemo } from 'react'

export default function TopBar() {
  const { reorder, stockout, anomaly } = useData()

  const stats = useMemo(() => {
    if (!reorder || !stockout || !anomaly) return null
    return {
      orderNow:    reorder.filter(r => r.AlertStatus === 'ORDER NOW').length,
      belowROP:    stockout.filter(r => r.BelowReorderPoint === 1).length,
      total:       stockout.length,
      anomalies:   anomaly.length,
      high:        anomaly.filter(r => r.Severity === 'HIGH').length,
    }
  }, [reorder, stockout, anomaly])

  if (!stats) return null

  return (
    <div style={{
      background: `${C.red}14`,
      border: `1px solid ${C.red}55`,
      borderRadius: 8,
      padding: '9px 16px',
      display: 'flex',
      alignItems: 'center',
      gap: 16,
      flexWrap: 'wrap',
      marginBottom: 16,
      fontSize: 12,
    }}>
      <span>⚠️ <b style={{ color: C.red }}>{stats.orderNow} ORDER NOW</b> reorder alerts</span>
      <span style={{ color: C.border }}>|</span>
      <span><b style={{ color: C.orange }}>{stats.belowROP}/{stats.total}</b> products below ROP</span>
      <span style={{ color: C.border }}>|</span>
      <span><b style={{ color: C.orange }}>{stats.anomalies}</b> anomalies detected (<b style={{ color: C.red }}>{stats.high} HIGH</b>)</span>
    </div>
  )
}
