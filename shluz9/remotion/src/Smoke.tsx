import React from 'react';
import {AbsoluteFill, interpolate, useCurrentFrame, Easing} from 'remotion';
export const Smoke: React.FC = () => {
  const f = useCurrentFrame();
  const o = interpolate(f, [0, 20], [0, 1], {easing: Easing.out(Easing.cubic), extrapolateRight: 'clamp'});
  return (
    <AbsoluteFill style={{background: '#06100d', justifyContent: 'center', alignItems: 'center'}}>
      <div style={{color: '#3cff8a', fontSize: 120, opacity: o, fontFamily: 'DejaVu Sans'}}>ШЛЮЗ 9</div>
    </AbsoluteFill>
  );
};
