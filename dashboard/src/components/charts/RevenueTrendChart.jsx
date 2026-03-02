import { useMemo, useState } from 'react'
import { ComposedChart, Line, Area, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts'
import { C, CATEGORY_COLORS, AXIS_STYLE, GRID_STYLE, TOOLTIP_STYLE, CHART_PALETTE } from '../../utils/colors'
import { fmtCurrency } from '../../utils/fmt'
import Card from '../ui/Card'

export default function RevenueTrendChart({ sales }) {
  const [byCategory, setByCategory] = useState(false)

  const chartData = useMemo(() => {
    if (!sales) return []
    if (!byCategory) {
      const map = {}
      sales.forEach(r => {
        map[r.YearMonth] = (map[r.YearMonth] || 0) + r.TotalRevenue
      })
      return Object.entries(map).sort(([a], [b]) => a < b ? -1 : 1)
        .map(([ym, rev]) => ({ ym, Total: rev }))
    }
    const cats = [...new Set(sales.map(r => r.Category))].sort()
    const map = {}
    sales.forEach(r => {
      if (!map[r.YearMonth]) map[r.YearMonth] = { ym: r.YearMonth }
      map[r.YearMonth][r.Category] = (map[r.YearMonth][r.Category] || 0) + r.TotalRevenue
    })
    return Object.values(map).sort((a, b) => a.ym < b.ym ? -1 : 1)
  }, [sales, byCategory])

  const categories = useMemo(() => sales ? [...new Set(sales.map(r => r.Category))].sort() : [], [sales])

  return (
    <Card>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 12 }}>
        <span style={{ fontWeight: 600, fontSize: 14, color: C.text }}>Monthly Revenue</span>
        <button onClick={() => setByCategory(b => !b)} style={{
          background: byCategory ? C.blue : 'transparent', border: `1px solid ${C.border}`,
          color: byCategory ? '#fff' : C.subtle, borderRadius: 6, padding: '4px 12px',
          fontSize: 11, cursor: 'pointer',
        }}>By Category</button>
      </div>
      <ResponsiveContainer width="100%" height={300}>
        <ComposedChart data={chartData} margin={{ top: 8, right: 16, left: 0, bottom: 0 }}>
          <CartesianGrid {...GRID_STYLE} />
          <XAxis dataKey="ym" {...AXIS_STYLE} interval={3} angle={-35} textAnchor="end" height={50} />
          <YAxis {...AXIS_STYLE} tickFormatter={v => fmtCurrency(v)} width={72} />
          <Tooltip {...TOOLTIP_STYLE} formatter={(v) => [fmtCurrency(v), '']} />
          {!byCategory && (
            <>
              <Area dataKey="Total" fill={`${C.blue}18`} stroke="none" />
              <Line dataKey="Total" stroke={C.blue} strokeWidth={2} dot={false} />
            </>
          )}
          {byCategory && categories.map((cat, i) => (
            <Line key={cat} dataKey={cat} stroke={CATEGORY_COLORS[cat] || CHART_PALETTE[i]} strokeWidth={2} dot={false} />
          ))}
          {byCategory && <Legend wrapperStyle={{ fontSize: 11, color: C.subtle }} />}
        </ComposedChart>
      </ResponsiveContainer>
    </Card>
  )
}
