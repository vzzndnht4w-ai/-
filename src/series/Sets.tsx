import React from 'react';
import {AbsoluteFill, interpolate, useCurrentFrame, useVideoConfig} from 'remotion';
import {FONT} from '../theme';
import {hash, useStep} from '../components/Vhs';
import {Character, Wobble} from './Rig';
import type {Char, Vhs} from '../types';

const INK = '#121212';
const L = {stroke: INK, strokeWidth: 7, strokeLinejoin: 'round' as const, strokeLinecap: 'round' as const};

/* ===================== фоны с персонажами ===================== */
const Kitchen: React.FC = () => (
  <g>
    <rect width="1080" height="1920" fill="#d8c79a" />
    {Array.from({length: 14}).map((_, i) => <rect key={i} x={i * 80} y="0" width="40" height="760" fill="#cdbb8b" />)}
    <rect y="720" width="1080" height="560" fill="#5f7f4c" /><rect y="712" width="1080" height="18" fill="#e9e1c4" {...L} strokeWidth={4} />
    {Array.from({length: 9}).map((_, i) => <path key={i} d={`M${i * 130} 730 L${i * 130} 1280`} stroke="#4c6a3c" strokeWidth="4" />)}
    {/* пол */}
    {Array.from({length: 14}).map((_, r) => Array.from({length: 9}).map((__, c) => <rect key={r + '-' + c} x={c * 130 - (r % 2) * 65} y={1280 + r * 52} width="130" height="52" fill={(r + c) % 2 ? '#8a7a60' : '#6f604c'} />))}
    <rect y="1270" width="1080" height="20" fill="#2f281f" opacity=".6" />
    {/* окно со шторой */}
    <rect x="330" y="230" width="300" height="380" fill="#1b2548" {...L} />
    {[[380, 300], [470, 360], [560, 280], [420, 480], [540, 520]].map(([x, y], i) => <rect key={i} x={x} y={y} width="16" height="22" fill="#ffd96a" />)}
    <path d="M330 230 Q380 420 340 610 L430 610 Q400 420 450 230Z" fill="#d6862a" {...L} strokeWidth={5} /><path d="M630 230 Q580 420 620 610 L530 610 Q560 420 510 230Z" fill="#d6862a" {...L} strokeWidth={5} />
    <path d="M480 230 L480 610" stroke={INK} strokeWidth="6" />
    {/* холодильник */}
    <rect x="-30" y="380" width="230" height="900" rx="18" fill="#e9e5d6" {...L} /><path d="M-30 760 L200 760" stroke={INK} strokeWidth="6" />
    <rect x="165" y="470" width="14" height="150" rx="6" fill="#aaa" {...L} strokeWidth={4} /><rect x="165" y="800" width="14" height="190" rx="6" fill="#aaa" {...L} strokeWidth={4} />
    <rect x="30" y="440" width="90" height="70" fill="#f6e08a" stroke={INK} strokeWidth="4" /><circle cx="140" cy="560" r="16" fill="#c43030" stroke={INK} strokeWidth="3" />
    {/* полка и телевизор */}
    <rect x="700" y="650" width="360" height="26" fill="#7a5a34" {...L} />
    <rect x="740" y="410" width="270" height="240" rx="18" fill="#3a3a3a" {...L} /><rect x="762" y="432" width="190" height="196" rx="30" fill="#4d7a73" stroke={INK} strokeWidth="4" />
    <circle cx="980" cy="470" r="10" fill="#999" /><circle cx="980" cy="520" r="10" fill="#999" />
    <path d="M830 410 L790 330 M900 410 L950 320" stroke={INK} strokeWidth="6" />
    {/* столешница + чайник */}
    <rect x="200" y="1020" width="880" height="40" fill="#b79c6a" {...L} /><rect x="200" y="1060" width="880" height="220" fill="#7d6a4a" {...L} />
    <path d="M880 1020 Q870 940 920 930 Q970 940 960 1020Z" fill="#c9442d" {...L} /><path d="M960 980 Q1010 960 1000 1010" fill="none" {...L} />
    {/* лампа */}
    <path d="M540 0 L540 130" stroke={INK} strokeWidth="6" /><path d="M470 190 Q540 90 610 190Z" fill="#d6c46a" {...L} />
    <ellipse cx="540" cy="200" rx="440" ry="620" fill="url(#lamp)" opacity=".55" />
    <defs><radialGradient id="lamp"><stop offset="0" stopColor="#ffe9a0" stopOpacity=".75" /><stop offset="1" stopColor="#ffe9a0" stopOpacity="0" /></radialGradient></defs>
  </g>
);

