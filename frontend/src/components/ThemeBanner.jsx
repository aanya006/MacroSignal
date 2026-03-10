import { Link, useNavigate } from 'react-router-dom'
import TemperatureBadge from './TemperatureBadge'

const ACCENT_HEX = {
  hot: '#ef4444',
  warm: '#f59e0b',
  cool: '#06b6d4',
}

function ThemeBanner({ theme, showLink = true }) {
  const accent = ACCENT_HEX[theme.score_label?.toLowerCase()] || '#06b6d4'
  const navigate = useNavigate()

  return (
    <div
      className="rounded-lg p-6"
      style={{ backgroundColor: 'rgba(30, 41, 59, 0.8)', borderBottom: `2px solid ${accent}` }}
    >
      <div className="flex items-start justify-between gap-4 min-w-0">
        <div className="min-w-0 flex-1">
          <h2 className="text-2xl font-bold text-slate-100">{theme.name}</h2>
          {theme.description && (
            <p className="mt-2 text-sm text-slate-400">{theme.description}</p>
          )}
        </div>
        <div className="flex items-center gap-3">
          {showLink === 'none' ? null : showLink && theme.slug ? (
            <Link
              to={`/theme/${theme.slug}`}
              className="flex items-center gap-1 text-xs text-slate-400 hover:text-slate-200 border border-slate-700 hover:border-slate-500 rounded-full px-3 py-1 transition-colors"
            >
              Full View <span className="text-[10px]">↗</span>
            </Link>
          ) : (
            <button
              onClick={() => navigate(-1)}
              className="flex items-center gap-1 text-xs text-slate-400 hover:text-slate-200 border border-slate-700 hover:border-slate-500 rounded-full px-3 py-1 transition-colors"
            >
              <span className="text-[10px]">↙</span> Close View
            </button>
          )}
          <TemperatureBadge label={theme.score_label} />
        </div>
      </div>
      <div className="flex gap-6 mt-4 text-sm">
        <div>
          <span className="text-slate-500 text-xs">Articles</span>
          <span className="ml-2 font-semibold text-slate-200">{theme.article_count}</span>
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
