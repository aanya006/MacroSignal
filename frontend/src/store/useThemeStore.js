import { create } from 'zustand'

const useThemeStore = create((set) => ({
  themes: [],
  selected_theme: null,
  loading: false,
  error: null,

  set_themes: (themes) => set({ themes }),
  set_selected_theme: (theme) => set({ selected_theme: theme }),
  set_loading: (loading) => set({ loading }),
  set_error: (error) => set({ error }),
}))

export default useThemeStore
