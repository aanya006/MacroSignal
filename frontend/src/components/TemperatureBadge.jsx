const TEMP_CONFIG = {
  hot: {
    color: '#f87171',
    bg: 'rgba(239, 68, 68, 0.2)',
    border: 'rgba(239, 68, 68, 0.3)',
  },
  warm: {
    color: '#fbbf24',
    bg: 'rgba(245, 158, 11, 0.2)',
    border: 'rgba(245, 158, 11, 0.3)',
  },
  cool: {
    color: '#22d3ee',
    bg: 'rgba(6, 182, 212, 0.2)',
    border: 'rgba(6, 182, 212, 0.3)',
  },
}

function TemperatureBadge({ label }) {
  const key = label ? label.toLowerCase() : 'cool'
  const config = TEMP_CONFIG[key] || TEMP_CONFIG.cool
  return (
    <span
      className="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-semibold"
      style={{
        color: config.color,
        backgroundColor: config.bg,
        border: `1px solid ${config.border}`,
      }}
    >
      {label ? label.toUpperCase() : 'COOL'}
    </span>
  )
}

export default TemperatureBadge
