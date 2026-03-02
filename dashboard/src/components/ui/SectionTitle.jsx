import { C } from '../../utils/colors'

export default function SectionTitle({ children }) {
  return (
    <div style={{
      fontSize: 11, fontWeight: 600, letterSpacing: '0.08em',
      textTransform: 'uppercase', color: C.subtle,
      margin: '20px 0 10px',
    }}>
      {children}
    </div>
  )
}
