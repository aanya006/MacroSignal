const DIRECTION_CONFIG = {
  positive: { symbol: '\u25B2', label: 'Bullish', className: 'text-green-500' },
  negative: { symbol: '\u25BC', label: 'Bearish', className: 'text-red-500' },
  neutral: { symbol: '\u2014', label: 'Neutral', className: 'text-slate-500' },
}

const ASSET_LABELS = {
  equities: 'Equities',
  bonds: 'Bonds',
  fx: 'FX',
  commodities: 'Commodities',
}

function CausalArrow() {
  return (
    <div className="flex justify-center py-1.5">
      <div className="relative">
        <div
          className="w-[3px] h-7 rounded-sm"
          style={{
            background: 'linear-gradient(to bottom, #f59e0b, #ef4444)',
            boxShadow: '0 0 8px rgba(245, 158, 11, 0.3)',
          }}
        />
        <div
          className="absolute -bottom-1.5 left-1/2 -translate-x-1/2 w-0 h-0"
          style={{
            borderLeft: '7px solid transparent',
            borderRight: '7px solid transparent',
            borderTop: '8px solid #ef4444',
            filter: 'drop-shadow(0 0 4px rgba(239, 68, 68, 0.4))',
          }}
        />
      </div>
    </div>
  )
}

function ImpactCard({ asset, impact, historical }) {
  const dir = DIRECTION_CONFIG[impact?.direction] || DIRECTION_CONFIG.neutral
  const displayLabel = historical && impact?.change
    ? `${dir.symbol} ${impact.change}`
    : `${dir.symbol} ${dir.label}`
  return (
    <div className="rounded-lg bg-[#1e293b] p-3 border border-[#334155]">
      <div className="flex justify-between items-center mb-1.5">
        <span className="text-[10px] font-bold uppercase tracking-wider text-slate-400">
          {ASSET_LABELS[asset] || asset}
        </span>
        <span className={`text-[11px] font-bold flex items-center gap-1 ${dir.className}`}>
          {displayLabel}
        </span>
      </div>
      <p className="text-xs text-slate-300 leading-relaxed">
        {impact?.summary || 'No data available'}
      </p>
    </div>
  )
}

function CausalChain({ chain, historical }) {
  if (!chain || typeof chain === 'string') {
    return (
      <div className="space-y-4">
        <div className="text-[11px] font-semibold uppercase tracking-[1.2px] text-slate-500">
          Causal Chain
        </div>
        <div className="rounded-lg bg-[#1e293b] p-4">
          <p className="text-sm text-slate-500">
            Causal analysis not yet available.
          </p>
        </div>
      </div>
    )
  }

  return (
    <div className="space-y-3">
      <div className="text-[11px] font-semibold uppercase tracking-[1.2px] text-slate-500">
        {historical ? 'What Happened' : 'Causal Chain'}
      </div>

      {/* Trigger */}
      <div className="rounded-lg bg-[#1e293b] p-3.5 border-l-[3px] border-l-red-500">
        <div className="text-[10px] font-bold uppercase tracking-[1px] text-red-500 mb-1.5">
          Trigger
        </div>
        <p className="text-[13px] text-slate-200 leading-relaxed">{chain.trigger}</p>
      </div>

      <CausalArrow />

      {/* Mechanism */}
      <div className="rounded-lg bg-[#1e293b] p-3.5 border-l-[3px] border-l-amber-500">
        <div className="text-[10px] font-bold uppercase tracking-[1px] text-amber-500 mb-1.5">
          Mechanism
        </div>
        <p className="text-[13px] text-slate-200 leading-relaxed">{chain.mechanism}</p>
      </div>

      <CausalArrow />

      {/* Asset Impacts */}
      <div className="text-[11px] font-semibold uppercase tracking-[1.2px] text-slate-500 mt-1">
        {historical ? 'Outcome' : 'Asset Impacts'}
      </div>
      <div className="grid grid-cols-2 gap-2">
        <ImpactCard asset="equities" impact={chain.impacts?.equities} historical={historical} />
        <ImpactCard asset="bonds" impact={chain.impacts?.bonds} historical={historical} />
        <ImpactCard asset="fx" impact={chain.impacts?.fx} historical={historical} />
        <ImpactCard asset="commodities" impact={chain.impacts?.commodities} historical={historical} />
      </div>

      {/* AI Disclaimer */}
      <div className="flex items-center gap-2 mt-2.5 text-[11px] text-slate-500">
        <span className="px-2 py-0.5 rounded bg-purple-500/15 text-purple-400 text-[10px] font-semibold">
          AI-Generated
        </span>
        For informational purposes only — not financial advice.
      </div>
    </div>
  )
}

export default CausalChain
