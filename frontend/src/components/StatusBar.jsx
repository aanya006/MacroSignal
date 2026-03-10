function StatusBar({ lastUpdated }) {
  const formatted = lastUpdated
    ? new Date(lastUpdated).toLocaleTimeString('en-SG', {
        hour: '2-digit',
        minute: '2-digit',
        second: '2-digit',
        hour12: false,
      })
    : '--:--:--'

  return (
    <footer className="h-8 px-6 flex items-center justify-between bg-[#0f172a] border-t border-slate-700 text-xs text-slate-500">
      <span>MacroSignal v1.0</span>
      <span className="text-slate-600 text-[10px]">AI-generated content is for informational purposes only and does not constitute investment advice under the Securities and Futures Act (Cap. 289) of Singapore.</span>
      <span>Last updated: {formatted}</span>
    </footer>
  )
}

export default StatusBar
