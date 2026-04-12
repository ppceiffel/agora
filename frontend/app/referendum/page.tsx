'use client'

import { useEffect, useState } from 'react'
import { useRouter } from 'next/navigation'
import AgoraHeader from '@/components/AgoraHeader'
import StepDots from '@/components/StepDots'
import { getCurrentReferendum } from '@/lib/api'
import { useAgoraStore } from '@/lib/store'

export default function ReferendumPage() {
  const router = useRouter()
  const { token, setReferendum } = useAgoraStore()
  const [ref, setRef] = useState<Awaited<ReturnType<typeof getCurrentReferendum>> | null>(null)
  const [error, setError] = useState('')
  const [expandedHistorique, setExpandedHistorique] = useState(false)
  const [expandedScientifique, setExpandedScientifique] = useState(false)

  useEffect(() => {
    if (!token) { router.replace('/auth'); return }
    getCurrentReferendum()
      .then((r) => { setRef(r); setReferendum(r) })
      .catch((e) => setError(e.message))
  }, [token, router, setReferendum])

  if (error) return (
    <div className="pt-10 text-center text-[#d46050] text-sm">{error}</div>
  )
  if (!ref) return (
    <div className="pt-10 text-center text-agora-sand text-sm">Chargement…</div>
  )

  const weekLabel = new Date(ref.week_start).toLocaleDateString('fr-FR', {
    day: 'numeric', month: 'long', year: 'numeric'
  })

  return (
    <>
      <AgoraHeader />
      <StepDots current={1} />

      {/* Badges */}
      <div className="flex gap-2 mb-3">
        <span className="text-[0.65rem] font-semibold uppercase tracking-wide px-2 py-0.5 rounded bg-[#c8860a18] text-agora-amber border border-[#c8860a33]">
          Semaine du {weekLabel}
        </span>
        {ref.news_source_title && (
          <span className="text-[0.65rem] font-semibold uppercase tracking-wide px-2 py-0.5 rounded bg-[#4c7a4818] text-[#6aaa60] border border-[#4c7a4833]">
            Sourcé
          </span>
        )}
      </div>

      {/* Question */}
      <h1
        style={{ fontFamily: "'Lora', Georgia, serif" }}
        className="text-[1.15rem] font-semibold text-agora-cream leading-[1.55] mb-4 tracking-[0.01em]"
      >
        {ref.question}
      </h1>

      {/* Résumé */}
      <div className="bg-agora-card border border-agora-border rounded-2xl p-4 mb-3">
        <p className="text-sm leading-7 text-[#9a7a58] m-0">{ref.summary}</p>
      </div>

      {/* Éclairage historique */}
      {ref.historical_context && (
        <div className="bg-agora-card border border-agora-border rounded-xl mb-2 overflow-hidden">
          <button
            onClick={() => setExpandedHistorique((v) => !v)}
            className="w-full px-4 py-3 text-left text-[0.84rem] font-semibold text-agora-sand flex justify-between items-center"
          >
            Éclairage historique
            <span className="text-agora-darker">{expandedHistorique ? '▲' : '▼'}</span>
          </button>
          {expandedHistorique && (
            <div className="px-4 pb-4 text-[0.83rem] leading-7 text-agora-cream prose prose-invert max-w-none"
              dangerouslySetInnerHTML={{ __html: ref.historical_context.replace(/\n\n/g, '</p><p>').replace(/^/, '<p>').replace(/$/, '</p>').replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>') }}
            />
          )}
        </div>
      )}

      {/* Éclairage scientifique */}
      {ref.scientific_context && (
        <div className="bg-agora-card border border-agora-border rounded-xl mb-4 overflow-hidden">
          <button
            onClick={() => setExpandedScientifique((v) => !v)}
            className="w-full px-4 py-3 text-left text-[0.84rem] font-semibold text-agora-sand flex justify-between items-center"
          >
            Éclairage scientifique
            <span className="text-agora-darker">{expandedScientifique ? '▲' : '▼'}</span>
          </button>
          {expandedScientifique && (
            <div className="px-4 pb-4 text-[0.83rem] leading-7 text-agora-cream"
              dangerouslySetInnerHTML={{ __html: ref.scientific_context.replace(/\n\n/g, '</p><p>').replace(/^/, '<p>').replace(/$/, '</p>').replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>') }}
            />
          )}
        </div>
      )}

      <p className="text-center text-[#5a3e28] text-[0.78rem] mb-3">
        Pour voter, réussis d&apos;abord le quiz de compréhension (2/3 minimum).
      </p>
      <button
        onClick={() => router.push('/quiz')}
        className="w-full bg-agora-amber text-agora-bg font-semibold text-sm rounded-xl py-3 hover:opacity-85 transition-opacity"
      >
        Passer le quiz →
      </button>
    </>
  )
}
