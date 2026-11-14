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
  look: 'cartoon' | 'info' | 'vhs';
  /** Для cartoon: время суток */
  sky?: 'day' | 'dusk';
  /** Для cartoon: плашка-контекст сверху (как «БРЯНСК • КОНТРАКТ») */
  tag?: string;
  /** Оттенок тёмного фона для info: red для блока рисков */
  mood?: 'neutral' | 'danger';
  items?: Item[];
  /** Кто говорит (для выбора голоса в tts.py) */
  speaker?: 'narrator' | 'zhora' | 'gena' | 'tv' | 'thug';
  /** look = 'vhs': 2D-сцена с персонажами или вставка (экран ТВ, книга, дверь…) */
  vhs?: Vhs;
  /** Звуковые эффекты: играют, когда прозвучит слово `cue` */
  sfx?: {name: 'modem' | 'click' | 'rewind' | 'static'; cue: string; volume?: number}[];
};

export type Vhs = {
  bg: 'kitchen' | 'street' | 'door' | 'tv-ad' | 'tv-news' | 'ledger' | 'calendar' | 'title';
  chars?: Char[];
  /** Камера: плавный наезд/отъезд от z0 к z1 вокруг точки (x,y) в долях кадра */
  cam?: {z0: number; z1: number; x: number; y: number};
  data?: {text?: string; lines?: string[]; focus?: string};
};

export type Pose = 'idle' | 'jar' | 'point' | 'shrug' | 'phone' | 'fist' | 'book' | 'panic' | 'crossed';
export type Mood = 'neutral' | 'angry' | 'smug' | 'shock' | 'sad' | 'sweat';
export type Char = {
  who: 'zhora' | 'gena' | 'thug';
  x: number;
  y?: number;
  scale?: number;
  pose?: Pose;
  mood?: Mood;
  talk?: boolean;      // двигает ртом, пока идёт озвучка сцены
  flip?: boolean;
  variant?: number;    // вариации у thug (цвет пиджака, причёска)
};

export type Script = {
  slug: string; title: string; scenes: Scene[];
  /** style 'vhs' включает помехи, таймкод и «пиратские» субтитры */
  style?: 'clean' | 'vhs';
  vhsDate?: string;                       // «14.09.1995» в углу
  music?: {name: 'eurodance'; volume: number};
};

export type Word = {text: string; start: number; end: number; hl: boolean};
export type TimedScene = {id: string; startSec: number; endSec: number; words: Word[]};
export type Timeline = {fps: number; totalSec: number; audio: string | null; scenes: TimedScene[]};
