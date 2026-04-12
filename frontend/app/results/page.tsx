'use client'

import { useEffect, useState } from 'react'
import { useRouter } from 'next/navigation'
import AgoraHeader from '@/components/AgoraHeader'
import StepDots from '@/components/StepDots'
import ValuesRadar from '@/components/ValuesRadar'
import { getResults, type VoteResults } from '@/lib/api'
import { useAgoraStore } from '@/lib/store'
import { GRADE_ORDER, GRADE_COLORS, VALUES_LABELS, VALUES_COLORS, VALUES_DESCRIPTIONS } from '@/lib/constants'

export default function ResultsPage() {
  const router = useRouter()
  const { token, referendum, voteGrade, quizPassed, fairplayRead, enlightenedScore } = useAgoraStore()
  const [results, setResults] = useState<VoteResults | null>(null)
  const [activeTab, setActiveTab] = useState<'jm' | 'valeurs'>('jm')

  useEffect(() => {
    if (!token) { router.replace('/auth'); return }
    if (!referendum) { router.replace('/referendum'); return }
    getResults(referendum.id).then(setResults).catch(() => {})
  }, [token, referendum, router])

  if (!results) return <div className="pt-10 text-center text-agora-sand text-sm">Chargement…</div>

  const median = results.median_grade
  const medianColor = GRADE_COLORS[median] || '#8a7a62'
  const medianIdx = GRADE_ORDER.indexOf(median as typeof GRADE_ORDER[number])

  const quizBonus = quizPassed ? 10 : 0
  const voteBonus = 10
  const fairplayBonus = fairplayRead ? 5 : 0
  const displayScore = enlightenedScore || (60 + quizBonus + voteBonus + fairplayBonus)

  // Values profile from store (referendum values_mapping + voteGrade)
  const getValuesScores = (): number[] | null => {
    if (!voteGrade || !referendum) return null
    // scores are fetched from the results already stored in the store; fallback to null
    return null
  }
  const valuesScores = getValuesScores()

  return (
    <>
      <AgoraHeader subtitle="Résultats" />
      <StepDots current={5} />

      {/* Score card */}
      <div className="bg-agora-card border border-[#c8860a44] rounded-2xl px-4 py-4 mb-4">
        <div className="flex items-center justify-between">
          <div>
            <div className="text-[0.62rem] font-bold uppercase tracking-widest text-agora-amber mb-1">
              Score Citoyen Éclairé
            </div>
            <div className="flex items-baseline gap-1">
              <span style={{ fontFamily: "'Lora', Georgia, serif" }} className="text-[2rem] font-bold text-agora-amber leading-none">
                {displayScore}
              </span>
              <span className="text-[0.72rem] text-agora-dark">/ 100 pts</span>
            </div>
          </div>
          <div className="flex flex-col gap-1.5 items-end">
            {quizBonus > 0 && <span className="text-[0.68rem] bg-agora-warm border border-agora-border rounded px-2 py-0.5 text-[#6aaa60]">✓ Quiz +{quizBonus}</span>}
            <span className="text-[0.68rem] bg-agora-warm border border-agora-border rounded px-2 py-0.5 text-agora-amber">✓ Vote +{voteBonus}</span>
            {fairplayBonus > 0 && <span className="text-[0.68rem] bg-agora-warm border border-agora-border rounded px-2 py-0.5 text-[#d46050]">✓ Fair-Play +{fairplayBonus}</span>}
          </div>
        </div>
        <div className="h-[5px] bg-agora-border rounded-full mt-3">
          <div
            className="h-full rounded-full"
            style={{ width: `${Math.min(displayScore, 100)}%`, background: 'linear-gradient(90deg,#8a5a0a,#c8860a)' }}
          />
        </div>
      </div>

      {/* Tabs */}
      <div className="flex border-b border-agora-border mb-4">
        {[{ id: 'jm', label: '⚖️ Résultats collectifs' }, { id: 'valeurs', label: '🧭 Profil de valeurs' }].map((t) => (
          <button
            key={t.id}
            onClick={() => setActiveTab(t.id as 'jm' | 'valeurs')}
            className={`flex-1 py-2 text-[0.78rem] font-semibold transition-colors ${
              activeTab === t.id
                ? 'text-agora-amber border-b-2 border-agora-amber -mb-px'
                : 'text-[#5a3e28]'
            }`}
          >
            {t.label}
          </button>
        ))}
      </div>

      {activeTab === 'jm' && (
        <>
          {/* Médiane */}
          <div className="bg-agora-card border border-agora-border rounded-2xl p-4 text-center mb-4">
            <div className="text-[0.62rem] font-bold uppercase tracking-widest text-agora-amber mb-2">
              Mention médiane · Jugement Majoritaire
            </div>
            <div style={{ fontFamily: "'Lora', Georgia, serif", color: medianColor }} className="text-2xl font-bold mb-1">
              {median}
            </div>
            <div className="text-[0.7rem] text-agora-dark">{results.total_votes.toLocaleString('fr-FR')} votes exprimés</div>
          </div>

          {/* Barre JM */}
          <div className="text-[0.62rem] font-bold uppercase tracking-widest text-agora-amber mb-3">
            Distribution &amp; médiane
          </div>
          <div className="relative mb-1">
            <div className="flex h-10 rounded-lg overflow-hidden">
              {GRADE_ORDER.map((g) => {
                const pct = results.distribution_pct[g] || 0
                const color = GRADE_COLORS[g]
                const isMed = g === median
                return (
                  <div
                    key={g}
                    style={{ width: `${pct}%`, background: color, boxShadow: isMed ? 'inset 0 0 0 2px rgba(237,224,200,0.3)' : undefined }}
                    className="flex items-center justify-center"
                  >
                    {pct >= 9 && <span className="text-[0.58rem] font-bold text-white/80">{pct}%</span>}
                  </div>
                )
              })}
            </div>
            {/* 50% marker */}
            <div className="absolute top-0 bottom-0 left-1/2 w-px bg-agora-cream/70 pointer-events-none">
              <div className="absolute -top-5 left-1/2 -translate-x-1/2 bg-agora-cream text-agora-bg text-[0.55rem] font-black rounded px-1">50%</div>
            </div>
          </div>
          <div className="flex mb-5">
            {GRADE_ORDER.map((g) => {
              const pct = results.distribution_pct[g] || 0
              const isMed = g === median
              return (
                <div key={g} style={{ width: `${pct}%` }} className="text-center">
                  <span style={{ color: isMed ? GRADE_COLORS[g] : '#3a2410', fontWeight: isMed ? 700 : 400 }} className="text-[0.55rem] leading-[1.4]">
                    {isMed ? '▲ ' : ''}{g.replace('Très ', 'T. ')}
                  </span>
                </div>
              )
            })}
          </div>

          {/* Explication médiane */}
          <div className="bg-[#161616] border border-agora-border rounded-2xl p-4">
            <div className="text-[0.62rem] font-bold uppercase tracking-widest text-agora-amber mb-1.5">
              Pourquoi « {median} » ?
            </div>
            <p className="text-[0.82rem] text-agora-sand leading-7 mb-2">
              La médiane est le premier grade où les votes cumulés franchissent{' '}
              <strong className="text-agora-cream">50 %</strong>.
            </p>
            <div className="text-[0.82rem] leading-8">
              {GRADE_ORDER.slice(0, medianIdx + 1).map((g, i) => {
                const pct = results.distribution_pct[g] || 0
                return (
                  <span key={g}>
                    <span style={{ color: GRADE_COLORS[g], fontWeight: 600 }}>{pct}%</span>
                    {i < medianIdx ? <span className="text-agora-darker"> + </span> : null}
                  </span>
                )
              })}{' '}
              = <strong style={{ color: medianColor }}>
                {GRADE_ORDER.slice(0, medianIdx + 1).reduce((s, g) => s + (results.distribution_pct[g] || 0), 0).toFixed(1)}%
              </strong>{' '}
              ≥ 50% → <strong style={{ color: medianColor }}>{median}</strong>
            </div>
          </div>
        </>
      )}

      {activeTab === 'valeurs' && (
        <div>
          {!voteGrade ? (
            <p className="text-agora-sand text-[0.85rem] mt-4">Vote d&apos;abord pour voir ton profil de valeurs.</p>
          ) : valuesScores ? (
            <>
              <ValuesRadar scores={valuesScores} label={voteGrade} />
              <div className="text-[0.62rem] font-bold uppercase tracking-widest text-agora-amber mb-3 mt-2">Détail</div>
              {[...VALUES_LABELS.map((name, i) => ({ name, score: valuesScores[i] }))].sort((a, b) => b.score - a.score).map(({ name, score }) => (
                <div key={name} className="mb-3">
                  <div className="flex justify-between items-baseline mb-1">
                    <span style={{ color: VALUES_COLORS[name] }} className="text-[0.82rem] font-semibold">{name}</span>
                    <span className="text-[0.68rem] text-agora-dark">{score}/10</span>
                  </div>
                  <div className="h-[5px] bg-agora-border rounded-full">
                    <div className="h-full rounded-full opacity-85" style={{ width: `${score * 10}%`, background: VALUES_COLORS[name] }} />
                  </div>
                  <p className="text-[0.7rem] text-agora-dark mt-0.5 leading-[1.5]">{VALUES_DESCRIPTIONS[name]}</p>
                </div>
              ))}
            </>
          ) : (
            <p className="text-agora-sand text-[0.82rem] mt-4">
              Le profil de valeurs sera disponible après synchronisation avec le serveur. Consultez votre profil complet sur{' '}
              <button onClick={() => router.push('/profil')} className="text-agora-amber underline">Mon profil</button>.
            </p>
          )}
          <p className="text-[#3a2410] text-[0.65rem] mt-4 leading-6">
            Esquisse indicative · S. Schwartz, <em>Basic Human Values</em> (1992),
            adapté au contexte civique français. Un seul vote ne suffit pas à établir
            un profil complet — il se précise au fil des référendums.
          </p>
        </div>
      )}

      <div className="text-center text-agora-darker text-[0.68rem] mt-6 mb-4 tracking-wide">
        Classement mis à jour chaque lundi · Revenez la semaine prochaine
      </div>

      <div className="grid grid-cols-2 gap-3">
        <button
          onClick={() => router.push('/profil')}
          className="bg-agora-warm border border-agora-border text-agora-cream font-semibold text-sm rounded-xl py-3 hover:border-agora-sand transition-colors"
        >
          Mon profil →
        </button>
        <button
          onClick={() => { useAgoraStore.getState().resetFlow(); router.push('/referendum') }}
          className="bg-agora-amber text-agora-bg font-semibold text-sm rounded-xl py-3 hover:opacity-85 transition-opacity"
        >
          Recommencer
        </button>
      </div>
    </>
  )
}
