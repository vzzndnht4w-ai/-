import React from 'react';
import {AbsoluteFill, interpolate, spring, useCurrentFrame, useVideoConfig} from 'remotion';
import {COLORS, FONT} from '../theme';
import type {Item} from '../types';

const useIn = (at: number) => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const p = spring({frame: frame - Math.round(at * fps), fps, config: {damping: 14, stiffness: 140}});
  return {p, visible: frame >= Math.round(at * fps)};
};

const One: React.FC<{item: Item; at: number; k: number}> = ({item, at, k}) => {
  const {p, visible} = useIn(at);
  if (!visible) return null;
  const tone = item.tone ?? 'info';
  const color = COLORS[tone];
  const base: React.CSSProperties = {
    fontFamily: FONT, fontWeight: 900, textTransform: 'uppercase', textAlign: 'center',
    opacity: p, transform: `translateY(${(1 - p) * 40 * k}px) scale(${0.92 + 0.08 * p})`,
  };
  const glow = `0 0 ${18 * k}px ${color}99, 0 0 ${3 * k}px ${color}`;
  if (item.kind === 'title') {
    return <div style={{...base, fontSize: 70 * k, color, textShadow: glow, letterSpacing: 1}}>{item.text}</div>;
  }
  if (item.kind === 'number') {
    return (
      <div style={{...base, color}}>
        <div style={{fontSize: 130 * k, lineHeight: 1.1, textShadow: glow}}>{item.text}</div>
        {item.sub && <div style={{display: 'inline-block', marginTop: 8 * k, fontSize: 28 * k, color: '#fff',
          border: '2px solid #ffffff88', borderRadius: 12 * k, padding: `${6 * k}px ${18 * k}px`}}>{item.sub}</div>}
      </div>
    );
  }
  if (item.kind === 'bar') {
    return (
      <div style={{...base, textAlign: 'left', width: '100%'}}>
        <div style={{fontSize: 32 * k, color, textShadow: glow, marginBottom: 10 * k}}>{item.text}</div>
        <div style={{height: 22 * k, borderRadius: 12 * k, background: '#ffffff18'}}>
          <div style={{height: '100%', width: `${item.value * 100 * p}%`, borderRadius: 12 * k, background: color,
            boxShadow: glow}} />
        </div>
      </div>
    );
  }
  // pill
  return (
    <div style={{...base, border: `${4 * k}px solid ${tone === 'info' ? '#ffffffcc' : color}`, borderRadius: 22 * k,
      padding: `${20 * k}px ${34 * k}px`, background: '#0b0e14cc', boxShadow: `0 0 ${24 * k}px ${color}55`,
      color: '#fff', fontSize: 46 * k, width: '100%'}}>
      {item.text}
      {item.sub && <div style={{fontSize: 24 * k, color: '#ffffffaa', marginTop: 4 * k}}>{item.sub}</div>}
    </div>
  );
};

export const Items: React.FC<{items: Item[]; times: number[]}> = ({items, times}) => {
  const {width} = useVideoConfig();
  const k = width / 1080;
  return (
    <AbsoluteFill style={{top: 110 * k, bottom: '42%', padding: `0 ${70 * k}px`, display: 'flex',
      flexDirection: 'column', alignItems: 'center', gap: 22 * k}}>
      {items.map((it, i) => <One key={i} item={it} at={times[i]} k={k} />)}
    </AbsoluteFill>
  );
};
