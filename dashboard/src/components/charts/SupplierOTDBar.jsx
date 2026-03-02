import { useMemo } from 'react'
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ReferenceLine, ResponsiveContainer, Cell } from 'recharts'
import { C, AXIS_STYLE, GRID_STYLE, TOOLTIP_STYLE } from '../../utils/colors'
import Card from '../ui/Card'

function barColor(v) {
  if (v < 25) return C.red
  if (v < 50) return C.orange
  return C.green
}

const CustomTooltip = ({ active, payload }) => {
  if (!active || !payload?.length) return null
  const d = payload[0]?.payload
  return (
    <div style={{ ...TOOLTIP_STYLE.contentStyle, padding: '10px 14px', fontSize: 12 }}>
      <div style={{ fontWeight: 700, marginBottom: 4 }}>{d.SupplierName}</div>
      <div>Country: {d.Country}</div>
      <div>OTD: <b>{d.OnTimeDeliveryPct?.toFixed(1)}%</b></div>
      <div>Avg Delay: {d.AvgDelayDays?.toFixed(1)} days</div>
      <div>Total Shipments: {d.TotalShipments}</div>
      <div>Rating: {d.Rating}</div>
    </div>
  )
}

export default function SupplierOTDBar({ supplier }) {
  const data = useMemo(() =>
    (supplier || []).slice().sort((a, b) => a.OnTimeDeliveryPct - b.OnTimeDeliveryPct),
    [supplier]
  )

  return (
    <Card>
      <div style={{ fontWeight: 600, fontSize: 14, color: C.text, marginBottom: 12 }}>Supplier On-Time Delivery %</div>
      <ResponsiveContainer width="100%" height={380}>
        <BarChart data={data} layout="vertical" margin={{ top: 0, right: 50, left: 0, bottom: 0 }}>
          <CartesianGrid {...GRID_STYLE} horizontal={false} />
          <XAxis type="number" {...AXIS_STYLE} domain={[0, 110]} tickFormatter={v => `${v}%`} />
          <YAxis type="category" dataKey="SupplierName" {...AXIS_STYLE} width={140} />
          <Tooltip content={<CustomTooltip />} />
          <ReferenceLine x={50} stroke={C.subtle} strokeDasharray="4 4" label={{ value: '50%', fill: C.subtle, fontSize: 10 }} />
          <Bar dataKey="OnTimeDeliveryPct" radius={[0, 4, 4, 0]} label={{ position: 'right', fill: C.subtle, fontSize: 10, formatter: v => `${v?.toFixed(0)}%` }}>
            {data.map((d, i) => <Cell key={i} fill={barColor(d.OnTimeDeliveryPct)} />)}
          </Bar>
        </BarChart>
      </ResponsiveContainer>
    </Card>
  )
}
