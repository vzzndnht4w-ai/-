import React from 'react';
import {RoomWindow} from './Flat';
import {Glow, Grad, Stains, makePersp, nz, poly} from './roomKit';

/** Окно ПОСЛЕ: та же геометрия, что RoomWindow (поверх него — плотная штора с одеялом и щели света). */
export const WindowSealed: React.FC = () => (
  <g>
    <RoomWindow />
    <defs>
      <Grad id="sl-cur" dir="h" stops={[[0, '#2a2a2f'], [0.2, '#3a383e'], [0.4, '#232227'], [0.62, '#3d3a40'], [0.8, '#26252a'], [1, '#34323a']]} />
      <Grad id="sl-slit" stops={[[0, '#b9cde0', 0.0], [0.08, '#b9cde0', 0.9], [0.92, '#9fb8d0', 0.7], [1, '#9fb8d0', 0]]} />
      <Grad id="sl-lamp" dir="h" stops={[[0, '#ffc878', 0], [1, '#ffc878', 0.22]]} />
      <Grad id="sl-fold" dir="h" stops={[[0, '#000', 0.5], [0.5, '#000', 0], [1, '#fff', 0.07]]} />
    </defs>
    {/* гасим лунное пятно на полу: окно закрыто */}
    <path d="M300 1236 L780 1236 L1020 1920 L120 1920Z" fill="#1a120f" opacity=".82" />
    {/* карниз и штора поверх окна и старой шторы */}
    <rect x="150" y="232" width="780" height="22" rx="10" fill="#1e1814" />
    <path d="M176 250 H900 L892 1030 Q540 1048 186 1030Z" fill="url(#sl-cur)" />
    {[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11].map((i) => {
      const x = 196 + i * 62;
      return <path key={i} d={`M${x} 254 Q${x + 12 * (i % 2 ? 1 : -1)} 640 ${x} 1030`} stroke={i % 2 ? '#fff' : '#000'} strokeOpacity={i % 2 ? 0.05 : 0.38} strokeWidth="14" fill="none" />;
    })}
    {/* одеяло, прижатое к подоконнику, и лента-фиксатор */}
    <path d="M180 930 Q540 880 900 930 L892 1034 Q540 1054 186 1034Z" fill="#454751" />
    <path d="M180 930 Q540 880 900 930" stroke="#6d7080" strokeOpacity=".5" strokeWidth="4" fill="none" />
    <path d="M200 960 Q540 920 880 960 M200 996 Q540 960 880 996" stroke="#000" strokeOpacity=".25" strokeWidth="5" fill="none" />
    <rect x="496" y="262" width="88" height="24" fill="#6a6a62" opacity=".55" />
    {/* щели света: правый край и верхний левый угол */}
    <rect x="886" y="290" width="12" height="640" fill="url(#sl-slit)" />
    <rect x="176" y="270" width="8" height="260" fill="url(#sl-slit)" opacity=".7" />
    <path d="M180 1034 L898 1034 L930 1100 L150 1100Z" fill="#9fb8d0" opacity=".05" />
    {/* тёплый отсвет торшера на шторе */}
    <rect x="176" y="250" width="724" height="790" fill="url(#sl-lamp)" />
    <rect x="176" y="250" width="724" height="790" fill="#000" opacity=".12" />
  </g>
);

