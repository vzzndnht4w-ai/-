#!/usr/bin/env python3
"""Звуковой дизайн серии 0 (процедурно, numpy): эмбиент-подложка + эффекты под действие в кадрах,
затем микс с озвучкой: приглушение под голос (sidechain), -14 LUFS. Правила: openmontage-craft/sound-design."""
import json, subprocess, sys
import numpy as np
from pathlib import Path
SR = 48000
ROOT = Path(__file__).resolve().parent.parent; EP = ROOT / "episodes/ep00_last_turn"; A = EP / "audio"
d = json.load(open(EP / "prompts.json")); rng = np.random.default_rng(7)
dur = {f["id"]: f["duration_sec"] for f in d["frames"]}
start = {}; t = 0.0
for f in d["frames"]: start[f["id"]] = t; t += f["duration_sec"]
TOTAL = t; N = int(TOTAL * SR) + SR
def tt(n): return np.arange(n) / SR
def lp(x, fc):  # простой ФНЧ (однополюсный)
    a = np.exp(-2 * np.pi * fc / SR); y = np.empty_like(x); s = 0.0
    for i in range(len(x)): s = (1 - a) * x[i] + a * s; y[i] = s
    return y
def lpf(x, fc, k=2):
    for _ in range(k): x = lp(x, fc)
    return x
def hp(x, fc): return x - lp(x, fc)
def env(n, a=.005, r=.3):
    e = np.ones(n); na = max(1, int(a * SR)); e[:na] = np.linspace(0, 1, na); e *= np.exp(-tt(n) / max(r, 1e-3)); return e
def noise(n): return rng.standard_normal(n)
L = np.zeros(N); R = np.zeros(N)
def put(x, at, gain=1.0, pan=0.0):
    i = int(at * SR)
    if i >= N or i < 0: return
    x = x[: N - i] * gain; L[i:i + len(x)] += x * (1 - max(0, pan)); R[i:i + len(x)] += x * (1 + min(0, pan))
def add(a, b):
    n = max(len(a), len(b)); return np.pad(a, (0, n - len(a))) + np.pad(b, (0, n - len(b)))
def amp(db): return 10 ** (db / 20)

# ---- «кирпичики» ----
def thud(f=55, r=.35, n=.7):
    k = int(n * SR); x = np.sin(2 * np.pi * (f + 40 * np.exp(-tt(k) / .04)) * tt(k)) * env(k, .002, r); x += lpf(noise(k), 400) * env(k, .001, .08) * .8; return x
def clunk(r=.5):
    k = int(.9 * SR); x = sum(np.sin(2 * np.pi * f * tt(k)) * env(k, .001, r / (1 + i)) * a for i, (f, a) in enumerate([(180, 1), (310, .6), (520, .4), (890, .25)])); x += hp(noise(k), 2500) * env(k, .001, .03) * .6; return x
def click(): k = int(.25 * SR); return (hp(noise(k), 3000) * env(k, .0005, .02) + np.sin(2 * np.pi * 1200 * tt(k)) * env(k, .0005, .03) * .5)
def hiss(n, fc=5000): k = int(n * SR); return hp(noise(k), fc) * np.sin(np.linspace(0, np.pi, k)) ** 1.5
def drip(): k = int(1.2 * SR); x = np.sin(2 * np.pi * (1800 - 600 * (1 - np.exp(-tt(k) / .02))) * tt(k)) * env(k, .001, .06); e = np.zeros(k); e += x; e[int(.17 * SR):] += x[:k - int(.17 * SR)] * .35; e[int(.34 * SR):] += x[:k - int(.34 * SR)] * .15; return e
def siren(n, f0=420, f1=640, rate=.9):
    k = int(n * SR); ph = np.cumsum(2 * np.pi * (f0 + (f1 - f0) * (0.5 + 0.5 * np.sin(2 * np.pi * rate * tt(k)))) / SR); x = np.sin(ph) + .35 * np.sin(2 * ph); return lpf(x, 1800, 1) * np.minimum(1, np.minimum(tt(k) * 4, (k / SR - tt(k)) * 4))
