import React from 'react';
import {AbsoluteFill, interpolate} from 'remotion';
import {FONT} from '../../theme';
import {AMBER, INK, PANEL, useAppear} from './common';

const lerp = (t: number, a = 0, b = 0.5) => interpolate(t, [a, b], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});

/** Схема квартиры сверху, зона y 0.08–0.40. doorAt/windowAt/latchAt — секунды относительно начала сцены. */
export const FlatPlan: React.FC<{appearAt?: number; doorAt?: number; windowAt?: number; latchAt?: number}> = ({
  appearAt = 0, doorAt = 1, windowAt = 2.5, latchAt,
}) => {
  const {frame, fps, k, o, dy, visible, t} = useAppear(appearAt, 0.5, 12);
  if (!visible) return null;
  const T = frame / fps;
  const pulse = (a: number) => 0.55 + 0.45 * Math.sin((T - a) * 5);
  const dp = lerp(T - doorAt, 0, 0.6), wp = lerp(T - windowAt, 0, 0.6), lp = latchAt === undefined ? 0 : lerp(T - latchAt, 0, 0.3);
  const lab = (x: number, y: number, s: string, c = INK, fs = 22, anchor: 'middle' | 'start' = 'middle') =>
    <text x={x} y={y} fill={c} fontFamily={FONT} fontWeight={800} fontSize={fs} textAnchor={anchor} letterSpacing="2" opacity={0.85}>{s}</text>;
  // план в координатах 1080-холста: x 100..980, y 190..720
  const line = {stroke: INK, strokeWidth: 3, fill: 'none', strokeLinejoin: 'round' as const};
  const arrow = (x1: number, y1: number, x2: number, y2: number, p: number, ps: number) => {
    const a = Math.atan2(y2 - y1, x2 - x1), L = Math.hypot(x2 - x1, y2 - y1);
    const ex = x1 + (x2 - x1) * p, ey = y1 + (y2 - y1) * p;
    const hs = 26;
    return (
      <g opacity={p > 0 ? 1 : 0} style={{filter: `drop-shadow(0 0 ${6 * ps}px rgba(224,160,48,.7))`}}>
        <line x1={x1} y1={y1} x2={ex} y2={ey} stroke={AMBER} strokeWidth={7} strokeLinecap="round" strokeDasharray="16 10" />
        {p > 0.95 && <path d={`M${x2} ${y2} L${x2 - hs * Math.cos(a - 0.5)} ${y2 - hs * Math.sin(a - 0.5)} L${x2 - hs * Math.cos(a + 0.5)} ${y2 - hs * Math.sin(a + 0.5)}Z`} fill={AMBER} />}
        <circle cx={x1} cy={y1} r={8 + 3 * ps * (p >= 1 ? 1 : 0)} fill={AMBER} />
        {L < 0 && null}
      </g>
    );
  };
  return (
    <AbsoluteFill style={{pointerEvents: 'none'}}>
      <svg width={1080 * k} height={1920 * k} viewBox="0 0 1080 1920" style={{opacity: o, transform: `translateY(${dy}px)`}}>
        <rect x={70} y={165} width={940} height={610} rx={6} fill={PANEL} opacity={0.82} />
        {/* внешние стены */}
        <rect x={110} y={210} width={860} height={500} {...line} strokeWidth={6} />
        {/* внутренние */}
        <path d="M110 470 H470 M470 210 V710 M720 210 V470 M720 470 H970 M470 340 H720" {...line} />
        {/* дверные проёмы (разрывы) */}
        <path d="M260 470 H330 M470 560 V620" stroke={PANEL} strokeWidth={8} />
        {lab(290, 345, 'КОМНАТА')}{lab(595, 280, 'КУХНЯ')}{lab(845, 455, 'КОМНАТА')}{lab(595, 420, 'ВАННАЯ', INK, 20)}{lab(340, 690, 'ПРИХОЖАЯ')}{lab(720, 600, 'КОРИДОР')}
        {/* входная дверь: левая стена прихожей, окно: верх комнаты справа */}
        <rect x={104} y={560} width={12} height={70} fill={AMBER} opacity={dp > 0 ? 1 : 0.55} />
        <line x1={780} y1={210} x2={910} y2={210} stroke="#8FA3AD" strokeWidth={9} opacity={wp > 0 ? 1 : 0.55} />
        {lab(168, 660, 'ДВЕРЬ', AMBER, 24)}
        {lab(845, 190, 'ОКНО', '#8FA3AD', 24)}
        {arrow(330, 595, 130, 595, dp, pulse(doorAt))}
        {arrow(845, 400, 845, 236, wp, pulse(windowAt))}
        {/* защёлка изнутри */}
        {lp > 0 && (
          <g opacity={lp} transform="translate(210 520)">
            <rect x={-14} y={0} width={28} height={22} rx={3} fill={AMBER} /><path d="M-8 0 v-9 a8 8 0 0 1 16 0 v9" stroke={AMBER} strokeWidth={4} fill="none" />
            {lab(0, 52, 'ИЗНУТРИ', AMBER, 18)}
          </g>
        )}
      </svg>
    </AbsoluteFill>
  );
};

