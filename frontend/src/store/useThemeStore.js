import { create } from 'zustand'
import { fetchThemes, fetchStatus } from '../api/client'

const useThemeStore = create((set, get) => ({
  themes: [],
  selected_theme: null,
  loading: false,
  error: null,
  last_updated: null,
  reference_now: null,

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

      // No auto-select — let user pick from the watch list
    } catch (err) {
      set({ error: err.message || 'Failed to load themes', loading: false })
    }
  },

  load_status: async () => {
    try {
      const res = await fetchStatus()
      const lastUpdated =
        res.data?.data?.last_ingestion || res.data?.meta?.last_updated || null
      const referenceNow = res.data?.data?.reference_now || null
      if (lastUpdated || referenceNow) {
        set({
          ...(lastUpdated && { last_updated: lastUpdated }),
          ...(referenceNow && { reference_now: new Date(referenceNow).getTime() }),
        })
      }
    } catch {
      // status endpoint failure is non-critical
    }
  },
}))

export default useThemeStore
