import { useMemo } from 'react'
import { ComposedChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts'
import { C, AXIS_STYLE, GRID_STYLE, TOOLTIP_STYLE } from '../../utils/colors'
import { fmtNum } from '../../utils/fmt'
import Card from '../ui/Card'

export default function ForecastTimelineChart({ forecast, horizon }) {
  const data = useMemo(() => {
    if (!forecast) return []
    const filtered = forecast.filter(r => r.HorizonDays === horizon)
    const map = {}
    filtered.forEach(r => {
      const d = r.ForecastDate?.slice(0, 10)
      if (!map[d]) map[d] = { date: d }
      map[d][r.ModelName] = (map[d][r.ModelName] || 0) + r.ForecastQty
    })
    return Object.values(map).sort((a, b) => a.date < b.date ? -1 : 1)
  }, [forecast, horizon])

  return (
    <Card>
      <div style={{ fontWeight: 600, fontSize: 14, color: C.text, marginBottom: 12 }}>
        Total Forecasted Demand — {horizon}-Day Horizon (All Products)
      </div>
      <ResponsiveContainer width="100%" height={300}>
        <ComposedChart data={data} margin={{ top: 8, right: 16, left: 0, bottom: 0 }}>
          <CartesianGrid {...GRID_STYLE} />
          <XAxis dataKey="date" {...AXIS_STYLE} interval={Math.floor(data.length / 6)} />
          <YAxis {...AXIS_STYLE} tickFormatter={fmtNum} />
          <Tooltip {...TOOLTIP_STYLE} formatter={(v) => [fmtNum(v, 0), '']} />
          <Legend wrapperStyle={{ fontSize: 11 }} />
          <Line dataKey="ARIMA" stroke={C.blue} strokeWidth={2} dot={false} />
          <Line dataKey="HoltWinters" stroke={C.orange} strokeWidth={2} dot={false} />
        </ComposedChart>
      </ResponsiveContainer>
    </Card>
  )
}
