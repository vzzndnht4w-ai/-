import React from 'react';
import {FONT} from '../theme';
import {hash} from '../components/Vhs';
import type {Char, Mood, Pose} from '../types';

const INK = '#121212';
const L = {stroke: INK, strokeWidth: 7, strokeLinejoin: 'round' as const, strokeLinecap: 'round' as const};
const thin = {...L, strokeWidth: 4};
const SKIN = ['#f0b98d', '#f3c7a0', '#e3a577', '#d99b6c'];

export const Wobble: React.FC<{seed: number}> = ({seed}) => (
  <filter id="wob" x="-5%" y="-5%" width="110%" height="110%">
    <feTurbulence type="fractalNoise" baseFrequency="0.03" numOctaves="2" seed={seed} />
    <feDisplacementMap in="SourceGraphic" scale="8" />
  </filter>
);

/* ---------- двухзвенная рука (IK) ---------- */
type P = [number, number];
function ik(s: P, t: P, l1: number, l2: number, _bend: number): {e: P; h: P} {
  const dx = t[0] - s[0], dy = t[1] - s[1];
  const d = Math.min(Math.hypot(dx, dy), l1 + l2 - 2);
  const a = Math.atan2(dy, dx);
  const cosA = Math.max(-1, Math.min(1, (l1 * l1 + d * d - l2 * l2) / (2 * l1 * d || 1)));
  const A = Math.acos(cosA);
  const side = s[0] < 0 ? -1 : 1;   // левое/правое плечо
  const cand = [A, -A].map((k) => [s[0] + l1 * Math.cos(a + k), s[1] + l1 * Math.sin(a + k)] as P);
  // локоть: ниже линии «плечо–кисть» и наружу от тела
  const score = (e: P) => e[1] + 0.8 * side * e[0];
  const e = score(cand[0]) >= score(cand[1]) ? cand[0] : cand[1];
  return {e, h: [s[0] + d * Math.cos(a), s[1] + d * Math.sin(a)]};
}
const Arm: React.FC<{s: P; t: P; l1: number; l2: number; bend: number; color: string; w?: number; skin: string}> =
  ({s, t, l1, l2, bend, color, w = 50, skin}) => {
    const {e, h} = ik(s, t, l1, l2, bend);
    const d = `M${s[0]} ${s[1]} L${e[0]} ${e[1]} L${h[0]} ${h[1]}`;
    return (
      <g>
        <path d={d} fill="none" stroke={INK} strokeWidth={w + 14} strokeLinecap="round" strokeLinejoin="round" />
        <path d={d} fill="none" stroke={color} strokeWidth={w} strokeLinecap="round" strokeLinejoin="round" />
        <circle cx={h[0]} cy={h[1]} r={w * 0.52} fill={skin} {...thin} />
      </g>
    );
  };

/* ---------- лицо ---------- */
const BROWS: Record<Mood, [number, number, number, number]> = { // угол левой, угол правой, подъём левой, подъём правой
  neutral: [0, 0, 0, 0], angry: [20, -20, 6, 6], smug: [0, -8, 0, 16],
  shock: [-6, 6, -22, -22], sad: [-16, 16, -4, -4], sweat: [-10, 10, -12, -12],
};
const MOUTHS = ['A', 'O', 'E', 'A', 'M', 'E'];

