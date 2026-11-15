#!/usr/bin/env python3
"""Озвучка серии 0: ElevenLabs. Артём — Wladimir (multilingual_v2), Громов — David (eleven_v3, stability 0.5).
Каждому кадру подгоняется длительность под реальную длину речи, затем пересобираются
prompts.json (duration_sec), subtitles.srt и audio/voiceover.mp3."""
import json, re, subprocess, wave, sys
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent
EP=ROOT/"episodes/ep00_last_turn"; TMP=EP/"audio/_vo"; TMP.mkdir(parents=True,exist_ok=True)
V=ROOT/"tools/voices"
import hashlib, os
SR = 48000
# voice_performance: Артём — тихий, усталый шёпот-дневник (Wladimir); Громов — хриплый командир (David, eleven_v3)
NARR = dict(engine="el", voice_id="Ep3Y4SsCIRz1gD3edazw", model="eleven_multilingual_v2",
            settings={"stability": 0.45, "similarity_boost": 0.8, "style": 0.35, "use_speaker_boost": True, "speed": 1.12})
GROM = dict(engine="el", voice_id="Ga0Zjw9ZBbevb3wIda0V", model="eleven_v3",
            settings={"stability": 0.5, "similarity_boost": 0.85},
            tags={"cmd": "[firm, commanding, low gravelly voice]", "whisper": "[whispering, hoarse, tense]"})
d=json.load(open(EP/"prompts.json"))
CACHE=EP/"audio/_el"; CACHE.mkdir(parents=True,exist_ok=True)
SPENT=[0]
import numpy as np, difflib
from faster_whisper import WhisperModel
WM=WhisperModel("small",device="cpu",compute_type="int8")
TAKES=3; SCORES={}
def _norm(x): return re.sub(r"[^а-яё ]","",x.lower().replace("ё","е").replace("й","и")).split()
def _asr_score(mp3,ref):
    raw=subprocess.run(["ffmpeg","-v","error","-i",str(mp3),"-ar","16000","-ac","1","-f","f32le","-"],capture_output=True,check=True).stdout
    segs,_=WM.transcribe(np.frombuffer(raw,np.float32),language="ru",beam_size=5)
    return difflib.SequenceMatcher(None,_norm(ref),_norm(" ".join(s.text for s in segs))).ratio()
def _take(t,voice,seed):
    key=hashlib.sha1(json.dumps([voice["voice_id"],voice["model"],voice["settings"],t,seed],ensure_ascii=False).encode()).hexdigest()[:16]
    mp3=CACHE/f"{key}.mp3"
    if not mp3.exists():
        body=json.dumps({"text":t,"model_id":voice["model"],"language_code":"ru","voice_settings":voice["settings"],"seed":seed})
        r=subprocess.run(["curl","-s","-m","120","-w","%{http_code}","-o",str(mp3),"-X","POST","-H","Content-Type: application/json","-d",body,
            f"https://api.elevenlabs.io/v1/text-to-speech/{voice['voice_id']}?output_format=mp3_44100_192"],capture_output=True,text=True)
        if r.stdout.strip()!="200": raise RuntimeError(f"ElevenLabs {r.stdout} {mp3.read_bytes()[:200]}")
        SPENT[0]+=len(t)
    return mp3
def tts(text,voice,ls,out):
    """ElevenLabs: TAKES дублей с разными seed, лучший по распознаванию речи (отсев коверканья слов). Кэш по хэшу."""
    ref=text.strip(); t=ref
    if voice.get("tags"):
        t=(voice["tags"]["whisper"]+" "+t.replace("Тихо. ","Тихо... ") if "Тихо" in t else voice["tags"]["cmd"]+" "+t)
    best=None
    for k in range(TAKES):
        mp3=_take(t,voice,1000+k*7); sc=_asr_score(mp3,ref)
        if best is None or sc>best[0]+1e-9: best=(sc,mp3)
        if sc>=0.995: break
    SCORES[ref]=round(best[0],3)
    subprocess.run(["ffmpeg","-y","-loglevel","error","-i",str(best[1]),"-ar",str(SR),"-ac","1","-c:a","pcm_s16le",str(out)],check=True)
def dur(p):
    with wave.open(str(p)) as w: return w.getnframes()/w.getframerate()

segs={}  # frame id -> list of (voice,text)
for f in d["frames"]:
    t=f["voiceover"].strip()
    parts=re.split(r"(«[^»]*»)",t); L=[]
    for p in parts:
        p=p.strip()
        if not re.search(r"\w",p): continue
        prev=L[-1][1] if L else ""
        if p.startswith("«") and (not L and p==t.rstrip(".")+"" or prev.endswith(":") or p==t.strip().rstrip(".")):
            L.append(("g",p.strip("«»").strip()))
        else:
            q=p.replace("«","").replace("»","")
            if L and L[-1][0]=="n": L[-1]=("n",L[-1][1]+" "+q)
            else: L.append(("n",q))
    segs[f["id"]]=L

