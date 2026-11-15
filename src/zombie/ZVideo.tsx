import React from 'react';
import {AbsoluteFill, Audio, Sequence, interpolate, staticFile, useCurrentFrame, useVideoConfig} from 'remotion';
import {Grade, Person, type Mood, type Pose} from './Flat';
import {CAST} from './cast';
import {BACKGROUNDS} from './Rooms';
import {UI} from './Ui';
import {Infected} from './Infected';
import {loadFonts} from '../theme';
import {norm} from '../lib/timing';
import type {Script, Timeline, Word} from '../types';

export type ZChar = {
  who: keyof typeof CAST; x: number; y?: number; h: number; mood?: Mood; pose?: Pose; flip?: boolean; lookX?: number;
  sil?: boolean; dim?: number; light?: 1 | -1;
  /** выезд в кадр по слову: с x=fromX за dur секунд */
  enter?: {cue: string; fromX: number; dur: number};
  /** смена позы/настроения по слову */
  swap?: {cue: string; pose?: Pose; mood?: Mood};
  /** плавное перемещение за сцену */
  to?: {x: number; y?: number; h: number; dur: number; fadeAt?: number};
  portrait?: boolean;
};
export type ZExtra =
  | {kind: 'wardrobe'; x: [number, number]; y: number; h: number; cue: string; stopCue: string}
  | {kind: 'water'; x: number; y: number; h: number}
  | {kind: 'candle'; x: number; y: number; h: number; cue?: string}
  | {kind: 'hand'; at: number};
export type ZUi = {kind: string; cue?: string; at?: number; until?: number; props?: Record<string, unknown>; cues?: Record<string, string>};
export type ZDef = {
  bg: string; bg2?: {id: string; cue?: string; at?: number}; blackUntil?: number;
  chars?: ZChar[]; extras?: ZExtra[]; infected?: {x: number; y: number; h: number; tilt?: number; opacity?: number}[];
  cam?: {z0: number; z1: number; x: number; y: number};
  danger?: boolean; red?: number | {from: number; to: number; cue: string}; flicker?: number;
  blur?: number; dim?: number; sound?: {text: string; start: number; end: number}[]; shakeCue?: string;
  ui?: ZUi[];
  sfx?: {name: string; at?: number; cue?: string; vol?: number; loop?: boolean}[];
};

const S = 1920 / 704;           // масштаб Person: высота фигуры ≈ 704 ед.
export const cueT = (words: Word[], cue: string, scene: string): number => {
  const c = norm(cue); const i = words.findIndex((w) => norm(w.text).includes(c));
  if (i < 0) throw new Error(`сцена ${scene}: не нашёл слово «${cue}» в озвучке`);
  return words[i].start;
};

const Silhouette: React.FC<{children: React.ReactNode}> = ({children}) => (
  <g style={{filter: 'brightness(0.08) contrast(1.2)'}}>{children}</g>
);

const Hand: React.FC<{x: number; y: number}> = ({x, y}) => (
  <g transform={`translate(${x},${y})`}>
    <path d="M-170 40 Q-110 -10 -40 -20 L40 -22 Q70 -10 70 14 Q70 46 36 52 L-40 64 Q-120 80 -170 70Z" fill="#e0b394" />
    {[-34, -10, 14, 36].map((fy, i) => <rect key={i} x={20} y={fy - 8} width={86 - i * 4} height="20" rx="10" fill="#e0b394" />)}
    <path d="M-170 40 Q-110 -10 -40 -20" fill="none" stroke="#a37557" strokeWidth="5" opacity=".5" />
  </g>
);

