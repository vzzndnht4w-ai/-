#!/usr/bin/env python3
"""Озвучка серий Piper (офлайн, голоса CC0) + пословные тайминги через Whisper.

  python3 scripts/tts_piper.py <slug> [--fake]

Читает  videos/<slug>/script.json: {"scenes":[{"id","minDur","lead","lines":[{"spk","text"}]}]}
Пишет   videos/<slug>/timeline.json  (формат как у tts.py + words[].spk)  и  public/audio/<slug>.mp3

Голоса (лицензия данных CC0, см. MODEL_CARD на huggingface.co/rhasspy/piper-voices):
  narrator = dmitri, mark = denis, lesha = denis (+высота), inna = denis (сдвиг высоты и формант, вынужденная мера:
  разрешённых женских русских голосов Piper нет — заменить на живой голос/лицензированный TTS).
"""
import argparse, difflib, json, re, subprocess, sys, tempfile
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
MODELS = Path("/tmp/piper")           # сюда скачаны *.onnx (см. fetch_piper_models)
FPS, GAP, TAIL = 30, 0.35, 1.0
SPK = {
    "narrator": {"model": "dmitri", "af": "highpass=f=90,lowpass=f=7000,acompressor=threshold=-20dB:ratio=3", "len": 0.94},
    "mark":     {"model": "denis",  "af": "highpass=f=160,lowpass=f=5200,volume=0.8", "len": 0.9},   # шёпот в кадре
    "mark_v":   {"model": "denis",  "af": "highpass=f=90,lowpass=f=6500,acompressor=threshold=-20dB:ratio=3", "len": 0.9},  # закадр (Марк пишет в тетрадь)
    "lesha":    {"model": "denis",  "af": "rubberband=pitch=1.16:formant=shifted,highpass=f=120", "len": 0.92},
    "inna":     {"model": "denis",  "af": "rubberband=pitch=1.38:formant=shifted,highpass=f=160", "len": 0.92},
}


def run(cmd, **kw):
    return subprocess.run(cmd, check=True, capture_output=True, **kw)


def fetch_piper_models():
    MODELS.mkdir(parents=True, exist_ok=True)
    base = "https://huggingface.co/rhasspy/piper-voices/resolve/main/ru/ru_RU"
    for v in {c["model"] for c in SPK.values()}:
        for ext in ("onnx", "onnx.json"):
            f = MODELS / f"{v}.{ext}"
            if not f.exists() or f.stat().st_size < 1000:
                run(["curl", "-sSL", "-m", "300", "-o", str(f), f"{base}/{v}/medium/ru_RU-{v}-medium.{ext}"])


def synth(text, spk, out):
    cfg = SPK[spk]
    raw = out.with_suffix(".raw.wav")
    run([sys.executable, "-m", "piper", "-m", str(MODELS / f"{cfg['model']}.onnx"), "-f", str(raw), "--length-scale", str(cfg["len"])],
        input=text.encode())
    run(["ffmpeg", "-y", "-v", "error", "-i", str(raw), "-af", cfg["af"], "-ar", "22050", "-ac", "1", str(out)])


def dur(path):
    r = run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(path)])
    return float(r.stdout.decode().strip())


def pcm16k(path):
    raw = run(["ffmpeg", "-v", "error", "-i", str(path), "-f", "f32le", "-ac", "1", "-ar", "16000", "-"]).stdout
    return np.frombuffer(raw, dtype=np.float32)


_wm = None
def asr_words(path):
    global _wm
    if _wm is None:
        from faster_whisper import WhisperModel
        _wm = WhisperModel("small", device="cpu", compute_type="int8")
    segs, _ = _wm.transcribe(pcm16k(path), language="ru", word_timestamps=True)
    return [(w.word.strip(), w.start, w.end) for s in segs for w in s.words]


N = lambda s: re.sub(r"[\W_]+", "", s.lower())


