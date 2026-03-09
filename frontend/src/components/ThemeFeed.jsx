import { useState, useRef, useCallback, useEffect } from 'react'
import ThemeFeedCard from './ThemeFeedCard'
import MemoryResultCard from './MemoryResultCard'
import { searchMemory } from '../api/client'

const QUICK_FILTERS = ['Fed Rate', 'MAS', 'China', 'Japan', 'Semiconductor']

function ThemeFeed({ themes, selectedTheme, onSelectTheme, onTabChange, onSelectMemoryTheme, selectedMemoryTheme }) {
  const [searchQuery, setSearchQuery] = useState('')
  const [activeTab, setActiveTab] = useState('live')
  const feedRef = useRef(null)

  // Memory search state
  const [memoryQuery, setMemoryQuery] = useState('')
  const [memoryResults, setMemoryResults] = useState([])
  const [memoryLoading, setMemoryLoading] = useState(false)
  const [fromDate, setFromDate] = useState('')
  const [toDate, setToDate] = useState('')
  const debounceRef = useRef(null)
  const abortRef = useRef(null)

  const filteredThemes = themes.filter((t) =>
    t.name.toLowerCase().includes(searchQuery.toLowerCase())
  )

  const handleKeyDown = useCallback(
    (e, index) => {
      if (e.key === 'ArrowDown' || e.key === 'ArrowUp') {
        e.preventDefault()
        const cards = feedRef.current?.querySelectorAll('[role="button"]')
        if (!cards) return
        const nextIndex =
          e.key === 'ArrowDown'
            ? Math.min(index + 1, cards.length - 1)
            : Math.max(index - 1, 0)
        cards[nextIndex]?.focus()
      }
      if (e.key === 'Enter') {
        onSelectTheme(filteredThemes[index])
      }
    },
    [filteredThemes, onSelectTheme]
  )

  const handleTabChange = useCallback((tab) => {
    setActiveTab(tab)
    onTabChange?.(tab)
  }, [onTabChange])

  // Debounced memory search with AbortController to prevent stale responses
  useEffect(() => {
    if (activeTab !== 'memory') return
    if (debounceRef.current) clearTimeout(debounceRef.current)

    debounceRef.current = setTimeout(() => {
      if (memoryQuery.length < 2) {
        setMemoryResults([])
        return
      }

      // Abort previous in-flight request
      if (abortRef.current) abortRef.current.abort()
      const controller = new AbortController()
      abortRef.current = controller

      // Compute end-of-month for `to` filter (F2 fix)
      let toParam = toDate || undefined
      if (toDate) {
        const [y, m] = toDate.split('-').map(Number)
        const endOfMonth = new Date(y, m, 0) // day 0 of next month = last day of this month
        toParam = endOfMonth.toISOString().slice(0, 10)
      }

      // Append -01 to fromDate (type="month" gives YYYY-MM)
      const fromParam = fromDate ? `${fromDate}-01` : undefined

      setMemoryLoading(true)
      searchMemory({ q: memoryQuery, from: fromParam, to: toParam })
        .then((res) => {
          if (controller.signal.aborted) return
          setMemoryResults(res.data?.data || [])
        })
        .catch((err) => {
          if (controller.signal.aborted) return
          setMemoryResults([])
        })
        .finally(() => {
          if (!controller.signal.aborted) setMemoryLoading(false)
        })
    }, 300)

    return () => {
      clearTimeout(debounceRef.current)
      if (abortRef.current) abortRef.current.abort()
    }
  }, [memoryQuery, fromDate, toDate, activeTab])

  const handleChipClick = useCallback((chip) => {
    setMemoryQuery(chip)
  }, [])

  return (
    <nav className="w-[320px] min-w-[320px] h-full flex flex-col bg-[#0f172a] border-r border-slate-700">
      {/* Tabs */}
      <div className="flex border-b border-slate-700">
        <button
          className={`flex-1 py-3 text-sm font-medium transition-colors ${
            activeTab === 'live'
              ? 'text-blue-400 border-b-2 border-blue-400'
              : 'text-slate-400 hover:text-slate-200'
          }`}
          onClick={() => handleTabChange('live')}
        >
          Live Themes
        </button>
        <button
          className={`flex-1 py-3 text-sm font-medium transition-colors ${
            activeTab === 'memory'
              ? 'text-blue-400 border-b-2 border-blue-400'
              : 'text-slate-400 hover:text-slate-200'
          }`}
          onClick={() => handleTabChange('memory')}
        >
          Memory Search
        </button>
      </div>

      {activeTab === 'live' ? (
        <>
          {/* Live search */}
          <div className="p-3">
            <input
              type="search"
              placeholder="Filter themes..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full px-3 py-2 rounded-md bg-[#1e293b] border border-slate-700 text-sm text-slate-200 placeholder-slate-500 focus:outline-none focus:ring-1 focus:ring-blue-500 focus:border-blue-500"
            />
          </div>

          {/* Live feed */}
          <div ref={feedRef} className="flex-1 overflow-y-auto px-3 pb-3 space-y-3">
            {filteredThemes.length > 0 ? (
              filteredThemes.map((theme, i) => (
                <ThemeFeedCard
                  key={theme.slug}
                  theme={theme}
                  isSelected={selectedTheme?.slug === theme.slug}
                  onSelect={onSelectTheme}
                  onKeyDown={(e) => handleKeyDown(e, i)}
                />
              ))
            ) : (
              <p className="text-sm text-slate-500 text-center py-8">
                {searchQuery
                  ? 'No themes match your search.'
                  : 'No themes available.'}
              </p>
            )}
          </div>
        </>
      ) : (
        <>
          {/* Memory search input */}
          <div className="p-3 space-y-3">
            <input
              type="search"
              placeholder="Search institutional memory..."
              value={memoryQuery}
              onChange={(e) => setMemoryQuery(e.target.value)}
              className="w-full px-3 py-2 rounded-md bg-[#1e293b] border border-slate-700 text-sm text-slate-200 placeholder-slate-500 focus:outline-none focus:ring-1 focus:ring-blue-500 focus:border-blue-500"
            />

            {/* Quick filter chips */}
            <div className="flex flex-wrap gap-1.5">
              {QUICK_FILTERS.map((chip) => (
                <button
                  key={chip}
                  onClick={() => handleChipClick(chip)}
                  className={`px-2.5 py-1 rounded-full text-[11px] font-medium transition-colors ${
                    memoryQuery === chip
                      ? 'bg-blue-500/20 text-blue-400 border border-blue-500/30'
                      : 'bg-[#1e293b] text-slate-400 border border-slate-700 hover:text-slate-200 hover:border-slate-500'
                  }`}
                >
                  {chip}
                </button>
              ))}
            </div>

            {/* Date range refinement */}
            <div className="flex gap-2">
              <input
                type="month"
                value={fromDate}
                onChange={(e) => setFromDate(e.target.value)}
                placeholder="From"
                aria-label="From date"
                className="flex-1 px-2 py-1.5 rounded-md bg-[#1e293b] border border-slate-700 text-[11px] text-slate-300 focus:outline-none focus:ring-1 focus:ring-blue-500"
              />
              <input
                type="month"
                value={toDate}
                onChange={(e) => setToDate(e.target.value)}
                placeholder="To"
                aria-label="To date"
                className="flex-1 px-2 py-1.5 rounded-md bg-[#1e293b] border border-slate-700 text-[11px] text-slate-300 focus:outline-none focus:ring-1 focus:ring-blue-500"
              />
            </div>
          </div>

          {/* Memory results */}
          <div className="flex-1 overflow-y-auto px-3 pb-3 space-y-2">
            {memoryLoading ? (
              <p className="text-sm text-slate-500 text-center py-8">
                Searching...
              </p>
            ) : memoryResults.length > 0 ? (
              memoryResults.map((theme, idx) => (
                <MemoryResultCard
                  key={theme.id || theme.slug || idx}
                  theme={theme}
                  isSelected={selectedMemoryTheme?.id === theme.id}
                  onSelect={onSelectMemoryTheme}
                />
              ))
            ) : memoryQuery.length >= 2 ? (
              <div className="text-center py-8">
                <p className="text-sm text-slate-500">
                  No matching historical themes found.
                </p>
                <p className="text-xs text-slate-600 mt-2">
                  Try: Fed Rate, MAS, China, Japan, Semiconductor
                </p>
              </div>
            ) : (
              <p className="text-sm text-slate-500 text-center py-8">
                Type at least 2 characters to search.
              </p>
            )}
          </div>
        </>
      )}
    </nav>
  )
}

export default ThemeFeed
