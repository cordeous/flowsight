import { C } from '../../utils/colors'

export default function Card({ children, style = {} }) {
  return (
    <div style={{
      background: C.surface,
      border: `1px solid ${C.border}`,
      borderRadius: 10,
      padding: '16px 20px',
      ...style,
    }}>
      {children}
    </div>
  )
}