const Street: React.FC = () => (
  <g>
    <defs><linearGradient id="dusk" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stopColor="#3b3560" /><stop offset=".6" stopColor="#c9805a" /><stop offset="1" stopColor="#e8b27a" /></linearGradient></defs>
    <rect width="1080" height="1300" fill="url(#dusk)" />
    {/* панельная многоэтажка */}
    <rect x="-20" y="120" width="1120" height="1160" fill="#8b8d93" {...L} />
    {Array.from({length: 9}).map((_, r) => Array.from({length: 6}).map((__, c) => {
      const lit = hash(r * 7 + c * 3 + 1) > 0.55;
      return <g key={r + '-' + c}><rect x={30 + c * 176} y={170 + r * 120} width="110" height="84" fill={lit ? '#ffd96a' : '#2b3550'} {...L} strokeWidth={5} /><path d={`M${85 + c * 176} ${170 + r * 120} L${85 + c * 176} ${254 + r * 120}`} stroke={INK} strokeWidth="4" /></g>;
    }))}
    {Array.from({length: 7}).map((_, i) => <path key={i} d={`M-20 ${200 + i * 160} L1100 ${200 + i * 160}`} stroke="#6f7178" strokeWidth="3" />)}
    <rect y="1280" width="1080" height="640" fill="#4a4a52" />
    <rect y="1280" width="1080" height="30" fill="#6c6c74" {...L} strokeWidth={4} />
    <ellipse cx="760" cy="1640" rx="240" ry="40" fill="#8fa6c4" opacity=".5" /><ellipse cx="260" cy="1760" rx="170" ry="28" fill="#8fa6c4" opacity=".4" />
    {/* фонарь */}
    <path d="M1010 1290 L1010 700" stroke={INK} strokeWidth="18" /><path d="M1010 700 Q960 680 920 700" fill="none" stroke={INK} strokeWidth="14" /><ellipse cx="920" cy="708" rx="36" ry="14" fill="#ffe08a" {...L} />
  </g>
);

export const VhsScene: React.FC<{vhs: Vhs; speaking: boolean}> = ({vhs, speaking}) => {
  const step = useStep(10);
  const chars: Char[] = vhs.chars ?? [];
  return (
    <svg viewBox="0 0 1080 1920" width="100%" height="100%" preserveAspectRatio="xMidYMid slice">
      <defs><Wobble seed={Math.floor(step / 2) % 7} /></defs>
      <g filter="url(#wob)">
        {vhs.bg === 'kitchen' ? <Kitchen /> : <Street />}
        {chars.map((c, i) => <Character key={i} c={c} speaking={speaking} step={step} />)}
      </g>
    </svg>
  );
};

/* ===================== вставки на весь кадр ===================== */
const Crt: React.FC<{children: React.ReactNode; step: number}> = ({children, step}) => (
  <g>
    <rect x="30" y="300" width="1020" height="860" rx="60" fill="#5a4630" {...L} />
    <rect x="30" y="300" width="1020" height="860" rx="60" fill="none" stroke="#7d6244" strokeWidth="14" opacity=".6" />
    <clipPath id="scr"><rect x="90" y="360" width="900" height="680" rx="70" /></clipPath>
    <g clipPath="url(#scr)">{children}</g>
    <rect x="90" y="360" width="900" height="680" rx="70" fill="none" stroke={INK} strokeWidth="10" />
    <path d="M140 400 Q300 380 420 400" fill="none" stroke="#fff" strokeWidth="10" opacity=".25" strokeLinecap="round" />
    {[0, 1, 2].map((i) => <circle key={i} cx={150 + i * 80} cy="1100" r="22" fill="#222" {...L} strokeWidth={4} />)}
    <rect x="780" y="1085" width="200" height="26" rx="6" fill="#222" {...L} strokeWidth={4} />
    <path d="M400 300 L300 150 M680 300 L790 140" stroke={INK} strokeWidth="10" strokeLinecap="round" />
    <rect x="200" y="1160" width="680" height="30" fill="#3a2d1e" {...L} strokeWidth={5} />
  </g>
);

