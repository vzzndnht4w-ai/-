import React from 'react';
import {AbsoluteFill, interpolate} from 'remotion';
import {FONT} from '../../theme';
import {AMBER, INK, PANEL, RED, STEEL, useAppear} from './common';

const SEG = 10;
const tone = (v: number) => (v <= 0.2 ? RED : v <= 0.4 ? AMBER : '#D9E2E4');

const Drop: React.FC<{c: string; s: number}> = ({c, s}) => (
  <svg width={s} height={s} viewBox="0 0 24 24"><path d="M12 2 C12 2 5 10 5 15 a7 7 0 0 0 14 0 C19 10 12 2 12 2Z" fill="none" stroke={c} strokeWidth="2" strokeLinejoin="round" /></svg>
);
const Can: React.FC<{c: string; s: number}> = ({c, s}) => (
  <svg width={s} height={s} viewBox="0 0 24 24"><g fill="none" stroke={c} strokeWidth="2"><path d="M5 6 v12 c0 2 14 2 14 0 V6" /><ellipse cx="12" cy="6" rx="7" ry="2.4" /><path d="M5 11 c0 2 14 2 14 0" opacity=".6" /></g></svg>
);

/** Ячейка со шкалой. shown — отображаемое значение, prev — прежнее (для выгорающих сегментов). */
const Cell: React.FC<{label: string; icon: React.ReactNode; v: number; prev: number; ft: number; k: number; frame: number; w: number}> = ({label, icon, v, prev, ft, k, frame, w}) => {
  const c = tone(v);
  const burning = ft >= 0 && ft < 6;
  const flash = ft >= 0 && ft < 4;
  const pulse = v <= 0.2 ? 0.5 + 0.5 * Math.sin((frame / 36) * Math.PI * 2) : 0;
  const jx = burning ? Math.sin(ft * 5) * 4 * k : 0;
  const segs = [];
  const sw = (w - 44 * k) / SEG;
  for (let i = 0; i < SEG; i++) {
    const on = i < Math.round(v * SEG), was = i < Math.round(prev * SEG);
    let op = on ? 1 : 0.14, col = on ? c : INK;
    if (!on && was && ft >= 0) { // выгорающий сегмент: мигает и гаснет
      op = ft < 6 ? (ft % 2 === 0 ? 1 : 0.3) : 0.14; col = '#E8EEF0';
    }
    segs.push(<div key={i} style={{position: 'absolute', left: i * sw, top: 0, width: sw - 5 * k, height: 20 * k, background: col, opacity: op * (on && v <= 0.2 ? 0.65 + 0.35 * pulse : 1)}} />);
  }
  return (
    <div style={{position: 'relative', width: w, height: 128 * k, background: PANEL, opacity: 0.88, border: `${2 * k}px solid ${v <= 0.2 ? RED : STEEL}`, boxSizing: 'border-box',
      transform: `translateX(${jx}px)`, boxShadow: v <= 0.2 ? `0 0 ${(14 + 18 * pulse) * k}px rgba(192,57,43,${0.25 + 0.3 * pulse})` : flash ? `0 0 ${20 * k}px rgba(224,160,48,.5)` : undefined}}>
      {flash && <div style={{position: 'absolute', inset: 0, background: '#fff', opacity: 0.12}} />}
      <div style={{position: 'absolute', left: 20 * k, top: 16 * k, display: 'flex', alignItems: 'center', gap: 10 * k}}>
        {icon}
        <span style={{fontFamily: FONT, fontWeight: 800, fontSize: 30 * k, letterSpacing: '0.1em', color: c}}>{label}</span>
      </div>
      <div style={{position: 'absolute', left: 22 * k, top: 80 * k, width: w - 44 * k, height: 20 * k}}>{segs}</div>
      {v <= 0 && (
        <svg width={w} height={128 * k} style={{position: 'absolute', left: 0, top: 0}}>
          {[[0.55, 0, 0.45, 0.4], [0.45, 0.4, 0.62, 0.7], [0.62, 0.7, 0.5, 1]].map(([a, b, cc, d], i) =>
            <line key={i} x1={a * w} y1={b * 128 * k} x2={cc * w} y2={d * 128 * k} stroke={RED} strokeWidth={2 * k} opacity={0.8} />)}
        </svg>
      )}
    </div>
  );
};

export const Hud: React.FC<{water?: number; food?: number; day?: number; appearAt?: number; waterPrev?: number; foodPrev?: number; changeAt?: number; dayPrev?: number; dayAt?: number}> = ({
  water = 1, food = 1, day = 1, appearAt = 0, waterPrev, foodPrev, changeAt = 0, dayPrev, dayAt = 0,
}) => {
  const {frame, fps, k, o, dy, visible, t} = useAppear(appearAt, 0.4, -10);
  if (!visible) return null;
  const ft = Math.round((t - changeAt) * fps); // кадров с момента изменения
  const after = ft >= 0;
  const wv = waterPrev !== undefined && !after ? waterPrev : water;
  const fv = foodPrev !== undefined && !after ? foodPrev : food;
  const W = 304 * k, gap = 12 * k, X = 40 * k;
  const dft = Math.round((t - dayAt) * fps);
  const rolling = dayPrev !== undefined && dft >= 0 && dft < 10;
  const showDay = dayPrev !== undefined && dft < 0 ? dayPrev : day;
  const roll = rolling ? interpolate(dft, [0, 10], [0, 1]) : 1;
  return (
    <AbsoluteFill style={{pointerEvents: 'none'}}>
      <div style={{position: 'absolute', left: X, top: 0.065 * 1920 * k + dy, display: 'flex', gap, opacity: o}}>
        <Cell label="ВОДА" icon={<Drop c={tone(wv)} s={34 * k} />} v={wv} prev={waterPrev ?? water} ft={waterPrev !== undefined ? ft : -1} k={k} frame={frame} w={W} />
        <Cell label="ЕДА" icon={<Can c={tone(fv)} s={34 * k} />} v={fv} prev={foodPrev ?? food} ft={foodPrev !== undefined ? ft : -1} k={k} frame={frame} w={W} />
        <div style={{position: 'relative', width: W, height: 128 * k, background: PANEL, opacity: 0.88, border: `${2 * k}px solid ${STEEL}`, boxSizing: 'border-box', overflow: 'hidden'}}>
          <div style={{position: 'absolute', left: 0, right: 0, top: 0, bottom: 0, display: 'flex', alignItems: 'center', justifyContent: 'center', fontFamily: FONT, fontWeight: 800, fontSize: 44 * k, color: '#D9E2E4', letterSpacing: '0.04em'}}>
            <span style={{display: 'inline-block', transform: rolling ? `translateY(${-(roll) * 40 * k}px)` : undefined, opacity: rolling ? 1 - roll : 1}}>ДЕНЬ {rolling ? dayPrev : showDay}</span>
            {rolling && <span style={{position: 'absolute', transform: `translateY(${(1 - roll) * 40 * k}px)`, opacity: roll}}>ДЕНЬ {day}</span>}
          </div>
        </div>
      </div>
    </AbsoluteFill>
  );
};
