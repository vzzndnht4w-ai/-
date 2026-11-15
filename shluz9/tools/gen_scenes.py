"""Стартовые кадры сцен серии: описание из prompts.json (дословно), стиль 2D-анимации, эталоны героев из references/.
python3 tools/gen_scenes.py episodes/ep00_last_turn [id,id,...]"""
import sys, json, concurrent.futures as cf
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent)); import gptunnel as g
ROOT = Path(__file__).resolve().parent.parent
ep = Path(sys.argv[1]).resolve(); only = set(map(int, sys.argv[2].split(","))) if len(sys.argv) > 2 else None
BASE = "dark graphic novel, heavy black ink, high contrast, desaturated palette with sickly green and rust-orange accents, film grain, dramatic shadows, hatching, vertical 9:16, "
STYLE = ("2D animated series, clean cel-shaded animation style, soft painterly shading, refined line work, cinematic dark palette with sickly green and rust-orange accents, dramatic rim lighting, vertical 9:16")
KEY = {"lean unshaven": "artyom", "woman in her late": "mara", "broad-shouldered": "gromov", "small boy": "lyosha", "infected person": "infected"}
d = json.load(open(ep / "prompts.json")); (ep / "images").mkdir(exist_ok=True)
def job(f):
    i = f["id"]; out = ep / "images" / f"{i:02d}.png"
    if out.exists() and out.stat().st_size > 10000 and not only: return i, "skip (exists)"
    scene = f["prompt"].replace(BASE, "")
    chars = [v for k, v in KEY.items() if k in scene][:3]
    note = (f" The characters must look exactly like the attached reference images ({', '.join(chars)}): same faces, hair, clothes and details." if chars else "")
    prompt = f"{STYLE}. {scene}.{note} Full frame illustration, no text, no watermark, no borders."
    refs = [g.data_url(ROOT / f"references/{c}.png") for c in chars]
    for attempt in range(3):
      try:
        return _run(f, i, out, scene, prompt, refs)
      except Exception as e:
        err = str(e)
    return i, f"error: {err[:200]}"
def _run(f, i, out, scene, prompt, refs):
    c, j = g.create("nano-banana-2-1", prompt=prompt, params={"resolution": "2K", "aspect_ratio": "9:16", "output_format": "png"},
                    inputs={"image_input": refs} if refs else None, idem=f"ep00-f{i:02d}-img-v1")
    if c not in (200, 201) or "id" not in j: return i, f"create {c}: {str(j)[:200]}"
    r = g.result(j["id"], every=6, timeout=900)
    if r.get("status") != "done": return i, f"failed: {str(r.get('error'))[:200]}"
    code = g.download(r["result"][0]["url"], out)
    if not out.exists() or out.stat().st_size < 10000: raise RuntimeError(f"download {code}")
    return i, f"ok {code} {out.stat().st_size//1024}KB price {r.get('price')}"
jobs = [f for f in d["frames"] if f["id"] != 1 and (not only or f["id"] in only)]
tot = 0
with cf.ThreadPoolExecutor(4) as ex:
    for i, msg in ex.map(job, jobs):
        print(i, msg, flush=True)
