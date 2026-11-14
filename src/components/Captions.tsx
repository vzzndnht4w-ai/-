import React from 'react';
import {AbsoluteFill, useCurrentFrame, useVideoConfig} from 'remotion';
import {FONT} from '../theme';
import {chunkWords} from '../lib/timing';
import type {Word} from '../types';

/** Субтитры по 2–3 слова: текущее слово — на жёлтой плашке, сказанные — белые, будущие — серые. */
export const Captions: React.FC<{words: Word[]; top?: string; pirate?: boolean}> = ({words, top = '66%', pirate}) => {
  const frame = useCurrentFrame();
  const {fps, width} = useVideoConfig();
  const t = frame / fps;
  const chunks = chunkWords(words);
  let ci = chunks.findIndex((c, i) => t >= c[0].start && (i === chunks.length - 1 || t < chunks[i + 1][0].start));
  if (ci < 0) return null;
  const chunk = chunks[ci];
  if (t > chunk[chunk.length - 1].end + 0.35) return null;
  const k = width / 1080;
  if (pirate) {
    // «пиратский перевод» 90-х: огромный жёлтый текст с чёрной обводкой, без плашек, по 2 строки
    const text = chunk.map((w) => w.text).join(' ');
    return (
      <AbsoluteFill style={{top: '70%', alignItems: 'center', padding: `0 ${40 * k}px`}}>
        <div style={{fontFamily: FONT, fontWeight: 900, fontSize: 104 * k, lineHeight: 1.08, color: '#ffe500', textAlign: 'center',
          textTransform: 'uppercase', WebkitTextStroke: `${9 * k}px #000`, paintOrder: 'stroke fill',
          textShadow: `${5 * k}px ${5 * k}px 0 #000`}}>{text}</div>
      </AbsoluteFill>
    );
  }
  return (
    <AbsoluteFill style={{top, alignItems: 'center', justifyContent: 'flex-start', padding: `0 ${60 * k}px`}}>
      <div style={{display: 'flex', flexWrap: 'wrap', justifyContent: 'center', gap: `${8 * k}px ${20 * k}px`,
        fontFamily: FONT, fontWeight: 900, fontSize: 92 * k, lineHeight: 1.15, textTransform: 'uppercase',
        textShadow: `0 ${6 * k}px ${24 * k}px rgba(0,0,0,.65)`}}>
        {chunk.map((w, i) => {
          const spoken = t >= w.start;
          const active = spoken && t < w.end + 0.05;
          return (
            <span key={i} style={{
              color: active ? '#111' : spoken ? '#fff' : 'rgba(255,255,255,.38)',
              background: active ? '#f5c518' : 'transparent',
              padding: `0 ${14 * k}px`, borderRadius: 14 * k,
            }}>{w.text}</span>
          );
        })}
      </div>
    </AbsoluteFill>
  );
};