/** Полоса света под дверью. x,y,w — доли кадра (центр полосы по y). shadowT 0..1 — тень слева направо. */
export const LightStrip: React.FC<{x?: number; y?: number; w?: number; intensity?: number; shadowT?: number; appearAt?: number; offAt?: number; thickness?: number}> = ({
  x = 0.3, y = 0.72, w = 0.4, intensity = 1, shadowT = -1, appearAt = 0, offAt, thickness = 8,
}) => {
  const {frame, fps, k, o, visible, width, height} = useAppear(appearAt, 0.25, 0);
  if (!visible) return null;
  const T = frame / fps;
  const flick = 1 + 0.06 * Math.sin(frame * 0.9) + 0.04 * Math.sin(frame * 2.3 + 1);
  const off = offAt === undefined ? 1 : 1 - lerp(T - offAt, 0, 5 / fps);
  const I = Math.max(0, intensity * o * off * flick);
  const px = x * width, py = y * height, pw = w * width, th = thickness * k;
  const sActive = shadowT >= 0 && shadowT <= 1;
  const sc = px - 0.15 * pw + shadowT * pw * 1.3; // центр тени
  const sw = pw * 0.22;
  const dim = (cx: number) => sActive ? 1 - 0.85 * Math.exp(-Math.pow((cx - sc) / sw, 2)) : 1;
  const N = 40;
  const cells = Array.from({length: N}, (_, i) => {
    const cx = px + ((i + 0.5) / N) * pw;
    return {cx, d: dim(cx)};
  });
  return (
    <AbsoluteFill style={{pointerEvents: 'none'}}>
      <svg width={width} height={height}>
        <defs>
          <linearGradient id="ls-core" gradientUnits="userSpaceOnUse" x1={px} x2={px + pw} y1="0" y2="0"><stop offset="0" stopColor="#C8742A" stopOpacity="0" /><stop offset=".12" stopColor="#E3A050" /><stop offset=".5" stopColor="#FFD58A" /><stop offset=".88" stopColor="#E3A050" /><stop offset="1" stopColor="#C8742A" stopOpacity="0" /></linearGradient>
          <filter id="ls-b" x="-20%" y="-1000%" width="140%" height="2200%"><feGaussianBlur stdDeviation={10 * k} /></filter>
          <filter id="ls-b2" x="-20%" y="-400%" width="140%" height="900%"><feGaussianBlur stdDeviation={2 * k} /></filter>
          <mask id="ls-m"><rect x={px} y={py - 80 * k} width={pw} height={160 * k} fill="#fff" /></mask>
        </defs>
        {/* свечение на полу и ядро, по сегментам для тени */}
        {cells.map((c, i) => (
          <g key={i} opacity={I * c.d}>
            <rect x={c.cx - pw / N / 2 - 1} y={py - th * 2} width={pw / N + 2} height={th * 5} fill="#C8742A" opacity={0.28} filter="url(#ls-b)" />
          </g>
        ))}
        <g mask="url(#ls-m)">
          {cells.map((c, i) => (
            <rect key={i} x={c.cx - pw / N / 2 - 0.5} y={py - th / 2} width={pw / N + 1} height={th} fill="url(#ls-core)" opacity={I * c.d} />
          ))}
        </g>
        {sActive && (
          <ellipse cx={sc} cy={py + th} rx={sw * 1.2} ry={36 * k} fill="#000" opacity={0.55 * Math.min(1, I + 0.2)} filter="url(#ls-b)" />
        )}
      </svg>
    </AbsoluteFill>
  );
};
