export type Tone = 'info' | 'good' | 'bad' | 'accent';

/** Один элемент инфографики. Появляется, когда в озвучке прозвучало слово `cue`. */
export type Item =
  | {kind: 'pill'; text: string; sub?: string; tone?: Tone; cue: string}
  | {kind: 'number'; text: string; sub?: string; tone?: Tone; cue: string}
  | {kind: 'bar'; text: string; value: number; tone?: Tone; cue: string}
  | {kind: 'title'; text: string; tone?: Tone; cue: string};

export type Scene = {
  id: string;
  /** Текст озвучки этой сцены. Ключевые слова для плашки субтитров — в *звёздочках*. */
  text: string;
  /** cartoon = мультяшная сцена, info = тёмный фон с инфографикой */
  look: 'cartoon' | 'info';
  /** Для cartoon: время суток */
  sky?: 'day' | 'dusk';
  /** Для cartoon: плашка-контекст сверху (как «БРЯНСК • КОНТРАКТ») */
  tag?: string;
  /** Оттенок тёмного фона для info: red для блока рисков */
  mood?: 'neutral' | 'danger';
  items?: Item[];
};

export type Script = {slug: string; title: string; scenes: Scene[]};

export type Word = {text: string; start: number; end: number; hl: boolean};
export type TimedScene = {id: string; startSec: number; endSec: number; words: Word[]};
export type Timeline = {fps: number; totalSec: number; audio: string | null; scenes: TimedScene[]};
