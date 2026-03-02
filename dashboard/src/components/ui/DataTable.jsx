import { useState, useMemo } from 'react'
import { C } from '../../utils/colors'

export default function DataTable({ rows = [], columns = [], rowStyle }) {
  const [search, setSearch]   = useState('')
  const [sortCol, setSortCol] = useState(null)
  const [sortDir, setSortDir] = useState(1)
  const [page, setPage]       = useState(0)
  const PAGE_SIZE = 10

  const filtered = useMemo(() => {
    if (!search) return rows
    const q = search.toLowerCase()
    return rows.filter(r =>
      columns.some(c => String(r[c.key] ?? '').toLowerCase().includes(q))
    )
  }, [rows, search, columns])

  const sorted = useMemo(() => {
    if (!sortCol) return filtered
    return [...filtered].sort((a, b) => {
      const va = a[sortCol], vb = b[sortCol]
      if (va == null) return 1
      if (vb == null) return -1
      return (va < vb ? -1 : va > vb ? 1 : 0) * sortDir
    })
  }, [filtered, sortCol, sortDir])

  const pages = Math.max(1, Math.ceil(sorted.length / PAGE_SIZE))
  const pageRows = sorted.slice(page * PAGE_SIZE, (page + 1) * PAGE_SIZE)

  const handleSort = (key) => {
    if (sortCol === key) setSortDir(d => -d)
    else { setSortCol(key); setSortDir(1) }
    setPage(0)
  }

  return (
    <div>
      <div style={{ marginBottom: 10 }}>
        <input
          value={search}
          onChange={e => { setSearch(e.target.value); setPage(0) }}
          placeholder="Search…"
          style={{
            background: C.bg, border: `1px solid ${C.border}`, borderRadius: 6,
            color: C.text, padding: '6px 12px', fontSize: 12, width: 220, outline: 'none',
          }}
        />
      </div>
      <div style={{ overflowX: 'auto' }}>
        <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: 12 }}>
          <thead>
            <tr>
              {columns.map(c => (
                <th key={c.key} onClick={() => handleSort(c.key)}
                  style={{
                    textAlign: c.align ?? 'left', padding: '8px 12px',
                    background: C.bg, color: C.subtle, fontWeight: 600,
                    fontSize: 11, letterSpacing: '0.06em', textTransform: 'uppercase',
                    borderBottom: `1px solid ${C.border}`, cursor: 'pointer',
                    whiteSpace: 'nowrap', userSelect: 'none',
                  }}>
                  {c.label} {sortCol === c.key ? (sortDir === 1 ? '↑' : '↓') : ''}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {pageRows.map((row, i) => (
              <tr key={i} style={{
                borderBottom: `1px solid ${C.border}`,
                background: rowStyle ? rowStyle(row) : (i % 2 === 1 ? `${C.surface}80` : 'transparent'),
              }}>
                {columns.map(c => (
                  <td key={c.key} style={{ padding: '8px 12px', color: C.text, textAlign: c.align ?? 'left' }}>
                    {c.render ? c.render(row[c.key], row) : (row[c.key] ?? '—')}
                  </td>
                ))}
              </tr>
            ))}
            {pageRows.length === 0 && (
              <tr><td colSpan={columns.length} style={{ padding: 24, textAlign: 'center', color: C.subtle }}>No results</td></tr>
            )}
          </tbody>
        </table>
      </div>
      {pages > 1 && (
        <div style={{ display: 'flex', gap: 6, marginTop: 10, alignItems: 'center' }}>
          <span style={{ color: C.subtle, fontSize: 11 }}>{sorted.length} rows</span>
          <button onClick={() => setPage(p => Math.max(0, p - 1))} disabled={page === 0}
            style={{ ...btnStyle, opacity: page === 0 ? 0.4 : 1 }}>←</button>
          <span style={{ color: C.text, fontSize: 12 }}>{page + 1} / {pages}</span>
          <button onClick={() => setPage(p => Math.min(pages - 1, p + 1))} disabled={page === pages - 1}
            style={{ ...btnStyle, opacity: page === pages - 1 ? 0.4 : 1 }}>→</button>
        </div>
      )}
    </div>
  )
}

const btnStyle = {
  background: 'none', border: `1px solid #2a2d3e`, borderRadius: 4,
  color: '#e8eaf6', padding: '3px 10px', cursor: 'pointer', fontSize: 12,
}
