import { useMemo } from 'react'
import { ScatterChart, Scatter, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend } from 'recharts'
import { C, SEVERITY_COLORS, AXIS_STYLE, GRID_STYLE, TOOLTIP_STYLE } from '../../utils/colors'
import Card from '../ui/Card'

const CustomTooltip = ({ active, payload }) => {
  if (!active || !payload?.length) return null
  const d = payload[0]?.payload
  return (
    <div style={{ ...TOOLTIP_STYLE.contentStyle, padding: '10px 14px', fontSize: 12 }}>
      <div style={{ fontWeight: 700, marginBottom: 4 }}>{d.ProductName}</div>
      <div>Date: {d.AnomalyDate?.slice(0, 10)}</div>
      <div>Score: <b>{d.AnomalyScore?.toFixed(3)}</b></div>
      <div>Feature: {d.FeatureName} = {d.FeatureValue?.toFixed(1)}</div>
      <div>Detector: {d.DetectorType}</div>
    </div>
  )
}

export default function AnomalyScatterChart({ anomaly, detectorFilter, severityFilter }) {
  const { high, medium } = useMemo(() => {
    let rows = anomaly || []
    if (detectorFilter !== 'all') rows = rows.filter(r => r.DetectorType === detectorFilter)
    if (severityFilter !== 'all') rows = rows.filter(r => r.Severity === severityFilter)
    const withTs = rows.map(r => ({ ...r, ts: new Date(r.AnomalyDate).getTime() }))
    return {
      high:   withTs.filter(r => r.Severity === 'HIGH'),
      medium: withTs.filter(r => r.Severity === 'MEDIUM'),
    }
  }, [anomaly, detectorFilter, severityFilter])

  const allTs = [...high, ...medium].map(r => r.ts)
  const [minTs, maxTs] = [Math.min(...allTs), Math.max(...allTs)]

  const fmtTick = (ts) => {
    const d = new Date(ts)
    return `${d.getMonth() + 1}/${d.getFullYear().toString().slice(2)}`
  }

  return (
    <Card>
      <div style={{ fontWeight: 600, fontSize: 14, color: C.text, marginBottom: 12 }}>Anomaly Score Timeline</div>
      <ResponsiveContainer width="100%" height={320}>
        <ScatterChart margin={{ top: 8, right: 16, left: 0, bottom: 0 }}>
          <CartesianGrid {...GRID_STYLE} />
          <XAxis dataKey="ts" type="number" domain={[minTs - 86400000, maxTs + 86400000]}
            {...AXIS_STYLE} tickFormatter={fmtTick} scale="time" />
          <YAxis dataKey="AnomalyScore" {...AXIS_STYLE} domain={[0, 1.1]}
            label={{ value: 'Score', angle: -90, position: 'insideLeft', fill: C.subtle, fontSize: 11 }} />
          <Tooltip content={<CustomTooltip />} />
          <Legend wrapperStyle={{ fontSize: 11 }} />
          <Scatter name="HIGH" data={high} fill={SEVERITY_COLORS.HIGH} opacity={0.85} />
          <Scatter name="MEDIUM" data={medium} fill={SEVERITY_COLORS.MEDIUM} opacity={0.85} />
        </ScatterChart>
      </ResponsiveContainer>
    </Card>
  )
}
