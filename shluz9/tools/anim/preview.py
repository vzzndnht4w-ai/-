import sys, time
sys.path.insert(0, '/home/user/-/shluz9/tools')
from anim.core import *
from anim import scenes
SP='/tmp/claude-0/-home-user--/eafafbda-e908-50f4-a8dd-849cdd39fd73/scratchpad/'
ids=[int(x) for x in sys.argv[1].split(',')]; tt=float(sys.argv[2]) if len(sys.argv)>2 else 1.5
ims=[]
for i in ids:
    fr=Frame(); c=fr.c
    t0=time.time()
    try: scenes.SCENES[i](c, tt, 5); print(i, round(time.time()-t0,2))
    except Exception as e:
        import traceback; traceback.print_exc(); print('FAIL',i)
    ims.append(Image.fromarray(fr.rgba()[...,:3]).resize((300,533)))
cols=min(6,len(ims)); rows=(len(ims)+cols-1)//cols
sheet=Image.new('RGB',(300*cols,533*rows))
for k,im in enumerate(ims): sheet.paste(im,((k%cols)*300,(k//cols)*533))
sheet.save(SP+'pv.png')
