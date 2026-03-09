function formatDateTime(dateStr) {
  if (!dateStr) return ''
  const date = new Date(dateStr)
  const now = new Date()
  const isToday = date.toDateString() === now.toDateString()

  if (isToday) {
    const diffMs = now - date
    const diffMins = Math.floor(diffMs / 60000)
    if (diffMins < 1) return 'Just now'
    if (diffMins < 60) return `${diffMins}m ago`
    const diffHours = Math.floor(diffMins / 60)
    return `${diffHours}h ago`
  }

  const datePart = date.toLocaleDateString('en-SG', {
    day: 'numeric',
    month: 'short',
    year: 'numeric',
  })
  const timePart = date.toLocaleTimeString('en-SG', {
    hour: '2-digit',
    minute: '2-digit',
    hour12: false,
  })
  return `${datePart}, ${timePart}`
}

function ArticleHero({ article }) {
  if (!article) return null

  return (
    <a
      href={article.url}
      target="_blank"
      rel="noopener noreferrer"
      className="block rounded-lg bg-[#1e293b] overflow-hidden hover:bg-[#334155] transition-colors group"
    >
      <div className="p-5">
        <h3 className="text-lg font-semibold text-slate-100 leading-snug group-hover:text-blue-400 transition-colors">
          {article.title}
        </h3>
        {article.ai_summary && (
          <p className="mt-2 text-sm text-slate-300 leading-relaxed">
            {article.ai_summary}
          </p>
        )}
        <div className="flex items-center gap-2 mt-3 text-xs text-slate-400">
          <span className="font-medium text-slate-300">{article.source_name}</span>
          <span aria-hidden="true">·</span>
          <time dateTime={article.published_at}>{formatDateTime(article.published_at)}</time>
        </div>
      </div>
    </a>
  )
}

export default ArticleHero
