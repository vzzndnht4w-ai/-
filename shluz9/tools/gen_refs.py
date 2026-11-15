import torch, sys
from diffusers import AutoPipelineForText2Image
from compel import Compel, ReturnedEmbeddingsType
BASE="dark graphic novel, heavy black ink, high contrast, desaturated palette with sickly green and rust-orange accents, film grain, dramatic shadows, hatching, vertical 9:16"
CH={
"artyom":'lean unshaven man in his mid-30s, short dark hair, tired eyes with dark circles, worn gray coverall with a "VENT MAINTENANCE" patch, headlamp hanging around his neck',
"mara":"woman in her late 20s, blonde hair tied in a ponytail, pale face, stained white doctor's coat, bandage on her left forearm",
"gromov":"broad-shouldered man in his mid-50s, gray stubble, scar across the left eyebrow, dark uniform jacket with a commander patch, ring of keys on his belt",
"lyosha":"small boy of 12, messy dark hair, large wide eyes, oversized knitted sweater, old headphones around his neck",
"infected":"infected person with gray skin, dark hollow eye sockets, unnaturally bent joints, always half-hidden in deep shadow",
}
pipe=AutoPipelineForText2Image.from_pretrained("stabilityai/sdxl-turbo",torch_dtype=torch.bfloat16,variant="fp16")
comp=Compel(tokenizer=[pipe.tokenizer,pipe.tokenizer_2],text_encoder=[pipe.text_encoder,pipe.text_encoder_2],returned_embeddings_type=ReturnedEmbeddingsType.PENULTIMATE_HIDDEN_STATES_NON_NORMALIZED,requires_pooled=[False,True],truncate_long_prompts=False)
import os; os.makedirs("references/candidates",exist_ok=True)
for name,desc in CH.items():
    pr=f"{BASE}, {desc}, centered half-body portrait, facing camera, plain dark background, no text"
    c,p=comp(pr)
    for s in range(4):
        im=pipe(prompt_embeds=c,pooled_prompt_embeds=p,num_inference_steps=4,guidance_scale=0.0,width=640,height=1024,generator=torch.Generator().manual_seed(100+s)).images[0]
        im.save(f"references/candidates/{name}_{s}.png"); print(name,s,flush=True)
