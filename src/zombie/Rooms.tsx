import React from 'react';
import {RoomWindow} from './Flat';

/**
 * Реестр фонов серии. Ключ = id из series/zombie/ep01_assets.json (bg_*).
 * Каждый фон — <g> в системе координат 1080×1920; пол начинается примерно с y=1230, ноги героев ~y=1440.
 * Свет/виньетку/зерно НЕ рисовать здесь — их накладывает <Grade/> поверх сцены.
 */
export const BACKGROUNDS: Record<string, React.FC> = {
  bg_window_yard: () => <RoomWindow open />,
};
