function formatDateRange(dateRange) {
  if (!dateRange?.earliest) return ''
  const fmt = (d) => {
    const date = new Date(d)
    return date.toLocaleDateString('en-SG', { month: 'short', year: 'numeric' })
  }
  const start = fmt(dateRange.earliest)
  const end = fmt(dateRange.latest)
  return start === end ? start : `${start} — ${end}`
}

function MemoryResultCard({ theme, isSelected, onSelect }) {
  return (
    <article
      role="button"
      tabIndex={0}
      onClick={() => onSelect(theme)}
      onKeyDown={(e) => e.key === 'Enter' && onSelect(theme)}
      className="p-3 rounded-lg bg-[#1e293b] border-l-2 cursor-pointer transition-all duration-200 hover:bg-[#334155] hover:shadow-lg hover:shadow-black/20 hover:-translate-y-0.5 focus:outline-none focus:ring-1 focus:ring-slate-500"
      style={{ borderLeftColor: isSelected ? '#8b5cf6' : 'transparent' }}
    >
      <h3 className="text-sm font-semibold text-slate-100 leading-tight">
        {theme.name}
      </h3>
      {theme.description && (
        <p className="text-xs text-slate-400 mt-1 line-clamp-2 leading-relaxed">
          {theme.description}
        </p>
      )}
      <div className="flex items-center gap-2 mt-1.5 text-[11px] text-slate-500">
        <span>{theme.article_count} articles</span>
        {theme.date_range?.earliest && (
          <>
            <span aria-hidden="true">·</span>
            <span>{formatDateRange(theme.date_range)}</span>
          </>
        )}
      </div>
    </article>
  )
}

export default MemoryResultCard
