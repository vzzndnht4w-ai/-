import React from 'react';
import {AbsoluteFill} from 'remotion';
import {FONT} from '../theme';
import {Grade, Person, RoomWindow, type Look} from './Flat';

export const MARK: Look = {skin: '#d9a784', hair: '#1d1a19', top: '#586a4e', inner: '#8a8f94', pants: '#4a525c', style: 'short', stubble: true};
export const INNA: Look = {skin: '#e4b99a', hair: '#2a1d17', top: '#6a7b6c', inner: '#a9a8a2', pants: '#2c3036', style: 'bun', width: 0.92};

export const TestScene: React.FC = () => (
  <AbsoluteFill style={{background: '#000'}}>
    <svg viewBox="0 0 1080 1920" width="100%" height="100%">
      <RoomWindow />
      <Person id="mark" look={MARK} mood="tired" pose="notebook" lookX={-6} x={350} y={1440-612*0.98} scale={0.98} lightSide={1} />
      <Person id="inna" look={INNA} mood="fear" pose="mouth" lookX={8} x={745} y={1450-612*0.94} scale={0.94} flip lightSide={-1} />
      <Grade />
    </svg>
    <AbsoluteFill style={{top: '80%', alignItems: 'center'}}>
      <div style={{fontFamily: FONT, fontWeight: 600, fontSize: 48, color: '#ececec', textShadow: '0 3px 10px #000, 0 0 4px #000', textAlign: 'center', padding: '0 70px'}}>Окно на уровне земли. Мы видим двор.</div>
    </AbsoluteFill>
  </AbsoluteFill>
);
