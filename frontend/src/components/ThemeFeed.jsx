import { useState, useRef, useCallback } from 'react'
import ThemeFeedCard from './ThemeFeedCard'

function ThemeFeed({ themes, selectedTheme, onSelectTheme }) {
  const [searchQuery, setSearchQuery] = useState('')
  const [activeTab, setActiveTab] = useState('live')
  const feedRef = useRef(null)

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
          onClick={() => setActiveTab('live')}
        >
          Live Themes
        </button>
        <button
          className={`flex-1 py-3 text-sm font-medium transition-colors ${
            activeTab === 'memory'
              ? 'text-blue-400 border-b-2 border-blue-400'
              : 'text-slate-400 hover:text-slate-200'
          }`}
          onClick={() => setActiveTab('memory')}
        >
          Memory Search
        </button>
      </div>

      {/* Search */}
      <div className="p-3">
        <input
          type="search"
          placeholder={
            activeTab === 'live'
              ? 'Filter themes...'
              : 'Search institutional memory...'
          }
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          className="w-full px-3 py-2 rounded-md bg-[#1e293b] border border-slate-700 text-sm text-slate-200 placeholder-slate-500 focus:outline-none focus:ring-1 focus:ring-blue-500 focus:border-blue-500"
        />
      </div>

      {/* Feed list */}
      <div ref={feedRef} className="flex-1 overflow-y-auto px-3 pb-3 space-y-3">
        {activeTab === 'live' ? (
          filteredThemes.length > 0 ? (
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
          )
        ) : (
          <p className="text-sm text-slate-500 text-center py-8">
            Memory search coming soon.
          </p>
        )}
      </div>
    </nav>
  )
}

export default ThemeFeed
