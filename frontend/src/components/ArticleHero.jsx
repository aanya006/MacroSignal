function formatDate(dateStr) {
  if (!dateStr) return ''
  return new Date(dateStr).toLocaleDateString('en-SG', {
    day: 'numeric',
    month: 'short',
    year: 'numeric',
  })
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
          <time dateTime={article.published_at}>{formatDate(article.published_at)}</time>
        </div>
      </div>
    </a>
  )
}

export default ArticleHero
