import { useParams } from 'react-router-dom'

function ThemeDetailPage() {
  const { slug } = useParams()

  return (
    <main className="min-h-screen bg-[#0f172a] text-slate-200 p-6">
      <h1 className="text-2xl font-bold text-white mb-4">Theme: {slug}</h1>
      <p className="text-slate-400">Theme detail view — coming soon...</p>
    </main>
  )
}

export default ThemeDetailPage
