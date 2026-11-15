import React from 'react';
import {FONT} from '../theme';

type P = [number, number];
const clamp = (v: number, a: number, b: number) => Math.max(a, Math.min(b, v));

/** Двухзвенная рука: локоть всегда ниже линии плечо–кисть и наружу от тела. */
export function arm(s: P, t: P, l1: number, l2: number): {e: P; h: P} {
  const dx = t[0] - s[0], dy = t[1] - s[1];
  const d = Math.min(Math.hypot(dx, dy), l1 + l2 - 2);
  const a = Math.atan2(dy, dx);
  const A = Math.acos(clamp((l1 * l1 + d * d - l2 * l2) / (2 * l1 * d || 1), -1, 1));
  const side = s[0] < 0 ? -1 : 1;
  const c = [A, -A].map((k) => [s[0] + l1 * Math.cos(a + k), s[1] + l1 * Math.sin(a + k)] as P);
  const sc = (e: P) => e[1] + 0.25 * side * e[0];
  return {e: sc(c[0]) >= sc(c[1]) ? c[0] : c[1], h: [s[0] + d * Math.cos(a), s[1] + d * Math.sin(a)]};
}

const shade = (hex: string, k: number) => {
  const n = parseInt(hex.slice(1), 16);
  const f = (v: number) => clamp(Math.round(v * k), 0, 255);
  return `#${[(n >> 16) & 255, (n >> 8) & 255, n & 255].map((v) => f(v).toString(16).padStart(2, '0')).join('')}`;
};

export type Look = {
  skin: string; hair: string; top: string; inner: string; pants: string; shoes?: string;
  style: 'short' | 'bun' | 'messy' | 'cap'; width?: number; stubble?: boolean; glasses?: boolean;
};
export type Mood = 'tired' | 'fear' | 'stern' | 'sad' | 'blank';
export type Pose = 'stand' | 'notebook' | 'mouth' | 'hug' | 'wall';

const POSES: Record<Pose, {l: P; r: P; item?: 'notebook'}> = {
  stand: {l: [-118, 392], r: [118, 392]},
  notebook: {l: [-44, 286], r: [50, 292], item: 'notebook'},
  mouth: {l: [-110, 372], r: [26, 96]},
  hug: {l: [66, 258], r: [-66, 262]},
  wall: {l: [-118, 392], r: [118, 392]},
};

