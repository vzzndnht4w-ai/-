import type {Look} from './Flat';

/** Герои серии: внешность фиксирована, одинакова во всех сценах. */
export const MARK: Look = {skin: '#d9a784', hair: '#1d1a19', top: '#586a4e', inner: '#8a8f94', pants: '#4a525c', style: 'short', stubble: true};
export const INNA: Look = {skin: '#e4b99a', hair: '#2a1d17', top: '#6a7b6c', inner: '#a9a8a2', pants: '#2c3036', style: 'bun', width: 0.92};
export const LYOSHA: Look = {skin: '#e6bd9c', hair: '#5a4330', top: '#6f7f90', inner: '#c4c1b8', pants: '#3d4a63', style: 'messy', width: 0.84, shoes: '#2a2d33'};
export const TAMARA: Look = {skin: '#d6ab92', hair: '#b9bcc0', top: '#7a5a45', inner: '#a4a094', pants: '#44413f', style: 'bun', width: 0.98};
export const CAST = {mark: MARK, inna: INNA, lesha: LYOSHA, tamara: TAMARA} as const;