const Announcer: React.FC<{talk: boolean; step: number; suit: string; tie: string; hair: string}> = ({talk, step, suit, tie, hair}) => {
  const open = talk && step % 2 === 0;
  return (
    <g transform={`translate(0,${talk && step % 2 ? -6 : 0})`}>
      <path d="M-190 330 Q-200 130 0 110 Q200 130 190 330Z" fill={suit} {...L} />
      <path d="M-40 118 L0 230 L40 118Z" fill="#f4f0e0" {...L} strokeWidth={5} /><path d="M0 150 L-16 230 L0 330 L16 230Z" fill={tie} {...L} strokeWidth={5} />
      <ellipse cx="0" cy="0" rx="92" ry="108" fill="#f0b98d" {...L} />
      <path d="M-98 -20 Q-110 -130 0 -132 Q110 -130 98 -20 Q80 -80 0 -78 Q-80 -80 -98 -20Z" fill={hair} {...L} />
      <circle cx="-36" cy="-4" r="11" fill="#fff" {...L} strokeWidth={4} /><circle cx="36" cy="-4" r="11" fill="#fff" {...L} strokeWidth={4} /><circle cx="-34" cy="-2" r="5" fill={INK} /><circle cx="38" cy="-2" r="5" fill={INK} />
      <path d="M-52 -30 L-20 -34 M52 -30 L20 -34" {...L} strokeWidth={8} />
      <path d="M-6 6 Q-24 44 0 48 Q22 46 6 6" fill="#e59a6a" {...L} strokeWidth={5} />
      <g transform="translate(0,72)">{open
        ? <g><path d="M-52 -6 Q0 52 52 -6 Q0 -20 -52 -6Z" fill="#4a0f1a" {...L} strokeWidth={5} /><rect x="-42" y="-8" width="84" height="12" fill="#fff" /></g>
        : <g><path d="M-52 -4 Q0 40 52 -4 Q0 -16 -52 -4Z" fill="#fff" {...L} strokeWidth={5} /><path d="M-40 4 L40 4" stroke={INK} strokeWidth="3" /></g>}</g>
    </g>
  );
};

const TvAd: React.FC<{text: string; speaking: boolean}> = ({text, speaking}) => {
  const step = useStep(10);
  const frame = useCurrentFrame();
  return (
    <g>
      <rect width="1080" height="1920" fill="#2a1e2e" />
      <Crt step={step}>
        <rect x="90" y="360" width="900" height="680" fill="#18206b" />
        {Array.from({length: 18}).map((_, i) => <polygon key={i} points="540,700 1700,700 1700,740" fill={i % 2 ? '#f2c230' : '#e0482a'} opacity=".5" transform={`rotate(${i * 20 + frame * 1.4} 540 700)`} />)}
        <g transform="translate(540,640)"><Announcer talk={speaking} step={step} suit="#2c3d8f" tie="#e0482a" hair="#2a1e14" /></g>
        <rect x="90" y="360" width="900" height="110" fill="#0d1246" opacity=".85" />
        <text x="540" y="438" textAnchor="middle" fontFamily={FONT} fontWeight={900} fontSize="62" fill="#ffd33a" stroke={INK} strokeWidth="3">{text}</text>
        <g transform={`translate(780,${770 + Math.sin(frame * 0.35) * 14}) rotate(${Math.sin(frame * 0.2) * 8})`}>
          <circle r="108" fill="#e0482a" {...L} /><text y="34" textAnchor="middle" fontFamily={FONT} fontWeight={900} fontSize="108" fill="#fff" stroke={INK} strokeWidth="4">х3</text>
        </g>
        {[0, 1, 2, 3].map((i) => <g key={i} transform={`translate(${150 + i * 50},${960 - ((frame * 4 + i * 50) % 120)})`}><circle r="22" fill="#f2c230" {...L} strokeWidth={4} /><text y="8" textAnchor="middle" fontFamily={FONT} fontWeight={900} fontSize="24" fill={INK}>₽</text></g>)}
        <rect x="90" y="975" width="900" height="65" fill="#0d1246" opacity=".9" />
        <text x={990 - ((frame * 8) % 2000)} y="1020" fontFamily={FONT} fontWeight={800} fontSize="34" fill="#fff">ТЕЛЕФОН ДЛЯ ВКЛАДЧИКОВ: 000-00-00 · ГАРАНТИЯ ЧЕСТНОГО СЛОВА · ТЕЛЕФОН ДЛЯ ВКЛАДЧИКОВ: 000-00-00</text>
      </Crt>
    </g>
  );
};

