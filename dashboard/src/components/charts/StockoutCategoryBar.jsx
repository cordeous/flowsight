import { useMemo } from 'react'
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts'
import { C, AXIS_STYLE, GRID_STYLE, TOOLTIP_STYLE } from '../../utils/colors'
import Card from '../ui/Card'

export default function StockoutCategoryBar({ stockout }) {
  const data = useMemo(() => {
    if (!stockout) return []
    const map = {}
    stockout.forEach(r => {
      if (!map[r.Category]) map[r.Category] = { name: r.Category, Stockout: 0, 'In Stock': 0 }
      if (r.IsStockout === 1) map[r.Category].Stockout++
      else map[r.Category]['In Stock']++
    })
    return Object.values(map)
  }, [stockout])

  return (
    <Card>
      <div style={{ fontWeight: 600, fontSize: 14, color: C.text, marginBottom: 12 }}>Stockout by Category</div>
      <ResponsiveContainer width="100%" height={240}>
        <BarChart data={data} margin={{ top: 8, right: 16, left: 0, bottom: 0 }}>
          <CartesianGrid {...GRID_STYLE} />
          <XAxis dataKey="name" {...AXIS_STYLE} />
          <YAxis {...AXIS_STYLE} />
          <Tooltip {...TOOLTIP_STYLE} />
          <Legend wrapperStyle={{ fontSize: 11 }} />
          <Bar dataKey="Stockout" fill={C.red} radius={[4, 4, 0, 0]} />
          <Bar dataKey="In Stock" fill={C.green} radius={[4, 4, 0, 0]} />
        </BarChart>
      </ResponsiveContainer>
    </Card>
  )
}
