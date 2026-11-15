import React from 'react';

/** Общие кирпичики плоских фонов серии: градиенты, обои, пол, плинтус, свет, пятна, перспектива. */
export type P = [number, number];
export type Stop = [number, string, number?];

export const Grad: React.FC<{id: string; stops: Stop[]; dir?: 'v' | 'h' | 'd'}> = ({id, stops, dir = 'v'}) => (
  <linearGradient id={id} x1="0" y1="0" x2={dir === 'v' ? 0 : 1} y2={dir === 'h' ? 0 : 1}>
    {stops.map(([o, c, a], i) => <stop key={i} offset={o} stopColor={c} stopOpacity={a ?? 1} />)}
  </linearGradient>
);

/** Тёплое световое пятно (радиальный градиент). */
export const Glow: React.FC<{id: string; x: number; y: number; r: number; color?: string; op?: number; sy?: number}> = ({id, x, y, r, color = '#ffd58a', op = 0.8, sy = 1}) => (
  <g>
    <defs><radialGradient id={id} cx=".5" cy=".5" r=".5">
      <stop offset="0" stopColor={color} stopOpacity={op} /><stop offset=".4" stopColor={color} stopOpacity={op * 0.34} /><stop offset="1" stopColor={color} stopOpacity="0" />
    </radialGradient></defs>
    <ellipse cx={x} cy={y} rx={r} ry={r * sy} fill={`url(#${id})`} />
  </g>
);

export const poly = (pts: P[]) => pts.map((p) => `${p[0].toFixed(1)},${p[1].toFixed(1)}`).join(' ');

/** Одноточечная перспектива: X,Y — смещение от точки схода при z=0 (ближняя плоскость), z∈[0,1] — глубина до дальней стены. */
export const makePersp = (vx: number, vy: number, sFar: number) => (X: number, Y: number, z: number): P => {
  const s = 1 / (1 + z * (1 / sFar - 1));
  return [vx + X * s, vy + Y * s];
};

/** Детерминированный «шум» без Math.random. */
export const nz = (i: number, s = 1) => {
  const v = Math.sin(i * 12.9898 + s * 78.233) * 43758.5453;
  return v - Math.floor(v);
};

/** Пятна/разводы: n эллипсов в прямоугольнике, детерминированно. */
export const Stains: React.FC<{x: number; y: number; w: number; h: number; n: number; seed?: number; color?: string; op?: number; rx?: number; tall?: boolean}> = ({x, y, w, h, n, seed = 1, color = '#000', op = 0.12, rx = 60, tall}) => (
  <g>{Array.from({length: n}, (_, i) => {
    const r = rx * (0.4 + nz(i, seed + 3));
    return <ellipse key={i} cx={x + nz(i, seed) * w} cy={y + nz(i, seed + 1) * h} rx={tall ? r * 0.3 : r} ry={tall ? r * 2.2 : r * 0.6} fill={color} opacity={op * (0.5 + nz(i, seed + 2))} />;
  })}</g>
);

/** Стена: вертикальный градиент + паттерн обоев (полоса и ромбики, как в RoomWindow). */
export const Wall: React.FC<{id: string; x?: number; y?: number; w?: number; h: number; top?: string; bot?: string; paper?: number}> = ({id, x = 0, y = 0, w = 1080, h, top = '#3b4a4f', bot = '#2a363a', paper = 1}) => (
  <g>
    <defs>
      <Grad id={`${id}-g`} stops={[[0, top], [1, bot]]} />
      <pattern id={`${id}-p`} width="90" height="120" patternUnits="userSpaceOnUse">
        <path d="M0 0 V120" stroke="#000" strokeOpacity=".08" strokeWidth="6" />
        <path d="M45 20 l8 14 l-8 14 l-8 -14Z M45 80 l8 14 l-8 14 l-8 -14Z" fill="#000" opacity=".07" />
      </pattern>
    </defs>
    <rect x={x} y={y} width={w} height={h} fill={`url(#${id}-g)`} />
    {paper > 0 && <rect x={x} y={y} width={w} height={h} fill={`url(#${id}-p)`} opacity={paper} />}
  </g>
);

