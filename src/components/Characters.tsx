import React from 'react';
import {AbsoluteFill, useCurrentFrame, useVideoConfig} from 'remotion';
import {FONT} from '../theme';
import {hash, useStep} from './Vhs';
import type {Char} from '../types';

const INK = '#111';
const L = {stroke: INK, strokeWidth: 7, strokeLinejoin: 'round' as const, strokeLinecap: 'round' as const};

/** Неровный контур: общий SVG-фильтр, зерно меняется каждые 2 шага → «кипящая» линия. */
export const Wobble: React.FC<{seed: number}> = ({seed}) => (
  <filter id="wob" x="-5%" y="-5%" width="110%" height="110%">
    <feTurbulence type="fractalNoise" baseFrequency="0.035" numOctaves="2" seed={seed} />
    <feDisplacementMap in="SourceGraphic" scale="7" />
  </filter>
);

const Mouth: React.FC<{open: boolean; y: number}> = ({open, y}) =>
  open ? <ellipse cx="0" cy={y} rx="26" ry="18" fill="#5a1520" {...L} strokeWidth={5} />
       : <path d={`M-26 ${y} Q0 ${y + 10} 26 ${y - 4}`} fill="none" {...L} strokeWidth={5} />;

const Bandit: React.FC<{mood: string; talk: boolean; step: number}> = ({mood, talk, step}) => {
  const open = talk && step % 2 === 0;
  const shock = mood === 'shock';
  return (
    <g>
      {/* ноги в «Abibas» */}
      <rect x="-70" y="330" width="52" height="150" fill="#1d3f8f" {...L} />
      <rect x="18" y="330" width="52" height="150" fill="#1d3f8f" {...L} />
      <rect x="-70" y="330" width="14" height="150" fill="#fff" opacity=".85" />
      <rect x="56" y="330" width="14" height="150" fill="#fff" opacity=".85" />
      <ellipse cx="-50" cy="486" rx="48" ry="20" fill="#eee" {...L} />
      <ellipse cx="50" cy="486" rx="48" ry="20" fill="#eee" {...L} />
      {/* спортивка */}
      <path d="M-120 130 Q-130 330 -90 350 L90 350 Q130 330 120 130 Z" fill="#1d3f8f" {...L} />
      <text x="0" y="334" textAnchor="middle" fontFamily={FONT} fontWeight={900} fontSize="34" fill="#fff" stroke={INK} strokeWidth="1.5">ABIBAS</text>
      {/* малиновый пиджак */}
      <path d="M-120 130 L-30 140 L-40 285 L-112 285 Q-135 220 -120 130 Z" fill="#b0123f" {...L} />
      <path d="M120 130 L30 140 L40 285 L112 285 Q135 220 120 130 Z" fill="#b0123f" {...L} />
      <path d="M-120 130 L-70 150 L-30 140 L-54 205 Z" fill="#8a0d31" {...L} strokeWidth={5} />
      <path d="M120 130 L70 150 L30 140 L54 205 Z" fill="#8a0d31" {...L} strokeWidth={5} />
      {/* цепь */}
      {[-46, -30, -14, 0, 14, 30, 46].map((x, i) => <circle key={x} cx={x} cy={150 + Math.abs(i - 3) * -5 + 24 + (i === 3 ? 18 : 0)} r="9" fill="#e8b923" {...L} strokeWidth={3} />)}
      <circle cx="0" cy="196" r="17" fill="#e8b923" {...L} strokeWidth={4} />
      {/* пейджер на поясе */}
      <rect x="62" y="318" width="40" height="26" rx="4" fill="#222" {...L} strokeWidth={4} />
      <rect x="68" y="323" width="20" height="9" fill="#9bd48a" />
      {/* левая рука с часами */}
      <rect x="-165" y="150" width="46" height="150" rx="22" fill="#b0123f" {...L} transform={`rotate(${shock ? -35 : 6} -142 160)`} />
      <circle cx="-150" cy="305" r="24" fill="#f0b98d" {...L} />
      <rect x="-172" y="286" width="44" height="14" fill="#e8b923" {...L} strokeWidth={4} />
      {/* правая рука: кирпич Motorola */}
      <g transform={`rotate(${shock ? 25 : -4} 140 160)`}>
        <rect x="119" y="150" width="46" height="130" rx="22" fill="#b0123f" {...L} />
        <circle cx="142" cy="288" r="24" fill="#f0b98d" {...L} />
        <rect x="124" y="170" width="46" height="150" rx="8" fill="#2b2b2b" {...L} transform="rotate(14 147 245)" />
        <rect x="148" y="116" width="8" height="70" fill="#2b2b2b" {...L} strokeWidth={4} transform="rotate(14 147 245)" />
        <rect x="134" y="190" width="24" height="30" fill="#8fc77a" transform="rotate(14 147 245)" />
      </g>
      {/* шея и голова: бритая, квадратная челюсть, нос-картошка */}
      <rect x="-30" y="95" width="60" height="50" fill="#e9ad7c" {...L} />
      <path d="M-86 -10 Q-96 -90 0 -96 Q96 -90 86 -10 Q96 50 60 96 Q0 120 -60 96 Q-96 50 -86 -10 Z" fill="#f0b98d" {...L} />
      <path d="M-84 -34 Q0 -70 84 -34 L84 -48 Q0 -100 -84 -48 Z" fill="#3a2a22" {...L} strokeWidth={4} />
      <path d="M-62 -22 L-14 -12" {...L} strokeWidth={9} /><path d="M62 -22 L14 -12" {...L} strokeWidth={9} />
      <circle cx="-34" cy={shock ? -2 : 4} r={shock ? 13 : 8} fill="#fff" {...L} strokeWidth={4} />
      <circle cx="34" cy={shock ? -2 : 4} r={shock ? 13 : 8} fill="#fff" {...L} strokeWidth={4} />
      <circle cx="-34" cy="4" r="4" fill={INK} /><circle cx="34" cy="4" r="4" fill={INK} />
      <path d="M-8 4 Q-30 52 -2 56 Q22 56 8 4" fill="#e59a6a" {...L} strokeWidth={5} />
      <g transform="translate(0,72)"><Mouth open={open || shock} y={0} /></g>
      <rect x="-12" y="86" width="24" height="10" fill="#e8b923" {...L} strokeWidth={3} />
    </g>
  );
};

