"""Генерация картинок через Gemini (Nano Banana). Ключ берётся ТОЛЬКО из переменной окружения GEMINI_KEY (в файлы не пишется)."""
import base64, json, os, subprocess, sys
from pathlib import Path
KEY = os.environ.get("GEMINI_KEY", "")
def gen(prompt, out, model="gemini-3-pro-image", refs=(), aspect="3:4", size="1K"):
    parts = [{"text": prompt}]
    for r in refs: parts.append({"inline_data": {"mime_type": "image/png", "data": base64.b64encode(Path(r).read_bytes()).decode()}})
    body = {"contents": [{"parts": parts}], "generationConfig": {"responseModalities": ["IMAGE"], "imageConfig": {"aspectRatio": aspect}}}
    if "3-pro" in model or "3.1" in model: body["generationConfig"]["imageConfig"]["imageSize"] = size
    r = subprocess.run(["curl", "-s", "-m", "180", "-w", "\n%{http_code}", "-H", "Content-Type: application/json", "-H", f"x-goog-api-key: {KEY}", "-d", json.dumps(body),
                        f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"], capture_output=True, text=True)
    txt, _, code = r.stdout.rpartition("\n")
    if code != "200": return False, f"{code}: {txt[:300]}"
    d = json.loads(txt)
    for c in d.get("candidates", []):
        for p in c.get("content", {}).get("parts", []):
            inl = p.get("inlineData") or p.get("inline_data")
            if inl: Path(out).write_bytes(base64.b64decode(inl["data"])); return True, "ok"
    return False, "no image: " + txt[:300]
