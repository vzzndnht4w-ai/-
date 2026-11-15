import React from 'react';
import {DoorLeaf, Floor, Glow, Grad, Shade, Skirting, Stains, Wall, WallShade, nz, poly} from './roomKit';

/* ───────── Дверь кухни в конце коридора ───────── */
/** Полотно закрытой двери. */
export const KITCHEN_DOOR = {x: 300, y: 330, w: 480, h: 882};
/**
 * Полоса света — отдельный элемент, легко анимировать (opacity / scaleX / scaleY / тень поверх).
 * ajar: вертикальная щель у косяка; closed: тонкая полоса под дверью (зазор 1212–1230).
 */
export const DOOR_LIGHT_STRIP = {
  ajar: {x: 752, y: 340, w: 16, h: 866},
  closed: {x: 304, y: 1215, w: 472, h: 9},
};

export const DoorLightStrip: React.FC<{kind: 'ajar' | 'closed'; opacity?: number}> = ({kind, opacity = 1}) => {
  const r = DOOR_LIGHT_STRIP[kind];
  return (
    <g id="door-light-strip" opacity={opacity}>
      <defs>
        <Grad id="dl-v" dir="h" stops={[[0, '#ffd58a', 0.55], [0.5, '#fff0c8', 1], [1, '#ffd58a', 0.55]]} />
        <Grad id="dl-h" stops={[[0, '#ffd58a', 0.6], [0.5, '#fff0c8', 1], [1, '#ffd58a', 0.6]]} />
      </defs>
      <rect x={r.x} y={r.y} width={r.w} height={r.h} fill={`url(#${kind === 'ajar' ? 'dl-v' : 'dl-h'})`} />
    </g>
  );
};

const DoorEnd: React.FC<{kind: 'ajar' | 'closed'; strip?: boolean}> = ({kind, strip = true}) => {
  const {x, y, w, h} = KITCHEN_DOOR;
  const ajar = kind === 'ajar';
  return (
    <g>
      <Wall id="kd-w" h={1230} top="#2c3a40" bot="#212c31" paper={0.7} />
      <defs>
        <Grad id="kd-side" dir="h" stops={[[0, '#000', 0.55], [0.22, '#000', 0], [0.78, '#000', 0], [1, '#000', 0.55]]} />
        <Grad id="kd-ceil" stops={[[0, '#000', 0.6], [1, '#000', 0]]} />
        <Grad id="kd-lv" stops={[[0, '#ffd58a', 0.4], [1, '#ffd58a', 0]]} />
        <Grad id="kd-leaf" dir="h" stops={[[0, '#566266'], [0.6, '#4a5558'], [1, '#2a3336']]} />
      </defs>
      <rect width="1080" height="1230" fill="url(#kd-side)" /><rect width="1080" height="420" fill="url(#kd-ceil)" />
      <WallShade y={900} h={330} op={0.1} />
      <Stains x={0} y={200} w={1080} h={900} n={20} seed={21} op={0.13} rx={50} tall />
      <Floor id="kd-fl" kind="lino" c1="#2f2c2a" c2="#14110e" />
      <Skirting x={0} w={256} y={1184} h={46} /><Skirting x={824} w={256} y={1184} h={46} />
      {/* коробка */}
      <rect x={x - 24} y={y - 24} width={w + 48} height={1230 - y + 24} fill="#2c3538" />
      <rect x={x - 24} y={y - 24} width={w + 48} height="6" fill="#6b777a" opacity=".5" />
      <rect x={x - 24} y={y - 24} width="5" height={1230 - y + 24} fill="#6b777a" opacity=".25" />
      {ajar ? (
        <g>
          <rect x={x} y={y} width={w} height={1230 - y} fill="#0a0c0e" />
          {strip && <rect x="720" y={y} width="60" height="880" fill="url(#kd-lv)" opacity=".5" />}
          <polygon points={poly([[x, y], [744, y + 16], [744, 1196], [x, 1212]])} fill="url(#kd-leaf)" />
          <polygon points={poly([[x + 56, y + 70], [700, y + 80], [700, y + 360], [x + 56, y + 350]])} fill="#000" opacity=".16" />
          <polygon points={poly([[x + 56, y + 440], [700, y + 410], [700, y + 790], [x + 56, y + 790]])} fill="#000" opacity=".16" />
          <rect x="740" y={y + 16} width="6" height={866 - 16} fill="#aab1ad" opacity=".28" />
          <path d="M300 330 L300 1212" stroke="#000" strokeOpacity=".4" strokeWidth="5" />
        </g>
      ) : (
        <g>
          <DoorLeaf id="kd-cl" x={x} y={y} w={w} h={h} />
          <rect x={x} y={1212} width={w} height="18" fill="#050607" />
        </g>
      )}
      <rect x={x} y={y + 20} width={w} height="0" />
      <Stains x={x} y={y + 40} w={w} h={h - 60} n={8} seed={34} op={0.22} rx={34} tall />
      {/* свет на полу из-за двери */}
      {strip && (ajar
        ? <polygon points={poly([[744, 1232], [782, 1232], [900, 1520], [650, 1520]])} fill="#ffd58a" opacity=".1" />
        : <polygon points={poly([[300, 1230], [780, 1230], [880, 1360], [200, 1360]])} fill="url(#kd-lv)" opacity=".7" />)}
      {strip && <DoorLightStrip kind={kind} />}
    </g>
  );
};
export const KitchenDoorAjar: React.FC<{strip?: boolean}> = ({strip}) => <DoorEnd kind="ajar" strip={strip} />;
export const KitchenDoorClosed: React.FC<{strip?: boolean}> = ({strip}) => <DoorEnd kind="closed" strip={strip} />;

