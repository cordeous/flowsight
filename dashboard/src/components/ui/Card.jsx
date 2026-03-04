export default function Card({ children, className = '', style = {} }) {
  return (
    <div
      className={`glass-card rounded-2xl p-5 md:p-6 transition-transform duration-300 hover:-translate-y-1 hover:shadow-2xl hover:shadow-indigo-500/10 ${className}`}
      style={style}
    >
      {children}
    </div>
  )
}
