import { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import { searchMemory } from '../api/client'

// Stop words to filter out when extracting search keywords
const STOP_WORDS = new Set([
  '&', 'and', 'the', 'of', 'in', 'on', 'for', 'to', 'a', 'an',
  'markets', 'market', 'sector', 'economy', 'economic', 'outlook',
  'global', 'general', 'policy', 'trajectory',
])

function extractKeyword(name) {
  const words = name.split(/\s+/).filter((w) => !STOP_WORDS.has(w.toLowerCase()))
  // Return the first meaningful word
  return words[0] || name.split(/\s+/)[0]
}

function HistoricalParallel({ theme }) {
  const [parallel, setParallel] = useState(null)
  const [loading, setLoading] = useState(false)

  useEffect(() => {
    if (!theme?.name || !theme?.slug) {
      setParallel(null)
      return
    }

    let cancelled = false
    setLoading(true)

    const keyword = extractKeyword(theme.name)
    searchMemory({ q: keyword })
      .then((res) => {
        if (cancelled) return
        const results = res.data?.data || []
        const match = results.find((r) => r.slug !== theme.slug)
        setParallel(match || null)
      })
      .catch(() => {
        if (!cancelled) setParallel(null)
      })
      .finally(() => {
        if (!cancelled) setLoading(false)
      })

    return () => { cancelled = true }
  }, [theme?.name, theme?.slug])

  if (loading || !parallel) return null

  const dateRange = parallel.date_range?.earliest
    ? `${new Date(parallel.date_range.earliest).toLocaleDateString('en-SG', { month: 'short', year: 'numeric' })}`
    : ''

  return (
    <div className="mt-4 pt-4 border-t border-dashed border-slate-700">
      <div className="flex items-center gap-2 mb-3">
        <span className="w-5 h-5 rounded-full bg-purple-500/20 text-purple-400 text-[10px] font-bold flex items-center justify-center">
          H
        </span>
        <span className="text-[11px] font-semibold uppercase tracking-[1.2px] text-purple-400">
          Historical Parallel
        </span>
      </div>

      <Link
        to={`/theme/${parallel.slug}`}
        className="block rounded-lg p-3 border border-purple-500/20 bg-purple-500/5 hover:bg-purple-500/10 transition-colors"
      >
        <div className="flex items-start justify-between gap-2">
          <h4 className="text-sm font-semibold text-purple-300">
            {parallel.name}
          </h4>
          {dateRange && (
            <span className="text-[10px] text-purple-400/70 whitespace-nowrap">
              {dateRange}
            </span>
          )}
        </div>
        <p className="text-xs text-slate-400 mt-1 line-clamp-2">
          {parallel.description}
        </p>
        <div className="flex items-center gap-2 mt-2 text-[10px] text-purple-400/60">
          <span>{parallel.article_count} articles</span>
          <span aria-hidden="true">·</span>
          <span>Peak: {String(parallel.peak_temperature || 'cool').toUpperCase()}</span>
        </div>
      </Link>
    </div>
  )
}

export default HistoricalParallel
