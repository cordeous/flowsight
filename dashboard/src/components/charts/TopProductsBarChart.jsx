import { useMemo } from 'react'
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Cell } from 'recharts'
import { C, AXIS_STYLE, GRID_STYLE, TOOLTIP_STYLE } from '../../utils/colors'
import { fmtCurrency } from '../../utils/fmt'
import Card from '../ui/Card'

export default function TopProductsBarChart({ sales }) {
  const data = useMemo(() => {
    if (!sales) return []
    const map = {}
    sales.forEach(r => { map[r.ProductName] = (map[r.ProductName] || 0) + r.TotalRevenue })
    return Object.entries(map)
      .sort((a, b) => b[1] - a[1]).slice(0, 12)
      .map(([name, value]) => ({ name: name.length > 22 ? name.slice(0, 20) + '…' : name, value }))
  }, [sales])

  return (
    <Card>
      <div style={{ fontWeight: 600, fontSize: 14, color: C.text, marginBottom: 12 }}>Top 12 Products by Revenue</div>
      <ResponsiveContainer width="100%" height={360}>
        <BarChart data={data} layout="vertical" margin={{ top: 0, right: 60, left: 0, bottom: 0 }}>
          <CartesianGrid {...GRID_STYLE} horizontal={false} />
          <XAxis type="number" {...AXIS_STYLE} tickFormatter={fmtCurrency} />
          <YAxis type="category" dataKey="name" {...AXIS_STYLE} width={160} />
          <Tooltip {...TOOLTIP_STYLE} formatter={(v) => [fmtCurrency(v, false), 'Revenue']} />
          <Bar dataKey="value" radius={[0, 4, 4, 0]} label={{ position: 'right', fill: C.subtle, fontSize: 10, formatter: fmtCurrency }}>
            {data.map((_, i) => <Cell key={i} fill={i === 0 ? C.blue : i < 3 ? `${C.blue}bb` : `${C.blue}66`} />)}
          </Bar>
        </BarChart>
      </ResponsiveContainer>
    </Card>
  )
}
