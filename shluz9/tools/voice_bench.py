import numpy as np
import torch, subprocess, difflib, re, sys, wave
from faster_whisper import WhisperModel
SP='/tmp/claude-0/-home-user--/c51cf852-1cd7-4249-b168-faeefc3635d4/scratchpad/'
T=["Радиоактивные осадки не просто убивали тех, кто остался наверху. Они за считаные часы превращали людей во что-то другое.",
   "Когда двухсотый выживший переступил порог, Громов посмотрел на толпу в узком коридоре, сжал связку ключей на поясе и отрывисто скомандовал.",
   "Ладони горели, металл надрывно визжал, гидравлика со стоном втягивала многотонную круглую дверь в пазы."]
imp=torch.package.PackageImporter('tools/voices/silero_v3_ru.pt'); m=imp.load_pickle("tts_models","model"); m.to('cpu')
wm=WhisperModel("small",device="cpu",compute_type="int8")
norm=lambda s: re.sub(r'[^а-яё ]','',s.lower().replace('ё','е')).split()
def load16(wav):
    raw=subprocess.run(['ffmpeg','-v','error','-i',wav,'-ar','16000','-ac','1','-f','f32le','-'],capture_output=True,check=True).stdout
    return np.frombuffer(raw,np.float32)
def score(wav,ref):
    segs,_=wm.transcribe(load16(wav),language='ru',beam_size=5); hyp=' '.join(s.text for s in segs)
    r,h=norm(ref),norm(hyp); return round(difflib.SequenceMatcher(None,r,h).ratio(),3), hyp
res={}
for name in ['aidar','eugene']:
    sc=[]
    for i,t in enumerate(T):
        p=SP+f'b_{name}_{i}.wav'; m.save_wav(text=t,speaker=name,sample_rate=48000,put_accent=True,put_yo=True,audio_path=p); sc.append(score(p,t)[0])
    res['silero_'+name]=sc
sc=[]
for i,t in enumerate(T):
    p=SP+f'b_piper_{i}.wav'
    subprocess.run(['piper','-m','tools/voices/ru_RU-ruslan-medium.onnx','--length-scale','1.14','-f',p],input=t.encode(),check=True,capture_output=True); sc.append(score(p,t)[0])
res['piper_ruslan']=sc
for k,v in res.items(): print(k,v,'mean',round(sum(v)/len(v),3))
