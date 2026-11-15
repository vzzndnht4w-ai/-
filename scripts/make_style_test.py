#!/usr/bin/env python3
"""Короткий стилевой тест для Colab/Kaggle: те же сюжеты двумя способами, чтобы выбрать плоский 2D-стиль.
  python3 scripts/make_style_test.py series/zombie/ep01_style_test.ipynb
A = SDXL base + плоский стиль в промпте; B = то же + LoRA ramel2/emotional-flat-illustration-sdxl-lora.
"""
import json, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
from make_notebook import md, code

STYLE = ("flat 2D vector illustration, simple geometric shapes, flat solid colors, minimal cel shading, no gradients, "
         "no outlines, clean readable shapes, dark moody atmosphere, desaturated cold palette, single warm light source, "
         "serious animated drama series, game cutscene art")
NEG = ("photo, photorealistic, realistic, oil painting, brush strokes, 3d render, detailed skin texture, pores, text, letters, "
       "numbers, watermark, logo, anime, chibi, gradients, blurry, deformed hands")
SUBJ = [
 {"id": "bg_room", "kind": "bg", "seed": 501, "prompt": "interior of a small ground-floor apartment room at night, a large window showing a dark courtyard with one faint streetlight, worn wallpaper, wooden floor, a single warm lamp glowing in the corner, empty room, no people"},
 {"id": "mark", "kind": "sprite", "seed": 502, "prompt": "full body standing pose of a thin tired man aged 40, short dark hair, light stubble, olive green jacket, grey trousers, holding a closed notebook, simple stylized flat face, isolated on a plain flat light grey background, nothing else in the image"},
 {"id": "inna", "kind": "sprite", "seed": 503, "prompt": "full body standing pose of a woman aged 32, short cropped dark brown hair, pale tired face, grey-green cardigan over a light top, dark trousers, arms at her sides, simple stylized flat face, isolated on a plain flat light grey background, nothing else in the image"},
]

cells = [
 md("""
# Стилевой тест: плоская 2D

1. **Colab:** *Среда выполнения → Сменить среду → T4 GPU*. **Kaggle:** *Accelerator → GPU T4*, *Internet → On*.
2. *Выполнить все*. ~8–10 минут (12 картинок).
3. В конце покажется лист сравнения и скачается `style_test.zip`. Пришли мне **лист (скриншот)** или архив.

Ряд **A** — чистый SDXL + стиль в промпте. Ряд **B** — то же + LoRA плоской иллюстрации.
"""),
 code("""
!pip -q install -U diffusers transformers accelerate safetensors peft compel pillow
import torch; assert torch.cuda.is_available(), "Включи GPU T4 и перезапусти"
"""),
 code("""
from diffusers import StableDiffusionXLPipeline, AutoencoderKL
from compel import CompelForSDXL
vae = AutoencoderKL.from_pretrained("madebyollin/sdxl-vae-fp16-fix", torch_dtype=torch.float16)
pipe = StableDiffusionXLPipeline.from_pretrained("stabilityai/stable-diffusion-xl-base-1.0", vae=vae,
        torch_dtype=torch.float16, variant="fp16", use_safetensors=True).to("cuda")
pipe.set_progress_bar_config(disable=True)
cmp = CompelForSDXL(pipe)
"""),
 code(f"""
STYLE = {STYLE!r}
NEG = {NEG!r}
SUBJ = {json.dumps(SUBJ, ensure_ascii=False)}
import os, time
from PIL import Image
os.makedirs("/tmp/style_test", exist_ok=True)
SIZES = {{"bg": (768, 1344), "sprite": (1024, 1024)}}
def run(tag, lora):
    if lora:
        pipe.load_lora_weights("ramel2/emotional-flat-illustration-sdxl-lora", weight_name="minimal_flat_illustration,_emotional_scene.safetensors", adapter_name="flat")
        pipe.set_adapters(["flat"], [0.8])
    else:
        try: pipe.disable_lora()
        except Exception: pass
    for s in SUBJ:
        w, h = SIZES[s["kind"]]
        for v in range(2):
            g = torch.Generator("cuda").manual_seed(s["seed"] + v * 1000)
            trig = "minimal flat illustration, " if lora else ""
            c = cmp(f"{{trig}}{{STYLE}}, {{s['prompt']}}", negative_prompt=NEG)
            img = pipe(prompt_embeds=c.embeds, pooled_prompt_embeds=c.pooled_embeds, negative_prompt_embeds=c.negative_embeds,
                       negative_pooled_prompt_embeds=c.negative_pooled_embeds, width=w, height=h, num_inference_steps=30,
                       guidance_scale=6.5, generator=g).images[0]
            img.save(f"/tmp/style_test/{{tag}}_{{s['id']}}_v{{v}}.png"); print(tag, s["id"], v)
run("A", False)
run("B", True)
"""),
 code("""
import glob
from PIL import ImageDraw
rows = []
for tag in "AB":
    ims = []
    for s in SUBJ:
        for v in range(2):
            im = Image.open(f"/tmp/style_test/{tag}_{s['id']}_v{v}.png").convert("RGB"); im = im.resize((int(im.width*420/im.height), 420))
            d = ImageDraw.Draw(im); d.rectangle((0,0,160,22), fill=(0,0,0)); d.text((4,4), f"{tag} {s['id']} v{v}", fill=(255,255,0)); ims.append(im)
    rows.append(ims)
W = max(sum(i.width for i in r) for r in rows)
sheet = Image.new("RGB", (W, 2*430), (20,20,20))
for k, r in enumerate(rows):
    x = 0
    for im in r: sheet.paste(im, (x, k*430)); x += im.width
sheet.save("/tmp/style_test/_sheet.jpg", quality=90); display(sheet)
"""),
 code("""
import shutil, os
z = shutil.make_archive("/tmp/style_test", "zip", "/tmp/style_test")
if os.path.exists("/kaggle/working"): shutil.copy(z, "/kaggle/working/")
else:
    from google.colab import files; files.download(z)
"""),
]
nb = {"cells": cells, "metadata": {"accelerator": "GPU", "kernelspec": {"name": "python3", "display_name": "Python 3"}, "language_info": {"name": "python"}}, "nbformat": 4, "nbformat_minor": 5}
Path(sys.argv[1]).write_text(json.dumps(nb, ensure_ascii=False, indent=1), encoding="utf-8")
print("ok", sys.argv[1])
