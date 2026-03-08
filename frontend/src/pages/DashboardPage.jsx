import { useEffect } from 'react'
import useThemeStore from '../store/useThemeStore'
import ThemeFeed from '../components/ThemeFeed'
import ThemeDetailPanel from '../components/ThemeDetailPanel'
import StatusBar from '../components/StatusBar'

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

  useEffect(() => {
    load_themes()
    load_status()
  }, [load_themes, load_status])

  return (
    <div className="h-screen flex flex-col bg-[#0f172a] text-slate-200">
      {/* Header */}
      <header className="h-14 px-6 flex items-center justify-between border-b border-slate-700 shrink-0">
        <h1 className="text-xl font-bold text-white tracking-tight">
          MacroSignal
        </h1>
        <span className="text-xs text-slate-500">
          Macro Intelligence Dashboard
        </span>
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
            />
            <ThemeDetailPanel theme={selected_theme} />
          </>
        )}
      </div>

      {/* Status bar */}
      <StatusBar lastUpdated={last_updated} />
    </div>
  )
}

export default DashboardPage
