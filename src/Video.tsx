import React from 'react';
import {AbsoluteFill, Audio, Sequence, staticFile, useCurrentFrame} from 'remotion';
import {BG, loadFonts} from './theme';
import {Captions} from './components/Captions';
import {Cartoon} from './components/Cartoon';
import {Items} from './components/Items';
import {VhsScene} from './components/Characters';
import {Shake, VhsOverlay} from './components/Vhs';
import {itemTimes, scenesOf} from './lib/timing';
import type {Script, Timeline} from './types';

export type VideoProps = {script: Script; timeline: Timeline};

/** Идёт ли сейчас речь (для движения рта у персонажей). */
const SpeakingCtx = (words: {start: number; end: number}[], fps: number) => {
  const f = useCurrentFrame();
  const t = f / fps;
  return words.some((w) => t >= w.start && t <= w.end + 0.08);
};
const speaking = SpeakingCtx;

export const Video: React.FC<VideoProps> = ({script, timeline}) => {
  loadFonts();
  const scenes = scenesOf(script, timeline);
  const fps = timeline.fps;
  return (
    <AbsoluteFill style={{background: BG.neutral}}>
      {timeline.audio && <Audio src={staticFile(timeline.audio)} />}
      {script.music && <Audio src={staticFile(`sfx/${script.music.name}.wav`)} volume={script.music.volume} loop />}
      {scenes.map((s) => {
        const from = Math.round(s.startSec * timeline.fps);
        const dur = Math.max(1, Math.round((s.endSec - s.startSec) * timeline.fps));
        // внутри <Sequence> время локальное: сдвигаем слова и триггеры на начало сцены
        const words = s.words.map((w) => ({...w, start: w.start - s.startSec, end: w.end - s.startSec}));
        const times = s.def.items ? itemTimes(s.def.items, words, 0) : [];
        return (
          <Sequence key={s.id} from={from} durationInFrames={dur}>
            {s.def.look === 'vhs' && s.def.vhs
              ? <Shake><VhsScene bg={s.def.vhs.bg} chars={s.def.vhs.chars} speaking={speaking(words, fps)} /></Shake>
              : s.def.look === 'cartoon'
                ? <Cartoon sky={s.def.sky} tag={s.def.tag} />
                : <AbsoluteFill style={{background: s.def.mood === 'danger' ? BG.danger : BG.neutral}} />}
            {s.def.items && <Items items={s.def.items} times={times} />}
            {(s.def.sfx ?? []).map((fx, i) => {
              const at = itemTimes([{kind: 'title', text: fx.name, cue: fx.cue}], words, 0)[0];
              return <Sequence key={i} from={Math.round(at * fps)}><Audio src={staticFile(`sfx/${fx.name}.wav`)} volume={fx.volume ?? 0.7} /></Sequence>;
            })}
            <Captions words={words} pirate={script.style === 'vhs'} />
          </Sequence>
        );
      })}
      {script.style === 'vhs' && <VhsOverlay date={script.vhsDate ?? '14.09.1995'} />}
    </AbsoluteFill>
  );
};