PAD_LEAD,PAD_TAIL=0.12,0.28
cur=0.0; srt=[]; concat=[]
def ts(x):
    h=int(x//3600);m=int(x%3600//60);s=x%60
    return f"{h:02d}:{m:02d}:{int(s):02d},{int(round((s-int(s))*1000)):03d}".replace(",1000",",999")
for f in d["frames"]:
    i=f["id"]; wavs=[]
    for k,(v,txt) in enumerate(segs[i]):
        out=TMP/f"{i:02d}_{k}.wav"
        if v=="g": tts(txt,GROM,0,out)
        else: tts(txt,NARR,0,out)
        wavs.append((out,txt))
    speech=sum(dur(o) for o,_ in wavs)+0.18*(len(wavs)-1)
    # быстрая речь — ни в коем случае не ускоряем: растягиваем кадр
    total=max(2.4, round(speech+PAD_LEAD+PAD_TAIL,2))
    f["duration_sec"]=round(total,2)
    f["_speech"]=round(speech,2)
    # субтитры: по фразам внутри кадра, пропорционально длине
    t0=cur+PAD_LEAD; allw=sum(len(t.split()) for _,t in wavs)
    for o,txt in wavs:
        ln=dur(o); srt.append((t0,t0+ln,txt)); t0+=ln+0.18
    # кадр-сегмент аудио: lead-silence + речь + хвост до total
    lst=TMP/f"{i:02d}_list.txt"; seg=TMP/f"{i:02d}_full.wav"
    ins=[]; fl=[f"anullsrc=r=48000:cl=mono:d={PAD_LEAD}"]
    cmd=["ffmpeg","-y","-loglevel","error","-f","lavfi","-t",str(PAD_LEAD),"-i","anullsrc=r=48000:cl=mono"]
    for o,_ in wavs: cmd+=["-i",str(o)]
    n=len(wavs)
    flt="[0:a]"+"".join(f"[{j+1}:a]" for j in range(n))+f"concat=n={n+1}:v=0:a=1[a];[a]apad=whole_dur={total}[o]"
    cmd+=["-filter_complex",flt,"-map","[o]","-ar","48000","-ac","1",str(seg)]
    subprocess.run(cmd,check=True)
    concat.append(seg); cur+=total
# склейка + обработка голоса
lst=TMP/"all.txt"; lst.write_text("".join(f"file '{p}'\n" for p in concat))
raw=TMP/"all.wav"
subprocess.run(["ffmpeg","-y","-loglevel","error","-f","concat","-safe","0","-i",str(lst),"-c","copy",str(raw)],check=True)
fx=("highpass=f=90,lowpass=f=7800,equalizer=f=220:t=q:w=1:g=2,acompressor=threshold=-22dB:ratio=3:attack=8:release=120:makeup=4,"
    "aecho=0.8:0.5:55|110:0.16|0.08,loudnorm=I=-16:TP=-1.5:LRA=8")
subprocess.run(["ffmpeg","-y","-loglevel","error","-i",str(raw),"-af",fx,"-ar","48000","-ac","2","-b:a","192k",str(EP/"audio/voiceover.mp3")],check=True)
groups=[]
with open(EP/"subtitles.srt","w",encoding="utf-8") as fh:
    n=0
    for a,b,txt in srt:
        # режем на строки по ~4–5 слов, время пропорционально
        words=[w for w in txt.split() if w!="—"]; chunks=[words[i:i+5] for i in range(0,len(words),5)]
        # не оставляем висячее одно слово
        if len(chunks)>1 and len(chunks[-1])==1:
            last=chunks.pop(); chunks[-1]=chunks[-1]+last
        tot=sum(len(c) for c in chunks); t=a
        for c in chunks:
            e=t+(b-a)*len(c)/tot; n+=1
            wl=sum(len(w) for w in c); tw=t; ws=[]
            for w in c:
                we=tw+(e-t)*len(w)/wl; ws.append({"text":w,"start":round(tw,3),"end":round(we,3)}); tw=we
            groups.append({"start":round(t,3),"end":round(e,3),"words":ws})
            fh.write(f"{n}\n{ts(t)} --> {ts(e)}\n{' '.join(c)}\n\n"); t=e
json.dump(d,open(EP/"prompts.json","w"),ensure_ascii=False,indent=2)
json.dump(groups,open(EP/"captions.json","w"),ensure_ascii=False,indent=1)
print("ElevenLabs characters sent:",SPENT[0]); print("worst ASR scores:",sorted(SCORES.items(),key=lambda x:x[1])[:8]); print("TOTAL",round(cur,1),"s")