def rumble(n, g=1.0): k = int(n * SR); x = lpf(noise(k), 90, 3) * 14; x *= (.6 + .4 * np.sin(2 * np.pi * 7 * tt(k))); return x * np.minimum(1, np.minimum(tt(k) * 3, (k / SR - tt(k)) * 3)) * g
def murmur(n):
    k = int(n * SR); x = lpf(hp(noise(k), 200), 1400, 2); m = (np.sin(2 * np.pi * 3.1 * tt(k)) * .5 + .5) * (np.sin(2 * np.pi * 1.3 * tt(k) + 1) * .5 + .5); return x * m * 5 * np.minimum(1, np.minimum(tt(k) * 2, (k / SR - tt(k)) * 2))
def heart(n, bpm=70):
    k = int(n * SR); x = np.zeros(k); p = 60 / bpm
    for j in range(int(n / p)):
        for off, g in ((0, 1), (.28, .7)):
            i = int((j * p + off) * SR); 
            if i < k: s = thud(48, .12, .25) * g; e = min(k, i + len(s)); x[i:e] += s[:e - i]
    return x
def scratch(n): k = int(n * SR); return hp(noise(k), 1800) * (np.random.default_rng(3).random(k) > .985) * 2.0
def stampede(n):
    k = int(n * SR); x = np.zeros(k); t0 = 0.0
    while t0 < n:
        s = thud(rng.uniform(70, 110), .08, .2) * rng.uniform(.4, 1); i = int(t0 * SR); e = min(k, i + len(s)); x[i:e] += s[:e - i]; t0 += max(.045, .16 - .1 * (t0 / n)) * rng.uniform(.8, 1.2)
    return x
def tape(n): k = int(n * SR); return hp(noise(k), 4000) * ((np.random.default_rng(5).random(k) > .995) * 1.0) * 3 + lpf(noise(k), 3000, 1) * .02

# ---- подложка: тёмный дрон + вентиляция, интенсивность по сценам ----
k = int(TOTAL * SR); tm = tt(k)
drone = (np.sin(2 * np.pi * 55 * tm) + .6 * np.sin(2 * np.pi * 82.4 * tm + 1) + .3 * np.sin(2 * np.pi * 110.5 * tm)) * (.7 + .3 * np.sin(2 * np.pi * .07 * tm))
vent = lpf(noise(k), 260, 2) * 9
tension = np.zeros(k)
for f in d["frames"]:
    i0, i1 = int(start[f["id"]] * SR), int((start[f["id"]] + f["duration_sec"]) * SR)
    lvl = 0.55 + 0.45 * (f["id"] / 34) ** 1.4
    if f["id"] in (7, 8, 9, 10, 11, 14, 15, 16, 17, 18): lvl = 1.0
    tension[i0:i1] = lvl
tension = lpf(tension, 3, 1)
bed = (drone * .5 + vent * .35) * tension
L[:k] += bed * amp(-29); R[:k] += bed * amp(-29)

