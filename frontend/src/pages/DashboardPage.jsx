import { useState, useEffect, useCallback } from 'react'
import useThemeStore from '../store/useThemeStore'
import ThemeFeed from '../components/ThemeFeed'
import ThemeDetailPanel from '../components/ThemeDetailPanel'
import MemoryDetailPanel from '../components/MemoryDetailPanel'
function formatTimeAgo(dateStr) {
  const diff = Math.floor((Date.now() - new Date(dateStr).getTime()) / 60000)
  if (diff < 1) return 'just now'
  if (diff < 60) return `${diff} min ago`
  const hrs = Math.floor(diff / 60)
  return `${hrs}h ago`
}

function DashboardPage() {
  const {
    themes,
    selected_theme,
    loading,
    error,
    last_updated,
    load_themes,
    load_status,
    set_selected_theme,
  } = useThemeStore()

  const [activeTab, setActiveTab] = useState('live')
  const [selectedMemoryTheme, setSelectedMemoryTheme] = useState(null)

  useEffect(() => {
    load_themes()
    load_status()
  }, [load_themes, load_status])

  const handleTabChange = useCallback((tab) => {
    setActiveTab(tab)
  }, [])

  const handleSelectMemoryTheme = useCallback((theme) => {
    setSelectedMemoryTheme(theme)
  }, [])

  return (
    <div className="h-screen flex flex-col bg-[#0f172a] text-slate-200">
      {/* Header */}
      <header className="h-14 px-6 flex items-center justify-between border-b border-slate-700 shrink-0">
        <h1 className="text-xl font-bold text-white tracking-tight">
          MacroSignal
        </h1>
        <div className="flex items-center gap-1.5 text-xs text-green-500">
          <span className="w-1.5 h-1.5 rounded-full bg-green-500 animate-pulse" />
          Live · Updated {last_updated ? formatTimeAgo(last_updated) : '--'}
        </div>
      </header>

      {/* Main content */}
      <div className="flex-1 flex min-h-0">
        {loading && themes.length === 0 ? (
          <div className="flex-1 flex items-center justify-center">
            <p className="text-slate-500 text-sm">Loading themes...</p>
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
              onTabChange={handleTabChange}
              onSelectMemoryTheme={handleSelectMemoryTheme}
              selectedMemoryTheme={selectedMemoryTheme}
            />
            {activeTab === 'memory' ? (
              <MemoryDetailPanel theme={selectedMemoryTheme} />
            ) : (
              <ThemeDetailPanel theme={selected_theme} />
            )}
          </>
        )}
      </div>

    </div>
  )
}

export default DashboardPage
