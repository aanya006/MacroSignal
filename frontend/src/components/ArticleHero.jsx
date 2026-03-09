import { useState } from 'react'

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
  const [imgFailed, setImgFailed] = useState(false)
  if (!article) return null

  const showImage = article.image_url && !imgFailed

  return (
    <a
      href={article.url}
      target="_blank"
      rel="noopener noreferrer"
      className="block rounded-lg bg-[#1e293b] overflow-hidden hover:bg-[#253348] transition-colors group"
    >
      {showImage ? (
        <img
          src={article.image_url}
          alt=""
          className="w-full h-[180px] object-cover"
          onError={() => setImgFailed(true)}
        />
      ) : (
        <div className="w-full h-[180px] bg-gradient-to-br from-[#253348] via-[#1a2744] to-[#2d2040] flex items-center justify-center">
          <span className="text-[13px] text-slate-600">Article hero image</span>
        </div>
      )}
      <div className="p-4">
        <h3 className="text-base font-semibold text-slate-100 leading-snug group-hover:text-blue-400 transition-colors">
          {article.title}
        </h3>
        <div className="flex items-center gap-2 mt-1.5 text-xs text-slate-400">
          <span className="font-medium text-slate-300">{article.source_name}</span>
          <span aria-hidden="true">·</span>
          <time dateTime={article.published_at}>{formatDateTime(article.published_at)}</time>
        </div>
        {article.ai_summary && (
          <p className="mt-2 text-[13px] text-slate-400 leading-relaxed">
            {article.ai_summary}
          </p>
        )}
      </div>
    </a>
  )
}

export default ArticleHero
