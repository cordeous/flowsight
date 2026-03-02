import { ScatterChart, Scatter, XAxis, YAxis, CartesianGrid, Tooltip, LabelList, ResponsiveContainer } from 'recharts'
import { C, AXIS_STYLE, GRID_STYLE, TOOLTIP_STYLE } from '../../utils/colors'
import Card from '../ui/Card'

const CustomTooltip = ({ active, payload }) => {
  if (!active || !payload?.length) return null
  const d = payload[0]?.payload
  return (
    <div style={{ ...TOOLTIP_STYLE.contentStyle, padding: '10px 14px', fontSize: 12 }}>
      <div style={{ fontWeight: 700, marginBottom: 4 }}>{d.SupplierName}</div>
      <div>Rating: {d.Rating}</div>
      <div>OTD: <b>{d.OnTimeDeliveryPct?.toFixed(1)}%</b></div>
      <div>Country: {d.Country}</div>
    </div>
  )
}

export default function SupplierRatingScatter({ supplier }) {
  return (
    <Card>
      <div style={{ fontWeight: 600, fontSize: 14, color: C.text, marginBottom: 12 }}>Supplier Rating vs OTD %</div>
      <ResponsiveContainer width="100%" height={260}>
        <ScatterChart margin={{ top: 8, right: 24, left: 0, bottom: 0 }}>
          <CartesianGrid {...GRID_STYLE} />
          <XAxis dataKey="Rating" {...AXIS_STYLE} domain={[0, 5.5]} label={{ value: 'Rating (1-5)', position: 'insideBottom', offset: -4, fill: C.subtle, fontSize: 11 }} height={44} />
          <YAxis dataKey="OnTimeDeliveryPct" {...AXIS_STYLE} label={{ value: 'OTD %', angle: -90, position: 'insideLeft', fill: C.subtle, fontSize: 11 }} />
          <Tooltip content={<CustomTooltip />} />
          <Scatter data={supplier || []} fill={C.blue} opacity={0.85}>
            <LabelList dataKey="SupplierName" position="top" style={{ fill: C.subtle, fontSize: 9 }}
              formatter={v => v?.split(' ')[0]} />
          </Scatter>
        </ScatterChart>
      </ResponsiveContainer>
    </Card>
  )
}
