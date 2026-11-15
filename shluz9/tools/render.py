#!/usr/bin/env python3
"""Рендер сцен серии в mp4-клипы (1080x1920, 30 fps) в 4 процесса.
python3 tools/render.py episodes/ep00_last_turn [id,id,...]"""
import sys, json, subprocess, time, os
from pathlib import Path
from multiprocessing import Pool
ROOT = Path(__file__).resolve().parent; sys.path.insert(0, str(ROOT))
FPS = 30
def render_scene(args):
    ep, fr = args
    from anim.core import Frame, camera, W, H
    from anim import scenes
    out = ep / "clips" / f"{fr['id']:02d}.mp4"; T = float(fr["duration_sec"]); n = int(round(T * FPS))
    fn = scenes.SCENES[fr["id"]]; motion = fr.get("motion", "zoom_in")
    p = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgba", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
        "-vf", "format=yuv420p", "-c:v", "libx264", "-preset", "medium", "-crf", "18", "-pix_fmt", "yuv420p", str(out)], stdin=subprocess.PIPE)
    f = Frame(); t0 = time.time()
    for i in range(n):
        t = i / FPS; c = f.c; c.save(); c.clear(0xFF000000)
        camera(c, motion, t, T); fn(c, t, T); c.restore()
        p.stdin.write(f.rgba().tobytes())
    p.stdin.close(); p.wait()
    return fr["id"], round(time.time() - t0, 1)
if __name__ == "__main__":
    ep = Path(sys.argv[1]).resolve(); (ep / "clips").mkdir(exist_ok=True)
    d = json.load(open(ep / "prompts.json")); only = set(map(int, sys.argv[2].split(","))) if len(sys.argv) > 2 else None
    jobs = sorted([(ep, f) for f in d["frames"] if not only or f["id"] in only], key=lambda a: -a[1]["duration_sec"])
    with Pool(4) as pool:
        for i, secs in pool.imap_unordered(render_scene, jobs): print("done", i, secs, flush=True)