/* ───────── Комната: стол ровно с тремя стульями ───────── */
const Chair: React.FC<{x: number; flip?: boolean}> = ({x, flip}) => (
  <g transform={flip ? `translate(${2 * x},0) scale(-1,1)` : undefined}>
    <defs><Grad id="tc-wood" dir="h" stops={[[0, '#5b4033'], [1, '#2e211a']]} /></defs>
    <rect x={x - 4} y="1150" width="14" height="148" fill="#2a1d17" /><rect x={x + 168} y="1176" width="14" height="140" fill="#3a281f" />
    <rect x={x - 4} y="880" width="16" height="280" fill="url(#tc-wood)" />
    {[0, 1, 2, 3].map((i) => <rect key={i} x={x + 8} y={900 + i * 52} width="9" height={i % 2 ? 46 : 52} fill="#4a3329" />)}
    <rect x={x - 6} y="1140" width="190" height="24" fill="#4b3429" />
    <rect x={x - 6} y="1140" width="190" height="6" fill="#8a6a55" opacity=".4" />
  </g>
);

export const TableThreeChairs: React.FC = () => (
  <g>
    <defs>
      <Grad id="tc-cloth" stops={[[0, '#8d9893'], [1, '#6e7a77']]} />
      <Grad id="tc-front" stops={[[0, '#5f6a68'], [1, '#3b4543']]} />
      <Grad id="tc-cone" stops={[[0, '#ffd58a', 0.26], [1, '#ffd58a', 0]]} />
    </defs>
    <Wall id="tc-w" h={1230} />
    <WallShade y={880} h={320} />
    <rect x="130" y="360" width="190" height="150" fill="#1a2226" /><rect x="142" y="372" width="166" height="126" fill="#33464c" /><path d="M142 470 Q200 420 250 450 T308 430 V498 H142Z" fill="#202d31" />
    <Floor id="tc-f" />
    <Skirting />
    {/* следы на месте четвёртого стула */}
    <g fill="#000" opacity=".3">{[[452, 1384], [634, 1384], [446, 1456], [640, 1456]].map(([cx, cy], i) => <ellipse key={i} cx={cx} cy={cy} rx="16" ry="6" />)}</g>
    <g stroke="#8a7a6a" strokeOpacity=".16" strokeWidth="3" fill="none" strokeLinecap="round">{[0, 1, 2, 3, 4].map((i) => <path key={i} d={`M${420 + i * 8} ${1374 + i * 18} Q${540 + (i % 2) * 14} ${1360 + i * 20} ${660 - i * 6} ${1378 + i * 17}`} />)}</g>
    {/* стул у дальней стороны */}
    <rect x="482" y="770" width="16" height="240" fill="#3a281f" /><rect x="598" y="770" width="16" height="240" fill="#3a281f" />
    {[790, 850].map((y) => <rect key={y} x="494" y={y} width="108" height="34" fill="#4b3429" />)}
    <rect x="476" y="1000" width="144" height="18" fill="#2e211a" />
    <Chair x={96} /><Chair x={984 - 4} flip />
    {/* лампа над столом — тёплый источник */}
    <rect x="538" y="0" width="4" height="290" fill="#15181b" />
    <polygon points={poly([[490, 380], [590, 380], [758, 1010], [322, 1010]])} fill="url(#tc-cone)" />
    <Glow id="tc-glow" x={540} y={380} r={520} op={0.55} />
    <path d="M492 380 L588 380 L564 292 L516 292Z" fill="#d8a45a" /><path d="M492 380 H588" stroke="#fff" strokeOpacity=".4" strokeWidth="4" /><circle cx="540" cy="384" r="14" fill="#ffe6b0" opacity=".85" />
    {/* стол со скатертью */}
    <polygon points={poly([[300, 1010], [780, 1010], [820, 1100], [260, 1100]])} fill="url(#tc-cloth)" />
    <polygon points={poly([[300, 1010], [780, 1010], [790, 1030], [290, 1030]])} fill="#fff" opacity=".08" />
    <polygon points={poly([[260, 1100], [820, 1100], [838, 1262], [242, 1262]])} fill="url(#tc-front)" />
    {[0, 1, 2, 3, 4, 5].map((i) => <path key={i} d={`M${290 + i * 100} 1102 Q${286 + i * 100 + (i % 2 ? 8 : -8)} 1190 ${284 + i * 100} 1262`} stroke="#000" strokeOpacity=".22" strokeWidth="9" fill="none" />)}
    <path d="M242 1262 Q540 1280 838 1262" stroke="#000" strokeOpacity=".3" strokeWidth="6" fill="none" />
    <ellipse cx="540" cy="1286" rx="340" ry="16" fill="#000" opacity=".3" />
    <g><ellipse cx="610" cy="1058" rx="42" ry="10" fill="#aab1ad" opacity=".7" /><rect x="588" y="1020" width="44" height="38" fill="#c5c9c4" opacity=".85" /><ellipse cx="610" cy="1020" rx="22" ry="6" fill="#3a3a36" /><path d="M632 1030 q18 0 16 14 q-2 10 -16 8" stroke="#c5c9c4" strokeWidth="5" fill="none" opacity=".85" /></g>
    <Stains x={0} y={300} w={1080} h={800} n={14} seed={41} op={0.12} rx={50} tall />
  </g>
);

