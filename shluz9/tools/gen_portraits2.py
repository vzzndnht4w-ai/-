import sys; from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent)); import gen_gemini as g
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
model = sys.argv[2] if len(sys.argv) > 2 else "gemini-3-pro-image"
for name in (sys.argv[1].split(",") if len(sys.argv) > 1 and sys.argv[1] != "all" else CH):
    prompt = f"{STYLE}. Character reference illustration: {CH[name]}. Three-quarter body, facing camera, neutral expression, plain dark teal background, no text, no watermark."
    ok, msg = g.gen(prompt, OUT / f"{name}_0.png", model=model); print(name, ok, msg[:200], flush=True)
