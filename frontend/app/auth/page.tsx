'use client'

import { useState } from 'react'
import { useRouter } from 'next/navigation'
import AgoraHeader from '@/components/AgoraHeader'
import { sendOtp, verifyOtp } from '@/lib/api'
import { useAgoraStore } from '@/lib/store'

export default function AuthPage() {
  const router = useRouter()
  const setToken = useAgoraStore((s) => s.setToken)

  const [phone, setPhone] = useState('')
  const [otpSent, setOtpSent] = useState(false)
  const [devCode, setDevCode] = useState<string | null>(null)
  const [otp, setOtp] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  const handleSendOtp = async () => {
    if (!phone.trim()) { setError('Veuillez entrer votre numéro.'); return }
    setLoading(true); setError('')
    try {
      const res = await sendOtp(phone.trim())
      setOtpSent(true)
      if (res.dev_code) setDevCode(res.dev_code)
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : 'Erreur lors de l\'envoi.')
    } finally {
      setLoading(false)
    }
  }

  const handleVerifyOtp = async () => {
    if (!otp.trim()) { setError('Entrez le code reçu.'); return }
    setLoading(true); setError('')
    try {
      const res = await verifyOtp(phone.trim(), otp.trim())
      setToken(res.access_token)
      router.push('/referendum')
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : 'Code incorrect.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <>
      <AgoraHeader subtitle="Référendum citoyen" />

      {/* Hero card */}
      <div className="bg-agora-card border border-[#c8860a44] rounded-2xl p-5 mb-5 text-center">
        <p
          style={{ fontFamily: "'Lora', Georgia, serif" }}
          className="italic text-[#c8b898] text-[0.95rem] leading-7 mb-4"
        >
          « Une question par semaine.<br />Sourcée. Débattue. Votée. »
        </p>
        <div className="flex justify-center gap-8">
          {[['4 821', 'votes'], ['87%', 'quiz réussi'], ['12', 'questions']].map(([val, lbl]) => (
            <div key={lbl}>
              <div style={{ fontFamily: "'Lora', Georgia, serif" }} className="text-2xl font-bold text-agora-amber">{val}</div>
              <div className="text-[0.6rem] text-[#5a3e28] uppercase tracking-widest mt-0.5">{lbl}</div>
            </div>
          ))}
        </div>
      </div>

      <div className="text-[0.62rem] font-bold tracking-widest uppercase text-agora-amber mb-2">
        Connexion sécurisée
      </div>

      <input
        type="tel"
        placeholder="+33 6 12 34 56 78"
        value={phone}
        onChange={(e) => setPhone(e.target.value)}
        disabled={otpSent}
        className="w-full bg-agora-card border border-agora-border rounded-xl px-3 py-3 text-agora-cream text-sm placeholder:text-[#3a2410] focus:outline-none focus:border-[#c8860a66] mb-3"
      />

      {!otpSent ? (
        <button
          onClick={handleSendOtp}
          disabled={loading}
          className="w-full bg-agora-amber text-agora-bg font-semibold text-sm rounded-xl py-3 hover:opacity-85 transition-opacity disabled:opacity-30"
        >
          {loading ? '...' : 'Recevoir mon code SMS'}
        </button>
      ) : (
        <>
          {devCode && (
            <div className="bg-[#1a2a1a] border border-[#4c7a4833] rounded-xl px-3 py-2 mb-3 text-[0.82rem] text-[#6aaa60]">
              Mode dev — code : <strong>{devCode}</strong>
            </div>
          )}
          <input
            type="text"
            maxLength={6}
            placeholder="123456"
            value={otp}
            onChange={(e) => setOtp(e.target.value)}
            className="w-full bg-agora-card border border-agora-border rounded-xl px-3 py-3 text-agora-cream text-sm placeholder:text-[#3a2410] focus:outline-none focus:border-[#c8860a66] mb-3"
          />
          <button
            onClick={handleVerifyOtp}
            disabled={loading}
            className="w-full bg-agora-amber text-agora-bg font-semibold text-sm rounded-xl py-3 hover:opacity-85 transition-opacity disabled:opacity-30"
          >
            {loading ? '...' : 'Valider'}
          </button>
        </>
      )}

      {error && <p className="text-[#d46050] text-[0.8rem] mt-2">{error}</p>}

      <p className="text-center text-[#3a2410] text-[0.68rem] mt-7 tracking-wide">
        Aucune publicité · Aucune donnée revendue · Vote anonyme
      </p>
    </>
  )
}
