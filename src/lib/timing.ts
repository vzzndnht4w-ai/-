import type {Item, Script, TimedScene, Timeline, Word} from '../types';

export const norm = (s: string) => s.toLowerCase().replace(/[^\p{L}\p{N}]/gu, '');

/** Время появления элемента (сек) = начало слова-триггера `cue`. Ищем строго вперёд по тексту. */
export function itemTimes(items: Item[], words: Word[], sceneStart: number): number[] {
  let from = 0;
  return items.map((it) => {
    const c = norm(it.cue);
    let idx = words.findIndex((w, i) => i >= from && norm(w.text).includes(c));
    if (idx < 0) idx = words.findIndex((w) => norm(w.text).includes(c));
    if (idx < 0) {
      throw new Error(`Не нашёл слово-триггер «${it.cue}» в озвучке сцены (элемент «${it.text}»)`);
    }
    from = idx;
    return words[idx].start;
  });
}

/** Разбиение слов на субтитровые блоки: до 3 слов / ~18 знаков, перенос после знаков препинания. */
export function chunkWords(words: Word[]): Word[][] {
  const out: Word[][] = [];
  let cur: Word[] = [];
  const len = () => cur.reduce((n, w) => n + w.text.length + 1, 0);
  words.forEach((w) => {
    if (cur.length && (cur.length >= 3 || len() + w.text.length > 18)) { out.push(cur); cur = []; }
    cur.push(w);
    if (/[,.!?…:;—]$/.test(w.text)) { out.push(cur); cur = []; }
  });
  if (cur.length) out.push(cur);
  return out;
}

export const scenesOf = (script: Script, tl: Timeline): (TimedScene & {def: Script['scenes'][number]})[] =>
  tl.scenes.map((t) => {
    const def = script.scenes.find((s) => s.id === t.id);
    if (!def) throw new Error(`В timeline.json есть сцена ${t.id}, которой нет в script.json — перезапусти scripts/tts.py`);
    return {...t, def};
  });
