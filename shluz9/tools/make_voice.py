#!/usr/bin/env python3
"""Озвучка серии 0: Piper (локально, русский). Артём — ruslan, Громов — denis.
Каждому кадру подгоняется длительность под реальную длину речи, затем пересобираются
prompts.json (duration_sec), subtitles.srt и audio/voiceover.mp3."""
import json, re, subprocess, wave, sys
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent
EP=ROOT/"episodes/ep00_last_turn"; TMP=EP/"audio/_vo"; TMP.mkdir(parents=True,exist_ok=True)
V=ROOT/"tools/voices"
NARR=(str(V/"ru_RU-ruslan-medium.onnx"),1.14)
GROM=("/tmp/piper/denis.onnx",1.12)
d=json.load(open(EP/"prompts.json"))

def tts(text,model,ls,out):
    subprocess.run(["piper","-m",model[0] if isinstance(model,tuple) else model,"--length-scale",str(ls),
      "--sentence-silence","0.35","--noise-scale","0.5","--noise-w-scale","0.6","-f",str(out)],
      input=text.encode(),check=True,capture_output=True)
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

PAD_LEAD,PAD_TAIL=0.25,0.55
cur=0.0; srt=[]; concat=[]
def ts(x):
    h=int(x//3600);m=int(x%3600//60);s=x%60
    return f"{h:02d}:{m:02d}:{int(s):02d},{int(round((s-int(s))*1000)):03d}".replace(",1000",",999")
for f in d["frames"]:
    i=f["id"]; wavs=[]
    for k,(v,txt) in enumerate(segs[i]):
        out=TMP/f"{i:02d}_{k}.wav"
        if v=="g": tts(txt,GROM,1.2,out)
        else: tts(txt,NARR,NARR[1],out)
        wavs.append((out,txt))
    speech=sum(dur(o) for o,_ in wavs)+0.18*(len(wavs)-1)
    # быстрая речь — ни в коем случае не ускоряем: растягиваем кадр
    total=max(float(f["duration_sec"]), round(speech+PAD_LEAD+PAD_TAIL,2))
    f["duration_sec"]=round(total,2)
    f["_speech"]=round(speech,2)
    # субтитры: по фразам внутри кадра, пропорционально длине
    t0=cur+PAD_LEAD; allw=sum(len(t.split()) for _,t in wavs)
    for o,txt in wavs:
        ln=dur(o); srt.append((t0,t0+ln,txt)); t0+=ln+0.18
    # кадр-сегмент аудио: lead-silence + речь + хвост до total
    lst=TMP/f"{i:02d}_list.txt"; seg=TMP/f"{i:02d}_full.wav"
    ins=[]; fl=[f"anullsrc=r=22050:cl=mono:d={PAD_LEAD}"]
    cmd=["ffmpeg","-y","-loglevel","error","-f","lavfi","-t",str(PAD_LEAD),"-i","anullsrc=r=22050:cl=mono"]
    for o,_ in wavs: cmd+=["-i",str(o)]
    n=len(wavs)
    flt="[0:a]"+"".join(f"[{j+1}:a]" for j in range(n))+f"concat=n={n+1}:v=0:a=1[a];[a]apad=whole_dur={total}[o]"
    cmd+=["-filter_complex",flt,"-map","[o]","-ar","22050","-ac","1",str(seg)]
    subprocess.run(cmd,check=True)
    concat.append(seg); cur+=total
# склейка + обработка голоса
lst=TMP/"all.txt"; lst.write_text("".join(f"file '{p}'\n" for p in concat))
raw=TMP/"all.wav"
subprocess.run(["ffmpeg","-y","-loglevel","error","-f","concat","-safe","0","-i",str(lst),"-c","copy",str(raw)],check=True)
fx=("highpass=f=90,lowpass=f=7800,equalizer=f=220:t=q:w=1:g=2,acompressor=threshold=-22dB:ratio=3:attack=8:release=120:makeup=4,"
    "aecho=0.8:0.5:55|110:0.16|0.08,loudnorm=I=-16:TP=-1.5:LRA=8")
subprocess.run(["ffmpeg","-y","-loglevel","error","-i",str(raw),"-af",fx,"-ar","44100","-ac","2","-b:a","192k",str(EP/"audio/voiceover.mp3")],check=True)
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
            fh.write(f"{n}\n{ts(t)} --> {ts(e)}\n{' '.join(c)}\n\n"); t=e
json.dump(d,open(EP/"prompts.json","w"),ensure_ascii=False,indent=2)
print("TOTAL",round(cur,1),"s")
