'use client'

import { useEffect, useState } from 'react'
import { useRouter } from 'next/navigation'
import AgoraHeader from '@/components/AgoraHeader'
import ValuesRadar from '@/components/ValuesRadar'
import { getMe, getHistory, type VoteHistoryItem } from '@/lib/api'
import { useAgoraStore } from '@/lib/store'
import { VALUES_LABELS, VALUES_COLORS, VALUES_DESCRIPTIONS, GRADE_COLORS } from '@/lib/constants'

export default function ProfilPage() {
  const router = useRouter()
  const { token } = useAgoraStore()
  const [profile, setProfile] = useState<Awaited<ReturnType<typeof getMe>> | null>(null)
  const [history, setHistory] = useState<VoteHistoryItem[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    if (!token) { router.replace('/auth'); return }
    Promise.all([getMe(token), getHistory(token)])
      .then(([p, h]) => { setProfile(p); setHistory(h) })
      .catch(() => {})
      .finally(() => setLoading(false))
  }, [token, router])

  if (loading) return <div className="pt-10 text-center text-agora-sand text-sm">Chargement…</div>
  if (!profile) return <div className="pt-10 text-center text-agora-sand text-sm">Non connecté.</div>

  const vp = profile.values_profile
  const n = vp?.votes_count || 0
  const scores = vp ? VALUES_LABELS.map((k) => vp.scores[k] ?? 5) : null

  const sortedValues = scores
    ? [...VALUES_LABELS.map((name, i) => ({ name, score: scores[i] }))].sort((a, b) => b.score - a.score)
    : []

  const MEDALS = ['🥇', '🥈', '🥉']

  return (
    <>
      <AgoraHeader subtitle="Mon profil de valeurs" />

      {/* Stats summary */}
      <div className="grid grid-cols-3 gap-2 mb-5">
        {[
          ['Score', profile.enlightened_score, 'pts'],
          ['Votes', profile.votes_count, 'référendums'],
          ['Fair-Play', profile.fairplay_count, 'lectures'],
        ].map(([label, value, unit]) => (
          <div key={label as string} className="bg-agora-card border border-agora-border rounded-xl p-3 text-center">
            <div style={{ fontFamily: "'Lora', Georgia, serif" }} className="text-xl font-bold text-agora-amber">{value}</div>
            <div className="text-[0.58rem] uppercase tracking-widest text-agora-darker mt-0.5">{label as string}</div>
            <div className="text-[0.6rem] text-[#3a2410] mt-0.5">{unit as string}</div>
          </div>
        ))}
      </div>

      {profile.nickname && (
        <div className="text-center text-agora-sand text-[0.82rem] mb-4">
          Citoyen : <strong className="text-agora-cream">{profile.nickname}</strong>
        </div>
      )}

      <p className="text-center text-[#5a3e28] text-[0.78rem] mb-4">
        Profil construit sur{' '}
        <strong className="text-agora-amber">{n} référendum{n > 1 ? 's' : ''}</strong>
        {' '}· Plus vous votez, plus le profil se précise.
      </p>

      {n === 0 || !scores ? (
        <div className="text-center text-agora-sand text-[0.85rem] mt-8">
          Aucun vote enregistré. Participez à un référendum pour voir votre profil.
        </div>
      ) : (
        <>
          <ValuesRadar scores={scores} label="Profil global" height={300} />

          <div className="text-[0.62rem] font-bold uppercase tracking-widest text-agora-amber mb-3 mt-2">
            Hiérarchie de vos valeurs
          </div>
          {sortedValues.map(({ name, score }, rank) => (
            <div key={name} className="mb-3">
              <div className="flex justify-between items-baseline mb-1">
                <span style={{ color: VALUES_COLORS[name] }} className="text-[0.82rem] font-semibold">
                  {rank < 3 ? MEDALS[rank] : `${rank + 1}.`}&nbsp; {name}
                </span>
                <span className="text-[0.68rem] text-agora-dark">{score}/10</span>
              </div>
              <div className="h-[5px] bg-agora-border rounded-full">
                <div className="h-full rounded-full opacity-85" style={{ width: `${score * 10}%`, background: VALUES_COLORS[name] }} />
              </div>
              <p className="text-[0.7rem] text-agora-dark mt-0.5 leading-[1.5]">{VALUES_DESCRIPTIONS[name]}</p>
            </div>
          ))}

          {/* Vote history */}
          {history.length > 0 && (
            <>
              <hr className="border-agora-border my-5" />
              <div className="text-[0.62rem] font-bold uppercase tracking-widest text-agora-amber mb-3">
                Votes pris en compte
              </div>
              {[...history].reverse().map((entry, i) => {
                const color = GRADE_COLORS[entry.grade] || '#8a6840'
                const date = new Date(entry.week_start).toLocaleDateString('fr-FR', { day: 'numeric', month: 'long', year: 'numeric' })
                return (
                  <div key={i} className="py-2.5 border-b border-[#1a1a1a]">
                    <div className="flex justify-between items-center mb-0.5">
                      <span className="text-[0.72rem] text-agora-sand">Semaine du {date}</span>
                      <span style={{ color }} className="text-[0.7rem] font-semibold">{entry.grade}</span>
                    </div>
                    <p style={{ fontFamily: "'Lora', Georgia, serif" }} className="italic text-[0.82rem] text-[#c8b898] leading-[1.5] m-0">
                      « {entry.question} »
                    </p>
                  </div>
                )
              })}
            </>
          )}

          <p className="text-[#3a2410] text-[0.65rem] mt-5 leading-6">
            Esquisse indicative · S. Schwartz, <em>Basic Human Values</em> (1992),
            adapté au contexte civique français.
          </p>
        </>
      )}

      <div className="mt-6">
        <button
          onClick={() => router.back()}
          className="w-full bg-agora-warm border border-agora-border text-agora-cream font-semibold text-sm rounded-xl py-3 hover:border-agora-sand transition-colors"
        >
          ← Retour aux résultats
        </button>
      </div>
    </>
  )
}
