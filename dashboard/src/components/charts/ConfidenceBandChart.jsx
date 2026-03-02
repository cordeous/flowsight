import { useMemo } from 'react'
import { ComposedChart, Area, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts'
import { C, AXIS_STYLE, GRID_STYLE, TOOLTIP_STYLE } from '../../utils/colors'
import { fmtNum } from '../../utils/fmt'
import Card from '../ui/Card'

export default function ConfidenceBandChart({ forecast, productId, horizon }) {
  const { data, productName } = useMemo(() => {
    if (!forecast || !productId) return { data: [], productName: '' }
    const rows = forecast.filter(r => r.ProductID === productId && r.HorizonDays === horizon)
      .sort((a, b) => a.ForecastDate < b.ForecastDate ? -1 : 1)

    const byModel = {}
    rows.forEach(r => {
      if (!byModel[r.ModelName]) byModel[r.ModelName] = []
      byModel[r.ModelName].push(r)
    })

    const arima = byModel['ARIMA'] || []
    const hw = byModel['HoltWinters'] || []
    const dates = [...new Set(rows.map(r => r.ForecastDate?.slice(0, 10)))].sort()

    const arimaMap = Object.fromEntries(arima.map(r => [r.ForecastDate?.slice(0, 10), r]))
    const hwMap = Object.fromEntries(hw.map(r => [r.ForecastDate?.slice(0, 10), r]))

    const data = dates.map(d => ({
      date: d,
      ARIMA: arimaMap[d]?.ForecastQty ?? null,
      Lower: arimaMap[d]?.LowerBound ?? null,
      Upper: arimaMap[d]?.UpperBound ?? null,
      HoltWinters: hwMap[d]?.ForecastQty ?? null,
    }))

    return { data, productName: arima[0]?.ProductName || `Product ${productId}` }
  }, [forecast, productId, horizon])

  return (
    <Card>
      <div style={{ fontWeight: 600, fontSize: 14, color: C.text, marginBottom: 12 }}>
        Forecast with Confidence Band — {productName} ({horizon}d)
      </div>
      <ResponsiveContainer width="100%" height={300}>
        <ComposedChart data={data} margin={{ top: 8, right: 16, left: 0, bottom: 0 }}>
          <CartesianGrid {...GRID_STYLE} />
          <XAxis dataKey="date" {...AXIS_STYLE} interval={Math.floor(data.length / 5)} />
          <YAxis {...AXIS_STYLE} tickFormatter={fmtNum} />
          <Tooltip {...TOOLTIP_STYLE} formatter={(v, n) => [fmtNum(v, 0), n]} />
          <Legend wrapperStyle={{ fontSize: 11 }} />
          <Area dataKey="Upper" fill={`${C.blue}18`} stroke="none" name="Upper Bound" legendType="none" />
          <Area dataKey="Lower" fill={C.bg} stroke="none" name="Lower Bound" legendType="none" />
          <Line dataKey="ARIMA" stroke={C.blue} strokeWidth={2} dot={false} />
          <Line dataKey="HoltWinters" stroke={C.orange} strokeWidth={2} dot={false} />
        </ComposedChart>
      </ResponsiveContainer>
    </Card>
  )
}
