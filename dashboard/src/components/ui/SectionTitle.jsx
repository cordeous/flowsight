export default function SectionTitle({ children }) {
  return (
    <h2 className="text-xs font-bold tracking-[0.15em] uppercase text-slate-500 mt-8 mb-4 border-b border-slate-200 pb-2 inline-flex items-center gap-2 group-hover:text-indigo-600 transition-colors">
      <span className="w-2 h-2 rounded-full bg-indigo-500 shadow-[0_0_10px_rgba(99,102,241,0.5)]"></span>
      {children}
    </h2>
  )
}
