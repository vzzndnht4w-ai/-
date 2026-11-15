import torch, json, sys, os
from pathlib import Path
from PIL import Image
from diffusers import AutoPipelineForText2Image
from compel import Compel, ReturnedEmbeddingsType
ROOT=Path(__file__).resolve().parent.parent; EP=ROOT/"episodes/ep00_last_turn"
OUT=EP/"images/candidates"; OUT.mkdir(parents=True,exist_ok=True)
N=int(sys.argv[1]) if len(sys.argv)>1 else 2
only=set(map(int,sys.argv[2].split(","))) if len(sys.argv)>2 else None
d=json.load(open(EP/"prompts.json"))
from transformers import CLIPVisionModelWithProjection
enc=CLIPVisionModelWithProjection.from_pretrained("h94/IP-Adapter",subfolder="sdxl_models/image_encoder",torch_dtype=torch.bfloat16)
pipe=AutoPipelineForText2Image.from_pretrained("stabilityai/sdxl-turbo",torch_dtype=torch.bfloat16,variant="fp16",image_encoder=enc)
pipe.load_ip_adapter("h94/IP-Adapter",subfolder="sdxl_models",weight_name="ip-adapter_sdxl.bin")
comp=Compel(tokenizer=[pipe.tokenizer,pipe.tokenizer_2],text_encoder=[pipe.text_encoder,pipe.text_encoder_2],returned_embeddings_type=ReturnedEmbeddingsType.PENULTIMATE_HIDDEN_STATES_NON_NORMALIZED,requires_pooled=[False,True],truncate_long_prompts=False)
KEY={"lean unshaven":"artyom","woman in her late":"mara","broad-shouldered":"gromov","small boy":"lyosha","infected person":"infected"}
def who(p): return [v for k,v in KEY.items() if k in p][:2]
for f in d["frames"]:
    if only and f["id"] not in only: continue
    chars=who(f["prompt"])
    if chars:
        ims=[Image.open(ROOT/f"references/{c}.png").convert("RGB").resize((448,512)) for c in chars]
        ref=Image.new("RGB",(448*len(ims),512)); [ref.paste(im,(448*i,0)) for i,im in enumerate(ims)]
        pipe.set_ip_adapter_scale(0.55 if len(chars)==1 else 0.45)
    else:
        ref=Image.new("RGB",(448,512)); pipe.set_ip_adapter_scale(0.0)
    c,p=comp(f["prompt"]+", detailed hands, correct anatomy, clean line art, no text, no watermark")
    for s in range(N):
        fn=OUT/f"{f['id']:02d}_{s}.png"
        if fn.exists(): continue
        im=pipe(prompt_embeds=c,pooled_prompt_embeds=p,ip_adapter_image=ref,num_inference_steps=4,guidance_scale=0.0,width=640,height=1152,generator=torch.Generator().manual_seed(1000*f["id"]+s)).images[0]
        im.save(fn); print(f["id"],s,flush=True)
