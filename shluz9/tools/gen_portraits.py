import json, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent)); import fal
ROOT = Path(__file__).resolve().parent.parent; OUT = ROOT / "references/portraits"; OUT.mkdir(parents=True, exist_ok=True)
STYLE = ("2D animated series character design, clean cel-shaded animation style, soft painterly shading, refined line work, "
         "cinematic dark palette with sickly green and rust-orange accents, subtle film grain, dramatic rim lighting")
CH = {
 "artyom": 'lean unshaven man in his mid-30s, short dark hair, tired eyes with dark circles, worn gray coverall with a "VENT MAINTENANCE" patch, headlamp hanging around his neck',
 "mara": "woman in her late 20s, blonde hair tied in a ponytail, pale face, stained white doctor's coat, bandage on her left forearm",
 "gromov": "broad-shouldered man in his mid-50s, gray stubble, scar across the left eyebrow, dark uniform jacket with a commander patch, ring of keys on his belt",
 "lyosha": "small boy of 12, messy dark hair, large wide eyes, oversized knitted sweater, old headphones around his neck",
 "infected": "infected person with gray skin, dark hollow eye sockets, unnaturally bent joints, always half-hidden in deep shadow",
}
only = sys.argv[1].split(",") if len(sys.argv) > 1 else list(CH)
for name in only:
    prompt = f"{STYLE}, {CH[name]}, three-quarter body character reference, facing camera, neutral expression, plain dark teal background, no text"
    res = fal.run("fal-ai/flux-pro/v1.1", {"prompt": prompt, "image_size": "portrait_4_3", "num_images": 3, "output_format": "png", "safety_tolerance": "5", "enable_safety_checker": False})
    for i, im in enumerate(res["images"]):
        p = OUT / f"{name}_{i}.png"; code = fal.download(im["url"], p); print(name, i, code, p.stat().st_size if p.exists() else 0, flush=True)
    json.dump({"prompt": prompt, "seed": res.get("seed")}, open(OUT / f"{name}.json", "w"), ensure_ascii=False)
