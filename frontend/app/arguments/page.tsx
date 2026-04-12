'use client'

import { useEffect, useState } from 'react'
import { useRouter } from 'next/navigation'
import AgoraHeader from '@/components/AgoraHeader'
import StepDots from '@/components/StepDots'
import { getArguments, markArgumentRead, type Argument } from '@/lib/api'
import { useAgoraStore } from '@/lib/store'

export default function ArgumentsPage() {
  const router = useRouter()
  const { token, referendum, quizPassed, fairplayRead, setFairplayRead, addReadArgument, readArgumentIds } = useAgoraStore()
  const [args, setArgs] = useState<{ pour: Argument[]; contre: Argument[] } | null>(null)
  const [error, setError] = useState('')

  useEffect(() => {
    if (!token) { router.replace('/auth'); return }
    if (!referendum) { router.replace('/referendum'); return }
    if (!quizPassed) { router.replace('/quiz'); return }
    getArguments(referendum.id)
      .then(setArgs)
      .catch((e) => setError(e.message))
  }, [token, referendum, quizPassed, router])

  const handleRead = async (id: string) => {
    if (!token || readArgumentIds.includes(id)) return
    try {
      await markArgumentRead(id, token)
      addReadArgument(id)
    } catch { /* ignore */ }
  }

  const hasReadBothSides = () => {
    if (!args) return false
    const readPour = args.pour.some((a) => readArgumentIds.includes(a.id))
    const readContre = args.contre.some((a) => readArgumentIds.includes(a.id))
    return readPour && readContre
  }

  if (error) return <div className="pt-10 text-center text-[#d46050] text-sm">{error}</div>
  if (!args) return <div className="pt-10 text-center text-agora-sand text-sm">Chargement…</div>

  const ArgItem = ({ arg, side }: { arg: Argument; side: 'pour' | 'contre' }) => {
    const isRead = readArgumentIds.includes(arg.id)
    const color = side === 'pour' ? '#4c7a48' : '#9a3028'
    return (
      <div
        className="py-2.5 border-b border-agora-border last:border-0 cursor-pointer"
        onClick={() => handleRead(arg.id)}
      >
        <div className="text-[0.78rem] leading-[1.6] text-[#c8b898] mb-1">{arg.content}</div>
        <div className="flex justify-between items-center">
          <span className="text-[0.62rem]" style={{ color }}>▲ {arg.upvotes.toLocaleString('fr-FR')}</span>
          {isRead && <span className="text-[0.6rem] text-[#4c7a48]">✓ lu</span>}
        </div>
      </div>
    )
  }

  return (
    <>
      <AgoraHeader subtitle="Les arguments" />
      <StepDots current={3} />

      {referendum && (
        <div className="bg-agora-card border border-agora-border rounded-2xl px-4 py-3 mb-3">
          <p style={{ fontFamily: "'Lora', Georgia, serif" }} className="italic text-[0.875rem] text-[#9a7a58] leading-[1.55] m-0">
            « {referendum.question} »
          </p>
        </div>
      )}

      <p className="text-center text-[#5a3e28] text-[0.78rem] mb-4">
        Les meilleurs arguments des deux côtés — cliquer pour marquer comme lu.
      </p>

      <div className="grid grid-cols-2 gap-3 mb-4">
        {/* Pour */}
        <div>
          <div className="text-[0.62rem] font-bold uppercase tracking-widest text-[#6aaa60] border-b border-[#4c7a4844] pb-1.5 mb-1">
            ✦ Pour
          </div>
          {args.pour.map((a) => <ArgItem key={a.id} arg={a} side="pour" />)}
          {args.pour.length === 0 && <p className="text-[0.72rem] text-agora-darker">Aucun argument</p>}
        </div>
        {/* Contre */}
        <div>
          <div className="text-[0.62rem] font-bold uppercase tracking-widest text-[#d46050] border-b border-[#b8403044] pb-1.5 mb-1">
            ✦ Contre
          </div>
          {args.contre.map((a) => <ArgItem key={a.id} arg={a} side="contre" />)}
          {args.contre.length === 0 && <p className="text-[0.72rem] text-agora-darker">Aucun argument</p>}
        </div>
      </div>

      {/* Fair-play */}
      <label className="flex items-start gap-2 cursor-pointer mb-4">
        <input
          type="checkbox"
          checked={fairplayRead || hasReadBothSides()}
          onChange={(e) => setFairplayRead(e.target.checked)}
          className="mt-0.5 accent-amber-600"
        />
        <span className="text-[0.78rem] text-agora-sand leading-5">
          J&apos;ai lu les arguments des deux côtés (+5 pts Fair-Play)
        </span>
      </label>

      <button
        onClick={() => router.push('/vote')}
        className="w-full bg-agora-amber text-agora-bg font-semibold text-sm rounded-xl py-3 hover:opacity-85 transition-opacity"
      >
        Voter →
      </button>
    </>
  )
}