/* ───────── Глухая внутренняя комната ───────── */
const Mattress: React.FC<{x: number; w: number; blanket: string; k: number}> = ({x, w, blanket, k}) => (
  <g>
    <polygon points={poly([[x + 14, 1238], [x + w - 14, 1238], [x + w + 10, 1336], [x - 10, 1336]])} fill="#6b6f6c" />
    {Array.from({length: 7}, (_, i) => <path key={i} d={`M${x + 24 + i * (w - 48) / 6} 1238 L${x - 6 + i * (w + 12) / 6} 1336`} stroke="#000" strokeOpacity=".12" strokeWidth="9" />)}
    <polygon points={poly([[x - 10, 1336], [x + w + 10, 1336], [x + w + 10, 1358], [x - 10, 1358]])} fill="#3d4240" />
    <polygon points={poly([[x + w * 0.3, 1244], [x + w - 12, 1244], [x + w + 6, 1330], [x + w * 0.26, 1330]])} fill={blanket} />
    <path d={`M${x + w * 0.3} 1244 L${x + w * 0.26} 1330`} stroke="#fff" strokeOpacity=".15" strokeWidth="4" />
    <ellipse cx={x + w * 0.16} cy={1286 + k} rx={w * 0.1} ry="22" fill="#8a8e8b" opacity=".6" />
    <ellipse cx={x + w / 2} cy="1362" rx={w * 0.52} ry="9" fill="#000" opacity=".3" />
  </g>
);

