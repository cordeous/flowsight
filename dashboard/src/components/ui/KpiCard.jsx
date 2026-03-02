import { C } from '../../utils/colors'

export default function KpiCard({ label, value, sub, accent = C.blue, icon }) {
  return (
    <div style={{
      background: C.surface,
      border: `1px solid ${C.border}`,
      borderTop: `3px solid ${accent}`,
      borderRadius: 10,
      padding: '16px 20px',
      flex: 1,
      minWidth: 160,
    }}>
      <div style={{ color: C.subtle, fontSize: 11, fontWeight: 600, letterSpacing: '0.07em', textTransform: 'uppercase', marginBottom: 8 }}>
        {icon && <span style={{ marginRight: 6 }}>{icon}</span>}{label}
      </div>
      <div style={{ fontSize: 28, fontWeight: 700, color: C.text, lineHeight: 1.1 }}>{value}</div>
      {sub && <div style={{ color: C.subtle, fontSize: 12, marginTop: 4 }}>{sub}</div>}
    </div>
  )
}