const Mouth: React.FC<{mood: Mood; talk: boolean; step: number; tooth?: boolean; w?: number}> = ({mood, talk, step, tooth, w = 30}) => {
  let shape = 'rest';
  if (talk) shape = MOUTHS[Math.floor(hash(step) * MOUTHS.length)];
  else if (mood === 'shock') shape = 'BIG';
  const fillM = '#4a0f1a';
  switch (shape) {
    case 'A': return <g><ellipse cx="0" cy="6" rx={w} ry="22" fill={fillM} {...thin} /><rect x={-w + 8} y="-14" width={2 * w - 16} height="10" fill="#f6f0dc" /></g>;
    case 'O': return <ellipse cx="0" cy="6" rx={w * 0.5} ry="20" fill={fillM} {...thin} />;
    case 'E': return <g><path d={`M${-w} 0 Q0 22 ${w} 0 Q0 -6 ${-w} 0Z`} fill={fillM} {...thin} /><rect x={-w + 6} y="-2" width={2 * w - 12} height="7" fill="#f6f0dc" /></g>;
    case 'M': return <path d={`M${-w} 4 Q0 10 ${w} 4`} fill="none" {...L} strokeWidth={6} />;
    case 'BIG': return <ellipse cx="0" cy="12" rx={w * 0.7} ry="34" fill={fillM} {...thin} />;
  }
  if (mood === 'angry') return <g><path d={`M${-w} 12 Q0 -6 ${w} 12`} fill="none" {...L} strokeWidth={6} /><rect x={-w * 0.6} y="2" width={w * 1.2} height="9" fill="#f6f0dc" stroke={INK} strokeWidth="3" /></g>;
  if (mood === 'smug') return <g><path d={`M${-w} 6 Q0 24 ${w} -8`} fill="none" {...L} strokeWidth={6} />{tooth && <rect x={w * 0.35} y="2" width="9" height="13" fill="#f2c230" stroke={INK} strokeWidth="2.5" />}</g>;
  if (mood === 'sad') return <path d={`M${-w} 14 Q0 -8 ${w} 14`} fill="none" {...L} strokeWidth={6} />;
  if (mood === 'sweat') return <path d={`M${-w} 6 Q${-w / 2} -4 0 6 Q${w / 2} 16 ${w} 6`} fill="none" {...L} strokeWidth={6} />;
  return <path d={`M${-w} 6 L${w} 6`} fill="none" {...L} strokeWidth={6} />;
};

const Eyes: React.FC<{mood: Mood; step: number; r: number; gap: number; dx: number; big?: boolean}> = ({mood, step, r, gap, dx, big}) => {
  const blink = step % 29 === 0;
  const R = mood === 'shock' ? r * 1.35 : r;
  return (
    <g>
      {[-gap, gap].map((x, i) => blink
        ? <path key={i} d={`M${x - R} 2 L${x + R} 2`} {...L} strokeWidth={6} />
        : <g key={i}><circle cx={x} cy="0" r={R} fill="#fff" {...thin} />
            <circle cx={x + dx} cy="2" r={mood === 'shock' ? R * 0.3 : R * 0.45} fill={INK} />
            <circle cx={x + dx - 2} cy="-2" r={R * 0.14} fill="#fff" /></g>)}
    </g>
  );
};

const Brows: React.FC<{mood: Mood; gap: number; y: number; w: number; thick?: number; uni?: boolean}> = ({mood, gap, y, w, thick = 11, uni}) => {
  const [al, ar, rl, rr] = BROWS[mood];
  return (
    <g>
      <path d={`M${-gap - w} ${y + rl} L${-gap + w} ${y + rl}`} {...L} strokeWidth={thick} transform={`rotate(${al} ${-gap} ${y + rl})`} />
      <path d={`M${gap - w} ${y + rr} L${gap + w} ${y + rr}`} {...L} strokeWidth={thick} transform={`rotate(${ar} ${gap} ${y + rr})`} />
      {uni && <path d={`M${-gap + w - 4} ${y + rl + 2} L${gap - w + 4} ${y + rr + 2}`} {...L} strokeWidth={thick - 2} />}
    </g>
  );
};

const Sweat: React.FC<{step: number; pts: P[]}> = ({step, pts}) => (
  <g>{pts.map(([x, y], i) => {
    const d = ((step * 6 + i * 22) % 70);
    return <path key={i} d="M0 -18 Q13 6 0 16 Q-13 6 0 -18Z" fill="#8fd3f4" {...thin} strokeWidth={3} transform={`translate(${x},${y + d})`} opacity={Math.max(0, 1 - d / 75)} />;
  })}</g>
);

