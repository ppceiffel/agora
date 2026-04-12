'use client'

import dynamic from 'next/dynamic'
import { VALUES_LABELS } from '@/lib/constants'

// Plotly ne fonctionne pas côté serveur — import dynamique obligatoire
const Plot = dynamic(() => import('react-plotly.js'), { ssr: false, loading: () => (
  <div className="h-80 flex items-center justify-center text-agora-sand text-sm">
    Chargement du radar…
  </div>
) })

interface ValuesRadarProps {
  scores: number[]          // 6 valeurs dans l'ordre VALUES_LABELS
  label?: string            // Légende du profil (ex: "Très favorable")
  height?: number
}

export default function ValuesRadar({ scores, label = 'Profil', height = 320 }: ValuesRadarProps) {
  const theta = [...VALUES_LABELS, VALUES_LABELS[0]]
  const r = [...scores, scores[0]]

  const data: Plotly.Data[] = [
    // Référence neutre
    {
      type: 'scatterpolar',
      r: Array(VALUES_LABELS.length + 1).fill(5),
      theta,
      fill: 'toself',
      fillcolor: 'rgba(138,122,98,0.06)',
      line: { color: 'rgba(138,122,98,0.25)', width: 1, dash: 'dot' },
      hoverinfo: 'skip',
      name: 'Neutre',
    } as Plotly.ScatterPolarData,
    // Profil utilisateur
    {
      type: 'scatterpolar',
      r,
      theta,
      fill: 'toself',
      fillcolor: 'rgba(200,134,10,0.13)',
      line: { color: '#c8860a', width: 2 },
      marker: { color: '#c8860a', size: 6 },
      hovertemplate: '<b>%{theta}</b><br>Score : %{r}/10<extra></extra>',
      name: label,
    } as Plotly.ScatterPolarData,
  ]

  const layout: Partial<Plotly.Layout> = {
    polar: {
      bgcolor: '#111111',
      radialaxis: {
        visible: true,
        range: [0, 10],
        tickvals: [2, 4, 6, 8, 10],
        tickfont: { color: '#3a2410', size: 8 },
        gridcolor: '#222222',
        linecolor: '#222222',
      },
      angularaxis: {
        tickfont: { family: 'Inter, sans-serif', color: '#ede0c8', size: 11 },
        gridcolor: '#222222',
        linecolor: '#222222',
      },
    },
    paper_bgcolor: '#080808',
    showlegend: false,
    margin: { t: 16, b: 16, l: 48, r: 48 },
    height,
  }

  return (
    <Plot
      data={data}
      layout={layout}
      config={{ displayModeBar: false, responsive: true }}
      style={{ width: '100%' }}
    />
  )
}
