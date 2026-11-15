"""Карты глубины для кадров (Depth-Anything-V2 Small, CPU). Больше значение = ближе к камере."""
import sys, numpy as np
from pathlib import Path
from PIL import Image
from transformers import pipeline
ep = Path(sys.argv[1]).resolve(); out = ep / "images/depth"; out.mkdir(exist_ok=True)
pipe = pipeline("depth-estimation", model="depth-anything/Depth-Anything-V2-Small-hf", device=-1)
for p in sorted((ep / "images").glob("[0-9][0-9].jpg")):
    o = out / (p.stem + ".png")
    if o.exists(): continue
    d = np.array(pipe(Image.open(p).convert("RGB"))["depth"], dtype=np.float32)
    lo, hi = np.percentile(d, 1), np.percentile(d, 99); d = np.clip((d - lo) / max(hi - lo, 1e-6), 0, 1)
    Image.fromarray((d * 255).astype(np.uint8)).resize((768, 1376), Image.BILINEAR).save(o); print(p.stem, flush=True)
