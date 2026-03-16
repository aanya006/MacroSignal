import { useState, useEffect, useRef } from 'react'
import { fetchMarketSignals } from '../api/client'
import useThemeStore from '../store/useThemeStore'

const SWIMLANES = [
  { key: 'Equities', label: 'Equities', color: 'border-blue-500', badge: 'bg-blue-500/20 text-blue-400' },
  { key: 'Bonds', label: 'Bonds', color: 'border-green-500', badge: 'bg-green-500/20 text-green-400' },
  { key: 'FX', label: 'FX', color: 'border-amber-500', badge: 'bg-amber-500/20 text-amber-400' },
  { key: 'Commodities', label: 'Commodities', color: 'border-orange-500', badge: 'bg-orange-500/20 text-orange-400' },
  { key: 'Crypto', label: 'Crypto', color: 'border-purple-500', badge: 'bg-purple-500/20 text-purple-400' },
  { key: 'Real Estate', label: 'Real Estate', color: 'border-teal-500', badge: 'bg-teal-500/20 text-teal-400' },
]

function formatRelativeTime(dateStr, referenceNow) {
  if (!dateStr) return ''
  const now = referenceNow || Date.now()
  const diff = Math.floor((now - new Date(dateStr).getTime()) / 60000)
  if (diff < 1) return 'just now'
  if (diff < 60) return `${diff}m ago`
  if (diff < 1440) return `${Math.floor(diff / 60)}h ago`
  return `${Math.floor(diff / 1440)}d ago`
}

function MarketSignalsPanel({ fromDate = '', toDate = '', selectedAssetClasses = [] }) {
  const referenceNow = useThemeStore((s) => s.reference_now)
  const [data, setData] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const debounceRef = useRef(null)
  const abortRef = useRef(null)

  useEffect(() => {
    if (debounceRef.current) clearTimeout(debounceRef.current)

    debounceRef.current = setTimeout(() => {
      if (abortRef.current) abortRef.current.abort()
      const controller = new AbortController()
      abortRef.current = controller

      setLoading(true)
      setError(null)

      const params = {}
      if (fromDate) params.from = `${fromDate}-01`
      if (toDate) {
        const [y, m] = toDate.split('-').map(Number)
        const endOfMonth = new Date(y, m, 0)
        params.to = endOfMonth.toISOString().slice(0, 10)
      }

      fetchMarketSignals(params)
        .then((res) => {
          if (controller.signal.aborted) return
          setData(res.data?.data || {})
        })
        .catch((err) => {
          if (controller.signal.aborted) return
          console.error('Market signals fetch error:', err)
          setError('Failed to load market signals.')
          setData({})
        })
        .finally(() => {
          if (!controller.signal.aborted) setLoading(false)
        })
    }, 300)

    return () => {
      clearTimeout(debounceRef.current)
      if (abortRef.current) abortRef.current.abort()
    }
  }, [fromDate, toDate])

  const filteredLanes = SWIMLANES.filter((lane) => selectedAssetClasses.includes(lane.key))

  if (loading) {
    return (
      <div className="flex-1 grid grid-cols-3 gap-3 p-4">
        {[...Array(3)].map((_, col) => (
          <div key={col} className="space-y-3">
            <div className="skeleton h-5 w-24" />
            {[...Array(4)].map((_, row) => (
              <div key={row} className="skeleton h-16 w-full rounded-lg" />
            ))}
          </div>
        ))}
      </div>
    )
  }

  return (
    <div className="flex-1 flex flex-col min-h-0 bg-[#0f172a]">
      {/* Error banner */}
      {error && (
        <div className="px-6 py-2 bg-red-500/10 border-b border-red-500/20 shrink-0">
          <p className="text-xs text-red-400">{error}</p>
        </div>
      )}

      {filteredLanes.length === 0 ? (
        <div className="flex-1 flex items-center justify-center">
          <p className="text-sm text-slate-500">Select at least one asset class to view signals.</p>
        </div>
      ) : (
        <div className="flex-1 grid gap-3 p-4 min-h-0 overflow-hidden" style={{ gridTemplateColumns: `repeat(${filteredLanes.length}, minmax(0, 1fr))` }}>
          {filteredLanes.map((lane) => {
            const articles = data?.[lane.key] || []
            return (
              <div key={lane.key} className="flex flex-col min-h-0">
                {/* Column header */}
                <div className={`flex items-center gap-2 mb-3 pb-2 border-l-4 pl-3 ${lane.color}`}>
                  <span className="text-sm font-medium text-slate-200">{lane.label}</span>
                  <span className={`text-[10px] px-1.5 py-0.5 rounded-full font-medium ${lane.badge}`}>
                    {articles.length}
                  </span>
                </div>

                {/* Scrollable article list */}
                <div className="flex-1 overflow-y-auto space-y-2 pt-1 pr-1">
                  {articles.length > 0 ? (
                    articles.map((article) => (
                      <div
                        key={article.id}
                        title={article.title}
                        onClick={() => window.open(article.url, '_blank', 'noopener,noreferrer')}
                        className="group bg-[#1e293b] rounded-lg p-3 cursor-pointer hover:bg-slate-700/50 transition-all duration-200 hover:shadow-lg hover:shadow-black/20 hover:-translate-y-0.5"
                      >
                        <p className="text-sm text-slate-200 line-clamp-2 leading-snug group-hover:text-blue-400 transition-colors">
                          {article.title}
                          <span className="inline-block ml-1 opacity-0 group-hover:opacity-100 transition-opacity text-blue-400">↗</span>
                        </p>
                        <p className="text-xs text-slate-500 mt-1.5">
                          <span className="font-medium text-slate-400">{article.source_name}</span> · {formatRelativeTime(article.published_at, referenceNow)}
                        </p>
                      </div>
                    ))
                  ) : (
                    <p className="text-xs text-slate-500 text-center py-6">No signals</p>
                  )}
                </div>
              </div>
            )
          })}
        </div>
      )}
    </div>
  )
}

export default MarketSignalsPanel