const TvNews: React.FC<{text: string; speaking: boolean}> = ({text, speaking}) => {
  const step = useStep(10);
  const frame = useCurrentFrame();
  return (
    <g>
      <rect width="1080" height="1920" fill="#2a1e2e" />
      <Crt step={step}>
        <rect x="90" y="360" width="900" height="680" fill="#2a58a8" />
        <rect x="90" y="760" width="900" height="280" fill="#16346a" />
        <g transform="translate(540,640)"><Announcer talk={speaking} step={step} suit="#3a3a40" tie="#9a1d2a" hair="#6a6a6a" /></g>
        <rect x="120" y="390" width="250" height="60" fill="#d0262e" {...L} strokeWidth={4} /><text x="245" y="436" textAnchor="middle" fontFamily={FONT} fontWeight={900} fontSize="38" fill="#fff">НОВОСТИ</text>
        <rect x="90" y="950" width="900" height="90" fill="#d0262e" /><text x={990 - ((frame * 9) % 1800)} y="1010" fontFamily={FONT} fontWeight={900} fontSize="48" fill="#fff">{text} · {text}</text>
      </Crt>
    </g>
  );
};

const Ledger: React.FC<{lines: string[]}> = ({lines}) => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const t = frame / fps;
  return (
    <g>
      <rect width="1080" height="1920" fill="#4a3a2a" />
      <g transform="rotate(-2 540 760)">
        <rect x="40" y="240" width="1000" height="1000" fill="#7a5a34" {...L} />
        <rect x="70" y="270" width="940" height="940" fill="#efe6c8" />
        {Array.from({length: 14}).map((_, i) => <path key={i} d={`M90 ${340 + i * 62} L990 ${340 + i * 62}`} stroke="#8a95a8" strokeWidth="3" />)}
        <path d="M200 270 L200 1210 M790 270 L790 1210" stroke="#c34a4a" strokeWidth="4" />
        <ellipse cx="860" cy="1100" rx="68" ry="62" fill="none" stroke="#8a6a3a" strokeWidth="8" opacity=".35" />
        {lines.map((ln, i) => {
          const at = 0.5 + i * 0.9;
          const p = interpolate(t, [at, at + 0.7], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
          const last = i === lines.length - 2;
          return (
            <g key={i} opacity={p > 0 ? 1 : 0}>
              <clipPath id={`ln${i}`}><rect x="90" y={310 + i * 150} width={900 * p} height="120" /></clipPath>
              <text x="106" y={392 + i * 150} fontFamily={FONT} fontWeight={800} fontSize={last ? 84 : 54} fill={i === lines.length - 1 ? '#2b4aa0' : '#b01212'} clipPath={`url(#ln${i})`} transform={`rotate(${(i % 2 ? 0.8 : -0.6)} 540 ${392 + i * 150})`}>{ln}</text>
              {last && p > 0.9 && <path d={`M110 ${412 + i * 150} L${110 + 780 * Math.min(1, (t - at - 0.7) * 4)} ${412 + i * 150}`} stroke="#b01212" strokeWidth="8" />}
            </g>
          );
        })}
        {/* капли пота на странице */}
        {[0, 1, 2].map((i) => { const d = ((t * 260 + i * 330) % 900); return <ellipse key={i} cx={300 + i * 250} cy={300 + d} rx="14" ry="20" fill="#8fd3f4" opacity={.65} stroke={INK} strokeWidth="3" />; })}
      </g>
    </g>
  );
};

