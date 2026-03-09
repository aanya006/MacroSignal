import { useState, useEffect } from 'react'
import { searchMemory } from '../api/client'

// Stop words to filter out when extracting search keywords
const STOP_WORDS = new Set([
  '&', 'and', 'the', 'of', 'in', 'on', 'for', 'to', 'a', 'an',
  'markets', 'market', 'sector', 'economy', 'economic', 'outlook',
  'global', 'general', 'policy', 'trajectory', 'new', 'risk',
  'dynamics', 'management', 'path', 'shift', 'conditions',
])

// Domain-aware synonyms so themes find relevant historical parallels
const KEYWORD_SYNONYMS = {
  'Energy': 'Oil',
  'Conflict': 'War',
  'Compute': 'Bubble',
  'BOJ': 'Franc',
  'Easing': 'Stimulus',
  'Slowdown': 'Crisis',
  'Fiscal': 'Debt',
  'Shadow': 'Financial',
}

function extractKeywords(name) {
  const words = name.split(/[\s&/]+/).filter((w) => {
    const lower = w.toLowerCase().replace(/[^a-z]/g, '')
    return lower.length > 1 && !STOP_WORDS.has(lower)
  })
  const cleaned = words.slice(0, 4).map((w) => w.replace(/[^a-zA-Z0-9+.-]/g, ''))
  // Add synonyms for better historical matching
  const extra = cleaned.flatMap((w) => KEYWORD_SYNONYMS[w] ? [KEYWORD_SYNONYMS[w]] : [])
  // Deduplicate and return up to 4 keywords
  return [...new Set([...cleaned, ...extra])].slice(0, 4)
}

function HistoricalParallel({ theme, onOpenPrecedent }) {
  const [parallel, setParallel] = useState(null)
  const [loading, setLoading] = useState(false)

  useEffect(() => {
    if (!theme?.name || !theme?.slug) {
      setParallel(null)
      return
    }

    let cancelled = false
    setLoading(true)

    const keywords = extractKeywords(theme.name)
    // Search with each keyword in parallel, pick the best match
    Promise.all(keywords.map((kw) => searchMemory({ q: kw }).catch(() => ({ data: { data: [] } }))))
      .then((responses) => {
        if (cancelled) return
        // Collect all unique matches (exclude self), track which appeared most
        const hits = new Map()
        for (const res of responses) {
          const results = res.data?.data || []
          for (const r of results) {
            if (r.slug === theme.slug) continue
            const prev = hits.get(r.slug)
            if (prev) {
              prev.count += 1
            } else {
              hits.set(r.slug, { ...r, count: 1 })
            }
          }
        }
        // Sort by number of keyword hits (more = better match), then by article_count
        const sorted = [...hits.values()].sort(
          (a, b) => b.count - a.count || (b.article_count || 0) - (a.article_count || 0)
        )
        setParallel(sorted[0] || null)
      })
      .catch(() => {
        if (!cancelled) setParallel(null)
      })
      .finally(() => {
        if (!cancelled) setLoading(false)
      })

    return () => { cancelled = true }
  }, [theme?.name, theme?.slug])

  if (loading) {
    return (
      <div className="mt-4 pt-4 border-t border-dashed border-slate-700 space-y-3">
        <div className="flex items-center gap-2">
          <div className="skeleton w-5 h-5 rounded-full" />
          <div className="skeleton h-3 w-32" />
        </div>
        <div className="skeleton h-24 w-full rounded-lg" />
      </div>
    )
  }

  if (!parallel) return null

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
          Historical Precedent
        </span>
      </div>

      <button
        onClick={() => onOpenPrecedent?.(parallel)}
        className="block w-full text-left rounded-lg p-3 border border-purple-500/20 bg-purple-500/5 hover:bg-purple-500/10 transition-colors cursor-pointer"
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
          <span>View full precedent →</span>
        </div>
      </button>
    </div>
  )
}

export default HistoricalParallel
