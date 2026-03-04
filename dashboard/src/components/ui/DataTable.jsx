import { useState, useMemo } from 'react'

export default function DataTable({ rows = [], columns = [], rowStyle }) {
  const [search, setSearch] = useState('')
  const [sortCol, setSortCol] = useState(null)
  const [sortDir, setSortDir] = useState(1)
  const [page, setPage] = useState(0)
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
    <div className="flex flex-col h-full w-full">
      <div className="mb-4 flex items-center justify-between gap-4 flex-wrap">
        <div className="relative">
          <svg className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
          </svg>
          <input
            value={search}
            onChange={e => { setSearch(e.target.value); setPage(0) }}
            placeholder="Search..."
            className="bg-slate-50/50 border border-slate-200 rounded-lg pl-9 pr-4 py-2 text-sm text-slate-700 placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent transition-all w-64 shadow-sm"
          />
        </div>
      </div>

      <div className="overflow-x-auto w-full rounded-xl border border-slate-200 bg-white/20 backdrop-blur-sm shadow-xl">
        <table className="w-full text-sm text-left">
          <thead className="bg-slate-50/60 sticky top-0 z-10 backdrop-blur-md">
            <tr>
              {columns.map(c => (
                <th
                  key={c.key}
                  onClick={() => handleSort(c.key)}
                  className={`px-4 py-3 text-xs font-semibold text-slate-500 tracking-wider uppercase border-b border-slate-200 cursor-pointer hover:bg-slate-100/50 transition-colors select-none whitespace-nowrap ${c.align === 'right' ? 'text-right' : 'text-left'}`}
                >
                  <div className={`flex items-center gap-2 ${c.align === 'right' ? 'justify-end' : 'justify-start'}`}>
                    {c.label}
                    {sortCol === c.key && (
                      <span className="text-indigo-500 font-bold">{sortDir === 1 ? '↑' : '↓'}</span>
                    )}
                  </div>
                </th>
              ))}
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-100">
            {pageRows.map((row, i) => {
              const customStyle = rowStyle ? rowStyle(row) : '';
              const bgClass = customStyle !== 'transparent' && customStyle ? customStyle : (i % 2 === 0 ? 'bg-transparent' : 'bg-slate-50/50');

              return (
                <tr key={i} className={`hover:bg-slate-100/50 transition-colors ${bgClass}`}>
                  {columns.map(c => (
                    <td key={c.key} className={`px-4 py-3 text-slate-600 ${c.align === 'right' ? 'text-right' : 'text-left'}`}>
                      {c.render ? c.render(row[c.key], row) : (row[c.key] ?? '—')}
                    </td>
                  ))}
                </tr>
              )
            })}
            {pageRows.length === 0 && (
              <tr>
                <td colSpan={columns.length} className="px-6 py-12 text-center text-slate-500 font-medium">
                  No results found matching your search.
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>

      {pages > 1 && (
        <div className="flex items-center justify-between mt-4 px-2">
          <span className="text-xs text-slate-500 font-medium">
            Showing {page * PAGE_SIZE + 1} to {Math.min((page + 1) * PAGE_SIZE, sorted.length)} of {sorted.length} entries
          </span>
          <div className="flex items-center gap-2 bg-white/50 p-1 rounded-lg border border-slate-200">
            <button
              onClick={() => setPage(p => Math.max(0, p - 1))}
              disabled={page === 0}
              className="px-3 py-1 rounded-md text-slate-500 hover:text-indigo-600 hover:bg-slate-100 disabled:opacity-30 disabled:hover:bg-transparent disabled:hover:text-slate-500 transition-all text-sm font-bold"
            >
              ←
            </button>
            <span className="text-xs font-semibold text-slate-700 bg-white shadow-sm border border-slate-100 px-2 py-1 rounded">
              {page + 1} / {pages}
            </span>
            <button
              onClick={() => setPage(p => Math.min(pages - 1, p + 1))}
              disabled={page === pages - 1}
              className="px-3 py-1 rounded-md text-slate-500 hover:text-indigo-600 hover:bg-slate-100 disabled:opacity-30 disabled:hover:bg-transparent disabled:hover:text-slate-500 transition-all text-sm font-bold"
            >
              →
            </button>
          </div>
        </div>
      )}
    </div>
  )
}