/** Пол с перспективой: градиент + доски/швы, сходящиеся к точке (vx, y). kind: wood | lino | tile. */
export const Floor: React.FC<{id: string; y?: number; c1?: string; c2?: string; kind?: 'wood' | 'lino' | 'tile'; vx?: number}> = ({id, y = 1230, c1 = '#3a2a22', c2 = '#1a120f', kind = 'wood', vx = 540}) => {
  const hh = 1920 - y;
  const n = kind === 'wood' ? 7 : 9;
  return (
    <g>
      <defs><Grad id={`${id}-f`} stops={[[0, c1], [1, c2]]} /></defs>
      <rect y={y} width="1080" height={hh} fill={`url(#${id}-f)`} />
      {Array.from({length: n}, (_, i) => (
        <path key={i} d={`M${vx + (i - (n - 1) / 2) * (kind === 'wood' ? 260 : 220) * 2.4} 1920 L${vx + (i - (n - 1) / 2) * (kind === 'wood' ? 52 : 40)} ${y}`} stroke="#000" strokeOpacity={kind === 'wood' ? 0.28 : 0.22} strokeWidth="4" />
      ))}
      {kind !== 'wood' && [0.1, 0.24, 0.42, 0.66, 1].map((t, i) => <rect key={i} y={y + t * t * hh * 0.95} width="1080" height={3 + i} fill="#000" opacity=".2" />)}
      {kind === 'tile' && [0.1, 0.24, 0.42, 0.66, 1].map((t, i) => <rect key={i} y={y + t * t * hh * 0.95 + 4 + i} width="1080" height="2" fill="#9fb3b0" opacity=".07" />)}
      <rect y={y} width="1080" height={hh * 0.12} fill="#000" opacity=".22" />
    </g>
  );
};

/** Плинтус: тёмная полоса и светлая кромка сверху. */
export const Skirting: React.FC<{y?: number; x?: number; w?: number; h?: number; c?: string}> = ({y = 1190, x = 0, w = 1080, h = 46, c = '#1d2326'}) => (
  <g><rect x={x} y={y} width={w} height={h} fill={c} /><rect x={x} y={y - 4} width={w} height="6" fill="#4a575b" /><rect x={x} y={y + h - 6} width={w} height="6" fill="#000" opacity=".3" /></g>
);

/** Тень у пола на стене (затемнение низа). */
export const WallShade: React.FC<{y: number; h: number; op?: number}> = ({y, h, op = 0.12}) => <rect y={y} width="1080" height={h} fill="#000" opacity={op} />;

/** Дверь в фас: коробка, полотно, две филёнки. */
export const DoorLeaf: React.FC<{id: string; x: number; y: number; w: number; h: number; c?: string; frame?: string}> = ({id, x, y, w, h, c = '#4a5558', frame = '#2c3538'}) => (
  <g>
    <defs><Grad id={`${id}-d`} dir="h" stops={[[0, c], [0.5, c], [1, '#262e31']]} /></defs>
    <rect x={x - 22} y={y - 22} width={w + 44} height={h + 22} fill={frame} />
    <rect x={x} y={y} width={w} height={h} fill={`url(#${id}-d)`} />
    <rect x={x + w * 0.12} y={y + h * 0.08} width={w * 0.76} height={h * 0.34} fill="#000" opacity=".16" />
    <rect x={x + w * 0.12} y={y + h * 0.5} width={w * 0.76} height={h * 0.4} fill="#000" opacity=".16" />
    <rect x={x + w * 0.12} y={y + h * 0.08} width={w * 0.76} height="4" fill="#fff" opacity=".08" />
    <rect x={x + w * 0.12} y={y + h * 0.5} width={w * 0.76} height="4" fill="#fff" opacity=".08" />
  </g>
);

/** Абажур-лампа на подставке (тёплый источник). */
export const Shade: React.FC<{x: number; y: number; s?: number; glow?: string}> = ({x, y, s = 1, glow}) => (
  <g transform={`translate(${x},${y}) scale(${s})`}>
    <rect x="-5" y="0" width="10" height="70" fill="#15181b" /><ellipse cx="0" cy="72" rx="26" ry="7" fill="#15181b" />
    <path d="M-44 0 L44 0 L28 -64 L-28 -64Z" fill="#d8a45a" /><path d="M-44 0 L44 0" stroke="#fff" strokeOpacity=".4" strokeWidth="4" />
    {glow && <circle cx="0" cy="-30" r="14" fill="#ffe6b0" opacity=".8" />}
  </g>
);
