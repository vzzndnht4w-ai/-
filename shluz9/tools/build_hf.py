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
# ---- субтитры: перегруппировка по смыслу (знаки препинания), не более 4 слов / 24 знаков в фразе ----
words = []
for g in caps:
    for w in g["words"]:
        if words and w["text"] in (",", ".", ";", ":", "!", "?", "…"):   # одиночный знак приклеиваем к предыдущему слову
            words[-1] = dict(words[-1], text=words[-1]["text"] + w["text"], end=w["end"]); continue
        words.append(dict(w))
phr = []; cur = []
def flush():
    global cur
    if cur: phr.append(cur); cur = []
for w in words:
    cur.append(w); txt = w["text"]
    punct = txt[-1:] in ".,!?…:;—"
    if punct or len(cur) >= 4 or sum(len(x["text"]) + 1 for x in cur) > 24:
        carry = None
        if not punct and len(cur) > 1 and len(txt) <= 3: carry = cur.pop()     # не заканчиваем фразу предлогом
        flush()
        if carry: cur.append(carry)
flush()
merged = []
for g in phr:   # одиночные слова приклеиваем к соседней фразе
    if merged and len(g) == 1 and len(merged[-1]) < 4 and g[0]["start"] - merged[-1][-1]["end"] < .5: merged[-1] += g
    else: merged.append(g)
caps = [{"start": g[0]["start"], "end": g[-1]["end"], "words": g} for g in merged]
groups = []; js = []
for i, g in enumerate(caps):
    words_html = "".join(f'<span class="w" id="g{i}w{k}">{w["text"]}</span> ' for k, w in enumerate(g["words"]))
    groups.append(f'    <div class="grp" id="g{i}">{words_html}</div>')
    prev_end = caps[i - 1]["end"] if i else 0; nxt = caps[i + 1]["start"] if i + 1 < len(caps) else 1e9
    a = max(.08, g["start"] - .05, prev_end + .03); b = min(g["end"] + .12, nxt - .04)
    if b <= a + .2: b = a + .2
    js.append(f'tl.set("#g{i}", {{opacity:0, scale:.92, y:18}}, 0); tl.to("#g{i}", {{opacity:1, scale:1, y:0, duration:.16, ease:"back.out(1.6)"}}, {a:.3f});')
    for k, w in enumerate(g["words"]):
        js.append(f'tl.to("#g{i}w{k}", {{color:"#ffb04d", scale:1.03, duration:.09, ease:"power2.out"}}, {w["start"]:.3f});')
        js.append(f'tl.to("#g{i}w{k}", {{color:"#ffffff", scale:1, duration:.16, ease:"power1.inOut"}}, {max(w["end"], w["start"] + .12):.3f});')
    js.append(f'tl.to("#g{i}", {{opacity:0, duration:.1, ease:"power2.in"}}, {b-.1:.3f}); tl.set("#g{i}", {{opacity:0, visibility:"hidden"}}, {b:.3f});')
cap = f'''<template>
  <style>
    @font-face {{ font-family: "ShluzCap"; src: url("assets/fonts/LiberationSans-Bold.ttf"); font-weight: 700; }}
    #root {{ position: absolute; inset: 0; }}
    #shade {{ position: absolute; left: 0; right: 0; bottom: 0; height: 760px; background: linear-gradient(to top, rgba(2,8,6,.72), rgba(2,8,6,0)); }}
    .grp {{ position: absolute; left: 90px; width: 900px; bottom: 560px; text-align: center; opacity: 0;
      font-family: "ShluzCap", sans-serif; font-weight: 700; font-size: 92px; line-height: 1.08; letter-spacing: -.5px; color: #fff;
      -webkit-text-stroke: 10px #050d0a; paint-order: stroke fill; text-shadow: 0 6px 22px rgba(0,0,0,.85); overflow: visible; }}
    .w {{ display: inline-block; color: rgba(255,255,255,.92); margin: 0 .09em; }}
  </style>
  <div id="root" data-composition-id="captions" data-width="1080" data-height="1920">
    <div id="shade"></div>
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
