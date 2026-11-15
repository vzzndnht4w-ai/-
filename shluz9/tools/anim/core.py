"""Ядро 2D-рендера (skia): краски, градиенты, свет, текстуры, камера."""
import skia, math, random
import numpy as np
from PIL import Image, ImageFilter
W, H = 1080, 1920

def _hx(h):
    h = h.lstrip('#')
    return ''.join(ch * 2 for ch in h) if len(h) == 3 else h
def C(h, a=1.0):
    h = _hx(h); r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
    return skia.Color(r, g, b, int(255 * max(0, min(1, a))))
def mix(a, b, k):
    a = _hx(a); b = _hx(b)
    r = [int(int(a[i:i+2], 16) * (1 - k) + int(b[i:i+2], 16) * k) for i in (0, 2, 4)]
    return '#%02x%02x%02x' % tuple(r)
def lerp(a, b, k): return a + (b - a) * k
def clamp(x, a=0.0, b=1.0): return max(a, min(b, x))
def ease(x): x = clamp(x); return x * x * (3 - 2 * x)

def hash1(n):
    n = (n * 127.1) % 1000.0
    return (math.sin(n) * 43758.5453) % 1.0
def noise1(x, seed=0):
    i = math.floor(x); f = x - i; f = f * f * (3 - 2 * f)
    return lerp(hash1(i + seed * 17.3), hash1(i + 1 + seed * 17.3), f)

def P(color, a=1.0, style='fill', w=1, blur=0, blend=None, shader=None):
    p = skia.Paint(AntiAlias=True)
    if isinstance(color, str): p.setColor(C(color, a))
    else: p.setColor(color)
    if style == 'stroke':
        p.setStyle(skia.Paint.kStroke_Style); p.setStrokeWidth(w)
        p.setStrokeCap(skia.Paint.kRound_Cap); p.setStrokeJoin(skia.Paint.kRound_Join)
    if blur: p.setMaskFilter(skia.MaskFilter.MakeBlur(skia.kNormal_BlurStyle, blur))
    if blend == 'add': p.setBlendMode(skia.BlendMode.kPlus)
    if blend == 'atop': p.setBlendMode(skia.BlendMode.kSrcATop)
    if blend == 'mul': p.setBlendMode(skia.BlendMode.kMultiply)
    if blend == 'screen': p.setBlendMode(skia.BlendMode.kScreen)
    if shader is not None: p.setShader(shader)
    return p

def lin(x0, y0, x1, y1, stops):
    cols = [C(c, a) for c, a, _ in stops]; pos = [s for _, _, s in stops]
    return skia.GradientShader.MakeLinear([(x0, y0), (x1, y1)], cols, pos)
def rad(x, y, r, stops):
    cols = [C(c, a) for c, a, _ in stops]; pos = [s for _, _, s in stops]
    return skia.GradientShader.MakeRadial((x, y), max(r, 1), cols, pos)

def poly(pts, close=True):
    p = skia.Path(); p.moveTo(*pts[0])
    for q in pts[1:]: p.lineTo(*q)
    if close: p.close()
    return p
def smooth(pts, close=True):
    """Гладкая кривая через точки (Catmull-Rom -> кубические Безье)."""
    n = len(pts); p = skia.Path(); p.moveTo(*pts[0])
    rng = range(n) if close else range(n - 1)
    for i in rng:
        p0 = pts[(i - 1) % n] if (close or i > 0) else pts[i]
        p1 = pts[i]; p2 = pts[(i + 1) % n]
        p3 = pts[(i + 2) % n] if (close or i + 2 < n) else p2
        c1 = (p1[0] + (p2[0] - p0[0]) / 6, p1[1] + (p2[1] - p0[1]) / 6)
        c2 = (p2[0] - (p3[0] - p1[0]) / 6, p2[1] - (p3[1] - p1[1]) / 6)
        p.cubicTo(*c1, *c2, *p2)
    if close: p.close()
    return p
def rect(l, t, r, b): return skia.Rect.MakeLTRB(l, t, r, b)
def oval_path(cx, cy, rx, ry):
    p = skia.Path(); p.addOval(rect(cx - rx, cy - ry, cx + rx, cy + ry)); return p
def capsule(x0, y0, x1, y1, r0, r1=None, steps=0):
    """Капсула-конечность с разной толщиной (единый контур без дыр)."""
    r1 = r0 if r1 is None else r1
    d = math.atan2(y1 - y0, x1 - x0); n = d + math.pi / 2
    nx, ny = math.cos(n), math.sin(n)
    p = skia.Path(); p.moveTo(x0 + nx * r0, y0 + ny * r0); p.lineTo(x1 + nx * r1, y1 + ny * r1)
    p.arcTo(rect(x1 - r1, y1 - r1, x1 + r1, y1 + r1), math.degrees(n), -180, False)
    p.lineTo(x0 - nx * r0, y0 - ny * r0)
    p.arcTo(rect(x0 - r0, y0 - r0, x0 + r0, y0 + r0), math.degrees(n) + 180, -180, False)
    p.close(); return p

