import React from 'react';
import {AbsoluteFill, interpolate, useCurrentFrame, useVideoConfig} from 'remotion';
import {FONT} from '../theme';

const SKY = {day: ['#8fb8e8', '#dcebf7'], dusk: ['#5b4a7a', '#e58a6b']} as const;

const Tree: React.FC<{x: number; h: number}> = ({x, h}) => (
  <polygon points={`${x},${900 - h} ${x - h * 0.28},900 ${x + h * 0.28},900`} fill="#2f5d3a" />
);

/** Плоская мультяшная сцена «учебный центр»: небо, лес, палатка, табличка, боец с пультом и дрон. */
export const Cartoon: React.FC<{sky?: 'day' | 'dusk'; tag?: string}> = ({sky = 'day', tag}) => {
  const frame = useCurrentFrame();
  const {fps, width} = useVideoConfig();
  const k = width / 1080;
  const [a, b] = SKY[sky];
  const t = frame / fps;
  const bob = Math.sin(t * 2.4) * 14;
  const drift = Math.sin(t * 0.7) * 40;
  const cloud = interpolate(frame % (fps * 40), [0, fps * 40], [-300, 1400]);
  const sway = Math.sin(t * 1.6) * 1.2;
  return (
    <AbsoluteFill style={{background: `linear-gradient(${a}, ${b})`}}>
      <svg viewBox="0 0 1080 1920" width="100%" height="100%" preserveAspectRatio="xMidYMid slice">
        <ellipse cx={cloud} cy="300" rx="130" ry="34" fill="#fff" opacity=".75" />
        <ellipse cx={cloud * 0.6 + 400} cy="460" rx="90" ry="24" fill="#fff" opacity=".55" />
        <g transform="translate(0,130)">
          {[60, 170, 280, 400, 520, 640, 760, 880, 1000].map((x, i) => <Tree key={x} x={x} h={230 + (i % 3) * 40} />)}
        </g>
        <g transform="translate(0,-170)">
        <rect x="0" y="1200" width="1080" height="900" fill="#6b8f3a" />
        <rect x="0" y="1200" width="1080" height="60" fill="#5a7d30" />
        {/* палатка */}
        <polygon points="760,1250 900,1050 1040,1250" fill="#4a6b34" />
        <polygon points="880,1250 900,1150 920,1250" fill="#2c4220" />
        {/* табличка */}
        <rect x="110" y="1090" width="10" height="170" fill="#7a5a3a" />
        <rect x="40" y="1000" width="250" height="100" rx="8" fill="#1f4a9c" />
        <text x="165" y="1058" textAnchor="middle" fill="#fff" fontFamily={FONT} fontWeight={900} fontSize="30">УЧЕБНЫЙ</text>
        <text x="165" y="1090" textAnchor="middle" fill="#fff" fontFamily={FONT} fontWeight={900} fontSize="30">ЦЕНТР</text>
        {/* конусы */}
        {[640, 720, 800].map((x) => <polygon key={x} points={`${x},1330 ${x + 16},1290 ${x + 32},1330`} fill="#ff8a1f" />)}
        {/* боец */}
        <g transform={`translate(${480 + drift * 0.3},0) rotate(${sway} 0 1250)`}>
          <rect x="-40" y="1100" width="80" height="160" rx="30" fill="#4b6a3c" />
          <rect x="-34" y="1230" width="28" height="100" fill="#3b5430" />
          <rect x="6" y="1230" width="28" height="100" fill="#3b5430" />
          <rect x="-40" y="1320" width="36" height="18" rx="6" fill="#222" />
          <rect x="4" y="1320" width="36" height="18" rx="6" fill="#222" />
          <rect x="30" y="1135" width="120" height="26" rx="12" fill="#4b6a3c" transform="rotate(-10 30 1148)" />
          <rect x="130" y="1100" width="64" height="40" rx="8" fill="#1d2433" />
          <circle cx="0" cy="1060" r="52" fill="#f1c9a0" />
          <path d="M-56 1048 A56 56 0 0 1 56 1048 L56 1038 L-56 1038 Z" fill="#d6283a" />
          <circle cx="-16" cy="1062" r="6" fill="#222" /><circle cx="18" cy="1062" r="6" fill="#222" />
          <rect x="-14" y="1082" width="28" height="7" rx="3" fill="#a5552f" />
        </g>
        </g>
        {/* дрон */}
        <g transform={`translate(${620 + drift},${620 + bob})`}>
          <rect x="-46" y="-10" width="92" height="28" rx="12" fill="#2a2f3a" />
          <rect x="-100" y="-20" width="70" height="6" rx="3" fill="#2a2f3a" />
          <rect x="30" y="-20" width="70" height="6" rx="3" fill="#2a2f3a" />
          <ellipse cx="-65" cy="-24" rx="40" ry="5" fill="#2a2f3a" opacity={0.35 + 0.3 * Math.abs(Math.sin(frame))} />
          <ellipse cx="65" cy="-24" rx="40" ry="5" fill="#2a2f3a" opacity={0.35 + 0.3 * Math.abs(Math.cos(frame))} />
        </g>
      </svg>
      {tag && (
        <div style={{position: 'absolute', top: 70 * k, left: 50 * k, fontFamily: FONT, fontWeight: 800, fontSize: 26 * k,
          color: '#f5c518', background: '#14181fdd', padding: `${10 * k}px ${22 * k}px`, borderRadius: 10 * k,
          letterSpacing: 2, textTransform: 'uppercase'}}>● {tag}</div>
      )}
    </AbsoluteFill>
  );
};
