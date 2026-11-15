#!/usr/bin/env python3
"""Собирает блокнот для Google Colab / Kaggle, который генерирует картинки серии по списку ассетов.

  python3 scripts/make_notebook.py series/zombie/ep01_assets.json series/zombie/ep01_generate.ipynb

Модели (все допускают коммерческое использование, лицензии — в sources.md серии):
  * stabilityai/stable-diffusion-xl-base-1.0   — CreativeML Open RAIL++-M
  * madebyollin/sdxl-vae-fp16-fix              — MIT (VAE без артефактов в fp16)
  * rembg (MIT) + модель isnet-general-use     — вырезание фона у спрайтов
"""
import json
import sys
from pathlib import Path


def md(text):
    return {"cell_type": "markdown", "metadata": {}, "source": text.strip().splitlines(keepends=True)}


def code(text):
    return {"cell_type": "code", "metadata": {}, "execution_count": None, "outputs": [],
            "source": text.strip().splitlines(keepends=True)}


def build(assets_path, out_path):
    data = json.loads(Path(assets_path).read_text(encoding="utf-8"))
    n_img = sum(a.get("variants", 1) for a in data["assets"])
    slug = f'{Path(assets_path).parent.name}_{Path(assets_path).stem.replace("_assets", "")}'

    cells = [
        md(f"""
# Генерация картинок: `{slug}`

**Что делать (один раз):**
1. **Colab:** меню *Среда выполнения → Сменить среду → T4 GPU*. **Kaggle:** справа *Settings → Accelerator → GPU T4*, и *Internet → On*.
2. Меню *Выполнить всё* (Colab: *Среда выполнения → Выполнить все*; Kaggle: *Run All*).
3. Ждать. Всего картинок: **{n_img}**, примерно 25–35 с на картинку на T4 → **~{max(1, round(n_img * 30 / 60))} мин**.
4. В конце скачается (Colab) или появится в *Output* (Kaggle) архив `{slug}_images.zip`. Пришли его мне.

Если сессия оборвалась — просто запусти всё заново: готовые картинки не перегенерируются (в Colab они сохраняются на Google Диск, если разрешишь доступ в ячейке 2).
"""),
        code("""
# 1. Установка библиотек (2–3 минуты)
!pip -q install -U diffusers transformers accelerate safetensors "rembg[gpu]" pillow
import torch
assert torch.cuda.is_available(), "Нет GPU! Включи T4 в настройках среды и перезапусти."
print("GPU:", torch.cuda.get_device_name(0))
"""),
        code(f"""
# 2. Папка для результатов (Colab: можно сохранить на Google Диск, чтобы не терять при обрыве)
import os
SLUG = {slug!r}
OUT = None
if os.path.exists("/kaggle/working"):
    OUT = f"/kaggle/working/{{SLUG}}"
else:
    try:
        from google.colab import drive
        drive.mount("/content/drive")
        OUT = f"/content/drive/MyDrive/{{SLUG}}"
    except Exception as e:
        print("Диск не подключён, сохраняю локально:", e)
        OUT = f"/content/{{SLUG}}"
os.makedirs(OUT, exist_ok=True)
print("Сохраняю в", OUT)
"""),
        code("""
# 3. Список картинок (собран режиссёром; не редактируй без нужды)
ASSETS = """ + json.dumps(data, ensure_ascii=False, indent=1) + """
print(len(ASSETS["assets"]), "ассетов")
"""),
        code("""
# 4. Загрузка модели SDXL (≈7 ГБ, 3–5 минут)
from diffusers import StableDiffusionXLPipeline, AutoencoderKL
vae = AutoencoderKL.from_pretrained("madebyollin/sdxl-vae-fp16-fix", torch_dtype=torch.float16)
pipe = StableDiffusionXLPipeline.from_pretrained(
    "stabilityai/stable-diffusion-xl-base-1.0", vae=vae,
    torch_dtype=torch.float16, variant="fp16", use_safetensors=True).to("cuda")
pipe.set_progress_bar_config(disable=True)
"""),
        code("""
# 5. Генерация (пропускает уже готовые файлы)
import time
from rembg import remove, new_session
cut_session = new_session("isnet-general-use")
SIZES = {"bg": (768, 1344), "sprite": (1024, 1024)}
style, neg = ASSETS["style_prefix"], ASSETS["negative"]
t0, done = time.time(), 0
for a in ASSETS["assets"]:
    w, h = SIZES[a["kind"]]
    for v in range(a.get("variants", 1)):
        path = f"{OUT}/{a['id']}_v{v}.png"
        if not os.path.exists(path):
            g = torch.Generator("cuda").manual_seed(int(a["seed"]) + v * 1000)
            img = pipe(prompt=f"{style}, {a['prompt']}", negative_prompt=neg, width=w, height=h,
                       num_inference_steps=30, guidance_scale=6.5, generator=g).images[0]
            img.save(path)
        if a["kind"] == "sprite":
            cut = f"{OUT}/{a['id']}_v{v}_cut.png"
            if not os.path.exists(cut):
                from PIL import Image
                remove(Image.open(path), session=cut_session).save(cut)
        done += 1
        print(f"[{done}] {a['id']} v{v}  ({time.time()-t0:.0f} с)")
print("Готово")
"""),
        code("""
# 6. Превью: все варианты одним листом
from PIL import Image
import glob, math
files = sorted(f for f in glob.glob(f"{OUT}/*.png") if not f.endswith("_cut.png"))
th = 220
thumbs = [Image.open(f).convert("RGB") for f in files]
thumbs = [t.resize((int(t.width * th / t.height), th)) for t in thumbs]
cols = 8; rows = math.ceil(len(thumbs) / cols)
sheet = Image.new("RGB", (cols * 240, rows * (th + 10)), "black")
for i, t in enumerate(thumbs):
    sheet.paste(t, ((i % cols) * 240, (i // cols) * (th + 10)))
sheet.save(f"{OUT}/_preview.jpg"); display(sheet)
"""),
        code("""
# 7. Архив для отправки
import shutil
zip_path = shutil.make_archive(f"/tmp/{SLUG}_images", "zip", OUT)
if os.path.exists("/kaggle/working"):
    shutil.copy(zip_path, "/kaggle/working/"); print("Скачай из Output →", os.path.basename(zip_path))
else:
    from google.colab import files; files.download(zip_path)
"""),
    ]
    nb = {"cells": cells, "metadata": {"accelerator": "GPU", "kernelspec": {"name": "python3", "display_name": "Python 3"},
                                        "language_info": {"name": "python"}, "colab": {"provenance": []}},
          "nbformat": 4, "nbformat_minor": 5}
    Path(out_path).write_text(json.dumps(nb, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"{out_path}: {len(data['assets'])} ассетов, {n_img} картинок")


if __name__ == "__main__":
    build(sys.argv[1], sys.argv[2])
