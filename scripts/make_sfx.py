#!/usr/bin/env python3
"""Оригинальные звуки и музыка, синтез кодом (никаких чужих сэмплов → свободно для монетизации).

  python3 scripts/make_sfx.py      → public/sfx/{eurodance,modem,click,rewind,static}.wav  (44.1 кГц, моно)
Детерминированно (фиксированный seed).
"""
import wave
from pathlib import Path
import numpy as np

SR = 44100
OUT = Path(__file__).resolve().parent.parent / "public" / "sfx"
rng = np.random.default_rng(1995)


def save(name, x, peak=0.9):
    x = x / max(1e-9, np.max(np.abs(x))) * peak
    with wave.open(str(OUT / f"{name}.wav"), "wb") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR)
        w.writeframes((x * 32767).astype("<i2").tobytes())


def t_(sec): return np.arange(int(sec * SR)) / SR
def midi(n): return 440.0 * 2 ** ((n - 69) / 12)
def env(n, a=0.005, d=0.1, s=0.0):
    t = np.arange(n) / SR
    return np.where(t < a, t / a, s + (1 - s) * np.exp(-(t - a) / d))
def lp(x, k):  # простой НЧ-фильтр
    return np.convolve(x, np.ones(k) / k, mode="same")


# ---------- Евродэнс: 140 BPM, Am – F – C – G, 8 тактов (петля ≈13.7 с) ----------
def eurodance():
    bpm = 140; beat = 60 / bpm; bars = 8
    n = int(bars * 4 * beat * SR); mix = np.zeros(n)
    def add(x, at):
        i = int(at * SR); mix[i:i + len(x)] += x[: n - i]
    # бочка 4/4, клэп на 2 и 4, открытый хэт на «и»
    for b in range(bars * 4):
        tt = t_(0.28); f = 50 + 110 * np.exp(-tt * 28)
        add(np.sin(2 * np.pi * np.cumsum(f) / SR) * env(len(tt), 0.001, 0.12) * 1.0, b * beat)
        add(rng.standard_normal(int(0.06 * SR)) * env(int(0.06 * SR), 0.001, 0.02) * 0.0, b * beat)
        if b % 2 == 1:
            nz = rng.standard_normal(int(0.18 * SR)); nz = nz - lp(nz, 12)
            add(nz * env(len(nz), 0.002, 0.05) * 0.55, b * beat)
        nz = rng.standard_normal(int(0.08 * SR)); nz = nz - lp(nz, 6)
        add(nz * env(len(nz), 0.001, 0.025) * 0.28, b * beat + beat / 2)
    # басс: октавами с «качелей» на восьмых, аккорды Am F C G
    roots = [45, 41, 48, 43]   # A2 F2 C3 G2
    for bar in range(bars):
        r = roots[bar % 4]
        for e in range(8):
            f = midi(r + (12 if e % 2 else 0)); dur = beat / 2 * 0.9
            tt = t_(dur); w = 2 * (tt * f % 1) - 1                # пила
            add(lp(w, 4)[: len(tt)] * env(len(tt), 0.003, 0.12, 0.3) * 0.5, (bar * 8 + e) * beat / 2)
    # пэд: сырые «супер-пилы»
    chords = [[57, 60, 64], [53, 57, 60], [55, 60, 64], [55, 59, 62]]
    for bar in range(bars):
        d = 4 * beat; tt = t_(d); pad = np.zeros(len(tt))
        for nn in chords[bar % 4]:
            for det in (-0.12, 0, 0.12):
                f = midi(nn) * 2 ** (det / 12); pad += 2 * (tt * f % 1) - 1
        pad = lp(pad, 8) * np.minimum(1, tt / 0.03) * np.minimum(1, (d - tt) / 0.1)
        add(pad * 0.07, bar * d)
    # лид: «пищащий» прямоугольник, мотив из 8 нот, вторая половина — вариация
    motif = [[0, 3, 7, 3, 12, 7, 3, 0], [0, 7, 12, 7, 15, 12, 7, 3]]
    base = [69, 65, 72, 67]
    for bar in range(bars):
        for k, st in enumerate(motif[(bar // 4) % 2]):
            f = midi(base[bar % 4] + st + 12); dur = beat / 2 * 0.85
            tt = t_(dur); sq = np.sign(np.sin(2 * np.pi * f * tt + 0.4 * np.sin(2 * np.pi * 5.5 * tt)))
            add(lp(sq, 3)[: len(tt)] * env(len(tt), 0.004, 0.09, 0.25) * 0.16, (bar * 8 + k) * beat / 2)
    return mix


# ---------- Модем 56k: несущая, перебор тонов, «шипящий» хендшейк ----------
def modem():
    parts = []
    def tone(f, d, a=0.5): tt = t_(d); return np.sin(2 * np.pi * f * tt) * a
    for f in (2100, 1300, 2100): parts.append(tone(f, 0.12))
    parts.append(np.zeros(int(0.08 * SR)))
    parts.append(tone(1200, 0.25, 0.4) + tone(2400, 0.25, 0.3))
    for _ in range(14):    # «качающие» пары частот
        f1, f2 = rng.choice([980, 1180, 1650, 1850, 2225, 2400]), rng.choice([1070, 1270, 1750, 1950, 2025, 2600])
        parts.append(tone(f1, 0.07, 0.35) + tone(f2, 0.07, 0.35))
    tt = t_(1.1); nz = rng.standard_normal(len(tt)); chirp = np.sin(2 * np.pi * (1500 + 700 * np.sin(2 * np.pi * 9 * tt)) * tt)
    parts.append(lp(nz, 2) * 0.35 + chirp * 0.35)                    # шипение + щебет
    parts.append(tone(2400, 0.15, 0.5))
    x = np.concatenate(parts); return x * np.minimum(1, np.arange(len(x)) / 500)


def click():   # кнопка кассетного магнитофона: тук + пружинный дребезг
    tt = t_(0.18); nz = rng.standard_normal(len(tt))
    thud = np.sin(2 * np.pi * 140 * tt) * np.exp(-tt * 70) * 0.9
    snap = (nz - lp(nz, 5)) * np.exp(-tt * 160) * 0.6
    x = thud + snap; x[int(0.09 * SR):] += (np.roll(snap, int(0.09 * SR)))[int(0.09 * SR):] * 0.35
    return x


def rewind():  # перемотка: нарастающий жужжащий свист с шумом
    tt = t_(0.9); f = 600 + 2600 * (tt / 0.9) ** 1.5
    x = np.sin(2 * np.pi * np.cumsum(f) / SR) * 0.4 + lp(rng.standard_normal(len(tt)), 3) * 0.3
    return x * np.minimum(1, tt / 0.05) * np.minimum(1, (0.9 - tt) / 0.08)


def static():  # трекинг-помеха: шум с «полосами»
    tt = t_(0.6); nz = rng.standard_normal(len(tt)); band = 0.4 + 0.6 * (np.sin(2 * np.pi * 7 * tt) > 0)
    return (nz - lp(nz, 3)) * band * np.minimum(1, tt / 0.01) * np.minimum(1, (0.6 - tt) / 0.05)


if __name__ == "__main__":
    OUT.mkdir(parents=True, exist_ok=True)
    save("eurodance", eurodance(), 0.9)
    save("modem", modem(), 0.8); save("click", click(), 0.9)
    save("rewind", rewind(), 0.7); save("static", static(), 0.6)
    print("ok:", ", ".join(sorted(p.name for p in OUT.glob("*.wav"))))
