import torch, time
from diffusers import AutoPipelineForText2Image
t=time.time()
pipe=AutoPipelineForText2Image.from_pretrained("stabilityai/sdxl-turbo",torch_dtype=torch.bfloat16,variant="fp16")
print("load",time.time()-t,flush=True)
p=open('prompts.md').read()
base="dark graphic novel, heavy black ink, high contrast, desaturated palette with sickly green and rust-orange accents, film grain, dramatic shadows, hatching"
pr=base+', lean unshaven man in his mid-30s, short dark hair, tired eyes with dark circles, worn gray coverall, headlamp hanging around his neck, extreme close-up of his face half in shadow, finger to lips'
t=time.time()
im=pipe(pr,num_inference_steps=4,guidance_scale=0.0,width=576,height=1024,generator=torch.Generator().manual_seed(7)).images[0]
print("gen",time.time()-t)
im.save('/tmp/claude-0/-home-user--/c51cf852-1cd7-4249-b168-faeefc3635d4/scratchpad/test1.png')
