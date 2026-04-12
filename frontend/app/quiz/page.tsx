'use client'

import { useEffect, useState } from 'react'
import { useRouter } from 'next/navigation'
import AgoraHeader from '@/components/AgoraHeader'
import StepDots from '@/components/StepDots'
import { getQuiz, validateQuiz } from '@/lib/api'
import { useAgoraStore } from '@/lib/store'

export default function QuizPage() {
  const router = useRouter()
  const { token, referendum, quizQuestions, setQuizQuestions, setQuizPassed } = useAgoraStore()
  const [answers, setAnswers] = useState<Record<string, string>>({})
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  useEffect(() => {
    if (!token) { router.replace('/auth'); return }
    if (!referendum) { router.replace('/referendum'); return }
    if (quizQuestions.length === 0) {
      getQuiz(referendum.id)
        .then(setQuizQuestions)
        .catch((e) => setError(e.message))
    }
  }, [token, referendum, quizQuestions, router, setQuizQuestions])

  const allAnswered = quizQuestions.length > 0 && quizQuestions.every((q) => answers[q.id])

  const handleSubmit = async () => {
    if (!referendum) return
    setLoading(true); setError('')
    try {
      const res = await validateQuiz(referendum.id, answers)
      setQuizPassed(res.passed)
      if (res.passed) {
        router.push('/arguments')
      } else {
        setError(`${res.score}/3 — Il faut au moins ${res.required} bonnes réponses. Relis la question.`)
        setTimeout(() => router.push('/referendum'), 2500)
      }
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : 'Erreur lors de la validation.')
    } finally {
      setLoading(false)
    }
  }

  if (error && !loading) return (
    <div className="pt-10 text-center text-[#d46050] text-sm">{error}</div>
  )
  if (quizQuestions.length === 0) return (
    <div className="pt-10 text-center text-agora-sand text-sm">Chargement…</div>
  )

  return (
    <>
      <AgoraHeader subtitle="Quiz de validation" />
      <StepDots current={2} />

      <p className="text-center text-[#5a3e28] text-[0.78rem] mb-5">
        3 questions · 2 bonnes réponses minimum
      </p>

      {quizQuestions.map((q, i) => (
        <div key={q.id} className="mb-5">
          <div className="text-[0.62rem] font-bold uppercase tracking-widest text-agora-amber mb-1">
            Question {i + 1} · {i + 1}/3
          </div>
          <div className="text-[0.9rem] font-semibold text-agora-cream leading-[1.55] mb-2">
            {q.question_text}
          </div>
          <div className="flex flex-col gap-1.5">
            {(['a', 'b', 'c'] as const).map((opt) => {
              const label = q[`option_${opt}`]
              const selected = answers[q.id] === opt
              return (
                <button
                  key={opt}
                  onClick={() => setAnswers((a) => ({ ...a, [q.id]: opt }))}
                  className={`text-left px-3.5 py-2.5 rounded-xl text-sm border transition-colors ${
                    selected
                      ? 'border-agora-amber bg-[#c8860a18] text-agora-cream'
                      : 'border-agora-border bg-agora-card text-agora-cream hover:border-[#c8860a55]'
                  }`}
                >
                  {label}
                </button>
              )
            })}
          </div>
        </div>
      ))}

      {error && <p className="text-[#d46050] text-[0.8rem] mb-3">{error}</p>}

      <button
        onClick={handleSubmit}
        disabled={!allAnswered || loading}
        className="w-full bg-agora-amber text-agora-bg font-semibold text-sm rounded-xl py-3 hover:opacity-85 transition-opacity disabled:opacity-30"
      >
        {loading ? '...' : 'Valider le quiz'}
      </button>
    </>
  )
}
