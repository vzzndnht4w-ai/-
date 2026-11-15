import React from 'react';
import {AbsoluteFill, interpolate} from 'remotion';
import {FONT} from '../../theme';
import {AMBER, BLOOD, INK, PANEL, RED, STEEL, useAppear} from './common';

/* ---------- ПРАВИЛО №N ---------- */
export const RulePlate: React.FC<{n?: number; title?: string; appearAt?: number; broken?: boolean; brokenAt?: number; mono?: boolean}> = ({
  n = 1, title = '', appearAt = 0, broken = false, brokenAt = 1.5, mono = false,
}) => {
  const {frame, fps, k, t, visible} = useAppear(appearAt, 0.01, 0);
  if (!visible) return null;
  const f = Math.round(t * fps);
  // 3-кадровое мерцание: выкл/вкл/выкл/вкл, затем стабильно; лёгкая дрожь первые 8 кадров
  const flick = f < 3 ? [0.15, 1, 0.3][f] : 1;
  const jx = f < 8 ? Math.sin(f * 7.1) * 3 * k : 0;
  const nl = Math.max(1, Math.ceil(title.length / 17)), W = 920 * k, H = (nl > 1 ? 300 : 240) * k, X = (1080 * k - W) / 2, Y = 0.14 * 1920 * k;
  const bt = (t - brokenAt) * fps;
  const sc = broken ? interpolate(bt, [0, 6], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'}) : 0;
  const bar = mono ? '#8A9396' : AMBER;
  const words = title.split(' ');
  // перенос на 2 строки по ~16 символов
  const lines: string[] = [];
  words.forEach((w) => {
    const l = lines[lines.length - 1];
    if (l !== undefined && (l + ' ' + w).length <= 17) lines[lines.length - 1] = l + ' ' + w; else lines.push(w);
  });
  const fs = lines.length > 2 || Math.max(...lines.map((l) => l.length)) > 20 ? 44 : 52;
  return (
    <AbsoluteFill style={{pointerEvents: 'none'}}>
      <div style={{position: 'absolute', left: X + jx, top: Y, width: W, height: H, opacity: flick * 0.97, filter: mono ? 'grayscale(1)' : undefined}}>
        <div style={{position: 'absolute', inset: 0, background: PANEL, opacity: 0.92, border: `${2 * k}px solid ${INK}`, boxSizing: 'border-box'}} />
        <div style={{position: 'absolute', left: 0, top: 0, bottom: 0, width: 10 * k, background: bar}} />
        <div style={{position: 'absolute', left: 48 * k, top: 34 * k, right: 30 * k, fontFamily: FONT, fontWeight: 800, fontSize: 40 * k, letterSpacing: '0.08em', color: bar}}>
          ПРАВИЛО №{n}
        </div>
        <div style={{position: 'absolute', left: 48 * k, top: 108 * k, right: 30 * k, fontFamily: FONT, fontWeight: 800, fontSize: fs * k, lineHeight: 1.18, color: '#E3EAEC'}}>
          {lines.map((l, i) => <div key={i}>{l}</div>)}
        </div>
        {broken && sc > 0 && (
          <>
            <svg width={W} height={H} style={{position: 'absolute', left: 0, top: 0}}>
              <path d={`M${60 * k} ${H - 30 * k} L${W - 50 * k} ${28 * k}`} stroke={BLOOD} strokeWidth={9 * k} strokeLinecap="round" fill="none"
                pathLength={1} strokeDasharray={1} strokeDashoffset={1 - sc} />
              <path d={`M${90 * k} ${H - 20 * k} L${W - 90 * k} ${60 * k}`} stroke={BLOOD} strokeWidth={3 * k} strokeLinecap="round" fill="none" opacity={0.7}
                pathLength={1} strokeDasharray={1} strokeDashoffset={1 - Math.max(0, sc * 1.2 - 0.2)} />
            </svg>
            <div style={{position: 'absolute', right: 28 * k, top: 38 * k, fontFamily: FONT, fontWeight: 800, fontSize: 30 * k, letterSpacing: '0.1em', color: '#D2584A', opacity: sc}}>
              НАРУШЕНО
            </div>
          </>
        )}
      </div>
    </AbsoluteFill>
  );
};

/* ---------- Оговорка ---------- */
export const Disclaimer: React.FC<{text?: string; appearAt?: number; center?: boolean; y?: number}> = ({
  text = 'Вымысел. Не инструкция.', appearAt = 0, center = false, y,
}) => {
  const {k, o, dy, height, visible} = useAppear(appearAt, 0.6, 6);
  if (!visible) return null;
  const yy = (y ?? (center ? 0.45 : 0.945)) * height;
  return (
    <AbsoluteFill style={{pointerEvents: 'none'}}>
      <div style={{position: 'absolute', left: 0, right: 0, top: yy + dy, transform: 'translateY(-50%)', textAlign: 'center', fontFamily: FONT, fontWeight: 600,
        fontSize: (center ? 40 : 30) * k, color: INK, opacity: o * (center ? 0.9 : 0.55), letterSpacing: '0.02em'}}>
        {text}
      </div>
    </AbsoluteFill>
  );
};

/* ---------- Плашка-метка ---------- */
export const InfoTag: React.FC<{text?: string; sub?: string; tone?: 'info' | 'danger'; appearAt?: number; y?: number}> = ({
  text = '', sub, tone = 'info', appearAt = 0, y = 0.2,
}) => {
  const {k, o, dy, height, visible} = useAppear(appearAt);
  if (!visible) return null;
  const col = tone === 'danger' ? '#D2584A' : AMBER;
  const fs = Math.min(60, Math.floor(820 / (Math.max(text.length, 1) * 0.78)));
  return (
    <AbsoluteFill style={{pointerEvents: 'none', alignItems: 'center'}}>
      <div style={{position: 'absolute', top: y * height + dy, transform: 'translateY(-50%)', maxWidth: 960 * k, opacity: o,
        background: PANEL, border: `${2 * k}px solid ${tone === 'danger' ? '#7A2B26' : INK}`, borderLeft: `${10 * k}px solid ${col}`,
        padding: `${22 * k}px ${38 * k}px`, boxShadow: `0 ${8 * k}px ${30 * k}px rgba(0,0,0,.6)`, textAlign: 'center'}}>
        <div style={{fontFamily: FONT, fontWeight: 800, fontSize: fs * k, letterSpacing: '0.05em', color: tone === 'danger' ? '#F0D8D4' : '#E3EAEC', whiteSpace: 'nowrap'}}>{text}</div>
        {sub && <div style={{fontFamily: FONT, fontWeight: 600, fontSize: 28 * k, marginTop: 8 * k, color: col, opacity: 0.9}}>{sub}</div>}
      </div>
    </AbsoluteFill>
  );
};

/* ---------- Титульная карточка ---------- */
export const TitleCard: React.FC<{text?: string; sub?: string; appearAt?: number}> = ({text = '', sub, appearAt = 0}) => {
  const {k, o, dy, height, visible} = useAppear(appearAt, 0.8, 10);
  return (
    <AbsoluteFill style={{background: '#000', opacity: visible ? 1 : 0}}>
      {visible && (
        <div style={{position: 'absolute', left: 0, right: 0, top: 0.42 * height + dy, transform: 'translateY(-50%)', textAlign: 'center', opacity: o, padding: `0 ${60 * k}px`}}>
          <div style={{fontFamily: FONT, fontWeight: 800, fontSize: 78 * k, letterSpacing: '0.04em', color: '#D9E2E4', lineHeight: 1.15}}>{text}</div>
          <div style={{width: 120 * k, height: 3 * k, background: AMBER, margin: `${34 * k}px auto 0`, opacity: 0.85}} />
          {sub && <div style={{fontFamily: FONT, fontWeight: 600, fontSize: 36 * k, color: STEEL, marginTop: 26 * k, filter: 'brightness(1.6)'}}>{sub}</div>}
        </div>
      )}
    </AbsoluteFill>
  );
};

/* ---------- Субтитры ---------- */
type W = {text: string; start: number; end: number};
export const Subtitle: React.FC<{words?: W[]; appearAt?: number; whisper?: boolean; shout?: boolean}> = ({words = [], appearAt = 0, whisper = false, shout = false}) => {
  const {frame, fps, k, height} = useAppear(appearAt, 0.01, 0);
  const t = frame / fps - appearAt;
  // блоки по ≤3 слова; звук в скобках — отдельный блок
  const blocks: W[][] = [];
  let cur: W[] = [];
  const isSnd = (w: W) => w.text.trim().startsWith('[');
  words.forEach((w) => {
    if (isSnd(w) || (cur.length && isSnd(cur[0])) || cur.length >= 3) { if (cur.length) blocks.push(cur); cur = []; }
    cur.push(w);
  });
  if (cur.length) blocks.push(cur);
  const bi = blocks.findIndex((b, i) => {
    const s = b[0].start, e = i + 1 < blocks.length ? Math.min(b[b.length - 1].end + 0.25, blocks[i + 1][0].start) : b[b.length - 1].end + 0.25;
    return t >= s && t < e;
  });
  if (bi < 0) return null;
  const b = blocks[bi];
  const snd = isSnd(b[0]);
  const fs = snd ? 40 : shout ? 57 : whisper ? 46 : 54;
  const base = snd ? 0.6 : whisper ? 0.75 : 0.92;
  const shadow = `0 0 ${3 * k}px rgba(0,0,0,.9), 0 ${2 * k}px ${12 * k}px rgba(0,0,0,.8), 0 0 ${1 * k}px #000`;
  return (
    <AbsoluteFill style={{pointerEvents: 'none'}}>
      <div style={{position: 'absolute', left: 60 * k, right: 60 * k, top: 0.83 * height, transform: 'translateY(-50%)', textAlign: 'center',
        fontFamily: FONT, fontWeight: shout ? 800 : 600, fontSize: fs * k, fontStyle: snd || whisper ? 'italic' : 'normal', opacity: base, textShadow: shadow, whiteSpace: 'nowrap'}}>
        {b.map((w, i) => {
          const active = !snd && t >= w.start && t < w.end;
          return <span key={i} style={{color: active ? '#FFF3E0' : '#B9C4C7', marginRight: i < b.length - 1 ? '0.3em' : 0}}>{w.text}</span>;
        })}
      </div>
    </AbsoluteFill>
  );
};
