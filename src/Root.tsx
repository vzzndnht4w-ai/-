import React from 'react';
import {Composition, staticFile} from 'remotion';
import {Video, VideoProps} from './Video';
import type {Script, Timeline} from './types';

/**
 * Каждое видео = папка videos/<slug>/ с script.json и timeline.json (его делает scripts/tts.py).
 * Список видео генерируется скриптом scripts/render.mjs → src/videos.generated.ts.
 */
import {VIDEOS} from './videos.generated';

export const Root: React.FC = () => (
  <>
    {Object.entries(VIDEOS).map(([slug, v]) => {
      const script = v.script as unknown as Script;
      const timeline = v.timeline as unknown as Timeline;
      return (
        <Composition<any, VideoProps>
          key={slug}
          id={slug}
          component={Video}
          width={1080}
          height={1920}
          fps={timeline.fps}
          durationInFrames={Math.max(1, Math.ceil(timeline.totalSec * timeline.fps))}
          defaultProps={{script, timeline}}
        />
      );
    })}
  </>
);
