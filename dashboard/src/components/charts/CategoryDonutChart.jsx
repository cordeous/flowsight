import { useMemo } from 'react'
import { PieChart, Pie, Cell, Tooltip, ResponsiveContainer } from 'recharts'
import { C, CATEGORY_COLORS, CHART_PALETTE, TOOLTIP_STYLE } from '../../utils/colors'
import { fmtCurrency } from '../../utils/fmt'
import Card from '../ui/Card'

export default function CategoryDonutChart({ sales }) {
  const data = useMemo(() => {
    if (!sales) return []
    const map = {}
    sales.forEach(r => { map[r.Category] = (map[r.Category] || 0) + r.TotalRevenue })
    return Object.entries(map).map(([name, value]) => ({ name, value }))
      .sort((a, b) => b.value - a.value)
  }, [sales])

  const total = data.reduce((s, d) => s + d.value, 0)

  return (
    <Card>
      <div style={{ fontWeight: 600, fontSize: 14, color: C.text, marginBottom: 12 }}>Revenue by Category</div>
      <ResponsiveContainer width="100%" height={260}>
        <PieChart>
          <Pie data={data} cx="50%" cy="50%" innerRadius={70} outerRadius={100}
            dataKey="value" nameKey="name" paddingAngle={2}>
            {data.map((entry, i) => (
              <Cell key={entry.name} fill={CATEGORY_COLORS[entry.name] || CHART_PALETTE[i]} />
            ))}
          </Pie>
          <Tooltip {...TOOLTIP_STYLE} formatter={(v) => [fmtCurrency(v), '']} />
        </PieChart>
      </ResponsiveContainer>
      <div style={{ display: 'flex', flexWrap: 'wrap', gap: '6px 16px', marginTop: 4 }}>
        {data.map((d, i) => (
          <div key={d.name} style={{ display: 'flex', alignItems: 'center', gap: 6, fontSize: 11, color: C.subtle }}>
            <div style={{ width: 10, height: 10, borderRadius: 2, background: CATEGORY_COLORS[d.name] || CHART_PALETTE[i] }} />
            {d.name} <span style={{ color: C.text }}>{((d.value / total) * 100).toFixed(1)}%</span>
          </div>
        ))}
      </div>
    </Card>
  )
}
