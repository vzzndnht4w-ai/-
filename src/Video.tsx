import React from 'react';
import {AbsoluteFill, Audio, Sequence, staticFile} from 'remotion';
import {BG, loadFonts} from './theme';
import {Captions} from './components/Captions';
import {Cartoon} from './components/Cartoon';
import {Items} from './components/Items';
import {itemTimes, scenesOf} from './lib/timing';
import type {Script, Timeline} from './types';

export type VideoProps = {script: Script; timeline: Timeline};

export const Video: React.FC<VideoProps> = ({script, timeline}) => {
  loadFonts();
  const scenes = scenesOf(script, timeline);
  return (
    <AbsoluteFill style={{background: BG.neutral}}>
      {timeline.audio && <Audio src={staticFile(timeline.audio)} />}
      {scenes.map((s) => {
        const from = Math.round(s.startSec * timeline.fps);
        const dur = Math.max(1, Math.round((s.endSec - s.startSec) * timeline.fps));
        // внутри <Sequence> время локальное: сдвигаем слова и триггеры на начало сцены
        const words = s.words.map((w) => ({...w, start: w.start - s.startSec, end: w.end - s.startSec}));
        const times = s.def.items ? itemTimes(s.def.items, words, 0) : [];
        return (
          <Sequence key={s.id} from={from} durationInFrames={dur}>
            {s.def.look === 'cartoon'
              ? <Cartoon sky={s.def.sky} tag={s.def.tag} />
              : <AbsoluteFill style={{background: s.def.mood === 'danger' ? BG.danger : BG.neutral}} />}
            {s.def.items && <Items items={s.def.items} times={times} />}
            <Captions words={words} />
          </Sequence>
        );
      })}
    </AbsoluteFill>
  );
};
