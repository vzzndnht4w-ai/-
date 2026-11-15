#!/usr/bin/env python3
"""Собирает проект HyperFrames (hf-ep00): клипы сцен + саундтрек + субтитры по словам. Рендер: cd hf-ep00 && hyperframes render"""
import json, shutil, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent; EP = ROOT / "episodes/ep00_last_turn"; HF = ROOT / "hf-ep00"
d = json.load(open(EP / "prompts.json")); caps = json.load(open(EP / "captions.json"))
(HF / "assets/fonts").mkdir(parents=True, exist_ok=True); (HF / "compositions").mkdir(exist_ok=True)
shutil.copy("/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf", HF / "assets/fonts/LiberationSans-Bold.ttf")
shutil.copy(EP / "audio/soundtrack.m4a", HF / "assets/soundtrack.m4a")
T = round(sum(f["duration_sec"] for f in d["frames"]), 3)
vids = []; t = 0.0
for f in d["frames"]:
    vids.append(f'    <video id="s{f["id"]:02d}" class="clip" src="assets/clips/{f["id"]:02d}.mp4" muted playsinline data-start="{t:.3f}" data-duration="{f["duration_sec"]:.3f}" data-track-index="0" style="position:absolute;left:0;top:0;width:1080px;height:1920px;object-fit:cover"></video>')
    t += f["duration_sec"]
index = f'''<!doctype html>
<html lang="ru">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=1080, height=1920" />
    <script src="assets/gsap.min.js"></script>
    <style>
      * {{ margin: 0; padding: 0; box-sizing: border-box; }}
      html, body {{ margin: 0; width: 1080px; height: 1920px; overflow: hidden; background: #000; }}
    </style>
  </head>
  <body>
    <div id="root" data-composition-id="main" data-start="0" data-duration="{T}" data-width="1080" data-height="1920">
{chr(10).join(vids)}
      <audio id="mix" src="assets/soundtrack.m4a" data-start="0" data-duration="{T}" data-track-index="2"></audio>
      <div id="captions" data-composition-id="captions" data-composition-src="compositions/captions.html" data-start="0" data-duration="{T}" data-track-index="1" data-track-kind="captions" data-width="1080" data-height="1920"></div>
    </div>
    <script>
      window.__timelines = window.__timelines || {{}};
      const tl = gsap.timeline({{ paused: true }});
      window.__timelines["main"] = tl;
    </script>
  </body>
</html>
'''
(HF / "index.html").write_text(index, encoding="utf-8")
groups = []; js = []
for i, g in enumerate(caps):
    words = "".join(f'<span class="w" id="g{i}w{k}">{w["text"]}</span> ' for k, w in enumerate(g["words"]))
    groups.append(f'    <div class="grp" id="g{i}"><span class="pill">{words}</span></div>')
    prev_end = caps[i - 1]["end"] if i else 0; nxt = caps[i + 1]["start"] if i + 1 < len(caps) else 1e9
    a = max(.1, g["start"] - .06, prev_end + .04); b = min(g["end"] + .05, nxt - .06)
    if b <= a + .2: b = a + .2
    js.append(f'tl.set("#g{i}", {{opacity:0, y:14}}, 0); tl.to("#g{i}", {{opacity:1, y:0, duration:.14, ease:"power2.out"}}, {a:.3f});')
    for k, w in enumerate(g["words"]):
        js.append(f'tl.to("#g{i}w{k}", {{color:"#9dffc2", duration:.08, ease:"none"}}, {w["start"]:.3f});')
    js.append(f'tl.to("#g{i}", {{opacity:0, duration:.12, ease:"power2.in"}}, {b-.12:.3f}); tl.set("#g{i}", {{opacity:0, visibility:"hidden"}}, {b:.3f});')
cap = f'''<template>
  <style>
    @font-face {{ font-family: "ShluzCap"; src: url("assets/fonts/LiberationSans-Bold.ttf"); font-weight: 700; }}
    #root {{ position: absolute; inset: 0; }}
    .grp {{ position: absolute; left: 110px; width: 740px; bottom: 540px; text-align: center; opacity: 0;
      font-family: "ShluzCap", sans-serif; font-weight: 700; font-size: 60px; line-height: 1.18; color: #f4efe2;
      text-shadow: 0 3px 0 #05100c, 0 0 18px rgba(0,0,0,.9), 3px 3px 10px rgba(0,0,0,.8); overflow: visible; }}
    .pill {{ background: rgba(4,12,9,.5); padding: 6px 24px 10px; border-radius: 24px; -webkit-box-decoration-break: clone; box-decoration-break: clone; }}
    .w {{ display: inline-block; color: #f4efe2; }}
  </style>
  <div id="root" data-composition-id="captions" data-width="1080" data-height="1920">
{chr(10).join(groups)}
  </div>
  <script>
    const tl = gsap.timeline({{ paused: true }});
    {chr(10).join(js)}
    window.__timelines["captions"] = tl;
  </script>
</template>
'''
(HF / "compositions/captions.html").write_text(cap, encoding="utf-8")
(HF / "hyperframes.json").write_text(json.dumps({"$schema": "https://hyperframes.heygen.com/schema/hyperframes.json", "paths": {"blocks": "compositions", "components": "compositions/components", "assets": "assets"}, "media": {"autoProxy": False}}, indent=2))
print("project built; duration", T, "scenes", len(d["frames"]), "caption groups", len(caps))
