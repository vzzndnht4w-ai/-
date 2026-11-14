#!/usr/bin/env python3
"""Озвучка + пословные тайминги.

  python3 scripts/tts.py <slug>           # настоящая озвучка (edge-tts, нужен доступ к speech.platform.bing.com)
  python3 scripts/tts.py <slug> --fake    # без сети: тайминги по длине текста, звука нет (для проверки вёрстки)

Читает  videos/<slug>/script.json
Пишет   videos/<slug>/timeline.json  и  public/audio/<slug>.mp3
"""
import argparse, asyncio, json, re, subprocess, sys, tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
FPS = 30
GAP = 0.30          # пауза между сценами, сек
TAIL = 1.2          # тишина в конце, сек
VOICE = "ru-RU-DmitryNeural"   # мужской; женский: ru-RU-SvetlanaNeural
RATE = "+0%"


def split_marked(text):
    """'Так *вот*, друг' -> [('Так',False),('вот,',True),...] (звёздочки = ключевые слова)"""
    out = []
    for tok in re.findall(r"\*[^*]+\*[^\s]*|[^\s]+", text):
        hl = tok.startswith("*")
        out.append((tok.replace("*", ""), hl))
    return out


def clean(text):
    return text.replace("*", "")


def probe(path):
    r = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(path)],
                       capture_output=True, text=True, check=True)
    return float(r.stdout.strip())


async def synth(text, out_mp3):
    import edge_tts
    comm = edge_tts.Communicate(clean(text), VOICE, rate=RATE, boundary="WordBoundary")
    words = []
    with open(out_mp3, "wb") as f:
        async for ch in comm.stream():
            if ch["type"] == "audio":
                f.write(ch["data"])
            elif ch["type"] == "WordBoundary":
                s = ch["offset"] / 1e7
                words.append({"text": ch["text"], "start": s, "end": s + ch["duration"] / 1e7})
    return words


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("slug")
    ap.add_argument("--fake", action="store_true")
    a = ap.parse_args()
    vdir = ROOT / "videos" / a.slug
    script = json.loads((vdir / "script.json").read_text(encoding="utf-8"))
    tmp = Path(tempfile.mkdtemp())
    scenes, parts, t = [], [], 0.0

    for i, sc in enumerate(script["scenes"]):
        marked = split_marked(sc["text"])
        if a.fake:
            per = [max(0.18, len(w) / 14.0) for w, _ in marked]   # ~14 знаков/сек
            words, c = [], 0.0
            for (w, hl), d in zip(marked, per):
                words.append({"text": w, "start": c, "end": c + d, "hl": hl}); c += d
            dur = c
        else:
            mp3 = tmp / f"{i:03d}.mp3"
            raw = asyncio.run(synth(sc["text"], mp3))
            hl_set = {re.sub(r"\W", "", w.lower()) for w, h in marked if h}
            words = [{**w, "hl": re.sub(r"\W", "", w["text"].lower()) in hl_set} for w in raw]
            dur = probe(mp3)
            parts.append(mp3)
        words = [{**w, "start": round(w["start"] + t, 3), "end": round(w["end"] + t, 3)} for w in words]
        scenes.append({"id": sc["id"], "startSec": round(t, 3), "endSec": round(t + dur + GAP, 3), "words": words})
        t += dur + GAP

    total = t + TAIL
    audio = None
    if not a.fake:
        out = ROOT / "public" / "audio"; out.mkdir(parents=True, exist_ok=True)
        lst = tmp / "list.txt"; sil = tmp / "gap.mp3"
        subprocess.run(["ffmpeg", "-y", "-v", "error", "-f", "lavfi", "-i", "anullsrc=r=24000:cl=mono", "-t", str(GAP),
                        "-q:a", "9", str(sil)], check=True)
        lst.write_text("".join(f"file '{p}'\nfile '{sil}'\n" for p in parts))
        subprocess.run(["ffmpeg", "-y", "-v", "error", "-f", "concat", "-safe", "0", "-i", str(lst),
                        "-ar", "44100", "-b:a", "128k", str(out / f"{a.slug}.mp3")], check=True)
        audio = f"audio/{a.slug}.mp3"

    (vdir / "timeline.json").write_text(json.dumps(
        {"fps": FPS, "totalSec": round(total, 3), "audio": audio, "scenes": scenes}, ensure_ascii=False, indent=1),
        encoding="utf-8")
    print(f"{a.slug}: {len(scenes)} сцен, {total:.1f} с, {'FAKE (без звука)' if a.fake else 'озвучено ' + VOICE}")


if __name__ == "__main__":
    sys.exit(main())
