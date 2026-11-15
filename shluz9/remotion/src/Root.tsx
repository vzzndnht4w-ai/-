import React from 'react';
import {Composition} from 'remotion';
import {Smoke} from './Smoke';
import {LottieTest} from './LottieTest';
export const Root: React.FC = () => (
  <>
    <Composition id="Smoke" component={Smoke} durationInFrames={30} fps={30} width={1080} height={1920} />
    <Composition id="LottieTest" component={LottieTest} durationInFrames={60} fps={30} width={400} height={400} />
  </>
);