def align(tokens, asr, total):
    """Сопоставляем слова сценария с распознанными (по порядку), остальным — интерполяция между якорями."""
    n = len(tokens)
    st, en = [None] * n, [None] * n
    if asr:
        sm = difflib.SequenceMatcher(None, [N(t) for t in tokens], [N(w[0]) for w in asr], autojunk=False)
        for a, b, size in sm.get_matching_blocks():
            for k in range(size):
                st[a + k], en[a + k] = asr[b + k][1], asr[b + k][2]
        # не совпавшие, но стоящие вплотную к якорям слова приблизим интерполяцией ниже
        lo = asr[0][1]; hi = asr[-1][2]
    else:
        lo, hi = 0.0, total
    i = 0
    while i < n:
        if st[i] is not None:
            i += 1; continue
        j = i
        while j < n and st[j] is None:
            j += 1
        a = en[i - 1] if i > 0 else lo
        b = st[j] if j < n else hi
        if b < a: b = a + 0.2 * (j - i)
        weights = [max(2, len(N(tokens[k]))) for k in range(i, j)]
        tot, c = sum(weights), a
        for k, wgt in zip(range(i, j), weights):
            d = (b - a) * wgt / tot
            st[k], en[k] = c, c + d
            c += d
        i = j
    return st, en


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("slug"); ap.add_argument("--fake", action="store_true")
    a = ap.parse_args()
    vdir = ROOT / "videos" / a.slug
    script = json.loads((vdir / "script.json").read_text(encoding="utf-8"))
    tmp = Path(tempfile.mkdtemp())
    if not a.fake:
        fetch_piper_models()
    scenes, parts, t = [], [], 0.0
    sil = lambda sec, name: (run(["ffmpeg", "-y", "-v", "error", "-f", "lavfi", "-i", "anullsrc=r=22050:cl=mono", "-t", f"{sec:.3f}", str(tmp / name)]), tmp / name)[1]
    for si, sc in enumerate(script["scenes"]):
        lead = sc.get("lead", 0.3)
        words, cur, wavs = [], lead, []
        if lead > 0: wavs.append(sil(lead, f"s{si}_lead.wav"))
        for li, ln in enumerate(sc.get("lines", [])):
            toks = ln["text"].replace("*", "").split()
            if a.fake:
                d = sum(max(0.18, len(x) / 13) for x in toks); st = []; c = 0
                for x in toks: st.append((c, c + max(0.18, len(x) / 13))); c += max(0.18, len(x) / 13)
                ws, we = [s for s, _ in st], [e for _, e in st]
            else:
                f = tmp / f"s{si}_l{li}.wav"
                synth(ln["text"].replace("*", ""), ln["spk"], f)
                d = dur(f); wavs.append(f)
                ws, we = align(toks, asr_words(f), d)
            for k, x in enumerate(toks):
                words.append({"text": x, "start": round(t + cur + ws[k], 3), "end": round(t + cur + we[k], 3), "hl": False, "spk": ln["spk"]})
            cur += d
            if li < len(sc.get("lines", [])) - 1:
                gap = ln.get("gap", GAP); wavs.append(sil(gap, f"s{si}_g{li}.wav")); cur += gap
        length = max(cur + 0.4, sc.get("minDur", 0))
        if length > cur: wavs.append(sil(length - cur, f"s{si}_pad.wav"))
        parts.extend(wavs)
        scenes.append({"id": sc["id"], "startSec": round(t, 3), "endSec": round(t + length, 3), "words": words})
        t += length
    total = t + TAIL
    audio = None
    if not a.fake:
        parts.append(sil(TAIL, "tail.wav"))
        lst = tmp / "list.txt"; lst.write_text("".join(f"file '{p}'\n" for p in parts))
        out = ROOT / "public" / "audio"; out.mkdir(parents=True, exist_ok=True)
        run(["ffmpeg", "-y", "-v", "error", "-f", "concat", "-safe", "0", "-i", str(lst), "-ar", "44100", "-b:a", "160k", str(out / f"{a.slug}.mp3")])
        audio = f"audio/{a.slug}.mp3"
    (vdir / "timeline.json").write_text(json.dumps({"fps": FPS, "totalSec": round(total, 3), "audio": audio, "scenes": scenes}, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"{a.slug}: {len(scenes)} сцен, {total:.1f} с, {'FAKE' if a.fake else 'озвучено Piper'}")


if __name__ == "__main__":
    main()
