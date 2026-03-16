import { useState } from 'react'
import useThemeStore from '../store/useThemeStore'

function formatDateTime(dateStr, referenceNow) {
  if (!dateStr) return ''
  const now = referenceNow || Date.now()
  const date = new Date(dateStr)
  const refDate = new Date(now)
  const isToday = date.toDateString() === refDate.toDateString()

  if (isToday) {
    const diffMs = now - date.getTime()
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

// Map known source names to their domain for logo lookup
const SOURCE_DOMAINS = {
  'Reuters': 'reuters.com',
  'Bloomberg': 'bloomberg.com',
  'Channel News Asia': 'channelnewsasia.com',
  'CNA': 'channelnewsasia.com',
  'The Business Times': 'businesstimes.com.sg',
  'Business Times': 'businesstimes.com.sg',
  'The Straits Times': 'straitstimes.com',
  'Straits Times': 'straitstimes.com',
  'Financial Times': 'ft.com',
  'Wall Street Journal': 'wsj.com',
  'South China Morning Post': 'scmp.com',
  'Nikkei Asia': 'asia.nikkei.com',
  'CNBC': 'cnbc.com',
  'BBC': 'bbc.com',
  'The Guardian': 'theguardian.com',
  'Forbes': 'forbes.com',
  'Fortune': 'fortune.com',
  'Yahoo Finance': 'finance.yahoo.com',
  'MAS': 'mas.gov.sg',
  'mas.gov.sg': 'mas.gov.sg',
  'European Central Bank': 'ecb.europa.eu',
}

function getSourceLogoUrl(sourceName, articleUrl) {
  // 1. Try known source domain map
  const knownDomain = SOURCE_DOMAINS[sourceName]
  if (knownDomain) return `https://logo.clearbit.com/${knownDomain}`

  // 2. Extract domain from article URL (works for direct URLs, not Google News)
  try {
    const u = new URL(articleUrl)
    if (!u.hostname.includes('google.com') && !u.hostname.includes('historical-seed')) {
      return `https://logo.clearbit.com/${u.hostname.replace(/^www\./, '')}`
    }
  } catch (_) {}

  return null
}

function ArticleCard({ article }) {
  const referenceNow = useThemeStore((s) => s.reference_now)
  const [imgFailed, setImgFailed] = useState(false)
  const [logoFailed, setLogoFailed] = useState(false)

  const articleImgSrc = article.image_url && !imgFailed ? article.image_url : null
  const logoSrc = !articleImgSrc && !logoFailed ? getSourceLogoUrl(article.source_name, article.url) : null

  return (
    <a
      href={article.url}
      target="_blank"
      rel="noopener noreferrer"
      className="flex gap-3 p-3 rounded-lg bg-[#1e293b] hover:bg-[#253348] transition-all duration-200 hover:shadow-lg hover:shadow-black/20 hover:-translate-y-0.5 group"
    >
      {articleImgSrc ? (
        <img
          src={articleImgSrc}
          alt=""
          className="w-16 h-12 rounded-md object-cover flex-shrink-0"
          onError={() => setImgFailed(true)}
        />
      ) : logoSrc ? (
        <div className="w-16 h-12 rounded-md bg-[#0f172a] flex-shrink-0 flex items-center justify-center p-2">
          <img
            src={logoSrc}
            alt={article.source_name}
            className="max-w-full max-h-full object-contain"
            onError={() => setLogoFailed(true)}
          />
        </div>
      ) : (
        <div className="w-16 h-12 rounded-md bg-[#334155] flex-shrink-0 flex items-center justify-center text-xs font-semibold text-slate-500">
          {article.source_name?.split(' ').map(w => w[0]).join('').toUpperCase().slice(0, 3) || '?'}
        </div>
      )}
      <div className="flex-1 min-w-0">
        <h4 className="text-[13px] font-medium text-slate-200 leading-snug group-hover:text-blue-400 transition-colors line-clamp-2">
          {article.title}
          <span className="inline-block ml-1 opacity-0 group-hover:opacity-100 transition-opacity text-blue-400">↗</span>
        </h4>
        <div className="flex items-center gap-2 mt-1 text-[11px] text-slate-500">
          <span className="font-medium text-slate-400">{article.source_name}</span>
          <span aria-hidden="true">·</span>
          <time dateTime={article.published_at}>{formatDateTime(article.published_at, referenceNow)}</time>
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
