import React from 'react';
import {AbsoluteFill} from 'remotion';
import {FONT} from '../theme';
import {Grade, Person, RoomWindow} from './Flat';

import {MARK, INNA} from './cast';

export const TestScene: React.FC = () => (
  <AbsoluteFill style={{background: '#000'}}>
    <svg viewBox="0 0 1080 1920" width="100%" height="100%">
      <RoomWindow />
      <Person id="mark" look={MARK} mood="tired" pose="notebook" mouth={0} lookX={-6} x={350} y={1440-612*0.98} scale={0.98} lightSide={1} />
      <Person id="inna" look={INNA} mood="fear" pose="mouth" lookX={8} x={745} y={1450-612*0.94} scale={0.94} flip lightSide={-1} />
      <Grade />
    </svg>
    <AbsoluteFill style={{top: '80%', alignItems: 'center'}}>
      <div style={{fontFamily: FONT, fontWeight: 600, fontSize: 48, color: '#ececec', textShadow: '0 3px 10px #000, 0 0 4px #000', textAlign: 'center', padding: '0 70px'}}>Окно на уровне земли. Мы видим двор.</div>
    </AbsoluteFill>
  </AbsoluteFill>
);
