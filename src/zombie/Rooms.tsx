import React from 'react';
import {RoomWindow} from './Flat';
import {BathTap, InnerRoom, KitchenDoorAjar, KitchenDoorClosed, TableThreeChairs} from './BgRooms';
import {FacadeAquarium, FacadeDark, HallKitchenOpen, WindowSealed} from './BgWindows';

/**
 * Реестр фонов серии. Ключ = id из series/zombie/ep01_assets.json (bg_*).
 * Каждый фон — <g> в системе координат 1080×1920; пол начинается примерно с y=1230, ноги героев ~y=1440.
 * Свет/виньетку/зерно НЕ рисовать здесь — их накладывает <Grade/> поверх сцены.
 */
export const BACKGROUNDS: Record<string, React.FC> = {
  bg_window_yard: () => <RoomWindow open />,
  bg_window_sealed: WindowSealed,
  bg_facade_aquarium: FacadeAquarium,
  bg_facade_dark: FacadeDark,
  bg_hall_kitchen_open: HallKitchenOpen,
  bg_kitchen_door_ajar: () => <KitchenDoorAjar />,
  bg_kitchen_door_closed: () => <KitchenDoorClosed />,
  bg_table_three_chairs: TableThreeChairs,
  bg_inner_room: InnerRoom,
  bg_bath_tap: BathTap,
};
