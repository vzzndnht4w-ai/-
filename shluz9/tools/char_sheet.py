import sys; sys.path.insert(0,'/home/user/-/shluz9/tools')
from anim.core import *; from anim import chars
SP='/tmp/claude-0/-home-user--/eafafbda-e908-50f4-a8dd-849cdd39fd73/scratchpad/'
who=sys.argv[1].split(',') if len(sys.argv)>1 else ['artyom','gromov','mara','lyosha']
out=sys.argv[2] if len(sys.argv)>2 else 'cs.png'
ims=[]
for w in who:
    fr=Frame(); c=fr.c; c.drawPaint(P('#0d1a16')); c.drawRect(rect(0,0,W,H),P('#000',1,shader=rad(540,700,900,[('#27413a',1,0),('#06100e',1,1)])))
    chars.bust(c,w,540,760,3.4,1.3,dict(lightx=-.6,lcol='#7fffb0'))
    ims.append(Image.fromarray(fr.rgba()[...,:3]).crop((0,200,1080,1500)).resize((540,650)))
sh=Image.new('RGB',(540*len(ims),650))
for i,im in enumerate(ims): sh.paste(im,(i*540,0))
sh.save(SP+out)