const Calendar: React.FC<{text: string}> = ({text}) => {
  const frame = useCurrentFrame();
  const day = Math.min(7, Math.floor(frame / 6));
  const phase = (frame % 6) / 6;
  return (
    <g>
      <rect width="1080" height="1920" fill="#c9b78a" />
      {Array.from({length: 14}).map((_, i) => <rect key={i} x={i * 80} y="0" width="40" height="1920" fill="#bda977" />)}
      <rect x="180" y="260" width="720" height="860" rx="14" fill="#f4eed8" {...L} />
      <rect x="180" y="260" width="720" height="150" fill="#b0123f" {...L} /><text x="540" y="368" textAnchor="middle" fontFamily={FONT} fontWeight={900} fontSize="88" fill="#fff">СЕНТЯБРЬ</text>
      {Array.from({length: 14}).map((_, i) => { const d = 14 + i; const cx = 270 + (i % 7) * 90, cy = 520 + Math.floor(i / 7) * 150;
        return <g key={i}><text x={cx} y={cy} textAnchor="middle" fontFamily={FONT} fontWeight={800} fontSize="52" fill={INK}>{d}</text>
          {i <= day && i < 7 && <path d={`M${cx - 34} ${cy - 44} L${cx + 34} ${cy + 14} M${cx + 34} ${cy - 44} L${cx - 34} ${cy + 14}`} stroke="#c01515" strokeWidth="9" strokeLinecap="round" />}</g>; })}
      <g transform={`translate(0,${phase * 40})`} opacity={1 - phase}><rect x="180" y="410" width="720" height="40" fill="#f4eed8" opacity=".0" /></g>
      <g transform={`translate(540,1300) rotate(${Math.sin(frame * 0.5) * 3})`}><text textAnchor="middle" fontFamily={FONT} fontWeight={900} fontSize="96" fill="#c01515" stroke="#fff" strokeWidth="2" opacity=".92">{text}</text></g>
    </g>
  );
};

const Title: React.FC<{text: string}> = ({text}) => {
  const frame = useCurrentFrame();
  const g = hash(Math.floor(frame / 3)) > 0.85 ? (hash(frame) - 0.5) * 40 : 0;
  return (
    <g>
      <rect width="1080" height="1920" fill="#08060c" />
      {Array.from({length: 40}).map((_, i) => <rect key={i} x="0" y={i * 48 + ((frame * 6) % 48)} width="1080" height="3" fill="#fff" opacity=".06" />)}
      <g transform={`translate(${540 + g},900)`}>
        {[16, 12, 8, 4].map((o, i) => <text key={i} y={o} x={o} textAnchor="middle" fontFamily={FONT} fontWeight={900} fontSize="190" fill={['#7a0d2a', '#a3123a', '#d11a4c', '#e0482a'][i]}>{text}</text>)}
        <text textAnchor="middle" fontFamily={FONT} fontWeight={900} fontSize="190" fill="#ffe500" stroke={INK} strokeWidth="6">{text}</text>
      </g>
      <text x="540" y="1060" textAnchor="middle" fontFamily={FONT} fontWeight={800} fontSize="44" fill="#fff" opacity=".8" letterSpacing="14">СЕРИЯ 1 · ВИДЕОКАССЕТА</text>
    </g>
  );
};

