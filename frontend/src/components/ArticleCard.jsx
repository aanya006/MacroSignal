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

function getSourceAbbrev(sourceName) {
  if (!sourceName) return '?'
  const abbrevMap = {
    'Reuters': 'R',
    'Bloomberg': 'BBG',
    'Channel News Asia': 'CNA',
    'CNA': 'CNA',
    'Business Times': 'BT',
    'Straits Times': 'ST',
    'Financial Times': 'FT',
    'Wall Street Journal': 'WSJ',
    'South China Morning Post': 'SCMP',
    'Nikkei Asia': 'NK',
    'Google News': 'GN',
  }
  return abbrevMap[sourceName] || sourceName.split(' ').map(w => w[0]).join('').toUpperCase().slice(0, 3)
}

function ArticleCard({ article }) {
  const abbrev = getSourceAbbrev(article.source_name)
  const [imgFailed, setImgFailed] = useState(false)
  const showImage = article.image_url && !imgFailed

  return (
    <a
      href={article.url}
      target="_blank"
      rel="noopener noreferrer"
      className="flex gap-3 p-3 rounded-lg bg-[#1e293b] hover:bg-[#253348] transition-colors group"
    >
      {showImage ? (
        <img
          src={article.image_url}
          alt=""
          className="w-16 h-12 rounded-md object-cover flex-shrink-0"
          onError={() => setImgFailed(true)}
        />
      ) : (
        <div className="w-16 h-12 rounded-md bg-[#334155] flex-shrink-0 flex items-center justify-center text-xs font-semibold text-slate-500">
          {abbrev}
        </div>
      )}
      <div className="flex-1 min-w-0">
        <h4 className="text-[13px] font-medium text-slate-200 leading-snug group-hover:text-blue-400 transition-colors line-clamp-2">
          {article.title}
        </h4>
        <div className="flex items-center gap-2 mt-1 text-[11px] text-slate-500">
          <span>{article.source_name}</span>
          <span aria-hidden="true">·</span>
          <time dateTime={article.published_at}>{formatDateTime(article.published_at)}</time>
        </div>
        {article.ai_summary && (
          <p className="mt-1 text-xs text-slate-400 leading-relaxed line-clamp-2">
            {article.ai_summary}
          </p>
        )}
      </div>
    </a>
  )
}

export default ArticleCard
