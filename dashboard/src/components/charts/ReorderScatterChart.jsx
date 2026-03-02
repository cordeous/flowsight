import { useMemo } from 'react'
import { ScatterChart, Scatter, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, ReferenceLine, Legend } from 'recharts'
import { C, ALERT_COLORS, AXIS_STYLE, GRID_STYLE, TOOLTIP_STYLE } from '../../utils/colors'
import Card from '../ui/Card'

const CustomTooltip = ({ active, payload }) => {
  if (!active || !payload?.length) return null
  const d = payload[0]?.payload
  return (
    <div style={{ ...TOOLTIP_STYLE.contentStyle, padding: '10px 14px', fontSize: 12 }}>
      <div style={{ fontWeight: 700, marginBottom: 4, color: '#e8eaf6' }}>{d?.ProductName}</div>
      <div>On Hand: <b>{d?.QuantityOnHand}</b></div>
      <div>ROP: <b>{d?.RecommendedROP}</b></div>
      <div>Status: <b style={{ color: ALERT_COLORS[d?.AlertStatus] }}>{d?.AlertStatus}</b></div>
    </div>
  )
}

export default function ReorderScatterChart({ reorder }) {
  const { byStatus, maxVal } = useMemo(() => {
    if (!reorder) return { byStatus: {}, maxVal: 100 }
    const statuses = ['ORDER NOW', 'ORDER SOON', 'OK']
    const byStatus = {}
    let max = 0
    statuses.forEach(s => { byStatus[s] = [] })
    reorder.forEach(r => {
      const s = r.AlertStatus
      if (byStatus[s]) byStatus[s].push(r)
      max = Math.max(max, r.RecommendedROP || 0, r.QuantityOnHand || 0)
    })
    return { byStatus, maxVal: max * 1.1 }
  }, [reorder])

  return (
    <Card>
      <div style={{ fontWeight: 600, fontSize: 14, color: C.text, marginBottom: 12 }}>Stock on Hand vs Reorder Point</div>
      <ResponsiveContainer width="100%" height={320}>
        <ScatterChart margin={{ top: 8, right: 16, left: 0, bottom: 0 }}>
          <CartesianGrid {...GRID_STYLE} />
          <XAxis dataKey="RecommendedROP" name="ROP" {...AXIS_STYLE} label={{ value: 'Recommended ROP', position: 'insideBottom', offset: -4, fill: C.subtle, fontSize: 11 }} height={44} domain={[0, maxVal]} />
          <YAxis dataKey="QuantityOnHand" name="On Hand" {...AXIS_STYLE} label={{ value: 'Qty On Hand', angle: -90, position: 'insideLeft', fill: C.subtle, fontSize: 11 }} domain={[0, maxVal]} />
          <Tooltip content={<CustomTooltip />} />
          <ReferenceLine segment={[{ x: 0, y: 0 }, { x: maxVal, y: maxVal }]}
            stroke={C.subtle} strokeDasharray="4 4" label={{ value: 'At ROP', fill: C.subtle, fontSize: 10 }} />
          {Object.entries(ALERT_COLORS).map(([status, color]) => (
            <Scatter key={status} name={status} data={byStatus[status] || []}
              fill={color} opacity={0.85} />
          ))}
          <Legend wrapperStyle={{ fontSize: 11, color: C.subtle }} />
        </ScatterChart>
      </ResponsiveContainer>
    </Card>
  )
}