# ---------- текстуры (генерируются один раз) ----------
_tex = {}
def _noise_img(w, h, scales, seed, streak=0.0, vertical=False):
    rng = np.random.default_rng(seed); acc = np.zeros((h, w), np.float32)
    for s, wt in scales:
        small = rng.random((max(2, h // s), max(2, w // s))).astype(np.float32)
        im = Image.fromarray((small * 255).astype(np.uint8)).resize((w, h), Image.BICUBIC)
        acc += np.asarray(im, np.float32) / 255 * wt
    acc /= sum(wt for _, wt in scales)
    if streak:
        st = rng.random((1, w) if not vertical else (h, 1)).astype(np.float32)
        st = np.repeat(st, h, 0) if not vertical else np.repeat(st, w, 1)
        im = Image.fromarray((st * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(2))
        acc = acc * (1 - streak) + np.asarray(im, np.float32) / 255 * streak
    return acc
def texture(name):
    if name in _tex: return _tex[name]
    if name == 'concrete': a = _noise_img(512, 512, [(4, .25), (16, .35), (64, .4)], 1, .18, True)
    elif name == 'metal': a = _noise_img(512, 512, [(2, .3), (8, .3), (48, .4)], 2, .5, False)
    elif name == 'rust': a = _noise_img(512, 512, [(3, .2), (12, .4), (40, .4)], 3)
    elif name == 'grain': a = _noise_img(256, 256, [(1, 1)], 4)
    else: raise KeyError(name)
    rgba = np.zeros((a.shape[0], a.shape[1], 4), np.uint8)
    a = 0.52 + 0.48 * (a - a.min()) / max(1e-6, a.max() - a.min())
    v = (a * 255).astype(np.uint8); rgba[..., 0] = v; rgba[..., 1] = v; rgba[..., 2] = v; rgba[..., 3] = 255
    img = skia.Image.fromarray(rgba, colorType=skia.kRGBA_8888_ColorType)
    _tex[name] = img; return img
def tex_shader(name, scale=1.0, ox=0, oy=0):
    m = skia.Matrix(); m.setScale(scale, scale); m.postTranslate(ox, oy)
    return texture(name).makeShader(skia.TileMode.kRepeat, skia.TileMode.kRepeat, skia.SamplingOptions(skia.FilterMode.kLinear), m)

def texture_fill(c, path, base, tex, scale=1.0, strength=0.25, ox=0, oy=0, dark=True):
    """Заливка цветом + мультиплицируемая текстура поверх (клип по path)."""
    c.save(); c.clipPath(path, doAntiAlias=True)
    c.drawPath(path, P(base))
    p = P('#ffffff', 1, blend='mul', shader=tex_shader(tex, scale, ox, oy))
    p.setAlphaf(clamp(strength * 1.5))
    c.drawPath(path, p); c.restore()

def glow(c, x, y, r, color, a=0.8, blend='add'):
    c.drawCircle(x, y, r, P(color, 1, shader=rad(x, y, r, [(color, a, 0), (color, a * 0.35, 0.35), (color, 0, 1)]), blend=blend))
def glow_ell(c, x, y, rx, ry, color, a=0.8, blend='add'):
    c.save(); c.translate(x, y); c.scale(1, ry / rx)
    glow(c, 0, 0, rx, color, a, blend); c.restore()

class Frame:
    """Поверхность кадра."""
    def __init__(self):
        self.surface = skia.Surface(W, H); self.c = self.surface.getCanvas()
    def rgba(self):
        return self.surface.makeImageSnapshot().toarray(colorType=skia.kRGBA_8888_ColorType)

def camera(c, motion, t, T, zoom=0.08, amp=1.0):
    """Камера в духе мультфильма: наезд, отъезд, панорамы, дрожь. Всегда с запасом по краям."""
    k = ease(t / max(T, 1e-6)); cx, cy = W / 2, H / 2; s = 1.0; dx = dy = 0.0
    if motion == 'zoom_in': s = 1.04 + zoom * k
    elif motion == 'zoom_out': s = 1.04 + zoom * (1 - k)
    elif motion == 'pan_right': s = 1.1; dx = lerp(40, -40, k)
    elif motion == 'pan_left': s = 1.1; dx = lerp(-40, 40, k)
    elif motion == 'tilt_up': s = 1.1; dy = lerp(-50, 50, k)
    elif motion == 'pan_down': s = 1.1; dy = lerp(50, -50, k)
    elif motion == 'shake':
        s = 1.08 + 0.02 * k; dx = (noise1(t * 14, 1) - .5) * 26 * amp; dy = (noise1(t * 14, 2) - .5) * 26 * amp
    else: s = 1.04 + 0.03 * k
    c.translate(cx + dx, cy + dy); c.scale(s, s); c.translate(-cx, -cy)