export const InnerRoom: React.FC = () => (
  <g>
    <defs><Grad id="ir-door" dir="h" stops={[[0, '#3f4a4c'], [1, '#272f31']]} /></defs>
    <Wall id="ir-w" h={1230} top="#37464a" bot="#27333a" paper={1.4} />
    <WallShade y={860} h={370} op={0.12} />
    <Stains x={0} y={100} w={1080} h={1000} n={30} seed={51} op={0.14} rx={44} tall />
    <Floor id="ir-f" />
    <Skirting />
    {/* дверь сбоку */}
    <DoorLeaf id="ir-d" x={60} y={560} w={190} h={630} c="#3f4a4c" />
    <circle cx="224" cy="900" r="9" fill="#7b8280" />
    {/* полка справа на высоте груди */}
    <rect x="780" y="900" width="270" height="16" fill="#4a382d" /><rect x="780" y="916" width="270" height="8" fill="#000" opacity=".35" />
    {[810, 1010].map((x) => <path key={x} d={`M${x} 916 V960 L${x + (x < 900 ? 24 : -24)} 916`} stroke="#15181b" strokeWidth="8" fill="none" />)}
    <rect x="930" y="858" width="62" height="42" rx="4" fill="#5d6b66" /><rect x="930" y="858" width="62" height="8" fill="#fff" opacity=".1" /><rect x="842" y="868" width="50" height="32" fill="#46404a" /><rect x="842" y="860" width="50" height="8" fill="#66606a" opacity=".6" />
    <ellipse cx="660" cy="1240" rx="420" ry="12" fill="#000" opacity=".28" />
    <Mattress x={380} w={300} blanket="#6a727a" k={0} /><Mattress x={712} w={300} blanket="#5a5f69" k={4} />
    {/* лампа на табурете — тёплый источник */}
    <Glow id="ir-glow" x={290} y={1030} r={500} op={0.5} />
    <polygon points={poly([[250, 1100], [330, 1100], [440, 1236], [160, 1236]])} fill="#ffd58a" opacity=".05" />
    <rect x="268" y="1120" width="12" height="170" fill="#2a1d17" /><rect x="322" y="1120" width="12" height="164" fill="#2a1d17" /><rect x="260" y="1110" width="82" height="16" rx="4" fill="#4a382d" />
    <Shade x={301} y={1040} s={0.8} glow="1" />
  </g>
);

/* ───────── Старая ванная ───────── */
/** Носик крана: сюда рисовать струю/капли. */
export const TAP_SPOUT = {x: 540, y: 858};