const Bush: React.FC<{x: number; y: number; s: number; seed: number}> = ({x, y, s, seed}) => (
  <g transform={`translate(${x},${y}) scale(${s})`} stroke="#090c10" fill="none" strokeLinecap="round">
    {Array.from({length: 16}, (_, i) => {
      const a = -Math.PI / 2 + (i - 7.5) * 0.17 + (nz(i, seed) - 0.5) * 0.3;
      const L = 230 + nz(i, seed + 1) * 170;
      const mx = Math.cos(a) * L * 0.55, my = Math.sin(a) * L * 0.55;
      const ex = Math.cos(a + 0.3) * L, ey = Math.sin(a + 0.3) * L;
      const f = a + 0.3 + (nz(i, seed + 2) - 0.5) * 1.2;
      return <g key={i}><path d={`M0 0 Q${mx + 12} ${my} ${ex} ${ey}`} strokeWidth={9 - (i % 3) * 2} />
        <path d={`M${mx} ${my} l${Math.cos(f) * 90} ${Math.sin(f) * 90}`} strokeWidth="4" />
        <path d={`M${ex} ${ey} l${Math.cos(f - 0.8) * 60} ${Math.sin(f - 0.8) * 60}`} strokeWidth="3" /></g>;
    })}
  </g>
);