/** Плоский персонаж: без контура, объём — градиентами и тёмной стороной, как в референсе. */
export const Person: React.FC<{id: string; look: Look; mood?: Mood; pose?: Pose; lookX?: number; flip?: boolean;
  x: number; y: number; scale?: number; lightSide?: 1 | -1}> = ({id, look, mood = 'tired', pose = 'stand', lookX = 0, flip, x, y, scale = 1, lightSide = 1}) => {
  const w = look.width ?? 1, ps = POSES[pose];
  const Lg = (n: string, c: string) => (
    <linearGradient id={`${id}-${n}`} x1={lightSide === 1 ? 1 : 0} y1="0" x2={lightSide === 1 ? 0 : 1} y2="0">
      <stop offset="0" stopColor={shade(c, 1.28)} /><stop offset=".35" stopColor={c} /><stop offset="1" stopColor={shade(c, 0.5)} />
    </linearGradient>);
  const Sleeve = ({s, t}: {s: P; t: P}) => {
    const {e, h} = arm(s, t, 112, 104);
    const d = `M${s[0]} ${s[1]} L${e[0]} ${e[1]} L${h[0]} ${h[1]}`;
    return <g><path d={d} fill="none" stroke={shade(look.top, 0.55)} strokeWidth="52" strokeLinecap="round" strokeLinejoin="round" />
      <path d={d} fill="none" stroke={`url(#${id}-top)`} strokeWidth="46" strokeLinecap="round" strokeLinejoin="round" />
      <circle cx={h[0]} cy={h[1]} r="22" fill={look.skin} /><circle cx={h[0]} cy={h[1]} r="22" fill={shade(look.skin, 0.8)} opacity=".25" /></g>;
  };
  const browY: Record<Mood, [number, number]> = {tired: [-3, 3], fear: [-14, -14], stern: [5, -5].map((v) => v) as [number, number], sad: [-6, 6], blank: [0, 0]};
  const [bl, br] = browY[mood];
  const eyeR = mood === 'fear' ? 12 : 9;
  const mouth = mood === 'fear' ? <ellipse cx="0" cy="92" rx="13" ry="16" fill="#2a1414" />
    : mood === 'sad' ? <path d="M-18 98 Q0 84 18 98" fill="none" stroke="#3a1c1c" strokeWidth="5" strokeLinecap="round" />
    : <path d="M-16 94 L16 94" fill="none" stroke="#3a1c1c" strokeWidth="5" strokeLinecap="round" />;
  return (
    <g transform={`translate(${x},${y}) scale(${(flip ? -1 : 1) * scale},${scale})`}>
      <defs>{Lg('top', look.top)}{Lg('pants', look.pants)}{Lg('in', look.inner)}
        <radialGradient id={`${id}-face`} cx={lightSide === 1 ? 0.65 : 0.35} cy=".4" r=".75"><stop offset="0" stopColor={shade(look.skin, 1.12)} /><stop offset=".6" stopColor={look.skin} /><stop offset="1" stopColor={shade(look.skin, 0.55)} /></radialGradient></defs>
      <ellipse cx="0" cy="612" rx={140 * w} ry="20" fill="#000" opacity=".4" />
      {/* ноги */}
      <rect x={-70 * w} y="405" width={56 * w} height="195" rx="18" fill={`url(#${id}-pants)`} /><rect x={14 * w} y="405" width={56 * w} height="195" rx="18" fill={`url(#${id}-pants)`} />
      <path d={`M${-80 * w} 600 Q${-70 * w} 578 ${-14 * w} 584 L${-12 * w} 612 L${-84 * w} 612Z`} fill={look.shoes ?? '#15171b'} /><path d={`M${80 * w} 600 Q${70 * w} 578 ${14 * w} 584 L${12 * w} 612 L${84 * w} 612Z`} fill={look.shoes ?? '#15171b'} />
      {/* торс */}
      <path d={`M${-104 * w} 128 Q${-118 * w} 300 ${-96 * w} 420 L${96 * w} 420 Q${118 * w} 300 ${104 * w} 128 Q0 100 ${-104 * w} 128Z`} fill={`url(#${id}-top)`} />
      <path d={`M${-34 * w} 126 L${34 * w} 126 L${28 * w} 420 L${-28 * w} 420Z`} fill={`url(#${id}-in)`} />
      <path d={`M${-34 * w} 126 L${-28 * w} 420`} stroke={shade(look.top, 0.45)} strokeWidth="5" /><path d={`M${34 * w} 126 L${28 * w} 420`} stroke={shade(look.top, 0.45)} strokeWidth="5" />
      <path d={`M${-70 * w} 200 Q${-80 * w} 300 ${-66 * w} 380`} fill="none" stroke={shade(look.top, 0.55)} strokeWidth="6" opacity=".6" />
      {/* руки */}
      {pose !== 'mouth' && <><Sleeve s={[-98 * w, 150]} t={ps.l} /><Sleeve s={[98 * w, 150]} t={ps.r} /></>}
      {pose === 'mouth' && <Sleeve s={[-98 * w, 150]} t={ps.l} />}
      {ps.item === 'notebook' && <g transform="translate(0,292) rotate(-4)"><rect x="-52" y="-40" width="104" height="80" rx="6" fill="#1f3b2d" /><rect x="-52" y="-40" width="104" height="80" rx="6" fill="none" stroke="#0e1d16" strokeWidth="4" /><path d="M-44 -22 H44 M-44 -2 H44 M-44 18 H30" stroke="#8fb39d" strokeWidth="3" opacity=".6" /></g>}
      {/* голова */}
      <rect x="-26" y="86" width="52" height="56" fill={shade(look.skin, 0.75)} />
      <ellipse cx="0" cy="30" rx="78" ry="92" fill={`url(#${id}-face)`} />
      <ellipse cx={-80} cy="38" rx="13" ry="22" fill={shade(look.skin, 0.9)} /><ellipse cx="80" cy="38" rx="13" ry="22" fill={shade(look.skin, 0.9)} />
      {look.stubble && <path d="M-60 62 Q0 150 60 62 Q40 118 0 124 Q-40 118 -60 62Z" fill="#1a1512" opacity=".28" />}
      {look.style === 'short' && <path d="M-80 18 Q-84 -78 0 -82 Q84 -78 80 18 Q70 -30 0 -34 Q-70 -30 -80 18Z" fill={look.hair} />}
      {look.style === 'messy' && <path d="M-82 20 Q-92 -84 -10 -88 Q70 -92 82 20 Q74 -40 30 -34 Q10 -52 -20 -34 Q-60 -40 -82 20Z" fill={look.hair} />}
      {look.style === 'bun' && <g><path d="M-80 20 Q-86 -78 0 -84 Q86 -78 80 20 Q64 -26 0 -30 Q-64 -26 -80 20Z" fill={look.hair} /><circle cx="0" cy="-96" r="30" fill={look.hair} /></g>}
      {look.style === 'cap' && <path d="M-82 8 Q-80 -86 0 -88 Q80 -86 82 8Z" fill={look.hair} />}
      <g transform={`translate(${lookX},0)`}>
        <path d={`M-52 ${-2 + bl} L-14 ${-6 + bl}`} stroke={look.hair} strokeWidth="9" strokeLinecap="round" transform={mood === 'stern' ? 'rotate(10 -30 0)' : undefined} />
        <path d={`M52 ${-2 + br} L14 ${-6 + br}`} stroke={look.hair} strokeWidth="9" strokeLinecap="round" transform={mood === 'stern' ? 'rotate(-10 30 0)' : undefined} />
        {[-32, 32].map((ex) => <g key={ex}><ellipse cx={ex} cy="22" rx={eyeR + 6} ry={eyeR + 2} fill="#e9e6df" /><circle cx={ex + lookX * 0.4} cy="24" r={eyeR - 3} fill="#16181c" /></g>)}
        {mood === 'tired' && [-32, 32].map((ex) => <path key={ex} d={`M${ex - 18} 38 Q${ex} 46 ${ex + 18} 38`} fill="none" stroke={shade(look.skin, 0.62)} strokeWidth="6" strokeLinecap="round" opacity=".7" />)}
        <path d="M0 30 L-6 62 L8 64" fill="none" stroke={shade(look.skin, 0.62)} strokeWidth="5" strokeLinecap="round" strokeLinejoin="round" />
        {mouth}
        {look.glasses && <g fill="none" stroke="#111" strokeWidth="5"><circle cx="-32" cy="22" r="26" /><circle cx="32" cy="22" r="26" /><path d="M-6 22 H6" /></g>}
      </g>
      {pose === 'mouth' && <Sleeve s={[98 * w, 150]} t={ps.r} />}
    </g>
  );
};

