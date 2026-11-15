#!/usr/bin/env python3
"""Подгоняет оживлённые клипы (anim/NN.mp4, ~5 с) под длительность сцены и кладёт в hf-ep00/assets/clips/.
Короткие сцены — обрезка; длиннее — замедление (до 1.5x) + ping-pong для динамичных сцен или заморозка последнего кадра."""
import json, subprocess, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent; EP = ROOT / "episodes/ep00_last_turn"; OUT = ROOT / "hf-ep00/assets/clips"
d = {f["id"]: f for f in json.load(open(EP / "prompts.json"))["frames"]}
PINGPONG = {23, 34}
for src in sorted((EP / "anim").glob("[0-9][0-9].mp4")):
    i = int(src.stem); T = float(d[i]["duration_sec"]); L = 5.04
    scale = "scale=1080:1920:flags=lanczos,setsar=1"
    if i in PINGPONG and T > L:
        fc = f"[0:v]{scale},fps=30,split=3[a][b][c];[b]reverse[r];[a][r][c]concat=n=3:v=1:a=0,trim=duration={T:.3f},setpts=PTS-STARTPTS"
    elif T > L:
        f = min(T / L, 1.5); hold = max(0.0, T - L * f)
        fc = f"[0:v]{scale},setpts=PTS*{f:.4f},minterpolate=fps=30:mi_mode=mci:mc_mode=aobmc:me_mode=bidir:vsbmc=1,tpad=stop_mode=clone:stop_duration={hold+1.0:.3f},trim=duration={T:.3f},setpts=PTS-STARTPTS"
    else:
        fc = f"[0:v]{scale},fps=30,trim=duration={T:.3f},setpts=PTS-STARTPTS"
    if i == 34: fc += f",fade=t=out:st={T-0.56:.3f}:d=0.04"
    tmp = OUT / f"{i:02d}.new.mp4"
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(src), "-filter_complex", fc + "[v]" if False else fc, "-an", "-c:v", "libx264", "-crf", "18", "-preset", "medium", "-pix_fmt", "yuv420p", str(tmp)], check=True)
    tmp.replace(OUT / f"{i:02d}.mp4"); print(i, "T", T, "ok", flush=True)
