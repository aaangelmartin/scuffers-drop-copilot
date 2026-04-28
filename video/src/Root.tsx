import React from 'react';
import { Composition } from 'remotion';
import { ScuffersVideo, TOTAL_DURATION, FPS, WIDTH, HEIGHT } from './ScuffersVideo';

export const RemotionRoot: React.FC = () => {
  return (
    <>
      <Composition
        id="ScuffersVideo"
        component={ScuffersVideo}
        durationInFrames={TOTAL_DURATION}
        fps={FPS}
        width={WIDTH}
        height={HEIGHT}
      />
    </>
  );
};
