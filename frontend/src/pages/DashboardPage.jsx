import { useState, useEffect, useCallback } from 'react'
import { useSearchParams, Link } from 'react-router-dom'
import useThemeStore from '../store/useThemeStore'
import ThemeFeed from '../components/ThemeFeed'
import ThemeDetailPanel from '../components/ThemeDetailPanel'
import MemoryDetailPanel from '../components/MemoryDetailPanel'
import MarketSignalsPanel from '../components/MarketSignalsPanel'

function DashboardPage() {
  const {
    themes,
    selected_theme,
    loading,
    error,
    reference_now,
    load_themes,
    load_status,
    set_selected_theme,
  } = useThemeStore()

  const [searchParams, setSearchParams] = useSearchParams()
  const activeTab = searchParams.get('tab') || 'live'
  const [selectedMemoryTheme, setSelectedMemoryTheme] = useState(null)
  const [signalsFromDate, setSignalsFromDate] = useState('')
  const [signalsToDate, setSignalsToDate] = useState('')
  const ALL_ASSET_CLASSES = ['Equities', 'Bonds', 'FX', 'Commodities', 'Crypto', 'Real Estate']
  const [selectedAssetClasses, setSelectedAssetClasses] = useState(ALL_ASSET_CLASSES)

  useEffect(() => {
    load_themes()
    load_status()
  }, [load_themes, load_status])

  const handleTabChange = useCallback((tab) => {
    setSearchParams((prev) => {
      const next = new URLSearchParams(prev)
      if (tab === 'live') {
        next.delete('tab')
      } else {
        next.set('tab', tab)
      }
      return next
    })
  }, [setSearchParams])

  const handleSelectMemoryTheme = useCallback((theme) => {
    setSelectedMemoryTheme(theme)
  }, [])

  // Called from HistoricalParallel to open a precedent from a live theme view
  const handleOpenPrecedent = useCallback((theme) => {
    setSearchParams((prev) => {
      const next = new URLSearchParams(prev)
      next.set('tab', 'memory')
      return next
    })
    setSelectedMemoryTheme(theme)
  }, [setSearchParams])


  return (
    <div className="h-screen flex flex-col bg-[#0f172a] text-slate-200">
      {/* Header */}
      <header className="h-14 px-6 flex items-center justify-between border-b border-slate-700 shrink-0">
        <Link to="/" className="flex items-center gap-2.5 hover:opacity-80 transition-opacity">
          <img src="/microsignal-icon.svg" alt="MacroSignal" className="h-6 w-auto" />
          <h1 className="text-xl font-bold text-white tracking-tight">
            MacroSignal
          </h1>
        </Link>
        <div className="flex items-center gap-1.5 text-xs text-slate-400">
          <span className="w-1.5 h-1.5 rounded-full bg-green-500 animate-pulse" />
          <span>Last updated {reference_now ? new Date(reference_now).toLocaleDateString('en-GB', { day: 'numeric', month: 'short', year: 'numeric' }) : '--'}</span>
        </div>
      </header>

      {/* Main content */}
      <div className="flex-1 flex min-h-0 min-w-0 overflow-hidden">
        {loading && themes.length === 0 ? (
          <div className="flex-1 flex min-h-0">
            {/* Sidebar skeleton */}
            <div className="w-[320px] min-w-[320px] border-r border-slate-700 p-3 space-y-3">
              <div className="skeleton h-9 w-full rounded-md" />
              {[...Array(6)].map((_, i) => <div key={i} className="skeleton h-20 w-full rounded-lg" />)}
            </div>
            {/* Main panel skeleton */}
            <div className="flex-1 p-6 space-y-4">
              <div className="skeleton h-32 w-full rounded-xl" />
              <div className="skeleton h-8 w-2/3" />
              <div className="skeleton h-48 w-full rounded-lg" />
            </div>
          </div>
        ) : error ? (
          <div className="flex-1 flex items-center justify-center">
            <p className="text-red-400 text-sm">{error}</p>
          </div>
        ) : (
          <>
            <ThemeFeed
              themes={themes}
              selectedTheme={selected_theme}
              onSelectTheme={set_selected_theme}
              activeTab={activeTab}
              onTabChange={handleTabChange}
              onSelectMemoryTheme={handleSelectMemoryTheme}
              selectedMemoryTheme={selectedMemoryTheme}
              signalsFromDate={signalsFromDate}
              signalsToDate={signalsToDate}
              onSignalsFromDateChange={setSignalsFromDate}
              onSignalsToDateChange={setSignalsToDate}
              allAssetClasses={ALL_ASSET_CLASSES}
              selectedAssetClasses={selectedAssetClasses}
              onSelectedAssetClassesChange={setSelectedAssetClasses}
            />
            <div key={activeTab} className="flex-1 flex min-h-0 min-w-0 overflow-hidden animate-fade-in">
              {activeTab === 'signals' ? (
                <MarketSignalsPanel fromDate={signalsFromDate} toDate={signalsToDate} selectedAssetClasses={selectedAssetClasses} />
              ) : activeTab === 'memory' ? (
                <MemoryDetailPanel theme={selectedMemoryTheme} />
              ) : (
                <ThemeDetailPanel theme={selected_theme} onOpenPrecedent={handleOpenPrecedent} />
              )}
            </div>
          </>
        )}
      </div>

    </div>
  )
}

export default DashboardPage
