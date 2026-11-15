import React from 'react';
import {Lottie, LottieAnimationData} from '@remotion/lottie';
// Минимальная Lottie-анимация: пульсирующий зелёный круг (индикатор шлюза)
const data: LottieAnimationData = {v: '5.7.0', fr: 30, ip: 0, op: 60, w: 400, h: 400, nm: 'lamp', ddd: 0, assets: [],
  layers: [{ddd: 0, ind: 1, ty: 4, nm: 'c', sr: 1, ks: {o: {a: 0, k: 100}, r: {a: 0, k: 0}, p: {a: 0, k: [200, 200, 0]}, a: {a: 0, k: [0, 0, 0]},
    s: {a: 1, k: [{t: 0, s: [80, 80, 100], e: [120, 120, 100], i: {x: [.4], y: [1]}, o: {x: [.6], y: [0]}}, {t: 30, s: [120, 120, 100], e: [80, 80, 100], i: {x: [.4], y: [1]}, o: {x: [.6], y: [0]}}, {t: 60}]}},
    ao: 0, shapes: [{ty: 'gr', it: [{ty: 'el', p: {a: 0, k: [0, 0]}, s: {a: 0, k: [120, 120]}}, {ty: 'fl', c: {a: 0, k: [0.24, 1, 0.54, 1]}, o: {a: 0, k: 100}}, {ty: 'tr', p: {a: 0, k: [0, 0]}, a: {a: 0, k: [0, 0]}, s: {a: 0, k: [100, 100]}, r: {a: 0, k: 0}, o: {a: 0, k: 100}}]}], ip: 0, op: 60, st: 0, bm: 0}]};
export const LottieTest: React.FC = () => <Lottie animationData={data} style={{width: 400, height: 400}} />;
