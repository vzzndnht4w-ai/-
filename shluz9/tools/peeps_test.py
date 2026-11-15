import re, cairosvg
from pathlib import Path
from PIL import Image
import io
A = Path("/home/user/op-creator/Flat Assets/Separate Atoms")
def inner(p, white=None, black=None):
    t = (A / p).read_text()
    t = re.sub(r'^.*?<svg[^>]*>', '', t, flags=re.S); t = t.rsplit('</svg>', 1)[0]
    t = re.sub(r'<title>.*?</title>|<desc>.*?</desc>|<!--.*?-->', '', t, flags=re.S)
    if white: t = t.replace('#FFFFFF', white).replace('#FFF', white)
    if black: t = t.replace('#000000', black)
    return t
def peep(body, head, face, fh, skin, cloth, hair, ink='#0b0f0e', acc=None):
    s = f'''<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" width="1136" height="1533" viewBox="0 0 1136 1533">
<g transform="translate(147,639)">{inner('body/'+body, cloth, ink)}</g>
<g transform="translate(372,180)">{inner('head/'+head, hair, ink)}
<g transform="translate(159,186)">{inner('face/'+face, skin, ink)}</g>
<g transform="translate(123,338)">{inner('facial-hair/'+fh, hair, ink)}</g></g></svg>'''
    return Image.open(io.BytesIO(cairosvg.svg2png(bytestring=s.encode(), output_width=568))).convert('RGBA')
cs = [("Shirt and Coat.svg","Short 3.svg","Tired.svg","Chin.svg",'#d9b192','#6b746d','#e8e1d0'),
      ("Blazer Black Tee.svg","Gray Short.svg","Serious.svg","Full 2.svg",'#cfa686','#2a3030','#b9b9b4'),
      ("Shirt and Coat.svg","Bun.svg","Calm.svg","* None.svg",'#ecd2bd','#e7eae4','#d9bd72'),
      ("Sweater.svg","Medium Bangs.svg","Fear.svg","* None.svg",'#e3bfa3','#7d8f7a','#3b2a22')]
sheet = Image.new('RGBA', (568*4, 766), '#10201b')
for i, c in enumerate(cs):
    im = peep(*c); sheet.alpha_composite(im, (i*568, 0))
sheet.convert('RGB').save('/tmp/claude-0/-home-user--/c51cf852-1cd7-4249-b168-faeefc3635d4/scratchpad/peeps.png')
