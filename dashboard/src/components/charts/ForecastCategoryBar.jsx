import { useMemo } from 'react'
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Cell } from 'recharts'
import { C, CATEGORY_COLORS, CHART_PALETTE, AXIS_STYLE, GRID_STYLE, TOOLTIP_STYLE } from '../../utils/colors'
import { fmtNum } from '../../utils/fmt'
import Card from '../ui/Card'

export default function ForecastCategoryBar({ forecast, horizon }) {
  const data = useMemo(() => {
    if (!forecast) return []
    const map = {}
    forecast.filter(r => r.HorizonDays === horizon && r.ModelName === 'ARIMA')
      .forEach(r => { map[r.Category] = (map[r.Category] || 0) + r.ForecastQty })
    return Object.entries(map).map(([name, value]) => ({ name, value }))
      .sort((a, b) => a.value - b.value)
  }, [forecast, horizon])

  return (
    <Card>
      <div style={{ fontWeight: 600, fontSize: 14, color: C.text, marginBottom: 12 }}>
        {horizon}-Day Forecast by Category (ARIMA)
      </div>
      <ResponsiveContainer width="100%" height={240}>
        <BarChart data={data} layout="vertical" margin={{ top: 0, right: 60, left: 0, bottom: 0 }}>
          <CartesianGrid {...GRID_STYLE} horizontal={false} />
          <XAxis type="number" {...AXIS_STYLE} tickFormatter={fmtNum} />
          <YAxis type="category" dataKey="name" {...AXIS_STYLE} width={130} />
          <Tooltip {...TOOLTIP_STYLE} formatter={(v) => [fmtNum(v, 0), 'Units']} />
          <Bar dataKey="value" radius={[0, 4, 4, 0]} label={{ position: 'right', fill: C.subtle, fontSize: 10, formatter: fmtNum }}>
            {data.map((d, i) => <Cell key={i} fill={CATEGORY_COLORS[d.name] || CHART_PALETTE[i]} />)}
          </Bar>
        </BarChart>
      </ResponsiveContainer>
    </Card>
  )
}
