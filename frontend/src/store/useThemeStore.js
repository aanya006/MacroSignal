import { create } from 'zustand'
import { fetchThemes, fetchStatus } from '../api/client'

const useThemeStore = create((set, get) => ({
  themes: [],
  selected_theme: null,
  loading: false,
  error: null,
  last_updated: null,

  set_themes: (themes) => set({ themes }),
  set_selected_theme: (theme) => set({ selected_theme: theme }),
  set_loading: (loading) => set({ loading }),
  set_error: (error) => set({ error }),

  load_themes: async () => {
    set({ loading: true, error: null })
    try {
      const res = await fetchThemes()
      const themes = res.data?.data || res.data || []
      const lastUpdated = res.data?.meta?.last_updated || null
      set({ themes, last_updated: lastUpdated, loading: false })

      // Auto-select hottest theme if none selected
      if (!get().selected_theme && themes.length > 0) {
        set({ selected_theme: themes[0] })
      }
    } catch (err) {
      set({ error: err.message || 'Failed to load themes', loading: false })
    }
  },

  load_status: async () => {
    try {
      const res = await fetchStatus()
      const lastUpdated =
        res.data?.data?.last_ingestion || res.data?.meta?.last_updated || null
      if (lastUpdated) {
        set({ last_updated: lastUpdated })
      }
    } catch {
      // status endpoint failure is non-critical
    }
  },
}))

export default useThemeStore
