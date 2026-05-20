import { useState, useEffect } from 'react'

interface EvalMetrics {
  speakerAccuracy: number
  personaConsistency: number
  guardrailMissRate: number
}

export function EvaluationPanel() {
  const [metrics, setMetrics] = useState<EvalMetrics>({
    speakerAccuracy: 0,
    personaConsistency: 0,
    guardrailMissRate: 0,
  })

  // P2: In production, this would poll AgentCore Evaluations API
  useEffect(() => {
    // Mock metrics for demo
    setMetrics({
      speakerAccuracy: 92,
      personaConsistency: 96,
      guardrailMissRate: 0,
    })
  }, [])

  return (
    <section aria-label="평가 지표" data-testid="evaluation-panel">
      <h2 className="text-sm font-semibold text-gray-300 mb-2">평가 지표 (P2)</h2>
      <div className="space-y-2">
        <MetricGauge
          label="화자 식별 정확도"
          value={metrics.speakerAccuracy}
          target={90}
          testId="eval-speaker-accuracy"
        />
        <MetricGauge
          label="페르소나 일관성"
          value={metrics.personaConsistency}
          target={95}
          testId="eval-persona-consistency"
        />
        <MetricGauge
          label="가드레일 누락률"
          value={metrics.guardrailMissRate}
          target={0}
          inverted
          testId="eval-guardrail-miss"
        />
      </div>
    </section>
  )
}

function MetricGauge({
  label,
  value,
  target,
  inverted = false,
  testId,
}: {
  label: string
  value: number
  target: number
  inverted?: boolean
  testId: string
}) {
  const isGood = inverted ? value <= target : value >= target
  const barColor = isGood ? 'bg-green-500' : 'bg-yellow-500'
  const displayValue = inverted ? `${value}%` : `${value}%`

  return (
    <div data-testid={testId} className="bg-gray-800 rounded p-2">
      <div className="flex justify-between text-[10px] mb-1">
        <span className="text-gray-400">{label}</span>
        <span className={isGood ? 'text-green-400' : 'text-yellow-400'}>
          {displayValue} (목표: {target}%)
        </span>
      </div>
      <div className="w-full h-1.5 bg-gray-700 rounded-full overflow-hidden">
        <div
          className={`h-full rounded-full transition-all ${barColor}`}
          style={{ width: `${Math.min(value, 100)}%` }}
        />
      </div>
    </div>
  )
}
