interface AgoraHeaderProps {
  subtitle?: string
}

export default function AgoraHeader({ subtitle }: AgoraHeaderProps) {
  return (
    <div className="text-center pt-8 pb-5">
      <div className="text-3xl mb-1">🏛️</div>
      <div
        style={{ fontFamily: "'Lora', Georgia, serif" }}
        className="text-2xl font-bold text-agora-cream tracking-wide"
      >
        Agora
      </div>
      {subtitle && (
        <div className="text-[0.7rem] text-[#5a3e28] mt-1 tracking-widest uppercase">
          {subtitle}
        </div>
      )}
    </div>
  )
}
