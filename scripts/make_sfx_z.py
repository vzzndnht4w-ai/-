#!/usr/bin/env python3
"""Звуки серии «Первый этаж»: тихие, сухие, синтез кодом (оригинал). → public/sfx/z_*.wav (22.05 кГц, моно)"""
import wave
from pathlib import Path
import numpy as np
SR = 22050
OUT = Path(__file__).resolve().parent.parent / "public" / "sfx"
rng = np.random.default_rng(7)
t_ = lambda s: np.arange(int(s * SR)) / SR
def lp(x, k): return np.convolve(x, np.ones(k) / k, mode="same")
def hp(x, k): return x - lp(x, k)
def env(n, a=0.003, d=0.1): t = np.arange(n) / SR; return np.where(t < a, t / a, np.exp(-(t - a) / d))
def save(name, x, peak=0.8):
    x = x / max(1e-9, np.max(np.abs(x))) * peak
    with wave.open(str(OUT / f"z_{name}.wav"), "wb") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR); w.writeframes((x * 32767).astype("<i2").tobytes())
def drip():
    t = t_(0.5); f = 1400 * np.exp(-t * 9) + 500
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 14)
def creak():   # скрип половицы/двери
    t = t_(1.1); f = 180 + 60 * np.sin(2 * np.pi * 3.2 * t) + 90 * t
    saw = 2 * ((np.cumsum(f) / SR) % 1) - 1
    return lp(saw, 6) * np.minimum(1, t / 0.15) * np.exp(-((t - 0.5) ** 2) / 0.12) * (0.6 + 0.4 * rng.random(len(t)))
def dishes():  # стук посуды
    out = np.zeros(int(1.2 * SR))
    for at, f in [(0.0, 2400), (0.18, 3100), (0.31, 1900), (0.5, 2700)]:
        n = int(0.25 * SR); t = np.arange(n) / SR
        hit = (np.sin(2 * np.pi * f * t) + 0.5 * np.sin(2 * np.pi * f * 2.7 * t)) * np.exp(-t * 28)
        i = int(at * SR); out[i:i + n] += hit[: len(out) - i]
    return out
def click():
    t = t_(0.14); nz = rng.standard_normal(len(t))
    return (np.sin(2 * np.pi * 180 * t) * np.exp(-t * 60) + hp(nz, 7) * np.exp(-t * 120) * 0.7)
def scrape():  # шкаф по полу
    t = t_(1.3); nz = lp(rng.standard_normal(len(t)), 5) * (0.5 + 0.5 * np.sin(2 * np.pi * 9 * t))
    return nz * np.minimum(1, t / 0.1) * np.minimum(1, (1.3 - t) / 0.2)
def water():   # струя → капли
    t = t_(6.0); nz = hp(rng.standard_normal(len(t)), 9)
    run = nz * np.where(t < 4.2, 1.0, np.exp(-(t - 4.2) * 3)) * 0.6
    d = np.zeros(len(t))
    for at in (4.6, 5.2, 5.9):
        i = int(at * SR); dr = drip()[: len(t) - i]; d[i:i + len(dr)] += dr
    return run + d * 0.8
def pen():
    t = t_(2.0); nz = hp(rng.standard_normal(len(t)), 4) * (np.sin(2 * np.pi * 6 * t) > 0.2) * 0.5
    return nz * np.minimum(1, t / 0.05) * np.minimum(1, (2.0 - t) / 0.1)
def keys():    # связка ключей
    out = np.zeros(int(1.0 * SR))
    for at in (0.0, 0.11, 0.2, 0.36, 0.5):
        n = int(0.3 * SR); t = np.arange(n) / SR; f = 3200 + 700 * rng.random()
        h = (np.sin(2 * np.pi * f * t) + 0.6 * np.sin(2 * np.pi * f * 1.9 * t)) * np.exp(-t * 22)
        i = int(at * SR); out[i:i + n] += h[: len(out) - i]
    return out
def handle():  # ручка двери: скрип + щелчок
    c = creak()[: int(0.9 * SR)]; k = np.zeros(int(1.6 * SR)); k[: len(c)] += c * 0.8
    cl = click(); i = int(1.1 * SR); k[i:i + len(cl)] += cl
    return k
def room():    # комнатный тон, зацикленный ровно (12 с)
    t = t_(12.0); x = 0.5 * np.sin(2 * np.pi * 55 * t) + 0.25 * np.sin(2 * np.pi * 110.5 * t) + 0.12 * lp(rng.standard_normal(len(t)), 40)
    return x
if __name__ == "__main__":
    OUT.mkdir(parents=True, exist_ok=True)
    for n, f, p in [("drip", drip, .6), ("creak", creak, .5), ("dishes", dishes, .6), ("click", click, .7), ("scrape", scrape, .5),
                    ("water", water, .5), ("pen", pen, .4), ("keys", keys, .6), ("handle", handle, .6), ("room", room, .25)]:
        save(n, f(), p)
    print("ok")
