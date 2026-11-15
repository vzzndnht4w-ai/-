import React from 'react';
import {Disclaimer, InfoTag, RulePlate, Subtitle, TitleCard} from './ui/Text';
import {Hud} from './ui/Hud';
import {FlatPlan, LightStrip} from './ui/Plans';

/** Реестр интерфейсных элементов серии (плашки, HUD, схема). Ключ — имя элемента, см. ep01_storyboard.md. */
export const UI: Record<string, React.FC<any>> = {
  rule_plate: RulePlate,
  disclaimer: Disclaimer,
  hud: Hud,
  info_tag: InfoTag,
  flat_plan: FlatPlan,
  subtitle: Subtitle,
  light_strip: LightStrip,
  title_card: TitleCard,
};
