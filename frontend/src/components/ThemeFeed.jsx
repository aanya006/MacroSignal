import { useState, useRef, useCallback, useEffect } from 'react'
import ThemeFeedCard from './ThemeFeedCard'
import MemoryResultCard from './MemoryResultCard'
import { searchMemory } from '../api/client'

// Crisis-type categories for precedent filtering (client-side)
const CRISIS_CATEGORIES = [
  { label: 'Currency & FX', keywords: ['currency', 'franc', 'peg', 'fx', 'devaluation', 'lira', 'peso', 'won'] },
  { label: 'Equity Crash', keywords: ['bubble', 'crash', 'dot-com', 'a-share', 'covid', 'equity', 'stock'] },
  { label: 'Policy Shock', keywords: ['taper', 'tantrum', 'cooling', 'property', 'stimulus', 'rate', 'policy'] },
  { label: 'Trade & Geopolitical', keywords: ['trade war', 'tariff', 'ukraine', 'russia', 'oil price war', 'geopolitical', 'sanctions'] },
  { label: 'Debt & Credit', keywords: ['debt', 'credit', 'subprime', 'financial crisis', 'gfc', 'sovereign', 'bailout'] },
]


function ThemeFeed({ themes, selectedTheme, onSelectTheme, activeTab: controlledTab, onTabChange, onSelectMemoryTheme, selectedMemoryTheme, signalsFromDate, signalsToDate, onSignalsFromDateChange, onSignalsToDateChange, allAssetClasses, selectedAssetClasses, onSelectedAssetClassesChange }) {
  const [searchQuery, setSearchQuery] = useState('')
  const [showCold, setShowCold] = useState(false)
  const activeTab = controlledTab || 'live'
  const feedRef = useRef(null)

  // Memory search state
  const [memoryQuery, setMemoryQuery] = useState('')
  const [memoryResults, setMemoryResults] = useState([])
  const [memoryLoading, setMemoryLoading] = useState(false)
  const [fromDate, setFromDate] = useState('')
  const [toDate, setToDate] = useState('')
  const [activeCategories, setActiveCategories] = useState([])
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
    onTabChange?.(tab)
  }, [onTabChange])

  // Fetch historical themes — on tab open (empty query = browse all), then debounced search
  useEffect(() => {
    if (activeTab !== 'memory') return
    if (debounceRef.current) clearTimeout(debounceRef.current)

    // For typed queries under 2 chars (but not empty), wait for more input
    if (memoryQuery.length > 0 && memoryQuery.length < 2) return

    debounceRef.current = setTimeout(() => {
      // Abort previous in-flight request
      if (abortRef.current) abortRef.current.abort()
      const controller = new AbortController()
      abortRef.current = controller

      // Compute end-of-month for `to` filter
      let toParam = toDate || undefined
      if (toDate) {
        const [y, m] = toDate.split('-').map(Number)
        const endOfMonth = new Date(y, m, 0)
        toParam = endOfMonth.toISOString().slice(0, 10)
      }

      const fromParam = fromDate ? `${fromDate}-01` : undefined

      setMemoryLoading(true)
      searchMemory({ q: memoryQuery || undefined, from: fromParam, to: toParam })
        .then((res) => {
          if (controller.signal.aborted) return
          setMemoryResults(res.data?.data || [])
        })
        .catch(() => {
          if (controller.signal.aborted) return
          setMemoryResults([])
        })
        .finally(() => {
          if (!controller.signal.aborted) setMemoryLoading(false)
        })
    }, memoryQuery ? 300 : 0) // Immediate fetch for browse-all, debounced for search

    return () => {
      clearTimeout(debounceRef.current)
      if (abortRef.current) abortRef.current.abort()
    }
  }, [memoryQuery, fromDate, toDate, activeTab])

  const handleCategoryToggle = useCallback((label) => {
    setActiveCategories((prev) =>
      prev.includes(label) ? prev.filter((c) => c !== label) : [...prev, label]
    )
  }, [])

  // Client-side category filtering on loaded results
  const filteredMemoryResults = activeCategories.length === 0
    ? memoryResults
    : memoryResults.filter((theme) => {
        const text = `${theme.name} ${theme.description || ''}`.toLowerCase()
        return activeCategories.some((catLabel) => {
          const cat = CRISIS_CATEGORIES.find((c) => c.label === catLabel)
          return cat?.keywords.some((kw) => text.includes(kw))
        })
      })

  return (
    <nav className="w-[320px] min-w-[320px] h-full flex flex-col bg-[#0f172a] border-r border-slate-700">
      {/* Tabs */}
      <div className="flex border-b border-slate-700">
        <button
          className={`flex-1 py-3 text-xs font-medium transition-colors ${
            activeTab === 'live'
              ? 'text-blue-400 border-b-2 border-blue-400'
              : 'text-slate-400 hover:text-slate-200'
          }`}
          onClick={() => handleTabChange('live')}
        >
          Watch List
        </button>
        <button
          className={`flex-1 py-3 text-xs font-medium transition-colors ${
            activeTab === 'signals'
              ? 'text-blue-400 border-b-2 border-blue-400'
              : 'text-slate-400 hover:text-slate-200'
          }`}
          onClick={() => handleTabChange('signals')}
        >
          Signals
        </button>
        <button
          className={`flex-1 py-3 text-xs font-medium transition-colors ${
            activeTab === 'memory'
              ? 'text-blue-400 border-b-2 border-blue-400'
              : 'text-slate-400 hover:text-slate-200'
          }`}
          onClick={() => handleTabChange('memory')}
        >
          Precedents
        </button>
      </div>

      {activeTab === 'live' ? (
        <>
          {/* Watch List search */}
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
          <div ref={feedRef} className="flex-1 overflow-y-auto p-3 space-y-3">
            {filteredThemes.length > 0 ? (() => {
              const hotWarm = filteredThemes.filter((t) => {
                const l = t.score_label?.toLowerCase()
                return l === 'hot' || l === 'warm'
              })
              const cold = filteredThemes.filter((t) => {
                const l = t.score_label?.toLowerCase()
                return l !== 'hot' && l !== 'warm'
              })
              return (
                <>
                  {hotWarm.map((theme, i) => (
                    <ThemeFeedCard
                      key={theme.slug}
                      theme={theme}
                      isSelected={selectedTheme?.slug === theme.slug}
                      onSelect={onSelectTheme}
                      onKeyDown={(e) => handleKeyDown(e, i)}
                    />
                  ))}
                  {cold.length > 0 && (
                    <>
                      <button
                        onClick={() => setShowCold(!showCold)}
                        className="w-full flex items-center justify-between px-4 py-3 rounded-lg bg-cyan-500/10 border border-cyan-500/25 hover:bg-cyan-500/15 hover:border-cyan-500/40 transition-colors"
                      >
                        <span className="text-xs font-semibold text-cyan-400">
                          {showCold ? 'Hide' : 'Show'} {cold.length} cool theme{cold.length !== 1 ? 's' : ''}
                        </span>
                        <span className={`text-xs text-cyan-400 transition-transform duration-200 ${showCold ? 'rotate-180' : ''}`}>
                          ▼
                        </span>
                      </button>
                      {showCold && cold.map((theme, i) => (
                        <ThemeFeedCard
                          key={theme.slug}
                          theme={theme}
                          isSelected={selectedTheme?.slug === theme.slug}
                          onSelect={onSelectTheme}
                          onKeyDown={(e) => handleKeyDown(e, hotWarm.length + i)}
                        />
                      ))}
                    </>
                  )}
                </>
              )
            })() : (
              <p className="text-sm text-slate-500 text-center py-8">
                {searchQuery
                  ? 'No themes match your search.'
                  : 'No themes available.'}
              </p>
            )}
          </div>
        </>
      ) : activeTab === 'signals' ? (
        <div className="flex-1 flex flex-col">
          {/* Date filter */}
          <div className="p-3 space-y-3 border-b border-slate-700">
            <p className="text-[11px] text-slate-400 font-medium uppercase tracking-wider">Date Range</p>
            <div className="flex gap-2">
              <input
                type="month"
                value={signalsFromDate}
                onChange={(e) => onSignalsFromDateChange(e.target.value)}
                placeholder="From"
                aria-label="From date"
                className="flex-1 px-2 py-1.5 rounded-md bg-[#1e293b] border border-slate-700 text-[11px] text-slate-300 focus:outline-none focus:ring-1 focus:ring-blue-500"
              />
              <input
                type="month"
                value={signalsToDate}
                onChange={(e) => onSignalsToDateChange(e.target.value)}
                placeholder="To"
                aria-label="To date"
                className="flex-1 px-2 py-1.5 rounded-md bg-[#1e293b] border border-slate-700 text-[11px] text-slate-300 focus:outline-none focus:ring-1 focus:ring-blue-500"
              />
            </div>
          </div>

          {/* Asset Class Filter */}
          <div className="p-4 space-y-3">
            <div className="flex items-center justify-between">
              <p className="text-xs text-slate-400 font-medium uppercase tracking-wider">Asset Classes</p>
              <button
                onClick={() => onSelectedAssetClassesChange(
                  selectedAssetClasses.length === allAssetClasses.length ? [] : allAssetClasses
                )}
                className="text-[11px] text-blue-400 hover:text-blue-300 transition-colors"
              >
                {selectedAssetClasses.length === allAssetClasses.length ? 'Clear All' : 'Select All'}
              </button>
            </div>
            <div className="space-y-1.5">
              {allAssetClasses.map((cls) => {
                const isSelected = selectedAssetClasses.includes(cls)
                return (
                  <button
                    key={cls}
                    onClick={() => {
                      onSelectedAssetClassesChange(
                        isSelected
                          ? selectedAssetClasses.filter((c) => c !== cls)
                          : [...selectedAssetClasses, cls]
                      )
                    }}
                    className={`w-full flex items-center gap-2.5 px-3 py-2.5 rounded-lg text-sm transition-colors ${
                      isSelected
                        ? 'bg-blue-500/15 text-blue-300 border border-blue-500/30'
                        : 'bg-[#1e293b] text-slate-500 border border-slate-700 hover:text-slate-300 hover:border-slate-500'
                    }`}
                  >
                    <span className={`w-4 h-4 rounded border flex items-center justify-center shrink-0 ${
                      isSelected ? 'bg-blue-500 border-blue-500' : 'border-slate-600'
                    }`}>
                      {isSelected && (
                        <svg className="w-2.5 h-2.5 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={3}>
                          <path strokeLinecap="round" strokeLinejoin="round" d="M5 13l4 4L19 7" />
                        </svg>
                      )}
                    </span>
                    {cls}
                  </button>
                )
              })}
            </div>
          </div>
        </div>
      ) : (
        <>
          {/* Memory search input */}
          <div className="p-3 space-y-3">
            <input
              type="search"
              placeholder="Search past events..."
              value={memoryQuery}
              onChange={(e) => setMemoryQuery(e.target.value)}
              className="w-full px-3 py-2 rounded-md bg-[#1e293b] border border-slate-700 text-sm text-slate-200 placeholder-slate-500 focus:outline-none focus:ring-1 focus:ring-blue-500 focus:border-blue-500"
            />

            {/* Crisis-type category filters */}
            <div className="flex flex-wrap gap-1.5">
              {CRISIS_CATEGORIES.map(({ label }) => {
                const isActive = activeCategories.includes(label)
                return (
                  <button
                    key={label}
                    onClick={() => handleCategoryToggle(label)}
                    className={`px-2.5 py-1 rounded-full text-[11px] font-medium transition-colors ${
                      isActive
                        ? 'bg-purple-500/20 text-purple-400 border border-purple-500/30'
                        : 'bg-[#1e293b] text-slate-400 border border-slate-700 hover:text-slate-200 hover:border-slate-500'
                    }`}
                  >
                    {label}
                  </button>
                )
              })}
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
          <div className="flex-1 overflow-y-auto p-3 space-y-2">
            {memoryLoading ? (
              <div className="space-y-2">
                {[...Array(5)].map((_, i) => (
                  <div key={i} className="skeleton h-16 w-full rounded-lg" />
                ))}
              </div>
            ) : filteredMemoryResults.length > 0 ? (
              filteredMemoryResults.map((theme, idx) => (
                <MemoryResultCard
                  key={theme.id || theme.slug || idx}
                  theme={theme}
                  isSelected={selectedMemoryTheme?.id === theme.id}
                  onSelect={onSelectMemoryTheme}
                />
              ))
            ) : (
              <div className="text-center py-8">
                <p className="text-sm text-slate-500">
                  {memoryQuery || activeCategories.length > 0
                    ? 'No matching past events found.'
                    : 'No historical events available.'}
                </p>
                {activeCategories.length > 0 && !memoryQuery && (
                  <button
                    onClick={() => setActiveCategories([])}
                    className="text-xs text-purple-400 mt-2 hover:text-purple-300 transition-colors"
                  >
                    Clear filters
                  </button>
                )}
              </div>
            )}
          </div>
        </>
      )}
    </nav>
  )
}

export default ThemeFeed
