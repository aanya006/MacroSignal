import { useState, useEffect, useCallback } from 'react'
import { fetchThemeDetail, fetchThemeArticles } from '../api/client'
import ThemeBanner from './ThemeBanner'
import RegionsMarketsBox from './RegionsMarketsBox'
import DateTimeline from './DateTimeline'
import ArticleHero from './ArticleHero'
import ArticleCard from './ArticleCard'
import CausalChain from './CausalChain'

function buildArticlesByDate(articles) {
  const map = {}
  for (const a of articles) {
    if (!a.published_at) continue
    const date = a.published_at.slice(0, 10)
    map[date] = (map[date] || 0) + 1
  }
  return map
}

function ThemeDetailPanel({ theme }) {
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
    return (
      <main className="flex-1 flex items-center justify-center text-slate-500">
        <p>Select a theme to view details</p>
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
    <main className="flex-1 overflow-y-auto p-6 space-y-6">
      {loading ? (
        <p className="text-sm text-slate-500">Loading details...</p>
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
          <div className="flex gap-6 min-h-0">
            {/* Articles column */}
            <div className="flex-1 space-y-4 min-w-0">
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
            <div className="w-[320px] min-w-[320px]">
              <CausalChain chain={themeData.causal_chain} />
            </div>
          </div>
        </>
      )}
    </main>
  )
}

export default ThemeDetailPanel
