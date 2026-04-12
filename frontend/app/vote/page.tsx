'use client'

import { useEffect, useState } from 'react'
import { useRouter } from 'next/navigation'
import AgoraHeader from '@/components/AgoraHeader'
import StepDots from '@/components/StepDots'
import { castVote } from '@/lib/api'
import { useAgoraStore } from '@/lib/store'
import { GRADE_ORDER, GRADE_COLORS, GRADE_SLUGS } from '@/lib/constants'

export default function VotePage() {
  const router = useRouter()
  const { token, referendum, quizPassed, setVoteGrade, setEnlightenedScore } = useAgoraStore()
  const [selectedGrade, setSelectedGrade] = useState<string | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  useEffect(() => {
    if (!token) { router.replace('/auth'); return }
    if (!referendum) { router.replace('/referendum'); return }
    if (!quizPassed) { router.replace('/quiz'); return }
  }, [token, referendum, quizPassed, router])

  const handleVote = async () => {
    if (!selectedGrade || !referendum || !token) return
    setLoading(true); setError('')
    try {
      const slug = GRADE_SLUGS[selectedGrade as keyof typeof GRADE_SLUGS]
      const res = await castVote(referendum.id, slug, quizPassed, token)
      setVoteGrade(selectedGrade)
      setEnlightenedScore(res.enlightened_score)
      router.push('/results')
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : 'Erreur lors du vote.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <>
      <AgoraHeader subtitle="Ton vote" />
      <StepDots current={4} />

      {referendum && (
        <div className="bg-agora-card border border-[#c8860a44] rounded-2xl px-4 py-4 mb-4">
          <div className="text-[0.62rem] font-bold uppercase tracking-widest text-agora-amber mb-1.5">
            La question
          </div>
          <p style={{ fontFamily: "'Lora', Georgia, serif" }} className="italic text-[0.9rem] text-[#c8b898] leading-[1.55] m-0">
            « {referendum.question} »
          </p>
        </div>
      )}

      <div className="text-[0.62rem] font-bold uppercase tracking-widest text-agora-amber mb-1">
        Ton évaluation
      </div>
      <p className="text-[#5a3e28] text-[0.78rem] mb-3">
        En Jugement Majoritaire, choisis la mention qui traduit le mieux ton opinion.
      </p>

      <div className="flex flex-col gap-2 mb-5">
        {GRADE_ORDER.map((grade) => {
          const color = GRADE_COLORS[grade]
          const selected = selectedGrade === grade
          return (
            <button
              key={grade}
              onClick={() => setSelectedGrade(grade)}
              className={`text-left px-4 py-3 rounded-xl text-sm border transition-colors flex items-center gap-2.5 ${
                selected
                  ? 'border-[var(--c)] bg-[color-mix(in_srgb,var(--c)_12%,transparent)]'
                  : 'border-agora-border bg-agora-card hover:border-[#c8860a55]'
              }`}
              style={{ '--c': color } as React.CSSProperties}
            >
              <span style={{ color }} className="text-base">●</span>
              <span className={selected ? 'text-agora-cream font-semibold' : 'text-agora-cream'}>
                {grade}
              </span>
            </button>
          )
        })}
      </div>

      {error && <p className="text-[#d46050] text-[0.8rem] mb-3">{error}</p>}

      <button
        onClick={handleVote}
        disabled={!selectedGrade || loading}
        className="w-full bg-agora-amber text-agora-bg font-semibold text-sm rounded-xl py-3 hover:opacity-85 transition-opacity disabled:opacity-30"
      >
        {loading ? '...' : 'Confirmer mon vote'}
      </button>
    </>
  )
}
