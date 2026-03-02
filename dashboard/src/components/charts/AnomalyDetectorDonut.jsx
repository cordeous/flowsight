import { useMemo } from 'react'
import { PieChart, Pie, Cell, Tooltip, ResponsiveContainer } from 'recharts'
import { C, CHART_PALETTE, TOOLTIP_STYLE } from '../../utils/colors'
import Card from '../ui/Card'

export default function AnomalyDetectorDonut({ anomaly }) {
  const data = useMemo(() => {
    if (!anomaly) return []
    const map = {}
    anomaly.forEach(r => { map[r.DetectorType] = (map[r.DetectorType] || 0) + 1 })
    return Object.entries(map).map(([name, value]) => ({
      name: name === 'isolation_forest' ? 'Isolation Forest' : 'Z-Score',
      value,
    }))
  }, [anomaly])

  return (
    <Card>
      <div style={{ fontWeight: 600, fontSize: 14, color: C.text, marginBottom: 12 }}>Anomalies by Detector</div>
      <ResponsiveContainer width="100%" height={220}>
        <PieChart>
          <Pie data={data} cx="50%" cy="50%" innerRadius={60} outerRadius={90}
            dataKey="value" nameKey="name" paddingAngle={3} label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
            labelLine={{ stroke: C.subtle }} fontSize={11}>
            {data.map((_, i) => <Cell key={i} fill={CHART_PALETTE[i]} />)}
          </Pie>
          <Tooltip {...TOOLTIP_STYLE} />
        </PieChart>
      </ResponsiveContainer>
    </Card>
  )
}
