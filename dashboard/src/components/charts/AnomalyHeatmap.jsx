import { useMemo } from 'react'
import Card from '../ui/Card'
import { C } from '../../utils/colors'

function heatColor(v) {
  if (!v) return 'transparent'
  if (v === 1) return `${C.orange}55`
  if (v === 2) return `${C.orange}99`
  return `${C.red}bb`
}

export default function AnomalyHeatmap({ anomaly }) {
  const { products, months, grid } = useMemo(() => {
    if (!anomaly) return { products: [], months: [], grid: {} }
    const grid = {}
    const monthSet = new Set()
    anomaly.forEach(r => {
      const m = r.AnomalyDate?.slice(0, 7)
      if (!m) return
      monthSet.add(m)
      if (!grid[r.ProductName]) grid[r.ProductName] = {}
      grid[r.ProductName][m] = (grid[r.ProductName][m] || 0) + 1
    })
    const months = [...monthSet].sort()
    const products = Object.keys(grid).sort((a, b) => {
      const sa = Object.values(grid[a]).reduce((x, y) => x + y, 0)
      const sb = Object.values(grid[b]).reduce((x, y) => x + y, 0)
      return sb - sa
    })
    return { products, months, grid }
  }, [anomaly])

  if (!products.length) return null
  const CELL_H = 22, LABEL_W = 150

  return (
    <Card>
      <div style={{ fontWeight: 600, fontSize: 14, color: C.text, marginBottom: 12 }}>
        Anomaly Heatmap (Product × Month)
        <span style={{ marginLeft: 12, fontSize: 11, color: C.subtle }}>
          <span style={{ color: C.orange }}>■</span> 1-2 &nbsp;
          <span style={{ color: C.red }}>■</span> 3+
        </span>
      </div>
      <div style={{ overflowX: 'auto' }}>
        <div style={{ minWidth: LABEL_W + months.length * 28 }}>
          <div style={{ display: 'flex', marginLeft: LABEL_W, marginBottom: 2 }}>
            {months.map(m => (
              <div key={m} style={{ width: 28, fontSize: 8, color: C.subtle, textAlign: 'center', transform: 'rotate(-60deg)', transformOrigin: 'bottom center', height: 36, lineHeight: '36px' }}>
                {m.slice(5)}
              </div>
            ))}
          </div>
          {products.map(prod => (
            <div key={prod} style={{ display: 'flex', alignItems: 'center', marginBottom: 2 }}>
              <div style={{ width: LABEL_W, fontSize: 10, color: C.subtle, paddingRight: 8, textAlign: 'right', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                {prod.length > 20 ? prod.slice(0, 18) + '…' : prod}
              </div>
              {months.map(m => {
                const v = grid[prod]?.[m] || 0
                return (
                  <div key={m} title={`${prod} — ${m}: ${v} anomaly${v !== 1 ? 'ies' : ''}`}
                    style={{ width: 26, height: CELL_H, background: heatColor(v), borderRadius: 2, margin: 1, border: `1px solid ${C.border}` }} />
                )
              })}
            </div>
          ))}
        </div>
      </div>
    </Card>
  )
}