/** Окно первого этажа панельного дома снаружи, из двора. lit=true — «аквариум», false — тёмное, зашторено. */
const Facade: React.FC<{lit: boolean}> = ({lit}) => {
  const wx = 290, wy = 590, ww = 500, wh = 470; // рама
  const dark = (x: number, y: number, w: number, h: number, k: string) => (
    <g key={k}><rect x={x - 14} y={y - 14} width={w + 28} height={h + 28} fill="#aab1ad" opacity=".42" /><rect x={x} y={y} width={w} height={h} fill="#080d13" />
      <path d={`M${x + 20} ${y + h} L${x + w * 0.55} ${y} L${x + w * 0.75} ${y} L${x + w * 0.2 + 20} ${y + h}Z`} fill="#6f8aa6" opacity=".06" />
      <rect x={x + w / 2 - 4} y={y} width="8" height={h} fill="#aab1ad" opacity=".4" /></g>
  );
  return (
    <g>
      <defs>
        <Grad id="fa-wall" stops={[[0, '#232b33'], [0.6, '#323c44'], [1, '#2a333a']]} />
        <Grad id="fa-gr" stops={[[0, '#1c2227'], [0.4, '#12161a'], [1, '#090b0e']]} />
        <Grad id="fa-int" stops={[[0, '#2d3c44'], [1, '#3e5159']]} />
        <Grad id="fa-flr" stops={[[0, '#3a2a22'], [1, '#1a120f']]} />
        <Grad id="fa-sky" dir="d" stops={[[0, '#2c4a6a', 0.55], [1, '#0a1018', 0.2]]} />
        <Grad id="fa-spill" stops={[[0, '#ffd58a', 0.34], [1, '#ffd58a', 0]]} />
        <Grad id="fa-cur" dir="h" stops={[[0, '#0f1318'], [0.2, '#1a2027'], [0.4, '#0c1014'], [0.62, '#1b2128'], [0.82, '#0d1115'], [1, '#161b21']]} />
        <clipPath id="fa-glass"><rect x={wx + 26} y={wy + 26} width={ww - 52} height={wh - 52} /></clipPath>
      </defs>
      <rect width="1080" height="1230" fill="url(#fa-wall)" />
      {/* стыки панелей и потёки */}
      {[330, 1150].map((y) => <g key={y}><rect y={y} width="1080" height="8" fill="#000" opacity=".4" /><rect y={y + 8} width="1080" height="3" fill="#8fa0a8" opacity=".1" /></g>)}
      {[120, 960].map((x) => <g key={x}><rect x={x} width="8" height="1150" fill="#000" opacity=".35" /><rect x={x + 8} width="3" height="1150" fill="#8fa0a8" opacity=".08" /></g>)}
      <Stains x={0} y={300} w={1080} h={800} n={26} seed={5} op={0.16} rx={40} tall />
      <rect y="1150" width="1080" height="80" fill="#1b2127" /><rect y="1150" width="1080" height="5" fill="#586870" opacity=".4" />
      {/* соседние окна: тёмные */}
      {dark(-70, 590, 170, 470, 'l')}{dark(960, 590, 170, 470, 'r')}
      {dark(wx, 130, ww, 330, 'u')}
      {/* окно: рама, стекло */}
      <rect x={wx - 16} y={wy - 16} width={ww + 32} height={wh + 32} fill="#4b575d" opacity=".5" />
      <rect x={wx} y={wy} width={ww} height={wh} fill="#aab1ad" /><rect x={wx} y={wy} width={ww} height={wh} fill="#000" opacity=".3" />
      <g clipPath="url(#fa-glass)">
        {lit ? (
          <g>
            <rect x="300" y="600" width="500" height="460" fill="url(#fa-int)" />
            <rect x="300" y="600" width="500" height="70" fill="#000" opacity=".35" />
            <rect x="300" y="940" width="500" height="120" fill="url(#fa-flr)" />
            <rect x="300" y="934" width="500" height="10" fill="#1d2326" />
            {/* проём в коридор */}
            <rect x="338" y="690" width="110" height="250" fill="#070b10" /><rect x="338" y="690" width="110" height="250" fill="none" stroke="#aab1ad" strokeOpacity=".3" strokeWidth="8" />
            <rect x="360" y="780" width="60" height="160" fill="#0e1822" />
            {/* шкаф со светом лампы, диван, стол */}
            <rect x="650" y="730" width="140" height="212" fill="#161c20" /><rect x="650" y="730" width="140" height="8" fill="#3a464a" />
            <rect x="474" y="866" width="150" height="76" rx="14" fill="#1a2227" /><rect x="474" y="846" width="150" height="34" rx="12" fill="#222c32" />
            <rect x="560" y="900" width="70" height="8" fill="#000" opacity=".3" />
            <Glow id="fa-lamp" x={716} y={720} r={230} op={0.85} />
            <g transform="translate(716,722)"><path d="M-30 0 L30 0 L20 -44 L-20 -44Z" fill="#d8a45a" /><rect x="-4" y="0" width="8" height="10" fill="#15181b" /></g>
            <path d="M326 620 Q352 760 330 930 M456 620 Q440 700 452 800" stroke="#a8b6bf" strokeOpacity=".18" strokeWidth="14" fill="none" />
          </g>
        ) : (
          <g>
            <rect x="300" y="600" width="500" height="460" fill="#06090d" />
            <rect x="316" y="616" width="470" height="430" fill="url(#fa-cur)" />
            {[0, 1, 2, 3, 4, 5, 6, 7].map((i) => <path key={i} d={`M${340 + i * 58} 616 Q${352 + i * 58} 830 ${340 + i * 58} 1040`} stroke="#000" strokeOpacity=".5" strokeWidth="10" fill="none" />)}
          </g>
        )}
        <path d="M316 1034 L560 616 L640 616 L396 1034Z M600 1034 L760 760 L760 880 L690 1034Z" fill="url(#fa-sky)" opacity=".7" />
      </g>
      <path d="M540 616 V1034 M316 800 H764" stroke="#aab1ad" strokeWidth="14" /><path d="M540 616 V1034 M316 800 H764" stroke="#000" strokeWidth="14" opacity=".3" />
      <rect x={wx + 26} y={wy + 26} width={ww - 52} height={wh - 52} fill="none" stroke="#c9cfca" strokeWidth="6" opacity=".45" />
      {/* отлив и сопли ржавчины */}
      <rect x={wx - 36} y={wy + wh} width={ww + 72} height="22" fill="#6c7679" /><rect x={wx - 36} y={wy + wh + 22} width={ww + 72} height="8" fill="#000" opacity=".4" />
      <Stains x={wx} y={wy + wh + 30} w={ww} h={90} n={10} seed={8} color="#1a1410" op={0.35} rx={24} tall />
      {/* земля */}
      <rect y="1230" width="1080" height="690" fill="url(#fa-gr)" /><rect y="1224" width="1080" height="12" fill="#000" opacity=".5" />
      {[[210, 1470, 190, 28], [800, 1380, 150, 20], [520, 1640, 260, 34]].map(([x, y, rx, ry], i) => <ellipse key={i} cx={x} cy={y} rx={rx} ry={ry} fill="#1e3248" opacity=".5" />)}
      {lit && <><path d="M300 1236 L800 1236 L980 1700 L130 1700Z" fill="url(#fa-spill)" /><Glow id="fa-halo" x={540} y={820} r={560} op={0.22} sy={0.9} /></>}
      <path d="M540 1260 L560 1900" stroke="#000" strokeOpacity=".3" strokeWidth="6" />
      {/* голые кусты у стены */}
      <Bush x={90} y={1290} s={1} seed={3} /><Bush x={1010} y={1270} s={0.8} seed={9} />
      <polygon points={poly([[0, 1230], [40, 1236], [0, 1260]])} fill="#000" />
    </g>
  );
};
export const FacadeAquarium: React.FC = () => <Facade lit />;
export const FacadeDark: React.FC = () => <Facade lit={false} />;