/** Комната с окном во двор: стена с обоями, подоконник, штора, торшер, свет и тьма. */
export const RoomWindow: React.FC<{open?: boolean}> = ({open}) => (
  <g>
    <defs>
      <linearGradient id="wall" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stopColor="#3b4a4f" /><stop offset="1" stopColor="#2a363a" /></linearGradient>
      <linearGradient id="night" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stopColor="#0c1524" /><stop offset="1" stopColor="#233a52" /></linearGradient>
      <linearGradient id="floor" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stopColor="#3a2a22" /><stop offset="1" stopColor="#1a120f" /></linearGradient>
      <linearGradient id="curt" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stopColor="#5a3d33" /><stop offset=".25" stopColor="#7a5547" /><stop offset=".5" stopColor="#4d3329" /><stop offset=".75" stopColor="#74503f" /><stop offset="1" stopColor="#3f2a22" /></linearGradient>
      <radialGradient id="lampglow" cx=".5" cy=".5" r=".5"><stop offset="0" stopColor="#ffd58a" stopOpacity=".9" /><stop offset=".4" stopColor="#e09a4a" stopOpacity=".32" /><stop offset="1" stopColor="#e09a4a" stopOpacity="0" /></radialGradient>
      <radialGradient id="lamp2" cx=".5" cy=".5" r=".5"><stop offset="0" stopColor="#ffe6b0" stopOpacity=".55" /><stop offset="1" stopColor="#ffe6b0" stopOpacity="0" /></radialGradient>
      <linearGradient id="moonpatch" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stopColor="#7fa3c9" stopOpacity=".34" /><stop offset="1" stopColor="#7fa3c9" stopOpacity="0" /></linearGradient>
      <pattern id="paper" width="90" height="120" patternUnits="userSpaceOnUse"><rect width="90" height="120" fill="none" /><path d="M0 0 V120" stroke="#000" strokeOpacity=".08" strokeWidth="6" /><path d="M45 20 l8 14 l-8 14 l-8 -14Z M45 80 l8 14 l-8 14 l-8 -14Z" fill="#000" opacity=".07" /></pattern>
      <clipPath id="glass"><rect x="262" y="330" width="556" height="560" /></clipPath>
    </defs>
    <rect width="1080" height="1920" fill="url(#wall)" /><rect width="1080" height="1920" fill="url(#paper)" />
    <rect y="1230" width="1080" height="690" fill="url(#floor)" />
    {[0, 1, 2, 3, 4, 5, 6].map((i) => <path key={i} d={`M${-200 + i * 260} 1920 L${380 + i * 50} 1230`} stroke="#000" strokeOpacity=".28" strokeWidth="4" />)}
    <rect y="1190" width="1080" height="46" fill="#1d2326" /><rect y="1186" width="1080" height="6" fill="#4a575b" />
    <rect x="0" y="880" width="1080" height="310" fill="#000" opacity=".1" />
    {/* окно */}
    <rect x="236" y="304" width="608" height="612" fill="#aab1ad" /><rect x="236" y="304" width="608" height="612" fill="#000" opacity=".25" />
    <g clipPath="url(#glass)">
      <rect x="262" y="330" width="556" height="560" fill="url(#night)" />
      <path d="M262 760 L262 560 L350 560 L350 520 L470 520 L470 600 L560 600 L560 480 L690 480 L690 570 L818 570 L818 760Z" fill="#0b121c" />
      {[[300, 600], [330, 660], [500, 560], [520, 640], [600, 530], [640, 600], [740, 610], [770, 680], [420, 700], [610, 690]].map(([x, y], i) => <rect key={i} x={x} y={y} width="22" height="30" fill={i % 3 ? '#e5b365' : '#8fb4d6'} opacity={i % 4 === 0 ? 0.35 : 0.85} />)}
      <rect x="262" y="760" width="556" height="130" fill="#070d15" />
      <path d="M262 892 Q330 800 380 880 Q430 780 470 890 Q540 790 600 890 Q660 800 720 890 Q780 780 818 892Z" fill="#0a1018" />
      <path d="M300 340 Q360 420 330 520 M780 330 Q740 440 770 540" stroke="#0a0f16" strokeWidth="9" fill="none" />
      <circle cx="700" cy="410" r="60" fill="url(#lamp2)" /><circle cx="700" cy="410" r="9" fill="#ffe6b0" />
      {open && <rect x="262" y="330" width="556" height="560" fill="#2c4a6a" opacity=".18" />}
    </g>
    <path d="M540 330 V890 M262 610 H818" stroke="#aab1ad" strokeWidth="14" /><path d="M540 330 V890 M262 610 H818" stroke="#000" strokeWidth="14" opacity=".25" />
    <rect x="236" y="304" width="608" height="612" fill="none" stroke="#c9cfca" strokeWidth="10" opacity=".7" />
    <rect x="210" y="916" width="660" height="30" fill="#c2c8c4" /><rect x="210" y="946" width="660" height="10" fill="#000" opacity=".35" />
    <rect x="640" y="838" width="70" height="78" rx="6" fill="#4c3a2f" /><path d="M648 838 Q675 780 700 838 M670 838 Q640 790 625 806 M680 838 Q720 790 742 806" stroke="#2f5a43" strokeWidth="9" fill="none" strokeLinecap="round" />
    {/* штора */}
    <path d="M170 250 H330 Q300 560 330 1000 L170 1000Z" fill="url(#curt)" />
    <path d="M214 250 Q200 600 214 1000 M262 250 Q250 600 262 1000 M300 250 Q290 600 302 1000" stroke="#000" strokeOpacity=".3" strokeWidth="5" fill="none" />
    <rect x="150" y="232" width="760" height="22" rx="10" fill="#2a1f1a" />
    {/* лунный свет на полу */}
    <path d="M300 1236 L780 1236 L1020 1920 L120 1920Z" fill="url(#moonpatch)" />
    {/* торшер */}
    <rect x="936" y="860" width="10" height="330" fill="#15181b" /><path d="M900 860 L982 860 L960 770 L922 770Z" fill="#d8a45a" /><path d="M900 860 L982 860" stroke="#fff" strokeOpacity=".4" strokeWidth="4" />
    <ellipse cx="941" cy="1190" rx="46" ry="10" fill="#0e1012" />
    <circle cx="941" cy="850" r="430" fill="url(#lampglow)" />
    <path d="M922 860 L860 1190 L1040 1190 L960 860Z" fill="#ffd58a" opacity=".1" />
  </g>
);

/** Свет, тьма, зерно — накладывается поверх всей сцены. */
export const Grade: React.FC<{dark?: number}> = ({dark = 0.55}) => (
  <g>
    <defs>
      <radialGradient id="vig" cx=".5" cy=".46" r=".78"><stop offset=".35" stopColor="#04070c" stopOpacity="0" /><stop offset="1" stopColor="#04070c" stopOpacity="0.9" /></radialGradient>
      <filter id="grain"><feTurbulence type="fractalNoise" baseFrequency=".8" numOctaves="2" seed="4" /><feColorMatrix values="0 0 0 0 .5  0 0 0 0 .5  0 0 0 0 .5  0 0 0 .13 0" /></filter>
    </defs>
    <rect width="1080" height="1920" fill="#06101c" opacity={dark * 0.45} />
    <rect width="1080" height="1920" fill="url(#vig)" />
    <rect width="1080" height="1920" filter="url(#grain)" />
  </g>
);
