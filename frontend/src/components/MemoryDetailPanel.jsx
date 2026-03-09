import { useState, useEffect } from 'react'
import { fetchThemeDetail, fetchThemeArticles } from '../api/client'
import ThemeBanner from './ThemeBanner'
import CausalChain from './CausalChain'

function formatHistoricalDate(dateStr) {
  if (!dateStr) return ''
  const d = new Date(dateStr)
  return d.toLocaleDateString('en-SG', { day: 'numeric', month: 'short', year: 'numeric' })
}

function TimelineEntry({ article, isLast }) {
  return (
    <div className="flex gap-3">
      {/* Timeline spine */}
      <div className="flex flex-col items-center">
        <div className="w-2 h-2 rounded-full bg-purple-500 mt-1.5 shrink-0" />
        {!isLast && <div className="w-px flex-1 bg-slate-700 mt-1" />}
      </div>
      {/* Content */}
      <div className="pb-5 min-w-0">
        <time className="text-[10px] font-medium text-purple-400/70 uppercase tracking-wider">
          {formatHistoricalDate(article.published_at)}
        </time>
        <h4 className="text-[13px] font-medium text-slate-200 leading-snug mt-0.5">
          {article.title}
        </h4>
        <span className="text-[11px] text-slate-500">{article.source_name}</span>
        {article.ai_summary && (
          <p className="mt-1 text-xs text-slate-400 leading-relaxed">
            {article.ai_summary}
          </p>
        )}
      </div>
    </div>
  )
}

function MemoryDetailPanel({ theme }) {
  const [detail, setDetail] = useState(null)
  const [allArticles, setAllArticles] = useState([])
  const [loading, setLoading] = useState(false)

  useEffect(() => {
    if (!theme?.slug) {
      setDetail(null)
      setAllArticles([])
      return
    }

    let cancelled = false
    setLoading(true)

    Promise.all([
      fetchThemeDetail(theme.slug),
      fetchThemeArticles(theme.slug),
    ])
      .then(([detailRes, articlesRes]) => {
        if (cancelled) return
        const d = detailRes.data?.data || detailRes.data
        const arts = articlesRes.data?.data || articlesRes.data || []
        setDetail(d)
        // Sort chronologically (oldest first) for the historical timeline
        setAllArticles([...arts].sort((a, b) => new Date(a.published_at) - new Date(b.published_at)))
      })
      .catch(() => {
        if (cancelled) return
        setDetail(theme)
        setAllArticles([])
      })
      .finally(() => {
        if (!cancelled) setLoading(false)
      })

    return () => { cancelled = true }
  }, [theme?.slug])

  if (!theme) {
    const greetings = [
      ['Explore the archives', 'Select a past event to see how it unfolded'],
      ['History doesn\'t repeat...', '...but it often rhymes. Pick a precedent to explore'],
      ['What happened before?', 'Browse historical events and their market outcomes'],
      ['Looking for parallels?', 'Select an event to see the causal chain and timeline'],
    ]
    const [title, subtitle] = greetings[Math.floor(Math.random() * greetings.length)]
    return (
      <main className="flex-1 flex items-center justify-center min-w-0">
        <div className="text-center space-y-5">
          {/* Animated signal bars — purple tinted */}
          <svg className="mx-auto w-20 h-20" viewBox="0 0 64 64" fill="none">
            <rect x="6" y="44" width="9" height="14" rx="2.5" fill="#8b5cf6" opacity="0.4">
              <animate attributeName="height" values="14;10;14" dur="1.5s" repeatCount="indefinite" begin="0s" />
              <animate attributeName="y" values="44;48;44" dur="1.5s" repeatCount="indefinite" begin="0s" />
            </rect>
            <rect x="20" y="34" width="9" height="24" rx="2.5" fill="#8b5cf6" opacity="0.6">
              <animate attributeName="height" values="24;18;24" dur="1.5s" repeatCount="indefinite" begin="0.2s" />
              <animate attributeName="y" values="34;40;34" dur="1.5s" repeatCount="indefinite" begin="0.2s" />
            </rect>
            <rect x="34" y="22" width="9" height="36" rx="2.5" fill="#a78bfa" opacity="0.8">
              <animate attributeName="height" values="36;28;36" dur="1.5s" repeatCount="indefinite" begin="0.4s" />
              <animate attributeName="y" values="22;30;22" dur="1.5s" repeatCount="indefinite" begin="0.4s" />
            </rect>
            <rect x="48" y="10" width="9" height="48" rx="2.5" fill="#c4b5fd">
              <animate attributeName="height" values="48;38;48" dur="1.5s" repeatCount="indefinite" begin="0.6s" />
              <animate attributeName="y" values="10;20;10" dur="1.5s" repeatCount="indefinite" begin="0.6s" />
            </rect>
          </svg>
          <div className="space-y-2">
            <p className="text-2xl font-semibold text-slate-200">{title}</p>
            <p className="text-base text-slate-500">{subtitle}</p>
          </div>
        </div>
      </main>
    )
  }

  const themeData = detail || theme
  const causalChain = themeData.causal_chain || theme.causal_chain

  return (
    <main className="flex-1 overflow-y-auto p-6 space-y-6">
      {loading ? (
        <div className="space-y-6 animate-pulse">
          <div className="rounded-lg border border-slate-700 p-5 space-y-3">
            <div className="skeleton h-6 w-3/4" />
            <div className="skeleton h-4 w-full" />
            <div className="skeleton h-4 w-2/3" />
          </div>
          <div className="flex gap-6">
            <div className="flex-1 space-y-3">
              <div className="skeleton h-32 w-full rounded-lg" />
              <div className="skeleton h-24 w-full rounded-lg" />
            </div>
            <div className="w-[380px] space-y-3">
              <div className="skeleton h-16 w-full rounded-lg" />
              <div className="skeleton h-16 w-full rounded-lg" />
              <div className="skeleton h-16 w-full rounded-lg" />
            </div>
          </div>
        </div>
      ) : (
        <>
          {/* Banner */}
          <ThemeBanner theme={themeData} showLink="none" />

          {/* Two-column layout: Causal Chain left (primary), Articles right */}
          <div className="flex gap-6 min-h-0">
            {/* Causal Chain — the main value prop for historical themes */}
            <div className="flex-1 min-w-0">
              <CausalChain chain={causalChain} historical={true} />
            </div>

            {/* How It Unfolded — narrative timeline */}
            <div className="w-[380px] shrink-0 overflow-hidden">
              <h3 className="text-[11px] font-semibold uppercase tracking-[1.2px] text-slate-500 mb-3">
                How It Unfolded
              </h3>

              {allArticles.length > 0 ? (
                <div>
                  {allArticles.map((article, i) => (
                    <TimelineEntry key={article.id} article={article} isLast={i === allArticles.length - 1} />
                  ))}
                </div>
              ) : (
                <p className="text-sm text-slate-500">No timeline available.</p>
              )}
            </div>
          </div>
        </>
      )}
    </main>
  )
}

export default MemoryDetailPanel
