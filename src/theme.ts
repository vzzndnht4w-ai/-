import {staticFile} from 'remotion';
import type {Tone} from './types';

export const FONT = "'VF Montserrat', 'Montserrat', sans-serif";
export const COLORS: Record<Tone, string> = {
  info: '#f5c518',   // жёлтый — нейтральная информация
  good: '#22e07a',   // зелёный — плюсы
  bad: '#ff4d5e',    // красный — риски
  accent: '#ffffff',
};
export const BG = {neutral: '#0b0e14', danger: '#16090c'};

let loaded = false;
export const loadFonts = () => {
  if (loaded || typeof document === 'undefined') return;
  loaded = true;
  const faces: [string, string, string][] = [
    ['cyrillic', '600', 'U+0301,U+0400-045F,U+0490-0491,U+04B0-04B1,U+2116'],
    ['latin', '600', 'U+0000-00FF,U+0131,U+0152-0153,U+2013-2014,U+2018-201D,U+2022,U+2026,U+20AC,U+2122,U+2212'],
    ['cyrillic', '800', 'U+0301,U+0400-045F,U+0490-0491,U+04B0-04B1,U+2116'],
    ['cyrillic', '900', 'U+0301,U+0400-045F,U+0490-0491,U+04B0-04B1,U+2116'],
    ['latin', '800', 'U+0000-00FF,U+0131,U+0152-0153,U+2013-2014,U+2018-201D,U+2022,U+2026,U+20AC,U+2122,U+2212'],
    ['latin', '900', 'U+0000-00FF,U+0131,U+0152-0153,U+2013-2014,U+2018-201D,U+2022,U+2026,U+20AC,U+2122,U+2212'],
    ['latin-ext', '900', 'U+0100-02BA,U+02BD-02C5,U+02C7-02CC,U+02CE-02D7,U+02DD-02FF,U+0304,U+0308,U+0329,U+1D00-1DBF,U+1E00-1E9F,U+1EF2-1EFF,U+2020,U+20A0-20AB,U+20AD-20C0,U+2113,U+2C60-2C7F,U+A720-A7FF'],
  ];
  faces.forEach(([sub, w, range]) => {
    const f = new FontFace('VF Montserrat', `url(${staticFile(`fonts/montserrat-${sub}-${w}-normal.woff2`)})`, {
      weight: w, unicodeRange: range,
    });
    f.load().then((ff) => (document.fonts as any).add(ff));
  });
};
