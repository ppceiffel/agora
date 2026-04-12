interface StepDotsProps {
  current: number
  total?: number
}

export default function StepDots({ current, total = 5 }: StepDotsProps) {
  return (
    <div className="flex justify-center items-center gap-2 mb-6">
      {Array.from({ length: total }, (_, i) => {
        const step = i + 1
        if (step === current) {
          return (
            <div
              key={step}
              className="h-[6px] w-5 rounded-sm bg-agora-amber"
              style={{ boxShadow: '0 0 8px #c8860a66' }}
            />
          )
        }
        if (step < current) {
          return <div key={step} className="h-[6px] w-[6px] rounded-full bg-[#c8860a88]" />
        }
        return <div key={step} className="h-[6px] w-[6px] rounded-full bg-agora-border" />
      })}
    </div>
  )
}