/* ---------- предметы ---------- */
const Jar: React.FC = () => (
  <g>
    <rect x="-70" y="-110" width="140" height="215" rx="22" fill="#cfe8dd" opacity=".55" {...L} />
    {[0, 1, 2, 3, 4].map((i) => <g key={i} transform={`translate(${(i % 2) * 8 - 4},${72 - i * 34}) rotate(${i % 2 ? 3 : -3})`}>
      <rect x="-56" y="-12" width="112" height="30" fill="#6fa86a" stroke={INK} strokeWidth="3" /><circle cx="0" cy="3" r="9" fill="#9cc98f" /></g>)}
    <rect x="-78" y="-132" width="156" height="30" rx="8" fill="#9a9a9a" {...L} />
    <rect x="-56" y="-30" width="112" height="44" fill="#fff5c2" stroke={INK} strokeWidth="4" />
    <text x="0" y="3" textAnchor="middle" fontFamily={FONT} fontWeight={900} fontSize="30" fill="#b01212">ОБЩАК</text>
  </g>
);
const Phone: React.FC = () => (
  <g><rect x="-22" y="-80" width="46" height="170" rx="9" fill="#2b2b2b" {...L} /><rect x="-12" y="-52" width="26" height="40" fill="#8fc77a" />
    {[0, 1, 2].map((r) => [0, 1, 2].map((c) => <rect key={r + '' + c} x={-14 + c * 11} y={0 + r * 14} width="8" height="9" fill="#777" />))}
    <rect x="-6" y="-138" width="9" height="62" fill="#2b2b2b" {...L} strokeWidth={4} />
    <text x="1" y="84" textAnchor="middle" fontFamily={FONT} fontWeight={900} fontSize="13" fill="#bbb">MOTOROLA?</text></g>
);
const Ledger: React.FC = () => (
  <g><rect x="-100" y="-62" width="200" height="130" fill="#7a5a34" {...L} />
    <rect x="-92" y="-54" width="90" height="112" fill="#efe6c8" /><rect x="2" y="-54" width="90" height="112" fill="#efe6c8" />
    {[-30, -8, 14, 36].map((y) => <g key={y}><path d={`M-84 ${y} L-10 ${y}`} stroke="#777" strokeWidth="3" /><path d={`M10 ${y} L84 ${y}`} stroke="#777" strokeWidth="3" /></g>)}
    <path d="M-80 -34 L-34 -34 M-80 -12 L-20 -12 M16 -34 L64 -34" stroke="#c01515" strokeWidth="5" /></g>
);

/* ---------- позы: куда тянутся руки (относительно центра головы) ---------- */
const POSES: Record<string, {l: P; r: P; item?: 'jar' | 'phone' | 'ledger'; at?: P; itemHand?: 'l' | 'r'}> = {
  idle: {l: [-150, 380], r: [150, 380]},
  crossed: {l: [70, 285], r: [-70, 285]},
  jar: {l: [-70, 290], r: [70, 290], item: 'jar', at: [0, 255]},
  point: {l: [-150, 380], r: [300, 90]},
  shrug: {l: [-250, 215], r: [250, 215]},
  phone: {l: [-150, 380], r: [100, 0], item: 'phone', at: [112, 20], itemHand: 'r'},
  fist: {l: [-150, 330], r: [225, 70]},
  book: {l: [-72, 300], r: [72, 295], item: 'ledger', at: [0, 285]},
  panic: {l: [-92, 45], r: [92, 45]},
};

/* ---------- персонажи ---------- */
type Props = {c: Char; talk: boolean; step: number};

