import { useMemo } from 'react'
import Card from '../ui/Card'
import { C } from '../../utils/colors'

function heatColor(v) {
  if (v == null) return C.border
  if (v < 1)   return '#dc354580'
  if (v < 2.5) return '#fd7e1480'
  if (v < 4)   return '#ffc10780'
  return '#19875480'
}

export default function TurnoverHeatmap({ turnover }) {
  const { products, months, grid } = useMemo(() => {
    if (!turnover) return { products: [], months: [], grid: {} }
    const prodSet = new Set(), monthSet = new Set()
    const grid = {}
    turnover.forEach(r => {
      prodSet.add(r.ProductName)
      monthSet.add(r.YearMonth)
      if (!grid[r.ProductName]) grid[r.ProductName] = {}
      grid[r.ProductName][r.YearMonth] = r.InventoryTurnoverRatio
    })
    const months = [...monthSet].sort()
    // show top 20 products by avg turnover for readability
    const products = [...prodSet].sort((a, b) => {
      const avgA = months.reduce((s, m) => s + (grid[a][m] || 0), 0) / months.length
      const avgB = months.reduce((s, m) => s + (grid[b][m] || 0), 0) / months.length
      return avgA - avgB
    }).slice(0, 20)
    return { products, months, grid }
  }, [turnover])

  if (!products.length) return null
  const CELL_H = 22, LABEL_W = 150

  return (
    <Card>
      <div style={{ fontWeight: 600, fontSize: 14, color: C.text, marginBottom: 12 }}>
        Inventory Turnover Heatmap (Top 20 Products)
        <span style={{ marginLeft: 12, fontSize: 11, color: C.subtle }}>
          <span style={{ color: '#dc3545' }}>■</span> &lt;1x &nbsp;
          <span style={{ color: '#fd7e14' }}>■</span> 1-2.5x &nbsp;
          <span style={{ color: '#ffc107' }}>■</span> 2.5-4x &nbsp;
          <span style={{ color: '#198754' }}>■</span> &gt;4x
        </span>
      </div>
      <div style={{ overflowX: 'auto' }}>
        <div style={{ minWidth: LABEL_W + months.length * 28 }}>
          {/* Month header */}
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
                const v = grid[prod]?.[m]
                return (
                  <div key={m} title={`${prod} — ${m}: ${v?.toFixed(2) ?? 'N/A'}x`}
                    style={{ width: 26, height: CELL_H, background: heatColor(v), borderRadius: 2, margin: 1 }} />
                )
              })}
            </div>
          ))}
        </div>
      </div>
    </Card>
  )
}
