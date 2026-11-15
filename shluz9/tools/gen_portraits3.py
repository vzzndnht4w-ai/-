import sys, json, concurrent.futures as cf
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent)); import gptunnel as g
ROOT = Path(__file__).resolve().parent.parent; OUT = ROOT / "references/portraits"; OUT.mkdir(parents=True, exist_ok=True)
STYLE = ("2D animated series character design, clean cel-shaded animation style, soft painterly shading, refined line work, "
         "cinematic dark palette with sickly green and rust-orange accents, dramatic rim lighting")
CH = {
 "artyom": 'lean unshaven man in his mid-30s, short dark hair, tired eyes with dark circles, worn gray coverall with a "VENT MAINTENANCE" patch, headlamp hanging around his neck',
 "mara": "woman in her late 20s, blonde hair tied in a ponytail, pale face, stained white doctor's coat, bandage on her left forearm",
 "gromov": "broad-shouldered man in his mid-50s, gray stubble, scar across the left eyebrow, dark uniform jacket with a commander patch, ring of keys on his belt",
 "lyosha": "small boy of 12, messy dark hair, large wide eyes, oversized knitted sweater, old headphones around his neck",
 "infected": "infected person with gray skin, dark hollow eye sockets, unnaturally bent joints, always half-hidden in deep shadow",
}
MODEL = "nano-banana-pro"
def job(a):
    name, i = a
    prompt = f"{STYLE}. Character reference illustration: {CH[name]}. Three-quarter body, facing camera, neutral expression, plain dark teal background, no text, no watermark."
    c, j = g.create(MODEL, prompt=prompt, params={"resolution": "1K", "aspect_ratio": "3:4", "output_format": "png"}, idem=f"portrait-{name}-{i}-v1")
    if c not in (200, 201) or "id" not in j: return name, i, f"create failed {c}: {str(j)[:200]}"
    r = g.result(j["id"])
    if r.get("status") != "done": return name, i, f"failed: {str(r.get('error'))[:200]}"
    url = r["result"][0]["url"]; p = OUT / f"{name}_{i}.png"; code = g.download(url, p)
    return name, i, f"ok {code} {p.stat().st_size if p.exists() else 0} price {r.get('price')}"
jobs = [(n, i) for n in (sys.argv[1].split(",") if len(sys.argv) > 1 else CH) for i in (0, 1)]
with cf.ThreadPoolExecutor(5) as ex:
    for n, i, msg in ex.map(job, jobs): print(n, i, msg, flush=True)
