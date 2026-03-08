import { useRef, useEffect } from 'react'

function formatDateLabel(dateStr) {
  const d = new Date(dateStr + 'T00:00:00')
  return d.toLocaleDateString('en-SG', { day: 'numeric', month: 'short' })
}

function getHeatLevel(count, maxCount) {
  if (maxCount === 0) return 'cold'
  const ratio = count / maxCount
  if (ratio >= 0.8) return 'critical'
  if (ratio >= 0.6) return 'high'
  if (ratio >= 0.35) return 'medium'
  if (ratio >= 0.15) return 'low'
  return 'cold'
}

const DOT_STYLES = {
  cold: {
    background: '#475569',
  },
  low: {
    background: '#92400e',
    boxShadow: '0 0 4px rgba(239, 68, 68, 0.15)',
  },
  medium: {
    background: '#dc2626',
    boxShadow: '0 0 6px rgba(239, 68, 68, 0.3)',
  },
  high: {
    background: '#ef4444',
    boxShadow: '0 0 10px rgba(239, 68, 68, 0.4), 0 0 20px rgba(239, 68, 68, 0.15)',
  },
  critical: {
    background: '#ef4444',
    boxShadow: '0 0 12px rgba(239, 68, 68, 0.5), 0 0 24px rgba(239, 68, 68, 0.2)',
  },
}

function DateTimeline({ articleDates, selectedDate, onSelectDate, articlesByDate }) {
  const scrollRef = useRef(null)
  const selectedRef = useRef(null)

  useEffect(() => {
    if (selectedRef.current) {
      selectedRef.current.scrollIntoView({
        behavior: 'smooth',
        block: 'nearest',
        inline: 'center',
      })
    }
  }, [selectedDate])

  if (!articleDates || articleDates.length === 0) return null

  const maxCount = Math.max(
    ...articleDates.map((d) => articlesByDate?.[d] || 1),
    1
  )

  // Precompute heat levels for connector styling
  const heatLevels = articleDates.map((d) =>
    getHeatLevel(articlesByDate?.[d] || 0, maxCount)
  )

  return (
    <div>
      <h3
        style={{
          fontSize: 11,
          fontWeight: 600,
          textTransform: 'uppercase',
          letterSpacing: '1.2px',
          color: '#64748b',
          marginBottom: 14,
        }}
      >
        Timeline : Last 30 Days
      </h3>
      <div
        style={{
          background: '#1e293b',
          borderRadius: 8,
          padding: '14px 16px',
        }}
      >
        <div
          ref={scrollRef}
          style={{
            display: 'flex',
            alignItems: 'center',
            gap: 0,
            overflowX: 'auto',
            padding: '8px 0',
            scrollbarWidth: 'thin',
            scrollbarColor: '#334155 transparent',
          }}
        >
          {articleDates.map((date, i) => {
            const isSelected = date === selectedDate
            const count = articlesByDate?.[date] || 0
            const heat = heatLevels[i]
            const isHot = heat === 'critical' || heat === 'high'

            // Connector between nodes (before each node except the first)
            const connector = i > 0 ? (
              <div
                key={`conn-${date}`}
                style={{
                  width: 16,
                  height: 2,
                  flexShrink: 0,
                  transition: 'all 0.2s',
                  borderRadius: 2,
                  ...(heatLevels[i - 1] === 'critical' || heatLevels[i - 1] === 'high' ||
                    heat === 'critical' || heat === 'high'
                    ? {
                        background: 'rgba(239, 68, 68, 0.4)',
                        boxShadow: '0 0 6px rgba(239, 68, 68, 0.2)',
                      }
                    : { background: '#334155' }),
                }}
              />
            ) : null

            return [
              connector,
              <button
                key={date}
                ref={isSelected ? selectedRef : null}
                onClick={() => onSelectDate(date)}
                style={{
                  display: 'flex',
                  flexDirection: 'column',
                  alignItems: 'center',
                  gap: 6,
                  cursor: 'pointer',
                  padding: '4px 8px',
                  flexShrink: 0,
                  transition: 'all 0.15s',
                  background: 'none',
                  border: 'none',
                  fontFamily: 'inherit',
                }}
              >
                {/* Date label */}
                <span
                  style={{
                    fontSize: 10,
                    whiteSpace: 'nowrap',
                    transition: 'all 0.15s',
                    color: isSelected
                      ? '#f1f5f9'
                      : isHot
                        ? '#ef4444'
                        : '#64748b',
                    fontWeight: isSelected || isHot ? 700 : 400,
                  }}
                >
                  {formatDateLabel(date)}
                </span>
                {/* Dot */}
                <span
                  style={{
                    width: 10,
                    height: 10,
                    borderRadius: '50%',
                    transition: 'all 0.2s',
                    ...DOT_STYLES[heat],
                    ...(isSelected
                      ? {
                          outline: '2px solid #f1f5f9',
                          outlineOffset: 2,
                        }
                      : {}),
                    ...(heat === 'critical'
                      ? {
                          animation: 'epicenter-pulse 2.5s ease-in-out infinite',
                        }
                      : {}),
                  }}
                />
              </button>,
            ]
          })}
        </div>
      </div>

      {/* Keyframe for critical pulse animation */}
      <style>{`
        @keyframes epicenter-pulse {
          0%, 100% { box-shadow: 0 0 12px rgba(239, 68, 68, 0.5), 0 0 24px rgba(239, 68, 68, 0.2); }
          50% { box-shadow: 0 0 16px rgba(239, 68, 68, 0.6), 0 0 32px rgba(239, 68, 68, 0.3); }
        }
      `}</style>
    </div>
  )
}

export default DateTimeline