const Acct: React.FC<{mood: string; talk: boolean; step: number}> = ({mood, talk, step}) => {
  const open = talk && step % 2 === 0;
  const shock = mood === 'shock';
  const drop = (step * 7) % 60;
  return (
    <g>
      <rect x="-48" y="330" width="40" height="150" fill="#3b3b44" {...L} />
      <rect x="8" y="330" width="40" height="150" fill="#3b3b44" {...L} />
      <ellipse cx="-30" cy="486" rx="40" ry="18" fill="#222" {...L} />
      <ellipse cx="30" cy="486" rx="40" ry="18" fill="#222" {...L} />
      {/* свитер Boys, толстый, с орнаментом */}
      <path d="M-105 130 Q-125 300 -85 350 L85 350 Q125 300 105 130 Z" fill="#6a7fa3" {...L} />
      {[170, 215, 260].map((y) => <path key={y} d={`M-100 ${y} L100 ${y}`} stroke="#d9d3b0" strokeWidth="9" opacity=".8" />)}
      <text x="0" y="300" textAnchor="middle" fontFamily={FONT} fontWeight={900} fontSize="40" fill="#fff" stroke={INK} strokeWidth="1.5">Boys</text>
      <path d="M-50 130 Q0 175 50 130" fill="none" {...L} />
      {/* амбарная книга */}
      <g transform={`rotate(${shock ? -12 : -4} 0 250)`}>
        <rect x="-88" y="190" width="176" height="130" fill="#7a5a34" {...L} />
        <rect x="-78" y="198" width="156" height="114" fill="#e9dfbf" />
        {[222, 244, 266, 288].map((y) => <path key={y} d={`M-66 ${y} L66 ${y}`} stroke="#666" strokeWidth="3" />)}
        <path d="M-60 214 L-30 214 M-60 236 L10 236 M-60 258 L-10 258" stroke="#b01212" strokeWidth="5" />
      </g>
      <circle cx="-95" cy="262" r="24" fill="#f0b98d" {...L} /><circle cx="95" cy="262" r="24" fill="#f0b98d" {...L} />
      {/* голова: круглая, лысеющий зачёс, огромные очки */}
      <rect x="-26" y="95" width="52" height="40" fill="#e9ad7c" {...L} />
      <ellipse cx="0" cy="0" rx="88" ry="96" fill="#f3c7a0" {...L} />
      <path d="M-60 -70 Q-10 -110 52 -70 Q10 -88 -60 -70" fill="#5a4636" {...L} strokeWidth={4} />
      <circle cx="-38" cy="2" r="40" fill="#cfe9f2" opacity=".75" {...L} /><circle cx="38" cy="2" r="40" fill="#cfe9f2" opacity=".75" {...L} />
      <path d="M-2 2 L2 2" {...L} />
      <circle cx="-38" cy={shock ? 0 : 6} r={shock ? 9 : 6} fill={INK} /><circle cx="38" cy={shock ? 0 : 6} r={shock ? 9 : 6} fill={INK} />
      <path d="M-4 24 Q-10 52 6 52" fill="none" {...L} strokeWidth={5} />
      <g transform="translate(0,76)"><Mouth open={open || shock} y={0} /></g>
      {/* пот */}
      {[[-78, -50, 0], [80, -30, 20], [-84, 40, 40]].map(([x, y, o], i) => {
        const d = (drop + o) % 60;
        return <path key={i} d="M0 -14 Q10 4 0 12 Q-10 4 0 -14 Z" fill="#8fd3f4" {...L} strokeWidth={3} transform={`translate(${x},${y + d})`} opacity={1 - d / 70} />;
      })}
    </g>
  );
};

