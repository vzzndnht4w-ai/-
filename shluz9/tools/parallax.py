#!/usr/bin/env python3
"""2.5D-анимация кадров: параллакс по карте глубины + свет, пыль, дрожь. 1080x1920, 30 fps, 4 процесса.
python3 tools/parallax.py episodes/ep00_last_turn [id,id,...]   → episodes/.../clips/NN.mp4"""
import sys, json, math, subprocess, time
from pathlib import Path
from multiprocessing import Pool
import numpy as np, cv2
W, H, FPS = 1080, 1920, 30
ALARM = {7, 8, 9, 10, 11, 14, 15, 16, 17, 18}; SHAKE = {9: 14, 23: 22, 34: 26}
HITS = {23: [.35, .9, 1.3, 2.2, 2.55, 3.4, 3.7, 4.3]}
def ease(x): x = min(1, max(0, x)); return x * x * (3 - 2 * x)
def nz(t, s):
    i = math.floor(t); f = t - i; f = f * f * (3 - 2 * f)
    h = lambda n: (math.sin(n * 127.1 + s * 311.7) * 43758.5453) % 1.0
    return h(i) * (1 - f) + h(i + 1) * f
def cam(motion, k, t):
    """k: 0..1 прогресс сцены → (cx, cy, zoom); cx,cy в [-1,1]."""
    e = ease(k)
    return {"zoom_in": (0.0, 0.0, 1.0 + .07 * e), "zoom_out": (0.0, 0.0, 1.07 - .07 * e), "pan_right": (-.8 + 1.6 * e, 0.0, 1.04),
            "pan_left": (.8 - 1.6 * e, 0.0, 1.04), "tilt_up": (0.0, .8 - 1.6 * e, 1.04), "pan_down": (0.0, -.8 + 1.6 * e, 1.04),
            "shake": (0.0, 0.0, 1.05 + .02 * e), "static_slow": (0.0, 0.0, 1.0 + .03 * e)}.get(motion, (0.0, 0.0, 1.0 + .05 * e))
def render(args):
    ep, fr = args; i = fr["id"]; T = float(fr["duration_sec"]); n = int(round(T * FPS)); out = ep / "clips" / f"{i:02d}.mp4"
    S = 1.16; sw, sh = int(W * S), int(H * S)
    img = cv2.imread(str(ep / f"images/{i:02d}.jpg")); img = cv2.resize(img, (sw, sh), interpolation=cv2.INTER_CUBIC)
    dep = cv2.imread(str(ep / f"images/depth/{i:02d}.png"), 0).astype(np.float32) / 255
    dep = cv2.GaussianBlur(cv2.resize(dep, (sw, sh), interpolation=cv2.INTER_CUBIC), (0, 0), 6)
    gx, gy = np.meshgrid(np.arange(W, dtype=np.float32), np.arange(H, dtype=np.float32))
    ox, oy = (sw - W) / 2, (sh - H) / 2
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32); vig = 1 - .38 * np.clip(((xx - W / 2) / (W * .75)) ** 2 + ((yy - H / 2) / (H * .75)) ** 2, 0, 1)[..., None]
    rng = np.random.default_rng(i); P = rng.random((70, 4)).astype(np.float32)
    p = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "bgr24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                          "-c:v", "libx264", "-preset", "medium", "-crf", "18", "-pix_fmt", "yuv420p", str(out)], stdin=subprocess.PIPE)
    motion = fr.get("motion", "zoom_in"); K = 38.0
    for f in range(n):
        t = f / FPS; k = f / max(1, n - 1); cx, cy, z = cam(motion, k, t)
        z += .004 * math.sin(t * 1.7)                      # дыхание кадра
        kx = ky = 0.0
        if i in SHAKE: a = SHAKE[i] * (.4 + .6 * k if i == 34 else 1); kx = (nz(t * 20, 1) - .5) * a; ky = (nz(t * 20, 2) - .5) * a
        punch = sum(math.exp(-(t - h) * 9) for h in HITS.get(i, []) if t >= h) if i in HITS else 0
        if i == 34: punch = (math.sin(t * 38) ** 2) * k ** 1.5
        z += .035 * punch
        px = cx * K + kx; py = cy * K * .6 + ky
        # смещение по глубине: ближнее (светлое) уходит сильнее дальнего
        dcrop = dep[int(oy):int(oy) + H, int(ox):int(ox) + W]
        mx = (gx - W / 2) / z + W / 2 + ox + (dcrop - .45) * px + cx * 14
        my = (gy - H / 2) / z + H / 2 + oy + (dcrop - .45) * py + cy * 14 * .6
        fr_img = cv2.remap(img, mx, my, cv2.INTER_LINEAR, borderMode=cv2.BORDER_REPLICATE).astype(np.float32)
        # свет: мерцание ламп, сигнальный пульс, вспышка щелчка замка
        fl = 1 - .10 * (1 - nz(t * 17, i)) * (1.6 if i in (9, 34) else 1)
        fr_img *= fl
        if i in ALARM:
            ph = (math.sin(t * 7.5) + 1) / 2; fr_img[..., 2] *= 1 + .16 * ph; fr_img[..., 1] *= 1 + .04 * ph
        if i == 20 and abs(t - T * .55) < .12: fr_img += 60 * (1 - abs(t - T * .55) / .12)
        if punch: fr_img[..., 2] *= 1 + .12 * min(punch, 1)
        fr_img *= vig
        # пыль / пепел
        ov = np.zeros((H, W), np.float32)
        for (a, b, c, d) in P:
            x = (a * W + math.sin(t * .6 + a * 9) * 22 + t * 14 * (d - .5)) % W; y = (b * H + t * (18 + 40 * c)) % H
            cv2.circle(ov, (int(x), int(y)), int(1 + float(c) * 3), float(.22 + .45 * float(d)), -1, cv2.LINE_AA)
        ov = cv2.GaussianBlur(ov, (0, 0), 1.2); fr_img += (ov * 150)[..., None]
        if i == 34 and t > T - .55: fr_img[:] = 0
        p.stdin.write(np.clip(fr_img, 0, 255).astype(np.uint8).tobytes())
    p.stdin.close(); p.wait(); return i
if __name__ == "__main__":
    ep = Path(sys.argv[1]).resolve(); (ep / "clips").mkdir(exist_ok=True)
    d = json.load(open(ep / "prompts.json")); only = set(map(int, sys.argv[2].split(","))) if len(sys.argv) > 2 else None
    jobs = sorted([(ep, f) for f in d["frames"] if not only or f["id"] in only], key=lambda a: -a[1]["duration_sec"])
    t0 = time.time()
    with Pool(4) as pool:
        for i in pool.imap_unordered(render, jobs): print("done", i, round(time.time() - t0), "s", flush=True)
