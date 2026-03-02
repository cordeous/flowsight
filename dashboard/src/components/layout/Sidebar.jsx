import { NavLink } from 'react-router-dom'
import { C } from '../../utils/colors'

const NAV = [
  { to: '/',           label: 'Executive',   icon: '📊' },
  { to: '/inventory',  label: 'Inventory',   icon: '📦' },
  { to: '/forecast',   label: 'Forecast',    icon: '📈' },
  { to: '/anomalies',  label: 'Anomalies',   icon: '⚠️' },
]

export default function Sidebar() {
  return (
    <aside style={{
      width: 200,
      background: C.surface,
      borderRight: `1px solid ${C.border}`,
      display: 'flex',
      flexDirection: 'column',
      padding: '24px 0',
      position: 'sticky',
      top: 0,
      height: '100vh',
      flexShrink: 0,
    }}>
      <div style={{ padding: '0 20px 28px', borderBottom: `1px solid ${C.border}` }}>
        <div style={{ fontSize: 18, fontWeight: 800, color: C.blue, letterSpacing: '-0.5px' }}>FlowSight</div>
        <div style={{ fontSize: 11, color: C.subtle, marginTop: 2 }}>Supply Chain Analytics</div>
      </div>
      <nav style={{ padding: '16px 8px', flex: 1 }}>
        {NAV.map(({ to, label, icon }) => (
          <NavLink key={to} to={to} end={to === '/'}
            style={({ isActive }) => ({
              display: 'flex',
              alignItems: 'center',
              gap: 10,
              padding: '9px 12px',
              marginBottom: 4,
              borderRadius: 8,
              textDecoration: 'none',
              fontSize: 13,
              fontWeight: isActive ? 600 : 400,
              color: isActive ? C.text : C.subtle,
              background: isActive ? `${C.blue}20` : 'transparent',
              borderLeft: isActive ? `2px solid ${C.blue}` : '2px solid transparent',
            })}>
            <span>{icon}</span>
            {label}
          </NavLink>
        ))}
      </nav>
      <div style={{ padding: '16px 20px', borderTop: `1px solid ${C.border}`, fontSize: 10, color: C.subtle }}>
        python scripts/run_all.py<br />then npm run build
      </div>
    </aside>
  )
}