S = start
# ---- эффекты по кадрам ----
put(tape(4.0), S[1], amp(-26)); put(thud(50, 1.2, 1.6), S[1] + .1, amp(-24))
put(drip(), S[2] + 1.2, amp(-22), .4); put(drip(), S[2] + 3.4, amp(-26), -.4)
put(rumble(dur[4], .9), S[4], amp(-22)); put(hiss(2, 900) * .3, S[4] + .2, amp(-34))
put(clunk(.8), S[6] + 2.8, amp(-17)); put(thud(45, .8, 1.0), S[6] + 2.9, amp(-16))
put(siren(dur[7] + dur[8] + dur[9], 420, 640, .55), S[7], amp(-27))
for fid in (10, 11): put(murmur(dur[fid]), S[fid], amp(-26 if fid == 10 else -23))
put(siren(dur[10] + dur[11] + dur[12] * 0, 420, 640, .55), S[10], amp(-30))
put(rumble(dur[9], 1.0), S[9], amp(-17))
for j in range(6): put(thud(rng.uniform(60, 90), .2, .4), S[9] + .5 + j * .75, amp(-24), rng.uniform(-.5, .5))
put(clunk(.5), S[14] + 3.2, amp(-26))
put(murmur(dur[15]) * 1.4, S[15], amp(-20)); put(clunk(.7), S[15] + dur[15] - 1.1, amp(-15)); put(thud(38, 1.0, 1.4), S[15] + dur[15] - 1.1, amp(-14))
put(heart(dur[16], 84), S[16], amp(-19))
put(rumble(dur[17], .9), S[17], amp(-22)); put(clunk(.6), S[17] + 1.2, amp(-19))
for j in range(7): put(add(click() * .8, hiss(.4, 3000) * .4), S[18] + .3 + j * (dur[18] - .6) / 7, amp(-24), -.3 if j % 2 else .3)
put(hiss(2.8, 6000), S[19] + .2, amp(-21)); put(rumble(dur[19], 1.0), S[19], amp(-20)); put(clunk(.8), S[19] + dur[19] - 1.0, amp(-16)); put(thud(40, .9, 1.2), S[19] + dur[19] - 1.0, amp(-15))
tl = S[20] + dur[20] * .55; put(clunk(.9), tl, amp(-12)); put(thud(40, 1.1, 1.5), tl, amp(-11)); put(click(), tl + .45, amp(-18)); put(click(), tl + .7, amp(-20))
put(heart(dur[21], 96), S[21], amp(-22))
for h in (.35, .9, 1.3, 2.2, 2.55, 3.4, 3.7, 4.3): put(add(thud(rng.uniform(55, 75), .3, .6), hp(noise(int(.15 * SR)), 1200) * env(int(.15 * SR), .001, .03) * .5), S[23] + h, amp(-15))
for h in (.35, .9, 1.3, 2.2): put(murmur(1.2) * .5, S[23] + h, amp(-30))
put(heart(dur[24] + dur[25], 70), S[24], amp(-23))
put(scratch(dur[25]), S[25], amp(-28)); put(rumble(dur[26] + dur[27], .6), S[26], amp(-27)); put(scratch(dur[26] + dur[27]) * 1.2, S[26], amp(-24))
for j in range(5): put(hp(noise(int(.25 * SR)), 900) * env(int(.25 * SR), .002, .05) * 2, S[27] + 1 + j * 1.4, amp(-25), rng.uniform(-.6, .6))
put(heart(dur[28] + dur[29], 100), S[28], amp(-17)); put(rumble(dur[28], .5), S[28], amp(-30))
put(scratch(dur[30]) * 1.5, S[30], amp(-23)); put(hp(noise(int(.3 * SR)), 1800)[:int(.3 * SR)] * env(int(.3 * SR), .003, .06), S[30] + 1.5, amp(-24))
put(rumble(dur[31], 1.4), S[31], amp(-19)); put(scratch(dur[31]) * 1.2, S[31], amp(-26))
put(heart(dur[32] + dur[33], 120), S[32], amp(-17))
# финал: топот набирает силу, затем резкая тишина
fin = dur[34] - .55; put(stampede(fin), S[34], amp(-12)); put(rumble(fin, 1.2), S[34], amp(-16)); put(scratch(fin) * 2, S[34], amp(-24))
cut = S[34] + fin; ci = int(cut * SR); fade = int(.02 * SR); L[ci:] = 0; R[ci:] = 0
L[ci - fade:ci] *= np.linspace(1, 0, fade); R[ci - fade:ci] *= np.linspace(1, 0, fade)
for ch in (L, R): ch[: int(.02 * SR)] *= np.linspace(0, 1, int(.02 * SR))
sfx = np.stack([L, R], 1)[: int(TOTAL * SR)]
sfx = np.tanh(sfx * 1.0)  # мягкий лимитер
import wave
def wr(path, x):
    x = np.clip(x, -1, 1); y = (x * 32767).astype("<i2")
    with wave.open(str(path), "wb") as w: w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes(y.tobytes())
wr(A / "ambient_sfx.wav", sfx)
# ---- микс: голос (-14 LUFS цель), подложка приглушается голосом ----
voice = A / "voiceover.mp3"; out = A / "soundtrack.m4a"
flt = ("[0:a]aformat=sample_rates=48000:channel_layouts=stereo,asplit=2[vo][sc];"
       "[1:a]aformat=sample_rates=48000:channel_layouts=stereo,volume=1.0[bed];"
       "[bed][sc]sidechaincompress=threshold=0.03:ratio=6:attack=15:release=350:makeup=1[duck];"
       "[vo][duck]amix=inputs=2:duration=longest:normalize=0,loudnorm=I=-14:TP=-1.5:LRA=9[o]")
subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(voice), "-i", str(A / "ambient_sfx.wav"), "-filter_complex", flt, "-map", "[o]", "-ar", "48000", "-c:a", "aac", "-b:a", "192k", str(out)], check=True)
print("total", round(TOTAL, 1), "->", out)
