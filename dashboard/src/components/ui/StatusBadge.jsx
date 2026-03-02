import { ALERT_COLORS, SEVERITY_COLORS, C } from '../../utils/colors'

export default function StatusBadge({ value, type = 'alert' }) {
  const map = type === 'severity' ? SEVERITY_COLORS : ALERT_COLORS
  const color = map[value] ?? C.grey
  return (
    <span style={{
      display: 'inline-block',
      background: `${color}22`,
      color: color,
      border: `1px solid ${color}55`,
      borderRadius: 4,
      padding: '2px 8px',
      fontSize: 11,
      fontWeight: 700,
      letterSpacing: '0.04em',
      whiteSpace: 'nowrap',
    }}>
      {value}
    </span>
  )
}