const Extras: React.FC<{def: ZDef; words: Word[]; id: string; over?: boolean}> = ({def, words, id, over}) => {
  const frame = useCurrentFrame(); const {fps} = useVideoConfig(); const t = frame / fps;
  return <>{(def.extras ?? []).filter((e) => (e.kind === 'hand') === !!over).map((e, i) => {
    if (e.kind === 'wardrobe') {
      const a = cueT(words, e.cue, id), b = cueT(words, e.stopCue, id);
      const x = interpolate(t, [a, b], e.x, {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'}) * 1080;
      const h = e.h * 1920, w = h * 0.5, y = e.y * 1920;
      return <g key={i}><rect x={x - w / 2} y={y - h} width={w} height={h} rx="8" fill="#3a2a22" /><rect x={x - w / 2 + 10} y={y - h + 12} width={w / 2 - 14} height={h - 24} fill="#4a362c" /><rect x={x + 4} y={y - h + 12} width={w / 2 - 14} height={h - 24} fill="#4a362c" /><rect x={x - 6} y={y - h * 0.55} width="12" height="40" fill="#8a7a5a" /></g>;
    }
    if (e.kind === 'water') {
      const h = e.h * 1920, x = e.x * 1080, y = e.y * 1920;
      return <g key={i}>{[-1, 0, 1].map((k) => <g key={k}><rect x={x + k * h * 0.42 - h * 0.16} y={y - h * 0.7} width={h * 0.32} height={h * 0.7} rx="12" fill="#9db8c4" opacity=".55" /><rect x={x + k * h * 0.42 - h * 0.17} y={y - h * 0.76} width={h * 0.34} height={h * 0.08} rx="4" fill="#59626a" /><rect x={x + k * h * 0.42 - h * 0.14} y={y - h * 0.48} width={h * 0.28} height={h * 0.46} rx="8" fill="#5e8aa0" opacity=".6" /></g>)}</g>;
    }
    if (e.kind === 'candle') {
      const on = e.cue ? t >= cueT(words, e.cue, id) : true;
      if (!on) return null;
      const h = e.h * 1920, x = e.x * 1080, y = e.y * 1920;
      return <g key={i}><rect x={x - h * 0.1} y={y - h} width={h * 0.2} height={h} rx="3" fill="#e4ddc8" /><rect x={x - h * 0.34} y={y - 4} width={h * 0.68} height={h * 0.1} rx="4" fill="#59626a" /></g>;
    }
    if (e.kind === 'hand' && over) {
      const p = interpolate(t, [e.at, e.at + 0.2], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
      return <g key={i} opacity={p}><Hand x={interpolate(p, [0, 1], [-100, 560])} y={1010} /></g>;
    }
    return null;
  })}</>;
};

const SceneView: React.FC<{def: ZDef; words: Word[]; id: string; dur: number}> = ({def, words, id, dur}) => {
  const frame = useCurrentFrame(); const {fps} = useVideoConfig(); const t = frame / fps;
  const Bg1 = BACKGROUNDS[def.bg]; if (!Bg1) throw new Error(`нет фона ${def.bg}`);
  const useBg2 = def.bg2 && t >= (def.bg2.at ?? cueT(words, def.bg2.cue!, id));
  const Bg = useBg2 ? BACKGROUNDS[def.bg2!.id] : Bg1;
  const speaking = (who: string) => words.some((w) => (w as any).spk === who && t >= w.start && t <= w.end + 0.06);
  const red = typeof def.red === 'number' ? def.red : def.red ? (t < cueT(words, def.red.cue, id) ? def.red.from : def.red.to) : 0;
  // камера
  const cam = def.cam; const pr = interpolate(frame, [0, Math.max(1, dur - 1)], [0, 1]);
  const z = cam ? cam.z0 + (cam.z1 - cam.z0) * (pr < 0.5 ? 2 * pr * pr : 1 - Math.pow(-2 * pr + 2, 2) / 2) : 1;
  const cx = (cam?.x ?? 0.5) * 1080, cy = (cam?.y ?? 0.5) * 1920;
  const shake = def.shakeCue ? Math.max(0, 1 - (t - cueT(words, def.shakeCue, id)) * 12) * (t >= cueT(words, def.shakeCue, id) ? 1 : 0) : 0;
  const sx = shake ? Math.sin(frame * 9) * 4 * shake : 0, sy = shake ? Math.cos(frame * 11) * 4 * shake : 0;
  return (
    <svg viewBox="0 0 1080 1920" width="100%" height="100%">
      <g transform={`translate(${cx + sx},${cy + sy}) scale(${z}) translate(${-cx},${-cy})`}>
        <g style={{filter: `${def.blur ? `blur(${def.blur}px) ` : ''}${def.dim ? `brightness(${1 - def.dim})` : ''}`.trim() || undefined}}><Bg /></g>
        <Extras def={def} words={words} id={id} />
        {(def.infected ?? []).map((f, i) => <Infected key={i} x={f.x * 1080} y={f.y * 1920 - 612 * (f.h * S) + 0} scale={f.h * S} tilt={f.tilt} opacity={f.opacity} />)}
        {(def.chars ?? []).map((c, i) => {
          let x = c.x, y = c.y ?? 0.8, h = c.h, mood = c.mood, pose = c.pose, op = 1;
          if (c.enter) { const a = cueT(words, c.enter.cue, id); x = interpolate(t, [a, a + c.enter.dur], [c.enter.fromX, c.x], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'}); if (t < a - 0.01) op = 0; }
          if (c.swap && t >= cueT(words, c.swap.cue, id)) { pose = c.swap.pose ?? pose; mood = c.swap.mood ?? mood; }
          if (c.to) { const k = interpolate(t, [0, c.to.dur], [0, 1], {extrapolateRight: 'clamp'}); x += (c.to.x - c.x) * k; y += ((c.to.y ?? y) - y) * k; h += (c.to.h - h) * k; if (c.to.fadeAt !== undefined) op = interpolate(t, [c.to.fadeAt, c.to.fadeAt + 0.3], [1, 0], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'}); }
          const sc = h * S;
          const talking = speaking(c.who);
          const mouth = talking ? 0.3 + 0.6 * Math.abs(Math.sin(t * 16 + i)) * (frame % 4 < 3 ? 1 : 0.4) : 0;
          const blink = (frame + i * 37) % 96 < 3;
          const py = c.portrait ? y * 1920 - 18 * sc : y * 1920 - 612 * sc;
          const el = <Person id={`${id}-${i}-${c.who}`} look={CAST[c.who]} mood={mood ?? 'tired'} pose={pose ?? 'stand'} lookX={c.lookX ?? 0} flip={c.flip}
            x={x * 1080} y={py} scale={sc} mouth={mouth} blink={blink} breath={Math.sin(t * 2.1 + i * 1.3)} lightSide={c.light ?? (x < 0.5 ? 1 : -1)} age={c.who === 'tamara'} />;
          return <g key={i} opacity={op * (c.dim ? 1 - c.dim : 1)}>{c.sil ? <Silhouette>{el}</Silhouette> : el}</g>;
        })}
        <Extras def={def} words={words} id={id} over />
        <Grade red={red} flicker={def.flicker} danger={def.danger} />
      </g>
    </svg>
  );
};

export const ZVideo: React.FC<{script: Script; timeline: Timeline; defs: Record<string, ZDef>}> = ({script, timeline, defs}) => {
  loadFonts();
  const fps = timeline.fps;
  return (
    <AbsoluteFill style={{background: '#000'}}>
      {timeline.audio && <Audio src={staticFile(timeline.audio)} />}
      <Audio src={staticFile('sfx/z_room.wav')} volume={0.07} loop />
      {timeline.scenes.map((s) => {
        const def = defs[s.id]; if (!def) throw new Error(`нет описания сцены ${s.id}`);
        const from = Math.round(s.startSec * fps), dur = Math.max(1, Math.round((s.endSec - s.startSec) * fps));
        const words = s.words.map((w) => ({...w, start: w.start - s.startSec, end: w.end - s.startSec}));
        const sound = def.sound ?? [];
        return (
          <Sequence key={s.id} from={from} durationInFrames={dur}>
            <SceneView def={def} words={words} id={s.id} dur={dur} />
            {def.blackUntil ? <BlackUntil sec={def.blackUntil} /> : null}
            {(def.sfx ?? []).map((fx, i) => <Sequence key={`sfx${i}`} from={Math.round((fx.at ?? cueT(words, fx.cue!, s.id)) * fps)}><Audio src={staticFile(`sfx/z_${fx.name}.wav`)} volume={fx.vol ?? 0.6} /></Sequence>)}
            {(def.ui ?? []).map((u, i) => {
              const C = UI[u.kind]; if (!C) throw new Error(`нет UI «${u.kind}»`);
              const at = u.at ?? (u.cue ? cueT(words, u.cue, s.id) : 0);
              const extra: Record<string, number> = {};
              Object.entries(u.cues ?? {}).forEach(([k, cue]) => { extra[k] = cueT(words, cue, s.id); });
              const node = <C appearAt={at} {...(u.props ?? {})} {...extra} />;
              return u.until ? <Sequence key={i} durationInFrames={Math.round(u.until * fps)}>{node}</Sequence> : <React.Fragment key={i}>{node}</React.Fragment>;
            })}
            {UI.subtitle && <UI.subtitle words={[...words.filter((w) => w.text), ...sound].sort((a, b) => a.start - b.start)} />}
          </Sequence>
        );
      })}
    </AbsoluteFill>
  );
};

const BlackUntil: React.FC<{sec: number}> = ({sec}) => {
  const f = useCurrentFrame(); const {fps} = useVideoConfig();
  return <AbsoluteFill style={{background: '#000', opacity: f / fps < sec ? 1 : 0}} />;
};