const Zhora: React.FC<Props & {pal?: {jacket: string; dark: string; hair?: string; skin?: number; cap?: boolean}}> = ({c, talk, step, pal = {jacket: '#b0123f', dark: '#860d30', hair: '#2a211c', skin: 0}}) => {
  const mood = c.mood ?? 'neutral', pose = POSES[c.pose ?? 'idle'] ?? POSES.idle;
  const skin = SKIN[pal.skin ?? 0];
  const tilt = mood === 'angry' ? -4 : mood === 'sad' ? 7 : mood === 'smug' ? 3 : 0;
  const bob = talk && step % 2 === 0 ? -7 : 0;
  const itemEl = pose.item === 'jar' ? <Jar /> : pose.item === 'phone' ? <Phone /> : pose.item === 'ledger' ? <Ledger /> : null;
  const idlePhone = !pose.item;
  return (
    <g>
      {/* ноги */}
      <rect x="-82" y="400" width="66" height="190" fill="#1d3f8f" {...L} /><rect x="16" y="400" width="66" height="190" fill="#1d3f8f" {...L} />
      <rect x="-82" y="400" width="16" height="190" fill="#f4f0e0" opacity=".9" /><rect x="66" y="400" width="16" height="190" fill="#f4f0e0" opacity=".9" />
      <path d="M-98 592 Q-90 556 -26 574 L-16 616 L-102 616Z" fill="#eaeaea" {...L} /><path d="M98 592 Q90 556 26 574 L16 616 L102 616Z" fill="#eaeaea" {...L} />
      {/* спортивка + надпись */}
      <path d="M-120 130 Q-140 330 -104 420 L104 420 Q140 330 120 130Z" fill="#1d3f8f" {...L} />
      <path d="M0 150 L0 400" stroke="#0e2a66" strokeWidth="6" />
      <text x="0" y="388" textAnchor="middle" fontFamily={FONT} fontWeight={900} fontSize="36" fill="#fff" stroke={INK} strokeWidth="1.5">ABIBAS</text>
      {/* малиновый пиджак с накладными плечами */}
      <path d="M-128 128 L-34 142 L-46 318 L-122 318 Q-150 220 -128 128Z" fill={pal.jacket} {...L} />
      <path d="M128 128 L34 142 L46 318 L122 318 Q150 220 128 128Z" fill={pal.jacket} {...L} />
      <path d="M-128 128 L-76 154 L-34 142 L-60 232Z" fill={pal.dark} {...L} strokeWidth={5} /><path d="M128 128 L76 154 L34 142 L60 232Z" fill={pal.dark} {...L} strokeWidth={5} />
      {/* цепь */}
      <path d="M-52 150 Q0 235 52 150" fill="none" stroke="#e8b923" strokeWidth="14" /><path d="M-52 150 Q0 235 52 150" fill="none" stroke={INK} strokeWidth="3" strokeDasharray="10 9" />
      <circle cx="0" cy="208" r="20" fill="#e8b923" {...thin} /><text x="0" y="216" textAnchor="middle" fontSize="22" fontFamily={FONT} fontWeight={900} fill={INK}>$</text>
      {/* пейджер */}
      <rect x="72" y="344" width="44" height="30" rx="5" fill="#222" {...thin} /><rect x="78" y="350" width="22" height="10" fill="#9bd48a" />
      {/* руки */}
      <Arm s={[-100, 150]} t={pose.l} l1={130} l2={125} bend={-1} color={pal.jacket} skin={skin} />
      <Arm s={[100, 150]} t={pose.r} l1={130} l2={125} bend={1} color={pal.jacket} skin={skin} />
      {/* золотые часы на левой руке */}
      <rect x={pose.l[0] - 28} y={pose.l[1] - 52} width="46" height="14" fill="#e8b923" {...thin} strokeWidth={3} />
      {itemEl && pose.at && <g transform={`translate(${pose.at[0]},${pose.at[1]}) scale(${pose.item === 'jar' ? 0.95 : pose.item === 'ledger' ? 0.8 : 0.85})`}>{itemEl}</g>}
      {idlePhone && <g transform={`translate(${pose.r[0] + 22},${pose.r[1] - 40}) rotate(12) scale(.7)`}><Phone /></g>}
      {/* шея, голова */}
      <rect x="-40" y="86" width="80" height="62" fill={skin} {...L} />
      <g transform={`translate(0,${bob}) rotate(${tilt} 0 100)`}>
        <path d="M-104 -14 Q-110 -112 0 -118 Q110 -112 104 -14 Q112 52 78 104 Q0 138 -78 104 Q-112 52 -104 -14Z" fill={skin} {...L} />
        <ellipse cx="-106" cy="14" rx="18" ry="28" fill={skin} {...L} /><ellipse cx="106" cy="14" rx="18" ry="28" fill={skin} {...L} />
        {pal.cap
          ? <g><path d="M-108 -34 Q0 -150 108 -34 L108 -14 L-108 -14Z" fill="#222" {...L} /><rect x="-60" y="-40" width="170" height="16" rx="6" fill="#222" {...L} /></g>
          : <path d="M-100 -40 Q0 -92 100 -40 L98 -70 Q0 -130 -98 -70Z" fill={pal.hair ?? '#2a211c'} {...L} strokeWidth={5} />}
        {[[-60, 60], [-40, 80], [40, 80], [60, 60], [-20, 92], [20, 92], [0, 70]].map(([x, y], i) => <circle key={i} cx={x} cy={y} r="2.8" fill={INK} opacity=".55" />)}
        <path d="M60 30 L84 78" {...L} strokeWidth={5} />
        <g transform="translate(0,-4)">
          <Brows mood={mood} gap={42} y={-26} w={32} thick={13} uni />
          <g transform="translate(0,6)"><Eyes mood={mood} step={step} r={14} gap={42} dx={c.flip ? -3 : 3} /></g>
          <path d="M-8 6 Q-34 58 -4 66 Q8 70 22 62 Q40 54 8 6" fill="#e59a6a" {...L} strokeWidth={5} />
          <circle cx="-12" cy="62" r="3.5" fill={INK} /><circle cx="14" cy="62" r="3.5" fill={INK} />
          <g transform="translate(0,92)"><Mouth mood={mood} talk={talk} step={step} tooth w={34} /></g>
        </g>
        {mood === 'sweat' && <Sweat step={step} pts={[[-90, -50], [92, -30]]} />}
      </g>
    </g>
  );
};

