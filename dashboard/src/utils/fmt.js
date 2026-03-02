export const fmtCurrency = (v, compact = true) => {
  if (v == null) return '—'
  if (compact && v >= 1e6) return `$${(v / 1e6).toFixed(1)}M`
  if (compact && v >= 1e3) return `$${(v / 1e3).toFixed(0)}K`
  return `$${Number(v).toLocaleString('en-US', { maximumFractionDigits: 0 })}`
}

export const fmtNum = (v, decimals = 0) => {
  if (v == null) return '—'
  if (Math.abs(v) >= 1e6) return `${(v / 1e6).toFixed(1)}M`
  if (Math.abs(v) >= 1e3) return `${(v / 1e3).toFixed(0)}K`
  return Number(v).toFixed(decimals)
}

export const fmtPct = (v, decimals = 1) =>
  v == null ? '—' : `${Number(v).toFixed(decimals)}%`

export const fmtDate = (s) => {
  if (!s) return '—'
  const d = new Date(s)
  return d.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' })
}
