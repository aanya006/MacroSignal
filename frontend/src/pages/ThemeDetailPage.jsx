import { useEffect, useState, useCallback } from 'react'
import { useParams, Link } from 'react-router-dom'
import { fetchThemeDetail, fetchThemeArticles } from '../api/client'
import ThemeBanner from '../components/ThemeBanner'
import RegionsMarketsBox from '../components/RegionsMarketsBox'
import DateTimeline from '../components/DateTimeline'
import ArticleHero from '../components/ArticleHero'
import ArticleCard from '../components/ArticleCard'
import StatusBar from '../components/StatusBar'
import CausalChain from '../components/CausalChain'

function buildArticlesByDate(articles) {
  const map = {}
  for (const a of articles) {
    if (!a.published_at) continue
    const date = a.published_at.slice(0, 10)
    map[date] = (map[date] || 0) + 1
  }
  return map
}

function ThemeDetailPage() {
  const { slug } = useParams()
  const [theme, setTheme] = useState(null)
  const [allArticles, setAllArticles] = useState([])
  const [selectedDate, setSelectedDate] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  useEffect(() => {
    let cancelled = false
    setLoading(true)
    setError(null)

    Promise.all([
      fetchThemeDetail(slug),
      fetchThemeArticles(slug),
    ])
      .then(([detailRes, articlesRes]) => {
        if (cancelled) return
        const d = detailRes.data?.data || detailRes.data
        const arts = articlesRes.data?.data || articlesRes.data || []
        setTheme(d)
        setAllArticles(arts)
        if (d?.article_dates?.length > 0) {
          setSelectedDate(d.article_dates[0])
        } else {
          setSelectedDate(null)
        }
      })
      .catch((err) => {
        if (cancelled) return
        setError(err.message || 'Failed to load theme')
      })
      .finally(() => {
        if (!cancelled) setLoading(false)
      })

    return () => { cancelled = true }
  }, [slug])

  const handleDateSelect = useCallback((date) => {
    setSelectedDate(date)
  }, [])

  const articlesByDate = buildArticlesByDate(allArticles)
  const filteredArticles = selectedDate
    ? allArticles.filter((a) => a.published_at?.startsWith(selectedDate))
    : allArticles

  const heroArticle = filteredArticles[0] || null
  const remainingArticles = filteredArticles.slice(1)

  return (
    <div className="h-screen flex flex-col bg-[#0f172a] text-slate-200">
      {/* Header */}
      <header className="h-14 px-6 flex items-center justify-between border-b border-slate-700 shrink-0">
        <Link to="/" className="text-xl font-bold text-white tracking-tight hover:text-blue-400 transition-colors">
          MacroSignal
        </Link>
        <span className="text-xs text-slate-500">Theme Detail</span>
      </header>

      {/* Content */}
      <main className="flex-1 overflow-y-auto p-6 space-y-6">
        {loading ? (
          <p className="text-sm text-slate-500">Loading theme...</p>
        ) : error ? (
          <p className="text-sm text-red-400">{error}</p>
        ) : theme ? (
          <>
            <ThemeBanner theme={theme} showLink={false} />

            <RegionsMarketsBox
              regionTags={theme.region_tags}
              assetTags={theme.asset_tags}
            />

            <DateTimeline
              articleDates={theme.article_dates}
              selectedDate={selectedDate}
              onSelectDate={handleDateSelect}
              articlesByDate={articlesByDate}
            />

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
                <CausalChain chain={theme.causal_chain} />
              </div>
            </div>
          </>
        ) : null}
      </main>

      <StatusBar lastUpdated={theme?.last_updated_at} />
    </div>
  )
}

export default ThemeDetailPage
