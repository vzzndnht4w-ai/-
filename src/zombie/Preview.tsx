import React from 'react';
import {AbsoluteFill} from 'remotion';
import {Grade} from './Flat';
import {BACKGROUNDS} from './Rooms';
import {UI} from './Ui';
import {loadFonts} from '../theme';

/** Предпросмотр одного фона (props: {id}) — для проверки стилей: remotion still ... zroom out/x.png --props='{"id":"bg_inner_room"}' */
export const RoomPreview: React.FC<{id: string}> = ({id}) => {
  const Bg = BACKGROUNDS[id];
  return (
    <AbsoluteFill style={{background: '#000'}}>
      <svg viewBox="0 0 1080 1920" width="100%" height="100%">{Bg ? <><Bg /><Grade /></> : null}</svg>
    </AbsoluteFill>
  );
};

/** Предпросмотр UI-элемента (props: {id, props}) на тёмном фоне. */
export const UiPreview: React.FC<{id: string; props?: Record<string, unknown>; bg?: string}> = ({id, props, bg}) => {
  loadFonts();
  const C = UI[id];
  return (
    <AbsoluteFill style={{background: bg ?? '#0a1018'}}>
      {C ? <C {...(props ?? {})} /> : null}
    </AbsoluteFill>
  );
};