const THUG_PALS = [
  {jacket: '#1f7a4a', dark: '#14573a', hair: '#3a2a1a', skin: 1},
  {jacket: '#6a2a8a', dark: '#4a1b63', cap: true, skin: 2},
  {jacket: '#a8661c', dark: '#7a4812', hair: '#1a1a1a', skin: 0},
  {jacket: '#b0123f', dark: '#860d30', hair: '#6a4a2a', skin: 3},
];

const Gena: React.FC<Props> = ({c, talk, step}) => {
  const mood = c.mood ?? 'neutral', pose = POSES[c.pose ?? 'book'] ?? POSES.book;
  const skin = SKIN[1];
  const tilt = mood === 'sad' ? 8 : mood === 'sweat' ? -3 : 0;
  const bob = talk && step % 2 === 0 ? -6 : 0;
  const tremble = mood === 'sweat' ? (step % 2 ? 2.5 : -2.5) : 0;
  const itemEl = pose.item === 'ledger' ? <Ledger /> : null;
  return (
    <g transform={`translate(${tremble},0)`}>
      <rect x="-58" y="400" width="48" height="190" fill="#3b3b44" {...L} /><rect x="10" y="400" width="48" height="190" fill="#3b3b44" {...L} />
      <path d="M-70 592 Q-64 560 -14 574 L-8 612 L-74 612Z" fill="#222" {...L} /><path d="M70 592 Q64 560 14 574 L8 612 L74 612Z" fill="#222" {...L} />
      {/* свитер Boys */}
      <path d="M-100 135 Q-132 300 -92 420 L92 420 Q132 300 100 135Z" fill="#6a7fa3" {...L} />
      {[190, 236, 282].map((y) => <path key={y} d={`M-110 ${y} L110 ${y}`} stroke="#e6dfb8" strokeWidth="10" opacity=".85" />)}
      {[-60, -20, 20, 60].map((x) => <path key={x} d={`M${x} 160 L${x} 410`} stroke="#4f6285" strokeWidth="4" opacity=".7" />)}
      <path d="M-54 132 Q0 190 54 132" fill="#566a8c" {...L} />
      <rect x="-60" y="330" width="120" height="50" rx="8" fill="#e8e0c0" opacity=".92" stroke={INK} strokeWidth="4" />
      <text x="0" y="368" textAnchor="middle" fontFamily={FONT} fontWeight={900} fontSize="38" fill="#c01515" stroke={INK} strokeWidth="1">Boys</text>
      <Arm s={[-88, 152]} t={pose.l} l1={125} l2={120} bend={-1} color="#6a7fa3" skin={skin} w={46} />
      <Arm s={[88, 152]} t={pose.r} l1={125} l2={120} bend={1} color="#6a7fa3" skin={skin} w={46} />
      {itemEl && pose.at && <g transform={`translate(${pose.at[0]},${pose.at[1]}) scale(.95)`}>{itemEl}</g>}
      <rect x="-34" y="92" width="68" height="52" fill={skin} {...L} />
      <g transform={`translate(0,${bob}) rotate(${tilt} 0 100)`}>
        <ellipse cx="0" cy="0" rx="96" ry="106" fill={skin} {...L} />
        <ellipse cx="-98" cy="6" rx="20" ry="30" fill={skin} {...L} /><ellipse cx="98" cy="6" rx="20" ry="30" fill={skin} {...L} />
        {/* плешь с зачёсом */}
        <path d="M-70 -82 Q-20 -126 60 -86" fill="none" {...L} strokeWidth={5} />
        {[-58, -34, -10, 14, 38].map((x, i) => <path key={x} d={`M${x} ${-92 + Math.abs(x) * 0.12} Q${x + 18} ${-114 + i * 2} ${x + 44} ${-90 + i * 3}`} fill="none" stroke="#4a3a2e" strokeWidth="5" strokeLinecap="round" />)}
        <path d="M-92 -20 L-98 -50 M92 -20 L98 -50" {...thin} />
        <g transform="translate(0,-2)">
          <Brows mood={mood} gap={44} y={-60} w={26} thick={9} />
          {/* огромные очки с бликами; глаза «увеличены» */}
          <circle cx="-44" cy="4" r="50" fill="#d8eef6" opacity=".78" {...L} /><circle cx="44" cy="4" r="50" fill="#d8eef6" opacity=".78" {...L} />
          <path d="M-6 4 Q0 -6 6 4" fill="none" {...L} />
          <path d="M-90 -6 L-100 -14 M90 -6 L100 -14" {...L} />
          <g transform="translate(0,4)"><Eyes mood={mood} step={step} r={19} gap={44} dx={c.flip ? -4 : 4} /></g>
          <path d="M-70 -16 Q-60 -34 -40 -34" fill="none" stroke="#fff" strokeWidth="6" strokeLinecap="round" opacity=".85" />
          <path d="M-6 52 Q-16 78 6 78" fill="none" {...L} strokeWidth={5} />
          <g transform="translate(0,96)"><Mouth mood={mood} talk={talk} step={step} w={30} />
            <rect x="-14" y="-8" width="14" height="22" fill="#f6f0dc" stroke={INK} strokeWidth="3" /><rect x="2" y="-8" width="14" height="22" fill="#f6f0dc" stroke={INK} strokeWidth="3" /></g>
        </g>
        <path d="M70 -60 L76 -30" stroke="#444" strokeWidth="5" /><rect x="58" y="-92" width="14" height="46" rx="5" fill="#1d3f8f" {...thin} transform="rotate(14 65 -70)" />
        {(mood === 'sweat' || mood === 'sad') && <Sweat step={step} pts={[[-100, -40], [104, -20], [-108, 40]]} />}
      </g>
    </g>
  );
};

export const FEET = 620;
export const Character: React.FC<{c: Char; speaking: boolean; step: number}> = ({c, speaking, step}) => {
  const talk = !!c.talk && speaking;
  const s = c.scale ?? 1.25;
  const y = c.y ?? 1290;
  const breathe = Math.sin(step * 0.45 + c.x) * 5;
  const squash = talk && step % 2 === 0 ? 1.025 : 1;
  const props = {c, talk, step};
  let body: React.ReactNode;
  if (c.who === 'zhora') body = <Zhora {...props} />;
  else if (c.who === 'gena') body = <Gena {...props} />;
  else body = <Zhora {...props} pal={THUG_PALS[(c.variant ?? 0) % THUG_PALS.length]} />;
  return (
    <g transform={`translate(${c.x},${y - FEET * s + breathe}) scale(${(c.flip ? -1 : 1) * s},${s * squash})`}>
      <ellipse cx="0" cy={FEET + 4} rx="150" ry="24" fill="#000" opacity=".28" />
      {body}
    </g>
  );
};
