#!/usr/bin/env python3
"""Озвучка + пословные тайминги.

  python3 scripts/tts.py <slug>           # настоящая озвучка (edge-tts, нужен доступ к speech.platform.bing.com)
  python3 scripts/tts.py <slug> --fake    # без сети: тайминги по длине текста, звука нет (для проверки вёрстки)

Читает  videos/<slug>/script.json
Пишет   videos/<slug>/timeline.json  и  public/audio/<slug>.mp3
"""
import argparse, asyncio, json, os, re, subprocess, sys, tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
FPS = 30
GAP = 0.30          # пауза между сценами, сек
TAIL = 1.2          # тишина в конце, сек
# Цепочка голосов: берём первый, которым удалось озвучить ВСЕ сцены (голос в одном видео не меняется).
# Сервис иногда отказывает конкретному голосу на конкретном тексте (NoAudioReceived) — тогда идём к следующему.
VOICES = ["ru-RU-DmitryNeural", "en-US-BrianMultilingualNeural", "ru-RU-SvetlanaNeural"]

# Спикеры сериала: голос → запасные голоса, высота/темп и «плёночный» фильтр ffmpeg.
# Если у сцены нет speaker — используется цепочка VOICES без обработки.
NASAL = "highpass=f=280,lowpass=f=3600,equalizer=f=1100:t=q:w=1.2:g=7,acompressor=threshold=-18dB:ratio=3"
PHONE = "highpass=f=350,lowpass=f=3200,acompressor=threshold=-20dB:ratio=4"
SPEAKERS = {
    "narrator": {"voices": ["ru-RU-DmitryNeural", "en-US-BrianMultilingualNeural"], "pitch": "-8Hz", "rate": "-6%", "af": NASAL},
    "zhora":    {"voices": ["en-US-BrianMultilingualNeural", "ru-RU-DmitryNeural"], "pitch": "-14Hz", "rate": "+4%", "af": None},
    "gena":     {"voices": ["ru-RU-DmitryNeural", "en-US-BrianMultilingualNeural"], "pitch": "+28Hz", "rate": "+14%", "af": None},
    "tv":       {"voices": ["ru-RU-SvetlanaNeural"], "pitch": "+0Hz", "rate": "+10%", "af": PHONE},
    "thug":     {"voices": ["en-US-BrianMultilingualNeural", "ru-RU-DmitryNeural"], "pitch": "-22Hz", "rate": "-4%", "af": None},
}
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


def restore_punct(raw, tokens):
    """TTS отдаёт слова без знаков препинания. Возвращаем их из текста сценария (по порядку),
    чтобы в субтитрах были «!» «?» «,» и блоки не склеивали разные фразы."""
    n = lambda x: re.sub(r"[\W_]+", "", x.lower())
    out, j = [], 0
    for w in raw:
        found = next((k for k in range(j, min(j + 4, len(tokens))) if n(tokens[k]) == n(w["text"])), None)
        if found is not None:
            out.append({**w, "text": tokens[found]}); j = found + 1
        else:
            out.append(w)
    return out


def probe(path):
    r = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(path)],
                       capture_output=True, text=True, check=True)
    return float(r.stdout.strip())


async def synth(text, out_mp3, voice, pitch="+0Hz", rate=None):
    import edge_tts
    comm = edge_tts.Communicate(clean(text), voice, rate=rate or RATE, pitch=pitch, boundary="WordBoundary",
                              proxy=os.environ.get("HTTPS_PROXY"))   # aiohttp сам прокси из env не берёт
    words = []
    with open(out_mp3, "wb") as f:
        async for ch in comm.stream():
            if ch["type"] == "audio":
                f.write(ch["data"])
            elif ch["type"] == "WordBoundary":
                s = ch["offset"] / 1e7
                words.append({"text": ch["text"], "start": s, "end": s + ch["duration"] / 1e7})
    return words


def synth_speakers(script, tmp):
    """Озвучивает сцены по спикерам. Для каждого спикера берём первый голос из списка,
    которым удалось озвучить ВСЕ его сцены (голос спикера внутри серии не меняется)."""
    out, chosen = {}, {}
    for spk in dict.fromkeys(sc["speaker"] for sc in script["scenes"] if sc.get("speaker")):
        cfg = SPEAKERS[spk]
        for voice in cfg["voices"]:
            try:
                res = {}
                for i, sc in enumerate(script["scenes"]):
                    if sc.get("speaker") != spk:
                        continue
                    mp3 = tmp / f"{i:03d}.mp3"
                    raw = asyncio.run(synth(sc["text"], mp3, voice, cfg["pitch"], cfg["rate"]))
                    if cfg["af"]:
                        flt = tmp / f"{i:03d}_f.mp3"
                        subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", str(mp3), "-af", cfg["af"], str(flt)], check=True)
                        mp3 = flt
                    res[i] = (mp3, raw)
                out.update(res); chosen[spk] = voice
                break
            except Exception as e:  # noqa: BLE001
                print(f"  {spk}: голос {voice} не справился ({type(e).__name__}) → следующий", file=sys.stderr)
        else:
            sys.exit(f"спикер {spk}: ни один голос не сработал")
    print("голоса:", chosen)
    return out


def build(a, voice):
    vdir = ROOT / "videos" / a.slug
    script = json.loads((vdir / "script.json").read_text(encoding="utf-8"))
    tmp = Path(tempfile.mkdtemp())
    scenes, parts, t = [], [], 0.0
    pre = {} if a.fake else synth_speakers(script, tmp)

    for i, sc in enumerate(script["scenes"]):
        marked = split_marked(sc["text"])
        if a.fake:
            per = [max(0.18, len(w) / 14.0) for w, _ in marked]   # ~14 знаков/сек
            words, c = [], 0.0
            for (w, hl), d in zip(marked, per):
                words.append({"text": w, "start": c, "end": c + d, "hl": hl}); c += d
            dur = c
        else:
            if i in pre:
                mp3, raw = pre[i]
            else:
                mp3 = tmp / f"{i:03d}.mp3"
                raw = asyncio.run(synth(sc["text"], mp3, voice))
            hl_set = {re.sub(r"\W", "", w.lower()) for w, h in marked if h}
            raw = restore_punct(raw, [w for w, _ in marked])
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
    print(f"{a.slug}: {len(scenes)} сцен, {total:.1f} с, {'FAKE (без звука)' if a.fake else 'озвучено (см. выше)' if not a.voice else 'озвучено ' + voice}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("slug")
    ap.add_argument("--fake", action="store_true")
    ap.add_argument("--voice", help="принудительно один голос, без цепочки")
    a = ap.parse_args()
    script = json.loads((ROOT / "videos" / a.slug / "script.json").read_text(encoding="utf-8"))
    chain = [a.voice] if a.voice else ([script["voice"]] if script.get("voice") else []) + VOICES
    if a.fake:
        return build(a, "fake")
    for v in dict.fromkeys(chain):
        try:
            return build(a, v)
        except Exception as e:  # noqa: BLE001
            print(f"голос {v} не справился ({type(e).__name__}), пробую следующий", file=sys.stderr)
    sys.exit("ни один голос не сработал — проверь доступ к speech.platform.bing.com")


if __name__ == "__main__":
    sys.exit(main())
