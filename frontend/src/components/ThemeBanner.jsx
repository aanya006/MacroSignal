import { Link } from 'react-router-dom'
import TemperatureBadge from './TemperatureBadge'

const ACCENT_HEX = {
  hot: '#ef4444',
  warm: '#f59e0b',
  cool: '#06b6d4',
}

function ThemeBanner({ theme, showLink = true }) {
  const accent = ACCENT_HEX[theme.score_label?.toLowerCase()] || '#06b6d4'

  return (
    <div
      className="rounded-lg p-6"
      style={{ backgroundColor: 'rgba(30, 41, 59, 0.8)', borderBottom: `2px solid ${accent}` }}
    >
      <div className="flex items-start justify-between gap-4">
        <div>
          <h2 className="text-2xl font-bold text-slate-100">{theme.name}</h2>
          {theme.description && (
            <p className="mt-2 text-sm text-slate-400">{theme.description}</p>
          )}
        </div>
        <div className="flex items-center gap-3">
          {showLink && theme.slug && (
            <Link
              to={`/theme/${theme.slug}`}
              className="text-xs text-blue-400 hover:text-blue-300 transition-colors"
            >
              Open full view
            </Link>
          )}
          <TemperatureBadge label={theme.score_label} />
        </div>
      </div>
      <div className="flex gap-6 mt-4 text-sm">
        <div>
          <span className="text-slate-500 text-xs">Articles</span>
          <span className="ml-2 font-semibold text-slate-200">{theme.article_count}</span>
        </div>
        <div>
          <span className="text-slate-500 text-xs">Score</span>
          <span className="ml-2 font-semibold text-slate-200">{theme.score_value?.toFixed(1) ?? '--'}</span>
        </div>
        {theme.date_range && (
          <div>
            <span className="text-slate-500 text-xs">Coverage</span>
            <span className="ml-2 font-semibold text-slate-200">
              {new Date(theme.date_range.earliest).toLocaleDateString('en-SG', { month: 'short', day: 'numeric' })}
              {' - '}
              {new Date(theme.date_range.latest).toLocaleDateString('en-SG', { month: 'short', day: 'numeric' })}
            </span>
          </div>
        )}
      </div>
    </div>
  )
}

export default ThemeBanner
