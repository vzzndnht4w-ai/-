import React from 'react';

/** Заражённый: только силуэт и светящиеся глаза — лица не показываем, страх через позу и звук. */
export const Infected: React.FC<{x: number; y: number; scale?: number; tilt?: number; glow?: number; rim?: string; opacity?: number}> =
({x, y, scale = 1, tilt = 6, glow = 1, rim = '#8fa3ad', opacity = 1}) => (
  <g transform={`translate(${x},${y}) scale(${scale})`} opacity={opacity}>
    <defs><filter id="infglow"><feGaussianBlur stdDeviation="6" /></filter></defs>
    <ellipse cx="0" cy="612" rx="120" ry="16" fill="#000" opacity=".35" />
    <g fill="#06080c">
      <rect x="-60" y="405" width="46" height="200" rx="16" /><rect x="14" y="405" width="46" height="200" rx="16" />
      <path d="M-96 130 Q-112 300 -84 420 L84 420 Q112 300 96 130 Q0 108 -96 130Z" />
      <path d="M-92 140 Q-130 300 -112 470" fill="none" stroke="#06080c" strokeWidth="38" strokeLinecap="round" />
      <path d="M92 140 Q132 300 114 470" fill="none" stroke="#06080c" strokeWidth="38" strokeLinecap="round" />
      <g transform={`rotate(${tilt} 0 110)`}>
        <rect x="-22" y="80" width="44" height="50" />
        <path d="M-60 6 C-62 -50 -30 -66 0 -66 C30 -66 62 -50 60 6 C58 50 30 92 0 98 C-30 92 -58 50 -60 6Z" />
      </g>
    </g>
    <g stroke={rim} strokeWidth="2.5" fill="none" opacity=".55"><path d="M-96 130 Q-112 300 -84 420" /><path d="M-60 6 C-62 -50 -30 -66 0 -66" transform={`rotate(${tilt} 0 110)`} /></g>
    <g transform={`rotate(${tilt} 0 110)`}>
      {[-22, 22].map((ex) => <g key={ex}><ellipse cx={ex} cy="12" rx="12" ry="7" fill="#fff4c8" opacity={0.5 * glow} filter="url(#infglow)" /><ellipse cx={ex} cy="12" rx="7" ry="3.6" fill="#fff4c8" opacity={0.95 * glow} /></g>)}
    </g>
  </g>
);
