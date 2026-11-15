import React from 'react';
import {useCurrentFrame} from 'remotion';
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
export type Pose = 'stand' | 'notebook' | 'mouth' | 'hug' | 'wall' | 'kettle' | 'candle';

const POSES: Record<Pose, {l: P; r: P; item?: 'notebook' | 'kettle' | 'candle'}> = {
  stand: {l: [-118, 392], r: [118, 392]},
  notebook: {l: [-44, 286], r: [50, 292], item: 'notebook'},
  mouth: {l: [-110, 372], r: [26, 96]},
  hug: {l: [66, 258], r: [-66, 262]},
  wall: {l: [-118, 392], r: [118, 392]},
  kettle: {l: [-118, 392], r: [62, 300], item: 'kettle'},
  candle: {l: [-118, 392], r: [56, 290], item: 'candle'},
};

/** Плоский персонаж: без контура, объём — градиентами и тёмной стороной, как в референсе. */
export const Person: React.FC<{id: string; look: Look; mood?: Mood; pose?: Pose; lookX?: number; flip?: boolean;
  x: number; y: number; scale?: number; lightSide?: 1 | -1; mouth?: number; blink?: boolean; breath?: number; age?: boolean}> =
({id, look, mood = 'tired', pose = 'stand', lookX = 0, flip, x, y, scale = 1, lightSide = 1, mouth = 0, blink = false, breath = 0, age = false}) => {
  const w = look.width ?? 1, ps = POSES[pose];
  const dk = (k: number) => shade(look.skin, k);
  const Lg = (n: string, c: string) => (
    <linearGradient id={`${id}-${n}`} x1={lightSide === 1 ? 1 : 0} y1="0" x2={lightSide === 1 ? 0 : 1} y2="0">
      <stop offset="0" stopColor={shade(c, 1.28)} /><stop offset=".35" stopColor={c} /><stop offset="1" stopColor={shade(c, 0.5)} />
    </linearGradient>);
  const Sleeve = ({s, t}: {s: P; t: P}) => {
    const {e, h} = arm(s, t, 112, 104);
    const d = `M${s[0]} ${s[1]} L${e[0]} ${e[1]} L${h[0]} ${h[1]}`;
    return <g><path d={d} fill="none" stroke={shade(look.top, 0.55)} strokeWidth="52" strokeLinecap="round" strokeLinejoin="round" />
      <path d={d} fill="none" stroke={`url(#${id}-top)`} strokeWidth="46" strokeLinecap="round" strokeLinejoin="round" />
      <circle cx={h[0]} cy={h[1]} r="21" fill={look.skin} /><circle cx={h[0]} cy={h[1]} r="21" fill={dk(0.8)} opacity=".22" /></g>;
  };
  // брови: [левая, правая] = [подъём, наклон°]; наклон >0 — внутренний край ниже (сердитый), <0 — выше (печальный/испуг)
  const B: Record<Mood, {lift: number; tilt: number}> = {tired: {lift: 2, tilt: -4}, fear: {lift: -12, tilt: -10}, stern: {lift: 4, tilt: 14}, sad: {lift: -2, tilt: -16}, blank: {lift: 0, tilt: 0}};
  const bm = B[mood];
  const eyeH = mood === 'fear' ? 1.5 : mood === 'tired' ? 0.72 : mood === 'stern' ? 0.85 : 1;
  const open = Math.max(mouth, mood === 'fear' && !blink ? 0.45 : 0);
  const lipC = '#8a4a47';
  const mw = mood === 'fear' ? 11 : 16 - open * 2;
  const faceMouth = open > 0.12
    ? <g><path d={`M${-mw} 77 Q0 ${76 - open} ${mw} 77 Q${mw * 0.9} ${80 + open * 15} 0 ${81 + open * 15} Q${-mw * 0.9} ${80 + open * 15} ${-mw} 77Z`} fill="#2a1213" />
        {mood !== 'fear' && <path d={`M${-mw + 2} 77.5 Q0 76 ${mw - 2} 77.5 L${mw - 4} ${81 + open * 2} Q0 ${80 + open * 2} ${-mw + 4} ${81 + open * 2}Z`} fill="#e9e3d6" opacity=".9" />}</g>
    : mood === 'sad' ? <path d="M-17 82 Q0 71 17 82" fill="none" stroke={lipC} strokeWidth="5" strokeLinecap="round" />
    : mood === 'stern' ? <path d="M-16 79 L16 79" fill="none" stroke={lipC} strokeWidth="5" strokeLinecap="round" />
    : <path d="M-17 77 Q-8 73 0 75 Q8 73 17 77 Q8 85 0 86 Q-8 85 -17 77Z" fill={lipC} opacity=".85" />;
  const Eye = ({cx, dir}: {cx: number; dir: number}) => {
    const ry = 9 * eyeH;
    if (blink) return <path d={`M${cx - 14} 18 Q${cx} 22 ${cx + 14} 18`} fill="none" stroke="#1a1416" strokeWidth="3.6" strokeLinecap="round" />;
    return <g>
      <path d={`M${cx - 15} 16 Q${cx} ${16 - ry} ${cx + 15} 16 Q${cx} ${16 + ry * 0.75} ${cx - 15} 16Z`} fill="#ece7df" />
      <circle cx={cx + lookX * 0.55} cy={16 + (mood === 'fear' ? 0 : 1)} r={Math.min(7.2, 5.4 + 1.4 * eyeH)} fill="#241b17" />
      <circle cx={cx + lookX * 0.55 - 2} cy={14} r="1.9" fill="#fff" opacity=".85" />
      <path d={`M${cx - 16} 16 Q${cx} ${15 - ry * 1.1} ${cx + 16} 16`} fill="none" stroke="#17110f" strokeWidth="3.4" strokeLinecap="round" />
      {mood === 'tired' && <path d={`M${cx - 13} 25 Q${cx} 31 ${cx + 13} 25`} fill="none" stroke={dk(0.55)} strokeWidth="4" strokeLinecap="round" opacity=".6" />}
    </g>;
  };
  return (
    <g transform={`translate(${x},${y}) scale(${(flip ? -1 : 1) * scale},${scale * (1 + breath * 0.006)})`}>
      <defs>{Lg('top', look.top)}{Lg('pants', look.pants)}{Lg('in', look.inner)}
        <radialGradient id={`${id}-face`} cx={lightSide === 1 ? 0.62 : 0.38} cy=".42" r=".8"><stop offset="0" stopColor={dk(1.1)} /><stop offset=".6" stopColor={look.skin} /><stop offset="1" stopColor={dk(0.55)} /></radialGradient></defs>
      <ellipse cx="0" cy="612" rx={140 * w} ry="20" fill="#000" opacity=".4" />
      <rect x={-70 * w} y="405" width={56 * w} height="195" rx="18" fill={`url(#${id}-pants)`} /><rect x={14 * w} y="405" width={56 * w} height="195" rx="18" fill={`url(#${id}-pants)`} />
      <path d={`M${-80 * w} 600 Q${-70 * w} 578 ${-14 * w} 584 L${-12 * w} 612 L${-84 * w} 612Z`} fill={look.shoes ?? '#15171b'} /><path d={`M${80 * w} 600 Q${70 * w} 578 ${14 * w} 584 L${12 * w} 612 L${84 * w} 612Z`} fill={look.shoes ?? '#15171b'} />
      <path d={`M${-104 * w} 128 Q${-118 * w} 300 ${-96 * w} 420 L${96 * w} 420 Q${118 * w} 300 ${104 * w} 128 Q0 100 ${-104 * w} 128Z`} fill={`url(#${id}-top)`} />
      <path d={`M${-34 * w} 126 L${34 * w} 126 L${28 * w} 420 L${-28 * w} 420Z`} fill={`url(#${id}-in)`} />
      <path d={`M${-34 * w} 126 L${-28 * w} 420`} stroke={shade(look.top, 0.45)} strokeWidth="5" /><path d={`M${34 * w} 126 L${28 * w} 420`} stroke={shade(look.top, 0.45)} strokeWidth="5" />
      <path d={`M${-70 * w} 200 Q${-80 * w} 300 ${-66 * w} 380`} fill="none" stroke={shade(look.top, 0.55)} strokeWidth="6" opacity=".6" />
      {pose !== 'mouth' && <><Sleeve s={[-98 * w, 150]} t={ps.l} /><Sleeve s={[98 * w, 150]} t={ps.r} /></>}
      {pose === 'mouth' && <Sleeve s={[-98 * w, 150]} t={ps.l} />}
      {ps.item === 'notebook' && <g transform="translate(0,292) rotate(-4)"><rect x="-52" y="-40" width="104" height="80" rx="6" fill="#1f3b2d" /><path d="M-44 -22 H44 M-44 -2 H44 M-44 18 H30" stroke="#8fb39d" strokeWidth="3" opacity=".6" /></g>}
      {ps.item === 'kettle' && <g transform="translate(66,300)"><path d="M-30 -10 Q-34 -50 0 -52 Q34 -50 30 -10 L36 24 L-36 24Z" fill="#4a6b6a" /><path d="M30 -20 Q56 -24 58 -44 L48 -46 Q46 -34 30 -34Z" fill="#4a6b6a" /><path d="M-26 -34 Q0 -70 26 -34" fill="none" stroke="#2a3a3a" strokeWidth="6" /><rect x="-36" y="20" width="72" height="8" rx="3" fill="#2a3a3a" /></g>}
      {ps.item === 'candle' && <g transform="translate(58,282)"><rect x="-9" y="-44" width="18" height="70" rx="3" fill="#e4ddc8" /><rect x="-30" y="24" width="60" height="9" rx="4" fill="#59626a" /><path d="M0 -44 V-54" stroke="#222" strokeWidth="3" /></g>}
      {/* шея и тень под подбородком */}
      <rect x="-27" y="84" width="54" height="58" fill={dk(0.72)} />
      <ellipse cx="0" cy="104" rx="46" ry="14" fill="#000" opacity=".22" />
      {/* уши */}
      <ellipse cx="-71" cy="30" rx="10" ry="17" fill={dk(0.88)} /><ellipse cx="71" cy="30" rx="10" ry="17" fill={dk(0.88)} />
      {/* голова: скулы и челюсть */}
      <path d="M-70 4 C-74 -58 -42 -78 0 -78 C42 -78 74 -58 70 4 C68 48 44 98 0 106 C-44 98 -68 48 -70 4Z" fill={`url(#${id}-face)`} />
      <ellipse cx={-34} cy="50" rx="22" ry="12" fill={dk(0.6)} opacity=".07" /><ellipse cx={34} cy="50" rx="22" ry="12" fill={dk(0.6)} opacity=".07" />
      {look.stubble && <path d="M-60 36 Q-58 92 0 102 Q58 92 60 36 Q44 72 0 70 Q-44 72 -60 36Z" fill="#17120f" opacity=".3" />}
      {age && <g stroke={dk(0.55)} strokeWidth="3" strokeLinecap="round" opacity=".55" fill="none"><path d="M-40 -44 Q0 -54 40 -44" /><path d="M-36 -34 Q0 -42 36 -34" /><path d="M-28 52 Q-30 68 -22 80" /><path d="M28 52 Q30 68 22 80" /></g>}
      {/* волосы */}
      {look.style === 'short' && <path d="M-74 4 C-82 -74 -40 -94 0 -94 C40 -94 82 -74 74 4 C66 -30 44 -50 0 -52 C-44 -50 -66 -30 -74 4Z" fill={look.hair} />}
      {look.style === 'messy' && <path d="M-76 6 C-90 -80 -40 -100 -4 -96 C50 -104 90 -70 76 6 C70 -34 52 -44 34 -40 C24 -56 4 -52 -8 -42 C-28 -52 -62 -40 -76 6Z" fill={look.hair} />}
      {look.style === 'bun' && <g><path d="M-74 6 C-80 -72 -40 -92 0 -92 C40 -92 80 -72 74 6 C62 -28 40 -46 0 -48 C-40 -46 -62 -28 -74 6Z" fill={look.hair} /><circle cx="0" cy="-102" r="28" fill={look.hair} /></g>}
      {look.style === 'cap' && <path d="M-76 0 Q-74 -92 0 -92 Q74 -92 76 0Z" fill={look.hair} />}
      {/* лицо */}
      <g>
        {[-1, 1].map((sd) => (
          <path key={sd} d={`M${sd * 12} -6 Q${sd * 26} -14 ${sd * 44} -6`} fill="none" stroke={look.hair} strokeWidth="7.5" strokeLinecap="round"
            transform={`translate(0,${bm.lift}) rotate(${bm.tilt * (sd === -1 ? 1 : -1) * -1} ${sd * 28} -8)`} />))}
        <Eye cx={-28} dir={-1} /><Eye cx={28} dir={1} />
        <path d="M0 22 C6 36 10 46 12 54 C6 60 -6 60 -12 54 C-8 50 -4 38 0 22Z" fill={dk(0.78)} opacity=".5" />
        <path d="M-12 55 Q0 61 12 55" fill="none" stroke={dk(0.5)} strokeWidth="3.5" strokeLinecap="round" opacity=".75" />
        {faceMouth}
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

/** Свет, тьма, зерно — накладывается поверх всей сцены. red — красная кромка 0..1, flicker — дрожь лампы 0..1. */
export const Grade: React.FC<{dark?: number; red?: number; flicker?: number; danger?: boolean}> = ({dark = 0.55, red = 0, flicker = 0, danger = false}) => {
  const f = useCurrentFrame();
  const fl = flicker ? flicker * (0.5 + 0.5 * Math.sin(f * 1.7) * Math.sin(f * 0.43 + 1)) * 0.5 : 0;
  return (
    <g>
      <defs>
        <radialGradient id="vig" cx=".5" cy=".46" r=".78"><stop offset=".35" stopColor="#04070c" stopOpacity="0" /><stop offset="1" stopColor="#04070c" stopOpacity="0.9" /></radialGradient>
        <radialGradient id="redge" cx=".5" cy=".5" r=".75"><stop offset=".5" stopColor="#8c1c1c" stopOpacity="0" /><stop offset="1" stopColor="#8c1c1c" stopOpacity="1" /></radialGradient>
        <filter id="grain"><feTurbulence type="fractalNoise" baseFrequency=".8" numOctaves="2" seed={4 + (f % 3)} /><feColorMatrix values="0 0 0 0 .5  0 0 0 0 .5  0 0 0 0 .5  0 0 0 .13 0" /></filter>
      </defs>
      <rect width="1080" height="1920" fill="#06101c" opacity={dark * 0.45} />
      {danger && <rect width="1080" height="1920" fill="#2a0707" opacity=".16" />}
      <rect width="1080" height="1920" fill="url(#vig)" />
      {red > 0 && <rect width="1080" height="1920" fill="url(#redge)" opacity={red} />}
      {fl > 0 && <rect width="1080" height="1920" fill="#000" opacity={fl} />}
      <rect width="1080" height="1920" filter="url(#grain)" />
    </g>
  );
};