export const BathTap: React.FC = () => (
  <g>
    <defs>
      <pattern id="bt-tile" width="72" height="72" patternUnits="userSpaceOnUse"><rect width="72" height="72" fill="#4c5d5a" /><rect x="3" y="3" width="66" height="30" fill="#fff" opacity=".04" /><path d="M0 0 H72 M0 0 V72" stroke="#10171a" strokeOpacity=".5" strokeWidth="4" /></pattern>
      <Grad id="bt-tg" stops={[[0, '#000', 0.5], [0.5, '#000', 0.1], [1, '#000', 0.4]]} />
      <Grad id="bt-ename" stops={[[0, '#b4c1c0'], [0.5, '#8d9c9c'], [1, '#56625f']]} />
      <Grad id="bt-ped" dir="h" stops={[[0, '#6c7a79'], [0.4, '#a6b3b2'], [1, '#56625f']]} />
      <Grad id="bt-metal" dir="h" stops={[[0, '#5d6668'], [0.4, '#c9d2d2'], [1, '#444c4e']]} />
    </defs>
    <rect width="1080" height="1230" fill="url(#bt-tile)" /><rect width="1080" height="1230" fill="url(#bt-tg)" />
    <rect width="1080" height="300" fill="#222d2c" /><rect y="296" width="1080" height="12" fill="#10171a" /><rect y="308" width="1080" height="4" fill="#8aa09b" opacity=".18" />
    <Stains x={0} y={320} w={1080} h={860} n={26} seed={61} op={0.15} rx={36} tall />
    <Floor id="bt-f" kind="tile" c1="#37423f" c2="#141a1b" />
    <Skirting c="#10171a" />
    {/* ванна на заднем плане */}
    <rect x="-10" y="936" width="450" height="30" fill="#9eacab" /><rect x="-10" y="936" width="450" height="12" fill="#10171a" opacity=".6" />
    <path d="M-10 966 H440 L420 1170 Q400 1196 370 1196 H60 Q20 1196 -10 1170Z" fill="url(#bt-ename)" />
    <ellipse cx="170" cy="1100" rx="80" ry="22" fill="#3a2f27" opacity=".12" />
    {[[90, 1040], [320, 1000], [260, 1130], [60, 1110]].map(([x, y], i) => <path key={i} d={`M${x} ${y} l${10 + i * 3} ${-4 + i} l-3 ${12 + i}Z`} fill="#2e2a26" opacity=".55" />)}
    <rect x="50" y="1194" width="46" height="30" fill="#2a3234" /><rect x="360" y="1194" width="46" height="30" fill="#2a3234" />
    <rect x="30" y="850" width="26" height="86" fill="url(#bt-metal)" /><path d="M43 850 Q43 820 90 826" stroke="#aab1ad" strokeWidth="14" fill="none" strokeLinecap="round" />
    {/* трубы справа */}
    <rect x="936" y="300" width="26" height="940" fill="url(#bt-metal)" /><rect x="986" y="300" width="20" height="940" fill="url(#bt-metal)" opacity=".8" />
    {[470, 900].map((y) => <rect key={y} x="926" y={y} width="86" height="18" fill="#3c4547" />)}
    {/* раковина на пьедестале */}
    <path d="M498 1000 Q490 1100 480 1230 H600 Q590 1100 582 1000Z" fill="url(#bt-ped)" />
    <ellipse cx="540" cy="1232" rx="86" ry="12" fill="#000" opacity=".35" />
    <path d="M404 906 Q410 1000 540 1030 Q670 1000 676 906Z" fill="url(#bt-ped)" />
    <ellipse cx="540" cy="906" rx="136" ry="30" fill="#c0cccb" /><ellipse cx="540" cy="910" rx="112" ry="22" fill="#5a6866" /><ellipse cx="540" cy="916" rx="12" ry="5" fill="#1c2425" />
    <rect x="404" y="900" width="272" height="6" fill="#fff" opacity=".12" />
    {/* кран */}
    <rect x="522" y="800" width="36" height="76" fill="url(#bt-metal)" /><rect x="530" y="858" width="20" height="14" fill="#1c2425" opacity=".5" />
    <rect x="532" y="760" width="16" height="50" fill="url(#bt-metal)" /><rect x="520" y="740" width="40" height="30" rx="10" fill="url(#bt-metal)" />
    {[-1, 1].map((s) => <g key={s}><rect x={540 + s * 70 - 8} y="868" width="16" height="30" fill="#6c7678" /><rect x={540 + s * 70 - 30} y="860" width="60" height="12" rx="6" fill="url(#bt-metal)" /></g>)}
    <rect x="470" y="880" width="140" height="6" fill="#000" opacity=".25" />
    {/* пластиковый табурет */}
    <ellipse cx="380" cy="1440" rx="70" ry="12" fill="#000" opacity=".3" />
    {[-44, 44].map((dx) => <rect key={dx} x={380 + dx - 6} y="1352" width="12" height="88" fill="#6f8289" />)}
    <ellipse cx="380" cy="1346" rx="70" ry="18" fill="#9bb0b6" /><ellipse cx="380" cy="1340" rx="70" ry="18" fill="#b2c4c9" /><ellipse cx="380" cy="1340" rx="40" ry="9" fill="#9bb0b6" />
    {/* голая лампочка — тёплый источник */}
    <rect x="538" y="0" width="4" height="150" fill="#15181b" /><Glow id="bt-glow" x={540} y={190} r={640} op={0.5} /><circle cx="540" cy="168" r="22" fill="#ffe6b0" /><rect x="526" y="140" width="28" height="22" fill="#2a2a2a" />
    {Array.from({length: 6}, (_, i) => <circle key={i} cx={100 + nz(i, 7) * 880} cy={330 + nz(i, 8) * 500} r="4" fill="#fff" opacity=".05" />)}
  </g>
);
