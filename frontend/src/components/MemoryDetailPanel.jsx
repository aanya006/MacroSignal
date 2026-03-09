import { useState, useEffect } from 'react'
import { fetchThemeDetail, fetchThemeArticles } from '../api/client'
import ThemeBanner from './ThemeBanner'
import RegionsMarketsBox from './RegionsMarketsBox'
import ArticleHero from './ArticleHero'
import ArticleCard from './ArticleCard'
import CausalChain from './CausalChain'

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
        setAllArticles(arts)
      })
      .catch(() => {
        if (cancelled) return
        // Fallback: use search result data directly
        setDetail(theme)
        setAllArticles([])
      })
      .finally(() => {
        if (!cancelled) setLoading(false)
      })

    return () => { cancelled = true }
  }, [theme?.slug])

  if (!theme) {
    return (
      <main className="flex-1 flex items-center justify-center text-slate-500">
        <p>Select a historical theme to view details</p>
      </main>
    )
  }

  const themeData = detail || theme
  const causalChain = themeData.causal_chain || theme.causal_chain
  const heroArticle = allArticles[0] || null
  const remainingArticles = allArticles.slice(1)

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

          {/* Two-column layout: Articles left, Causal Chain right */}
          <div className="flex gap-6 min-h-0">
            {/* Articles column */}
            <div className="flex-1 space-y-4 min-w-0">
              <h3 className="text-sm font-semibold uppercase tracking-wide text-slate-400">
                Articles
              </h3>

              {heroArticle && <ArticleHero article={heroArticle} />}

              {remainingArticles.length > 0 && (
                <div className="space-y-3">
                  {remainingArticles.map((article) => (
                    <ArticleCard key={article.id} article={article} />
                  ))}
                </div>
              )}

              {allArticles.length === 0 && (
                <p className="text-sm text-slate-500">No articles available.</p>
              )}
            </div>

            {/* Causal Chain column — historical mode */}
            <div className="w-[320px] min-w-[320px]">
              <CausalChain chain={causalChain} historical={true} />
            </div>
          </div>
        </>
      )}
    </main>
  )
}

export default MemoryDetailPanel
