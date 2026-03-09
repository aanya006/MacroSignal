import TemperatureBadge from './TemperatureBadge'

const BORDER_HEX = {
  hot: '#ef4444',
  warm: '#f59e0b',
  cool: '#06b6d4',
}

function formatRecency(lastUpdated) {
  if (!lastUpdated) return ''
  const diff = Date.now() - new Date(lastUpdated).getTime()
  const minutes = Math.floor(diff / 60000)
  if (minutes < 1) return 'Just now'
  if (minutes < 60) return `${minutes}m ago`
  const hours = Math.floor(minutes / 60)
  if (hours < 24) return `${hours}h ago`
  const days = Math.floor(hours / 24)
  return `${days}d ago`
}

function ThemeFeedCard({ theme, isSelected, onSelect, onKeyDown }) {
  const label = theme.score_label ? theme.score_label.toLowerCase() : 'cool'
  const borderColor = isSelected
    ? BORDER_HEX[label] || '#06b6d4'
    : 'transparent'

  return (
    <article
      role="button"
      tabIndex={0}
      onClick={() => onSelect(theme)}
      onKeyDown={onKeyDown}
      className={`p-3 rounded-lg border-l-2 cursor-pointer transition-all duration-200 hover:shadow-lg hover:shadow-black/20 hover:-translate-y-0.5 focus:outline-none focus:ring-1 focus:ring-slate-500 ${
        isSelected ? 'bg-[#253348]' : 'bg-[#1e293b] hover:bg-[#334155]'
      }`}
      style={{ borderLeftColor: borderColor }}
    >
      <div className="flex items-start justify-between gap-2">
        <h3 className="text-sm font-semibold text-slate-100 leading-tight">
          {theme.name}
        </h3>
        <TemperatureBadge label={theme.score_label} />
      </div>
      <div className="flex items-center gap-3 mt-1.5 text-[11px] text-slate-400">
        <span>{theme.article_count} articles</span>
        {theme.last_updated_at && (
          <>
            <span aria-hidden="true">·</span>
            <span>{formatRecency(theme.last_updated_at)}</span>
          </>
        )}
      </div>
    </article>
  )
}

export default ThemeFeedCard
