const REGION_COLORS = {
  singapore: { bg: 'rgba(239, 68, 68, 0.15)', color: '#f87171' },
  us: { bg: 'rgba(59, 130, 246, 0.15)', color: '#60a5fa' },
  china: { bg: 'rgba(245, 158, 11, 0.15)', color: '#fbbf24' },
  europe: { bg: 'rgba(168, 85, 247, 0.15)', color: '#c084fc' },
  japan: { bg: 'rgba(236, 72, 153, 0.15)', color: '#f472b6' },
  asean: { bg: 'rgba(34, 197, 94, 0.15)', color: '#4ade80' },
}

const ASSET_COLORS = {
  equities: { bg: 'rgba(34, 197, 94, 0.15)', color: '#4ade80' },
  bonds: { bg: 'rgba(59, 130, 246, 0.15)', color: '#60a5fa' },
  fx: { bg: 'rgba(245, 158, 11, 0.15)', color: '#fbbf24' },
  commodities: { bg: 'rgba(168, 85, 247, 0.15)', color: '#c084fc' },
}

function getColor(tag, map) {
  const key = tag.toLowerCase().trim()
  for (const [k, v] of Object.entries(map)) {
    if (key.includes(k)) return v
  }
  return { bg: 'rgba(100, 116, 139, 0.15)', color: '#94a3b8' }
}

function TagPill({ tag, colorMap }) {
  const { bg, color } = getColor(tag, colorMap)
  return (
    <span
      className="px-2.5 py-1 rounded-full text-xs font-medium"
      style={{ backgroundColor: bg, color }}
    >
      {tag}
    </span>
  )
}

function RegionsMarketsBox({ regionTags, assetTags }) {
  if (!regionTags?.length && !assetTags?.length) return null

  return (
    <div className="flex flex-wrap items-center gap-2">
      {regionTags?.map((tag) => (
        <TagPill key={tag} tag={tag} colorMap={REGION_COLORS} />
      ))}
      {assetTags?.map((tag) => (
        <TagPill key={tag} tag={tag} colorMap={ASSET_COLORS} />
      ))}
    </div>
  )
}

export default RegionsMarketsBox