/** Узкий коридор: вдали открытый проём на тёмную кухню с распахнутым окном. */
export const HallKitchenOpen: React.FC = () => {
  const P = makePersp(540, 770, 0.37);
  const W = 540, H = 1150;
  const q = (...pts: [number, number, number][]) => poly(pts.map(([X, Y, z]) => P(X, Y, z)));
  const [fx0, fy0] = P(-W, -H, 1), [fx1, fy1] = P(W, H, 1);
  const coat = (z: number, c: string, i: number) => (
    <g key={i}><polygon points={q([W - 6, -300, z - 0.03], [W - 6, -300, z + 0.03], [W - 80, 100, z + 0.045], [W - 70, 520, z + 0.035], [W - 80, 520, z - 0.035], [W - 80, 90, z - 0.045])} fill={c} />
      <polygon points={q([W - 6, -300, z - 0.03], [W - 6, -300, z + 0.03], [W - 80, 100, z + 0.045], [W - 80, 90, z - 0.045])} fill="#000" opacity=".25" />
      <circle cx={P(W - 4, -320, z)[0]} cy={P(W - 4, -320, z)[1]} r="5" fill="#9aa4a6" /></g>
  );
  return (
    <g>
      <defs>
        <Grad id="hl-l" dir="h" stops={[[0, '#2a3538'], [1, '#202a2e']]} />
        <Grad id="hl-r" dir="h" stops={[[0, '#1a2327'], [1, '#2a353a']]} />
        <Grad id="hl-c" stops={[[0, '#10171b'], [1, '#222c30']]} />
        <Grad id="hl-f" stops={[[0, '#2f2c2a'], [1, '#17130f']]} />
        <Grad id="hl-far" stops={[[0, '#2a363a'], [1, '#1f292d']]} />
        <Grad id="hl-night" stops={[[0, '#16263a'], [1, '#2f4e6e']]} />
        <Grad id="hl-door" dir="h" stops={[[0, '#44504f'], [1, '#2c3638']]} />
      </defs>
      <rect width="1080" height="1920" fill="#10161a" />
      <polygon points={q([-W, -H, 0], [W, -H, 0], [W, -H, 1], [-W, -H, 1])} fill="url(#hl-c)" />
      <polygon points={q([-W, -H, 0], [-W, -H, 1], [-W, H, 1], [-W, H, 0])} fill="url(#hl-l)" />
      <polygon points={q([W, -H, 0], [W, -H, 1], [W, H, 1], [W, H, 0])} fill="url(#hl-r)" />
      <polygon points={q([-W, H, 0], [W, H, 0], [W, H, 1], [-W, H, 1])} fill="url(#hl-f)" />
      <rect x={fx0} y={fy0} width={fx1 - fx0} height={fy1 - fy0} fill="url(#hl-far)" />
      {/* линолеум: продольные швы и поперечные плашки */}
      {[-360, -180, 0, 180, 360].map((X) => <path key={X} d={`M${P(X, H, 0)[0]} ${P(X, H, 0)[1]} L${P(X, H, 1)[0]} ${P(X, H, 1)[1]}`} stroke="#000" strokeOpacity=".3" strokeWidth="4" />)}
      {[0.08, 0.2, 0.36, 0.55, 0.78].map((z) => <path key={z} d={`M${P(-W, H, z)[0]} ${P(-W, H, z)[1]} L${P(W, H, z)[0]} ${P(W, H, z)[1]}`} stroke="#000" strokeOpacity=".18" strokeWidth="3" />)}
      {/* плинтус */}
      <polygon points={q([-W, 1030, 0], [-W, H, 0], [-W, H, 1], [-W, 1030, 1])} fill="#161d20" /><polygon points={q([W, 1030, 0], [W, H, 0], [W, H, 1], [W, 1030, 1])} fill="#161d20" />
      {/* дверь в комнату на левой стене */}
      <polygon points={q([-W, -560, 0.34], [-W, -560, 0.62], [-W, H - 60, 0.62], [-W, H - 60, 0.34])} fill="url(#hl-door)" />
      <polygon points={q([-W + 2, -450, 0.38], [-W + 2, -450, 0.58], [-W + 2, 100, 0.58], [-W + 2, 100, 0.38])} fill="#000" opacity=".16" />
      <polygon points={q([-W + 2, 250, 0.38], [-W + 2, 250, 0.58], [-W + 2, 950, 0.58], [-W + 2, 950, 0.38])} fill="#000" opacity=".16" />
      {/* вешалка и пальто справа */}
      <polygon points={q([W, -340, 0.06], [W - 16, -340, 0.06], [W - 16, -320, 0.6], [W, -320, 0.6])} fill="#12171a" />
      {coat(0.14, '#2a3238', 0)}{coat(0.26, '#352f2c', 1)}{coat(0.4, '#222a30', 2)}
      <polygon points={q([W, 700, 0.1], [W - 6, 700, 0.1], [W - 6, 700, 0.7], [W, 700, 0.7])} fill="#0e1316" />
      {/* дальняя стена: проём на кухню */}
      <rect x="410" y="500" width="260" height="700" fill="#aab1ad" opacity=".25" />
      <rect x="426" y="516" width="228" height="684" fill="#070b10" />
      <rect x="426" y="516" width="228" height="684" fill="none" stroke="#000" strokeWidth="6" opacity=".5" />
      <rect x="426" y="1100" width="228" height="95" fill="#15130f" />
      {/* кухня: окно настежь, штора на ветру */}<g transform="translate(7 -60) scale(1.15 1.15) translate(-71 -0)">
      <rect x="505" y="672" width="72" height="118" fill="url(#hl-night)" />
      <path d="M505 672 L474 652 L474 792 L505 790Z" fill="#9fb8d0" opacity=".38" /><path d="M505 672 L474 652 L474 792 L505 790Z" fill="none" stroke="#aab1ad" strokeWidth="3" opacity=".7" />
      <path d="M505 666 H577 M541 672 V790" stroke="#aab1ad" strokeWidth="4" opacity=".5" />
      <path d="M578 664 Q556 720 586 760 Q566 780 580 800 L596 800 Q604 760 584 720 Q600 690 592 664Z" fill="#a9b8c4" opacity=".4" />
      <rect x="486" y="930" width="46" height="60" fill="#0b0f12" /><rect x="570" y="900" width="32" height="90" fill="#0b0f12" /></g>
      {/* настенная лампа — тёплый источник */}
      {(() => { const [sx, sy] = P(-W, -420, 0.15); return <g><Glow id="hl-glow" x={sx + 40} y={sy} r={330} op={0.5} />
        <polygon points={q([-W, -460, 0.13], [-W, -460, 0.17], [-W + 40, -380, 0.17], [-W + 40, -380, 0.13])} fill="#d8a45a" /></g>; })()}
      <Stains x={0} y={300} w={1080} h={900} n={18} seed={12} op={0.14} rx={50} tall />
    </g>
  );
};
