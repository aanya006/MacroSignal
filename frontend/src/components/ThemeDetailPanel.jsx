import { useState, useEffect, useCallback } from 'react'
import { fetchThemeDetail, fetchThemeArticles } from '../api/client'
import ThemeBanner from './ThemeBanner'
import RegionsMarketsBox from './RegionsMarketsBox'
import DateTimeline from './DateTimeline'
import ArticleHero from './ArticleHero'
import ArticleCard from './ArticleCard'
import CausalChain from './CausalChain'
import HistoricalParallel from './HistoricalParallel'

function buildArticlesByDate(articles) {
  const map = {}
  for (const a of articles) {
    if (!a.published_at) continue
    const date = a.published_at.slice(0, 10)
    map[date] = (map[date] || 0) + 1
  }
  return map
}

function ThemeDetailPanel({ theme, onOpenPrecedent }) {
  const [detail, setDetail] = useState(null)
  const [allArticles, setAllArticles] = useState([])
  const [selectedDate, setSelectedDate] = useState(null)
  const [loading, setLoading] = useState(false)

  useEffect(() => {
    if (!theme?.slug) {
      setDetail(null)
      setAllArticles([])
      setSelectedDate(null)
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
        setAllArticles(arts)
        // Default to most recent date
        if (d?.article_dates?.length > 0) {
          setSelectedDate(d.article_dates[0])
        } else {
          setSelectedDate(null)
        }
      })
      .catch(() => {
        if (cancelled) return
        setDetail(theme)
        setAllArticles([])
        setSelectedDate(null)
      })
      .finally(() => {
        if (!cancelled) setLoading(false)
      })

    return () => { cancelled = true }
  }, [theme?.slug])

  const handleDateSelect = useCallback((date) => {
    setSelectedDate(date)
  }, [])

  if (!theme) {
    const greetings = [
      ['Hey there!', 'Pick a theme to see what\'s moving the markets'],
      ['Welcome back!', 'Let\'s see what\'s shaping the macro landscape'],
      ['What\'s on your radar?', 'Select a theme from the watch list to dive in'],
      ['Ready to explore?', 'Choose a theme and unpack the signals'],
      ['Let\'s get started!', 'Tap a theme to see the full picture'],
      ['Checking in?', 'Pick a theme to catch up on the latest'],
    ]
    const [title, subtitle] = greetings[Math.floor(Math.random() * greetings.length)]
    return (
      <main className="flex-1 flex items-center justify-center min-w-0">
        <div className="text-center space-y-5">
          {/* Pulsing compass/crosshair */}
          <svg className="mx-auto w-20 h-20" viewBox="0 0 64 64" fill="none">
            {/* Outer ring pulse */}
            <circle cx="32" cy="32" r="28" stroke="#6366f1" strokeWidth="1.5" opacity="0.2">
              <animate attributeName="r" values="28;30;28" dur="2s" repeatCount="indefinite" />
              <animate attributeName="opacity" values="0.2;0.1;0.2" dur="2s" repeatCount="indefinite" />
            </circle>
            {/* Inner ring */}
            <circle cx="32" cy="32" r="18" stroke="#818cf8" strokeWidth="1.5" opacity="0.4" />
            {/* Crosshair lines */}
            <line x1="32" y1="8" x2="32" y2="20" stroke="#818cf8" strokeWidth="1.5" strokeLinecap="round" opacity="0.5" />
            <line x1="32" y1="44" x2="32" y2="56" stroke="#818cf8" strokeWidth="1.5" strokeLinecap="round" opacity="0.5" />
            <line x1="8" y1="32" x2="20" y2="32" stroke="#818cf8" strokeWidth="1.5" strokeLinecap="round" opacity="0.5" />
            <line x1="44" y1="32" x2="56" y2="32" stroke="#818cf8" strokeWidth="1.5" strokeLinecap="round" opacity="0.5" />
            {/* Center dot */}
            <circle cx="32" cy="32" r="4" fill="#a78bfa">
              <animate attributeName="r" values="4;5;4" dur="2s" repeatCount="indefinite" />
            </circle>
          </svg>
          <div className="space-y-2">
            <p className="text-2xl font-semibold text-slate-200">{title}</p>
            <p className="text-base text-slate-500">{subtitle}</p>
          </div>

          {/* Temperature legend */}
          <p className="text-xs text-slate-500">Themes are ranked by momentum, not just volume.</p>
          <div className="flex items-center justify-center gap-4">
            <span className="flex items-center gap-1.5 text-xs text-slate-400">
              <span className="inline-block w-2 h-2 rounded-full bg-red-500" />
              Hot — breaking now
            </span>
            <span className="flex items-center gap-1.5 text-xs text-slate-400">
              <span className="inline-block w-2 h-2 rounded-full bg-amber-400" />
              Warm — developing
            </span>
            <span className="flex items-center gap-1.5 text-xs text-slate-400">
              <span className="inline-block w-2 h-2 rounded-full bg-slate-500" />
              Cool — quiet
            </span>
          </div>
        </div>
      </main>
    )
  }

  const themeData = detail || theme
  const articlesByDate = buildArticlesByDate(allArticles)

  // Filter articles by selected date (client-side)
  const filteredArticles = selectedDate
    ? allArticles.filter((a) => a.published_at?.startsWith(selectedDate))
    : allArticles

  const heroArticle = filteredArticles[0] || null
  const remainingArticles = filteredArticles.slice(1)

  return (
    <main className="flex-1 overflow-y-auto overflow-x-hidden p-6 space-y-6 min-w-0">
      {loading ? (
        <div className="space-y-6 animate-pulse">
          {/* Banner skeleton */}
          <div className="rounded-xl overflow-hidden border border-slate-700 p-5 space-y-3">
            <div className="skeleton h-6 w-3/4" />
            <div className="skeleton h-4 w-full" />
            <div className="skeleton h-4 w-2/3" />
            <div className="flex gap-2 mt-2">
              <div className="skeleton h-5 w-16 rounded-full" />
              <div className="skeleton h-5 w-20 rounded-full" />
              <div className="skeleton h-5 w-14 rounded-full" />
            </div>
          </div>
          {/* Timeline skeleton */}
          <div className="flex gap-2">
            {[...Array(8)].map((_, i) => <div key={i} className="skeleton h-8 w-14 rounded-full" />)}
          </div>
          {/* Articles skeleton */}
          <div className="flex gap-6">
            <div className="flex-1 space-y-3">
              <div className="skeleton h-48 w-full rounded-lg" />
              <div className="skeleton h-20 w-full rounded-lg" />
              <div className="skeleton h-20 w-full rounded-lg" />
            </div>
            <div className="w-[320px] space-y-3">
              <div className="skeleton h-32 w-full rounded-lg" />
              <div className="skeleton h-24 w-full rounded-lg" />
            </div>
          </div>
        </div>
      ) : (
        <>
          {/* Banner */}
          <ThemeBanner theme={themeData} />

          {/* Region & Asset Tags */}
          <RegionsMarketsBox
            regionTags={themeData.region_tags}
            assetTags={themeData.asset_tags}
          />

          {/* Date Timeline */}
          <DateTimeline
            articleDates={themeData.article_dates}
            selectedDate={selectedDate}
            onSelectDate={handleDateSelect}
            articlesByDate={articlesByDate}
          />

          {/* Two-column layout: Articles left, Causal Chain right */}
          <div className="flex gap-6 min-h-0 min-w-0">
            {/* Articles column */}
            <div className="flex-1 space-y-4 min-w-0 overflow-hidden">
              <h3 className="text-sm font-semibold uppercase tracking-wide text-slate-400">
                Articles
                {selectedDate && (
                  <span className="ml-2 font-normal normal-case tracking-normal text-slate-500">
                    — {new Date(selectedDate + 'T00:00:00').toLocaleDateString('en-SG', { day: 'numeric', month: 'short', year: 'numeric' })}
                  </span>
                )}
              </h3>

              {heroArticle && <ArticleHero article={heroArticle} />}

              {remainingArticles.length > 0 && (
                <div className="space-y-3">
                  {remainingArticles.map((article) => (
                    <ArticleCard key={article.id} article={article} />
                  ))}
                </div>
              )}

              {filteredArticles.length === 0 && (
                <p className="text-sm text-slate-500">No articles found for this date.</p>
              )}
            </div>

            {/* Causal Chain column */}
            <div className="w-[320px] shrink-0 overflow-hidden">
              <CausalChain chain={themeData.causal_chain} />
              <HistoricalParallel theme={themeData} onOpenPrecedent={onOpenPrecedent} />
            </div>
          </div>
        </>
      )}
    </main>
  )
}

export default ThemeDetailPanel
