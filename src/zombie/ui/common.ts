import {interpolate, useCurrentFrame, useVideoConfig} from 'remotion';

export const INK = '#C9D3D6';
export const PANEL = '#0B0F12';
export const AMBER = '#E0A030';
export const BLOOD = '#8C1C1C';
export const RED = '#C0392B';
export const STEEL = '#4A5659';

/** Вход: fade + небольшой сдвиг вверх. t — секунды с момента появления. */
export const useAppear = (appearAt = 0, dur = 0.35, shift = 14) => {
  const frame = useCurrentFrame();
  const {fps, width, height} = useVideoConfig();
  const k = width / 1080;
  const t = frame / fps - appearAt;
  const p = interpolate(t, [0, dur], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
  const e = 1 - Math.pow(1 - p, 3);
  return {frame, fps, width, height, k, t, visible: t >= 0, o: e, dy: (1 - e) * shift * k};
};