const Door: React.FC<{speaking: boolean; focus: boolean}> = ({speaking, focus}) => {
  const step = useStep(10);
  const queue: Char[] = [
    {who: 'thug', x: 210, y: 1390, scale: 1.2, variant: 0, mood: 'sad', talk: focus},
    {who: 'thug', x: 470, y: 1330, scale: 1.0, variant: 1, mood: 'angry', flip: false},
    {who: 'thug', x: 680, y: 1290, scale: 0.86, variant: 2, mood: 'sad'},
    {who: 'thug', x: 850, y: 1262, scale: 0.74, variant: 3, mood: 'angry', pose: 'crossed'},
    {who: 'thug', x: 980, y: 1244, scale: 0.64, variant: 0, mood: 'sad'},
  ].map((c) => ({...c, pose: (c as Char).pose ?? 'crossed'}) as Char).reverse();
  return (
    <svg viewBox="0 0 1080 1920" width="100%" height="100%" preserveAspectRatio="xMidYMid slice">
      <defs><Wobble seed={Math.floor(step / 2) % 7} /></defs>
      <g filter="url(#wob)">
        <rect width="1080" height="1920" fill="#b9b39e" />
        {Array.from({length: 12}).map((_, r) => Array.from({length: 9}).map((__, c) => <rect key={r + '-' + c} x={c * 130} y={r * 110} width="126" height="106" fill="#c9c3ac" stroke="#a69f86" strokeWidth="3" />))}
        <rect x="140" y="170" width="800" height="150" fill="#1d3f8f" {...L} />
        <text x="540" y="278" textAnchor="middle" fontFamily={FONT} fontWeight={900} fontSize="84" fill="#ffd33a" stroke={INK} strokeWidth="3">ТРОЙНОЙ КАПИТАЛ</text>
        <rect x="560" y="420" width="380" height="800" fill="#4a2f22" {...L} /><rect x="590" y="460" width="320" height="300" fill="#2a2a30" stroke={INK} strokeWidth="6" />
        <circle cx="610" cy="860" r="18" fill="#ccc" {...L} strokeWidth={4} />
        <g transform="rotate(-3 750 960)"><rect x="620" y="880" width="260" height="190" fill="#f4f0e0" stroke={INK} strokeWidth="4" />
          <text x="750" y="930" textAnchor="middle" fontFamily={FONT} fontWeight={900} fontSize="38" fill="#c01515">ЗАКРЫТО</text>
          <text x="750" y="975" textAnchor="middle" fontFamily={FONT} fontWeight={800} fontSize="22" fill={INK}>ТЕХНИЧЕСКИЙ</text><text x="750" y="1004" textAnchor="middle" fontFamily={FONT} fontWeight={800} fontSize="22" fill={INK}>ПЕРЕРЫВ</text>
          <text x="750" y="1040" textAnchor="middle" fontFamily={FONT} fontWeight={800} fontSize="20" fill="#555">(навсегда)</text></g>
        <rect y="1240" width="1080" height="680" fill="#6c6c74" />
        {queue.map((c, i) => <Character key={i} c={c} speaking={speaking} step={step} />)}
      </g>
    </svg>
  );
};

export const Insert: React.FC<{vhs: Vhs; speaking: boolean}> = ({vhs, speaking}) => {
  const step = useStep(10);
  const d = vhs.data ?? {};
  let body: React.ReactNode = null;
  switch (vhs.bg) {
    case 'tv-ad': body = <TvAd text={d.text ?? ''} speaking={speaking} />; break;
    case 'tv-news': body = <TvNews text={d.text ?? ''} speaking={speaking} />; break;
    case 'ledger': body = <Ledger lines={d.lines ?? []} />; break;
    case 'calendar': body = <Calendar text={d.text ?? ''} />; break;
    case 'title': body = <Title text={d.text ?? ''} />; break;
  }
  return (
    <svg viewBox="0 0 1080 1920" width="100%" height="100%" preserveAspectRatio="xMidYMid slice">
      <defs><Wobble seed={Math.floor(step / 2) % 7} /></defs>
      <g filter="url(#wob)">{body}</g>
    </svg>
  );
};

export const FullDoor = Door;

/* ===================== камера ===================== */
export const Camera: React.FC<{cam?: Vhs['cam']; children: React.ReactNode}> = ({cam, children}) => {
  const frame = useCurrentFrame();
  const {durationInFrames, width, height} = useVideoConfig();
  if (!cam) return <AbsoluteFill>{children}</AbsoluteFill>;
  const p = interpolate(frame, [0, Math.max(1, durationInFrames - 1)], [0, 1], {extrapolateRight: 'clamp'});
  const e = p < 0.5 ? 2 * p * p : 1 - Math.pow(-2 * p + 2, 2) / 2;
  const z = cam.z0 + (cam.z1 - cam.z0) * e;
  const cx = cam.x * width, cy = cam.y * height;
  return <AbsoluteFill style={{transform: `translate(${cx}px,${cy}px) scale(${z}) translate(${-cx}px,${-cy}px)`, transformOrigin: '0 0'}}>{children}</AbsoluteFill>;
};
