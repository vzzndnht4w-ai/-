import React from 'react';
import {AbsoluteFill, useCurrentFrame, useVideoConfig} from 'remotion';
import {FONT} from '../theme';

/** Детерминированный «шум» от номера кадра (рендер обязан быть повторяемым). */
export const hash = (n: number) => { const x = Math.sin(n * 127.1 + 311.7) * 43758.5453; return x - Math.floor(x); };

/** Дёрганая частота кадров: возвращает номер кадра, «замороженный» до rate к/с. */
export const useStep = (rate = 10) => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  return Math.floor(frame / (fps / rate));
};

/** Тряска всей картинки + выцветание. Оборачивает контент сцены. */
export const Shake: React.FC<{children: React.ReactNode}> = ({children}) => {
  const frame = useCurrentFrame();
  const dx = (hash(frame) - 0.5) * 5;
  const dy = (hash(frame + 99) - 0.5) * 4;
  return <AbsoluteFill style={{transform: `translate(${dx}px, ${dy}px)`, filter: 'saturate(.72) contrast(1.12) brightness(.96) sepia(.12)'}}>{children}</AbsoluteFill>;
};

/** Помехи трекинга сверху/снизу, строчки, шум, виньетка, таймкод PLAY ► дата. */
export const VhsOverlay: React.FC<{date: string}> = ({date}) => {
  const frame = useCurrentFrame();
  const {fps, width, height} = useVideoConfig();
  const k = width / 1080;
  const sec = Math.floor(frame / fps);
  const tc = `${String(Math.floor(sec / 60)).padStart(2, '0')}:${String(sec % 60).padStart(2, '0')}`;
  // полосы трекинга: нижняя всегда есть и «ползёт», верхняя — вспышками
  const botH = (70 + 40 * hash(Math.floor(frame / 3))) * k;
  const topOn = hash(Math.floor(frame / 12) + 7) > 0.55;
  const topH = (24 + 50 * hash(Math.floor(frame / 2) + 3)) * k;
  const bar = (h: number, pos: 'top' | 'bottom', seed: number): React.CSSProperties => ({
    position: 'absolute', left: 0, right: 0, [pos]: 0, height: h,
    background: `repeating-linear-gradient(90deg, rgba(255,255,255,.${6 + Math.floor(hash(seed) * 3)}) 0 ${10 * k}px, rgba(0,0,0,.55) ${10 * k}px ${22 * k}px)`,
    mixBlendMode: 'screen', transform: `translateX(${(hash(seed + 1) - 0.5) * 60 * k}px)`, opacity: 0.85,
  });
  const noiseX = Math.floor(hash(frame) * 200);
  return (
    <AbsoluteFill style={{pointerEvents: 'none'}}>
      {/* строчки */}
      <AbsoluteFill style={{background: `repeating-linear-gradient(0deg, rgba(0,0,0,.18) 0 ${2 * k}px, transparent ${2 * k}px ${4 * k}px)`}} />
      {/* зерно */}
      <AbsoluteFill style={{opacity: 0.10, backgroundImage: 'url("data:image/svg+xml;utf8,<svg xmlns=\'http://www.w3.org/2000/svg\' width=\'200\' height=\'200\'><filter id=\'n\'><feTurbulence baseFrequency=\'.9\' numOctaves=\'2\' seed=\'3\'/></filter><rect width=\'200\' height=\'200\' filter=\'url(%23n)\'/></svg>")', backgroundPosition: `${noiseX}px ${noiseX / 2}px`}} />
      {/* виньетка */}
      <AbsoluteFill style={{background: 'radial-gradient(ellipse at center, transparent 55%, rgba(0,0,0,.5) 100%)'}} />
      <div style={bar(botH, 'bottom', frame)} />
      {topOn && <div style={bar(topH, 'top', frame + 500)} />}
      {/* цветовой «разъезд» полосы */}
      <div style={{position: 'absolute', left: 0, right: 0, bottom: botH, height: 5 * k, background: 'rgba(255,0,60,.35)', mixBlendMode: 'screen'}} />
      {/* таймкод */}
      <div style={{position: 'absolute', top: 64 * k, left: 54 * k, fontFamily: FONT, fontWeight: 800, fontSize: 40 * k, color: '#fff',
        textShadow: `${3 * k}px 0 rgba(255,0,60,.7), ${-3 * k}px 0 rgba(0,200,255,.6)`, letterSpacing: 2}}>
        PLAY ► {date}
      </div>
      <div style={{position: 'absolute', top: 64 * k, right: 54 * k, fontFamily: FONT, fontWeight: 800, fontSize: 40 * k, color: '#fff',
        textShadow: `${3 * k}px 0 rgba(255,0,60,.7), ${-3 * k}px 0 rgba(0,200,255,.6)`}}>{tc}</div>
    </AbsoluteFill>
  );
};