export const VhsCharacter: React.FC<{c: Char; speaking: boolean; step: number}> = ({c, speaking, step}) => {
  const bounce = Math.sin(step * 0.9 + c.x) * 6;
  const talk = !!c.talk && speaking;
  const Comp = c.who === 'bandit' ? Bandit : Acct;
  return (
    <g transform={`translate(${c.x},${760 + bounce}) scale(${c.flip ? -1 : 1},1)`}>
      <ellipse cx="0" cy="490" rx="130" ry="22" fill="#000" opacity=".25" />
      <Comp mood={c.mood ?? 'idle'} talk={talk} step={step} />
    </g>
  );
};

const Market: React.FC = () => (
  <g>
    <rect width="1080" height="1920" fill="#8a8f98" />
    <rect y="1250" width="1080" height="670" fill="#5d5a52" />
    {[0, 1, 2, 3, 4, 5].map((i) => <rect key={i} x={i * 190 - 30} y="560" width="170" height="40" fill={i % 2 ? '#c3302f' : '#e9dfc4'} {...L} strokeWidth={5} />)}
    <rect x="40" y="260" width="1000" height="150" fill="#1d3f8f" {...L} />
    <text x="540" y="360" textAnchor="middle" fontFamily={FONT} fontWeight={900} fontSize="76" fill="#ffe500" stroke={INK} strokeWidth="3">ВИДЕО-ПРОКАТ</text>
    {[0, 1, 2, 3, 4].map((i) => <rect key={i} x={50 + i * 200} y="620" width="140" height="250" fill="#444" {...L} strokeWidth={5} />)}
  </g>
);
const Room: React.FC = () => (
  <g>
    <rect width="1080" height="1920" fill="#7b5b46" />
    {Array.from({length: 18}).map((_, i) => <rect key={i} x={i * 64} y="0" width="32" height="1250" fill="#6a4c39" />)}
    <rect y="1250" width="1080" height="670" fill="#4a3a30" />
    <rect x="620" y="520" width="360" height="300" fill="#222" {...L} /><rect x="640" y="540" width="320" height="250" fill="#2d4a47" />
    <rect x="70" y="420" width="360" height="520" fill="#a33a3a" {...L} />
    {[0, 1, 2].map((i) => <path key={i} d={`M70 ${520 + i * 140} L430 ${520 + i * 140}`} stroke="#e6c35a" strokeWidth="10" />)}
  </g>
);

export const VhsScene: React.FC<{bg: 'market' | 'room'; chars: Char[]; speaking: boolean}> = ({bg, chars, speaking}) => {
  const step = useStep(10);
  return (
    <AbsoluteFill>
      <svg viewBox="0 0 1080 1920" width="100%" height="100%" preserveAspectRatio="xMidYMid slice">
        <defs><Wobble seed={Math.floor(step / 2) % 7} /></defs>
        <g filter="url(#wob)">
          {bg === 'market' ? <Market /> : <Room />}
          {chars.map((c, i) => <VhsCharacter key={i} c={c} speaking={speaking} step={step} />)}
        </g>
      </svg>
    </AbsoluteFill>
  );
};
