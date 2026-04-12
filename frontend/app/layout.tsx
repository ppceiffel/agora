import type { Metadata } from 'next'
import { Lora, Inter } from 'next/font/google'
import './globals.css'

const inter = Inter({ subsets: ['latin'], variable: '--font-inter' })
const lora = Lora({ subsets: ['latin'], variable: '--font-lora', style: ['normal', 'italic'] })

export const metadata: Metadata = {
  title: 'Agora — Le Référendum Intelligent',
  description: 'Une question par semaine. Sourcée. Débattue. Votée.',
  manifest: '/manifest.json',
  themeColor: '#080808',
  viewport: 'width=device-width, initial-scale=1, maximum-scale=1',
}

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="fr" className={`${inter.variable} ${lora.variable}`}>
      <body className="bg-agora-bg text-agora-cream min-h-screen">
        <div className="max-w-[460px] mx-auto px-4 pb-16">
          {children}
        </div>
      </body>
    </html>
  )
}
