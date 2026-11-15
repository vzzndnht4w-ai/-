"""Персонажи: чистая 2D-иллюстрация — контур, двухтоновая светотень, нормальная анатомия.
Голова + плечи (бюст) с дыханием, морганием, поворотом, эмоциями; руки; силуэты; заражённые."""
from .core import *

SPECS = {
 'artyom': dict(skin='#d2a284', shade='#9a6a58', hi='#e6bea0', hair='#1d1613', hair_s='#0b0807', hair_h='#4a3a30',
                cloth='#5a655e', cloth_s='#39433e', cloth_h='#78857c', jaw=.80, cheek=.97, brow=1.0, stub=.55, stub_c='#2a1d19',
                eye='#5a4331', eyew=.92, age=.6, nose=1.0, ear=1.0, hairstyle='short', lash=0),
 'gromov': dict(skin='#c49a7c', shade='#8e6150', hi='#d9b294', hair='#9a9a96', hair_s='#5f5f5c', hair_h='#c8c8c4',
                cloth='#2b3234', cloth_s='#171b1d', cloth_h='#46514f', jaw=.98, cheek=1.02, brow=1.35, stub=.7, stub_c='#8d8e8a',
                eye='#3b3733', eyew=.86, age=1.0, nose=1.18, ear=1.0, hairstyle='buzz', scar=True, lash=0),
 'mara': dict(skin='#ebcab3', shade='#b98a78', hi='#f6dccb', hair='#d6b45f', hair_s='#a5833a', hair_h='#f0d890',
              cloth='#dfe3dc', cloth_s='#a9afa8', cloth_h='#f6f8f3', jaw=.70, cheek=.88, brow=.62, stub=0, stub_c='#000',
              eye='#5f8794', eyew=1.06, age=.2, nose=.82, ear=.9, hairstyle='ponytail', lash=1),
 'lyosha': dict(skin='#e0b99c', shade='#a97a62', hi='#efcdb3', hair='#33241c', hair_s='#18100c', hair_h='#5a4538',
                cloth='#78897a', cloth_s='#4b5a4d', cloth_h='#97a899', jaw=.74, cheek=.96, brow=.62, stub=0, stub_c='#000',
                eye='#33281f', eyew=1.18, age=0, nose=.7, ear=1.0, hairstyle='messy', child=True, lash=0),
}
LINE = '#120b09'

def _flip(pts): return [(-x, y) for x, y in pts]

def face_pts(sp):
    j, ch = max(sp['jaw'], .9), sp['cheek']; ch2 = ch if not sp.get('child') else ch * 1.03
    right = [(0, -112), (46, -106), (76, -82), (86 * ch, -42), (88 * ch2, 0), (82 * ch, 34), (68 * j, 66), (50 * j, 92), (28 * j, 106), (0, 110)]
    left = _flip(right[1:-1][::-1])
    return right + left
def face_path(sp): return smooth(face_pts(sp))

def ink(c, path, w=2.4, a=.95, color=LINE): c.drawPath(path, P(color, a, 'stroke', w))

def cel(c, path, base, shade, edge, side=1, hi=None, hi_a=0.0, line=2.4, w=95):
    """Заливка + резкая тень по терминатору (тень со стороны side) + обводка."""
    c.drawPath(path, P(base)); c.save(); c.clipPath(path, doAntiAlias=True)
    sh = smooth([(edge + side * 4, -190), (edge - side * 6, -60), (edge + side * 2, 20), (edge - side * 8, 90), (edge, 190), (side * 400, 190), (side * 400, -190)])
    c.drawPath(sh, P(shade, .82)); c.restore()
    if line: ink(c, path, line)

def eyelid_open(t, seed=0, period=3.6, closed=0.0):
    ph = (t + seed * 1.7) % period
    b = 0.0
    if ph < .15: b = math.sin(ph / .15 * math.pi)
    elif 1.8 < ph < 1.92 and period > 3: b = math.sin((ph - 1.8) / .12 * math.pi) * .8
    return clamp(1 - max(b, closed))

def brow_shape(x0, y0, x1, y1, th, arch):
    """Сужающаяся бровь: толстая у переносицы, тонкая к виску."""
    mx, my = (x0 + x1) / 2, (y0 + y1) / 2 - arch
    top = [(x0, y0 - th), (mx, my - th * .8), (x1, y1 - th * .25)]; bot = [(x1, y1 + th * .15), (mx, my + th * .5), (x0, y0 + th * .7)]
    return smooth(top + bot)

def eye(c, sp, cx, cy, side, eo, look, o, t):
    w = 19 * sp['eyew']; h = (9.2 + 3 * o.get('fear', 0)) * sp['eyew'] * eo * (1.12 if sp.get('child') else 1)
    sq = o.get('squint', 0) * 3.5
    ox, ix = cx + side * w, cx - side * w * .96   # внешний / внутренний уголки
    top = [(ix, cy + 1), (cx - side * w * .35, cy - h - 2 + sq), (cx + side * w * .35, cy - h * 1.02 + sq), (ox, cy - 1)]
    bot = [(ox, cy - 1 + 1.5), (cx + side * w * .4, cy + h * .62), (cx - side * w * .3, cy + h * .68)]
    eye_p = smooth(top + bot)
    c.drawPath(eye_p, P('#e9e3d6')); c.save(); c.clipPath(eye_p, doAntiAlias=True)
    c.drawRect(rect(cx - w * 1.4, cy - h * 2, cx + w * 1.4, cy - h * .25 + sq * 0), P(sp['shade'], .38))
    px = cx + look[0] * 6 - side * 0; py = cy + look[1] * 3.5; ir = 8.6 * (1.15 if sp.get('child') else 1) * (1 - o.get('fear', 0) * .08)
    c.drawCircle(px, py + 1, ir, P(sp['eye'])); c.drawCircle(px, py + 1, ir * .52, P('#070606'))
    c.drawCircle(px, py + 1, ir, P('#000', 1, 'stroke', 1.6))
    c.drawCircle(px - ir * .35, py - ir * .35, 2.5, P('#fff', .95)); c.drawCircle(px + ir * .3, py + ir * .4, 1.2, P('#fff', .5))
    c.drawRect(rect(cx - w * 1.4, cy - h - 4 + sq, cx + w * 1.4, cy - h * .3 + sq), P('#000', .32, blur=2.5))   # тень века на глазе
    c.restore()
    # верхнее веко — толстая линия, нижнее тоньше
    c.drawPath(smooth(top, False), P(LINE, 1, 'stroke', 3.6 * (1.15 if sp['age'] > .5 else 1)))
    c.drawPath(smooth([bot[0], bot[1], bot[2], (ix, cy + 1.5)], False), P(LINE, .55, 'stroke', 1.4))
    # складка века
    c.drawPath(smooth([(ix, cy - 2), (cx, cy - h * 1.55 - 5 + sq * .5), (ox + side * 2, cy - 2)], False), P(sp['shade'], .85, 'stroke', 1.8))
    if sp.get('lash'):
        c.drawPath(smooth([(ox - side * 3, cy - h * .7), (ox + side * 5, cy - h * 1.1 - 2), (ox + side * 8, cy - h * 1.5 - 3)], False), P(LINE, 1, 'stroke', 2.2))
    # мешки/тени под глазами
    if sp['age'] > .3:
        a = .38 + .3 * o.get('tired', 0)
        c.drawPath(smooth([(ix + side * -2, cy + h * .9 + 4), (cx, cy + h * .9 + 10), (ox - side * 2, cy + h * .75 + 4)], False), P('#4a2f3b', a, 'stroke', 7, blur=3))
        c.drawPath(smooth([(ix, cy + h + 11), (cx, cy + h + 15), (ox - side * 4, cy + h + 10)], False), P(sp['shade'], .6, 'stroke', 1.6))

def brows(c, sp, cx, cy, side, o):
    th = 4.2 * sp['brow'] * (.7 if sp.get('child') else 1)
    inner_up = o.get('worry', 0) * 7 + o.get('fear', 0) * 8 - o.get('frown', 0) * 5
    outer_up = o.get('fear', 0) * 5 - o.get('frown', 0) * 1 + o.get('tired', 0) * 1.5
    x0 = cx - side * 22; y0 = cy - 26 - inner_up; x1 = cx + side * 28; y1 = cy - 25 - outer_up + (o.get('frown', 0) * 2)
    col = sp['hair'] if sp['hairstyle'] != 'ponytail' else sp['hair_s']
    if sp['hairstyle'] == 'buzz': col = sp['hair_s']
    p = brow_shape(x0, y0, x1, y1, th, 3 + sp['brow'])
    c.drawPath(p, P(col)); ink(c, p, 1.2, .8)

def nose(c, sp, ox, side_s):
    n = sp['nose']; tip = 34 * n
    br = smooth([(ox - 5, -18), (ox - 8 * n, 12), (ox - 12 * n, tip - 4), (ox, tip + 4), (ox + 12 * n, tip - 4), (ox + 8 * n, 12), (ox + 5, -18)])
    # теневая плоскость носа со стороны тени
    pl = poly([(ox + side_s * 4, -20), (ox + side_s * 14 * n, tip - 3), (ox + side_s * 2, tip + 4), (ox + side_s * 2, -4)])
    c.drawPath(pl, P(sp['shade'], .85))
    c.drawPath(smooth([(ox - 6 * n, tip - 1), (ox - 12 * n, tip - 5), (ox - 11 * n, tip - 12)], False), P(LINE, .8, 'stroke', 1.8))
    c.drawPath(smooth([(ox + 6 * n, tip - 1), (ox + 12 * n, tip - 5), (ox + 11 * n, tip - 12)], False), P(LINE, .8, 'stroke', 1.8))
    c.drawPath(smooth([(ox - 9 * n, tip + 1), (ox - 3, tip + 6), (ox + 3, tip + 6), (ox + 9 * n, tip + 1)], False), P('#3a1d14', .9, 'stroke', 2.6))
    c.drawPath(smooth([(ox - 3, 8), (ox - 4, tip - 14)], False), P(sp['hi'], .9, 'stroke', 2.2))

def mouth(c, sp, ox, o, side_s):
    y = 66 + (4 if sp.get('child') else 0); w = 20 * (.85 if sp.get('child') else 1)
    open_ = o.get('mouth', 0) * 15; sm = o.get('smile', 0) * 5 - o.get('frown', 0) * 1.5 - o.get('worry', 0) * 1.5 - o.get('tired', 0) * 1
    lip = '#a2574f' if sp.get('lash') or sp.get('child') else '#8a4f46'
    if sp['age'] > .6: lip = '#7a463e'
    if open_ > 1.5:
        mp = smooth([(ox - w, y - sm * .2), (ox - w * .4, y - 4), (ox + w * .4, y - 4), (ox + w, y - sm * .2), (ox + w * .6, y + open_ * .7), (ox, y + open_), (ox - w * .6, y + open_ * .7)])
        c.drawPath(mp, P('#240c0c')); c.save(); c.clipPath(mp, doAntiAlias=True)
        c.drawRect(rect(ox - w, y - 4, ox + w, y + 3), P('#e4ddcd')); c.drawPath(oval_path(ox, y + open_ * .95, w * .55, open_ * .45), P('#8a3a3a')); c.restore()
        ink(c, mp, 1.8, .9)
        c.drawPath(smooth([(ox - w * .6, y + open_ * .75 + 3), (ox, y + open_ + 5), (ox + w * .6, y + open_ * .75 + 3)], False), P(lip, 1, 'stroke', 4.5))
    else:
        c.drawPath(smooth([(ox - w, y - sm * .15), (ox - w * .45, y - 4.5), (ox, y - 2.5), (ox + w * .45, y - 4.5), (ox + w, y - sm * .15), (ox + w * .5, y + 1.5), (ox - w * .5, y + 1.5)]), P(lip))
        c.drawPath(smooth([(ox - w * .55, y + 1), (ox, y + 8.5), (ox + w * .55, y + 1)], False), P(lip, .9, 'stroke', 5.2))
        c.drawPath(smooth([(ox - w * 1.04, y - sm * .15 - sm * .4), (ox - w * .4, y + .5), (ox + w * .4, y + .5), (ox + w * 1.04, y - sm * .15 - sm * .4)], False), P(LINE, .95, 'stroke', 2.4))
    c.drawPath(smooth([(ox - w * .5, y + 12), (ox, y + 14), (ox + w * .5, y + 12)], False), P(sp['shade'], .65, 'stroke', 2.6, blur=1.2))
    c.drawPath(smooth([(ox - 5, y - 10), (ox, y - 8.5), (ox + 5, y - 10)], False), P(sp['shade'], .6, 'stroke', 1.8))

def ear(c, sp, sx, shade_side):
    ex = sx * (86 * sp['cheek'] + 2); k = sp['ear']
    p = smooth([(ex - sx * 6, -14 * k), (ex + sx * 8 * k, -18 * k), (ex + sx * 15 * k, -2 * k), (ex + sx * 12 * k, 22 * k), (ex + sx * 4, 36 * k), (ex - sx * 6, 30 * k)])
    c.drawPath(p, P(sp['skin'])); c.save(); c.clipPath(p, doAntiAlias=True)
    if sx == shade_side: c.drawPath(p, P(sp['shade'], .8))
    c.restore(); ink(c, p, 2.0)
    c.drawPath(smooth([(ex + sx * 9 * k, -8 * k), (ex + sx * 5 * k, 6 * k), (ex + sx * 8 * k, 20 * k)], False), P(sp['shade'], 1, 'stroke', 2.2))
    c.drawPath(smooth([(ex + sx * 2, 8 * k), (ex + sx * 3, 20 * k)], False), P(LINE, .6, 'stroke', 1.4))

def hair_strands(c, color, pts_list, w=2.0, a=.55):
    for pts in pts_list: c.drawPath(smooth(pts, False), P(color, a, 'stroke', w))

def hair_front(c, sp, o, side_s, t):
    hs = sp['hairstyle']; hc, hs_c, hh = sp['hair'], sp['hair_s'], sp['hair_h']
    sway = math.sin(t * 1.1) * 1.2
    if hs == 'short':
        p = smooth([(-90, -18), (-94, -78), (-60, -118), (-8, -132), (52, -124), (92, -92), (90, -18), (82, -52), (62, -78), (28, -98 + sway), (-14, -94), (-52, -80), (-74, -50)])
        c.drawPath(p, P(hc)); c.save(); c.clipPath(p, doAntiAlias=True)
        c.drawRect(rect(-120, -150, 120, 0), P(hs_c, 1, shader=lin(-side_s * 30, 0, side_s * 90, 0, [(hs_c, 0, 0), (hs_c, .95, 1)])))
        hair_strands(c, hh, [[(-70, -100), (-30, -118), (20, -116)], [(-50, -86), (0, -106), (50, -104)], [(-20, -96), (30, -108), (70, -92)]], 3.2, .5)
        hair_strands(c, hs_c, [[(-80, -70), (-72, -40)], [(70, -76), (78, -44)], [(-10, -92), (-24, -70), (-36, -52)]], 2.6, .7)
        c.restore(); ink(c, p, 2.4)
        c.drawPath(smooth([(-48, -86), (-30, -96), (-6, -92)], False), P(hc, 1, 'stroke', 5))   # чёлка-прядь
    elif hs == 'buzz':
        p = smooth([(-90, -14), (-92, -70), (-62, -112), (-8, -124), (50, -116), (90, -76), (90, -14), (82, -40), (62, -62), (30, -78), (-10, -84), (-48, -72), (-74, -44)])
        c.drawPath(p, P(hc)); c.save(); c.clipPath(p, doAntiAlias=True)
        c.drawRect(rect(-120, -150, 120, 0), P(hs_c, 1, shader=lin(-side_s * 30, 0, side_s * 90, 0, [(hs_c, 0, 0), (hs_c, .9, 1)])))
        for i in range(70):
            x = -88 + hash1(i * 4.1) * 176; y = -120 + hash1(i * 2.3) * 56
            c.drawLine(x, y, x + (hash1(i * 7) - .5) * 10, y + 7 + hash1(i) * 5, P(hs_c if i % 2 else hh, .55, 'stroke', 1.4))
        c.restore(); ink(c, p, 2.4)
    elif hs == 'ponytail':
        p = smooth([(-94, -6), (-96, -80), (-60, -124), (-4, -136), (58, -126), (94, -92), (96, -6), (88, -46), (66, -70), (36, -84), (6, -76), (-24, -62), (-52, -48), (-78, -28)])
        c.drawPath(p, P(hc)); c.save(); c.clipPath(p, doAntiAlias=True)
        c.drawRect(rect(-120, -150, 120, 0), P(hs_c, 1, shader=lin(-side_s * 20, 0, side_s * 90, 0, [(hs_c, 0, 0), (hs_c, .85, 1)])))
        hair_strands(c, hh, [[(-88, -40), (-62, -96), (-8, -122)], [(-70, -30), (-30, -80), (30, -112)], [(20, -112), (66, -108), (90, -76)], [(-40, -50), (0, -94), (50, -104)]], 3.6, .6)
        hair_strands(c, hs_c, [[(-90, -20), (-84, -60)], [(78, -92), (92, -56)], [(-20, -70), (-52, -48)]], 2.4, .7)
        c.restore(); ink(c, p, 2.4)
        # пробор и чёлка набок
        c.drawPath(smooth([(-20, -128), (-14, -100), (6, -78)], False), P(hs_c, .8, 'stroke', 2.2))
        for (x, y, dx, dy) in [(-64, -44, 2, 30), (-76, -30, -3, 26)]:
            sp_ = smooth([(x, y), (x + dx * .6, y + dy * .6), (x + dx, y + dy)], False); c.drawPath(sp_, P(hc, 1, 'stroke', 5.5)); ink(c, sp_, 1.0, .6)
    elif hs == 'messy':
        pts = [(-96, -8), (-98, -70), (-78, -110), (-40, -128), (-8, -112), (24, -134), (58, -120), (88, -100), (102, -62), (94, -8), (84, -44), (58, -66), (36, -52), (6, -72), (-22, -50), (-48, -64), (-78, -44)]
        p = smooth(pts); c.drawPath(p, P(hc)); c.save(); c.clipPath(p, doAntiAlias=True)
        c.drawRect(rect(-120, -150, 120, 0), P(hs_c, 1, shader=lin(-side_s * 20, 0, side_s * 90, 0, [(hs_c, 0, 0), (hs_c, .9, 1)])))
        hair_strands(c, hh, [[(-84, -84), (-50, -112), (-10, -108)], [(10, -112), (50, -118), (86, -96)], [(-60, -70), (-30, -96)]], 3.0, .55)
        c.restore(); ink(c, p, 2.4)
        for (x, y, dx, dy) in [(-30, -56, -6, 18), (4, -70, 10, 20), (-56, -60, -12, 14), (40, -60, 8, 16)]:
            sp_ = smooth([(x, y), (x + dx * .5, y + dy * .6), (x + dx, y + dy)], False); c.drawPath(sp_, P(hc, 1, 'stroke', 6)); ink(c, sp_, 1.0, .6)

def hair_back(c, sp):
    hs = sp['hairstyle']
    if hs == 'ponytail':
        p = smooth([(-98, -40), (-84, -118), (0, -140), (86, -118), (100, -40), (110, 20), (130, 90), (112, 160), (82, 120), (74, 40), (-70, 40), (-82, 120), (-108, 150), (-122, 80), (-108, 10)])
        c.drawPath(p, P(sp['hair_s'])); ink(c, p, 2.2)
    if hs == 'messy':
        p = smooth([(-100, -30), (-92, -118), (0, -142), (94, -118), (102, -30), (88, 20), (-88, 20)]); c.drawPath(p, P(sp['hair_s'])); ink(c, p, 2.2)

def stubble(c, sp, fp):
    if sp['stub'] <= 0: return
    c.save(); c.clipPath(fp, doAntiAlias=True)
    st = smooth([(-92, 8), (-70, 14), (-52, 36), (-30, 56), (-18, 52), (0, 56), (18, 52), (30, 56), (52, 36), (70, 14), (92, 8), (100, 130), (-100, 130)])
    c.drawPath(st, P(sp['stub_c'], sp['stub'] * .62, blur=2.5))
    for i in range(380):
        x = (hash1(i * 3.7) - .5) * 190; y = 8 + hash1(i * 6.1) * 112
        inside = (y > 52 and abs(x) < 84 - (y - 52) * .6) or (y > 8 and abs(x) > 56 and abs(x) < 92 - (y - 8) * .25) or (y > 54 and abs(x) < 70)
        if inside and hash1(i * 1.7) > .35: c.drawCircle(x, y, 1.0, P(sp['stub_c'], .5))
    c.restore()

def head(c, who, t, o=None):
    """Голова в локальных координатах (радиус ≈100), центр (0,0)."""
    o = o or {}; sp = dict(SPECS[who]); R = 100
    if o.get('pale'):
        for k in ('skin', 'shade', 'hi'): sp[k] = mix(sp[k], '#cdd5cb', o['pale'])
    turn = o.get('turn', 0.0); look = o.get('look', (0, 0)); tilt = o.get('tilt', 0.0)
    eo = o.get('eyes', eyelid_open(t, hash1(len(who)), closed=o.get('squint', 0) * .5))
    lightx = o.get('lightx', -.6); lcol = o.get('lcol', '#7fffb0'); under = o.get('under', 0.0)
    side_s = 1 if lightx < 0 else -1          # сторона тени
    edge = side_s * 30 - turn * 6 * side_s
    c.save(); c.rotate(tilt)
    hair_back(c, sp)
    # шея
    nk = smooth([(-38, 70), (-40, 112), (-52, 150), (52, 150), (40, 112), (38, 70)])
    c.drawPath(nk, P(sp['skin'])); c.save(); c.clipPath(nk, doAntiAlias=True)
    c.drawPath(smooth([(side_s * -4, 60), (side_s * -2, 150), (side_s * 80, 150), (side_s * 80, 60)]), P(sp['shade']))
    c.drawPath(oval_path(0, 80, 70, 40), P(sp['shade'], .95, blur=4))   # тень от подбородка
    c.restore(); ink(c, nk, 2.2)
    for sx in (-1, 1): ear(c, sp, sx, side_s)
    fp = face_path(sp)
    cel(c, fp, sp['skin'], sp['shade'], edge, side_s, line=0)
    c.save(); c.clipPath(fp, doAntiAlias=True)
    # подсветка скул и лба (бликовые плоскости)
    c.drawPath(smooth([(-side_s * 40, -70), (-side_s * 20, -50), (-side_s * 52, -40), (-side_s * 66, -58)]), P(sp['hi'], .55))
    c.drawPath(smooth([(-side_s * 30, 24), (-side_s * 58, 14), (-side_s * 70, 34), (-side_s * 40, 40)]), P(sp['hi'], .45))
    if under:
        c.drawRect(rect(-140, -140, 140, 150), P('#000', 1, shader=lin(0, 115, 0, -115, [(lcol, .55 * under, 0), (lcol, .0, .65), ('#000', .55 * under, 1)])))
    # тень от чёлки/лба
    c.drawPath(smooth([(-90, -50), (-40, -64), (40, -66), (90, -50), (90, -24), (-90, -24)]), P(sp['shade'], .35, blur=7))
    c.restore()
    stubble(c, sp, fp)
    ink(c, fp, 2.6)
    ox = turn * 8
    for side in (-1, 1):
        cx_ = side * 37 + ox; cy_ = -6
        brows(c, sp, cx_, cy_, side, o); eye(c, sp, cx_, cy_, side, eo, look, o, t)
    nose(c, sp, ox * 1.4, side_s); mouth(c, sp, ox, o, side_s)
    if sp['age'] > .5:
        for sx in (-1, 1):
            c.drawPath(smooth([(sx * 25 + ox, 26), (sx * 33 + ox, 50), (sx * 29 + ox, 66)], False), P(sp['shade'], .9, 'stroke', 2.0))
    if sp.get('scar'):
        sc = smooth([(46 + ox, -52), (58 + ox, -34), (70 + ox, -10)], False); c.drawPath(sc, P('#d49a92', .95, 'stroke', 3.6)); c.drawPath(sc, P('#7a3a3a', .6, 'stroke', 1.2))
        for k in range(4): c.drawLine(49 + k * 7 + ox, -46 + k * 11, 57 + k * 7 + ox, -50 + k * 11, P('#7a3a3a', .7, 'stroke', 1.4))
    hair_front(c, sp, o, side_s, t)
    # контровой свет по кромке
    c.save(); c.clipPath(fp, doAntiAlias=True)
    sg = -side_s
    c.drawRect(rect(-140, -140, 140, 150), P(lcol, 1, shader=lin(sg * 98, 0, sg * 74, 0, [(lcol, .26, 0), (lcol, 0, 1)]), blend='add'))
    c.restore()
    c.restore()

def torso(c, who, t, o=None, scale_w=1.0):
    """Плечи/одежда. Шея выходит из верхней точки y≈130."""
    o = o or {}; sp = SPECS[who]; br = math.sin(t * 2 * math.pi * .28) * o.get('breath', 1.0)
    lcol = o.get('lcol', '#7fffb0'); lightx = o.get('lightx', -.6); side_s = 1 if lightx < 0 else -1
    k = .78 if sp.get('child') else 1.0; sw = 205 * scale_w * k; top = 128 - br * 1.5
    pts = [(-sw * 1.06, 780), (-sw * 1.04, 300), (-sw * .98, 226), (-sw * .78, 168), (-sw * .5, top + 14), (-52, top - 2), (0, top - 8),
           (52, top - 2), (sw * .5, top + 14), (sw * .78, 168), (sw * .98, 226), (sw * 1.04, 300), (sw * 1.06, 780)]
    body = smooth(pts)
    cel(c, body, sp['cloth'], sp['cloth_s'], -side_s * 20, side_s, line=0)
    c.save(); c.clipPath(body, doAntiAlias=True)
    # тень от головы и воротника на груди
    c.drawPath(oval_path(0, top + 34, 110, 52), P('#000', .32, blur=10))
    # складки: клиновидные тени
    for (x0, y0, x1, y1, x2, y2) in [(-sw * .8, 300, -sw * .6, 420, -sw * .9, 470), (sw * .55, 380, sw * .72, 520, sw * .45, 600), (-sw * .2, 470, -sw * .05, 600, -sw * .3, 700)]:
        c.drawPath(smooth([(x0, y0), (x1, y1), (x2, y2), (x0 + 14, y1)]), P(sp['cloth_s'], .8))
    c.restore()
    ink(c, body, 2.8)
    if who == 'artyom': _artyom_cloth(c, sp, sw, top, br)
    elif who == 'gromov': _gromov_cloth(c, sp, sw, top)
    elif who == 'mara': _mara_cloth(c, sp, sw, top)
    else: _lyosha_cloth(c, sp, sw, top)
    c.save(); c.clipPath(body, doAntiAlias=True)
    sg = -side_s
    c.drawRect(rect(-sw * 1.2, 0, sw * 1.2, 800), P(lcol, 1, shader=lin(sg * sw * 1.04, 0, sg * sw * .82, 0, [(lcol, .4, 0), (lcol, 0, 1)]), blend='add'))
    c.restore()

def _artyom_cloth(c, sp, sw, top, br):
    col = LINE
    # воротник-стойка
    cl = smooth([(-62, top - 6), (-70, top + 40), (-24, top + 64), (0, top + 30), (24, top + 64), (70, top + 40), (62, top - 6), (30, top - 14), (0, top - 4), (-30, top - 14)])
    c.drawPath(cl, P(sp['cloth_s'])); ink(c, cl, 2.2)
    c.drawLine(0, top + 40, 0, 780, P(col, .9, 'stroke', 3))
    for i in range(14): c.drawLine(-5, top + 56 + i * 22, 5, top + 56 + i * 22, P('#9a9a8c', .8, 'stroke', 2))
    # карман на груди, швы плеча
    pk = poly([(80, 300), (170, 296), (170, 372), (80, 376)]); c.drawPath(pk, P(sp['cloth_s'], .9)); ink(c, pk, 2.2); c.drawLine(80, 322, 170, 320, P(col, .8, 'stroke', 2))
    c.drawPath(smooth([(-sw * .52, top + 18), (-sw * .82, 176), (-sw * .98, 240)], False), P(col, .55, 'stroke', 2.2))
    c.drawPath(smooth([(sw * .52, top + 18), (sw * .82, 176), (sw * .98, 240)], False), P(col, .55, 'stroke', 2.2))
    # нашивка VENT MAINTENANCE
    c.save(); c.translate(-sw * .56, 290); c.rotate(-3)
    pt = skia.Path().addRRect(skia.RRect.MakeRectXY(rect(-54, -24, 54, 24), 5, 5)); c.drawPath(pt, P('#c06f26')); c.drawPath(skia.Path().addRRect(skia.RRect.MakeRectXY(rect(-49, -19, 49, 19), 3, 3)), P('#2b1e12', .9, 'stroke', 2))
    c.drawSimpleText('VENT', -17, -4, skia.Font(skia.Typeface('DejaVu Sans', skia.FontStyle.Bold()), 10.5), P('#1d1209'))
    c.drawSimpleText('MAINTENANCE', -41, 12, skia.Font(skia.Typeface('DejaVu Sans', skia.FontStyle.Bold()), 7.6), P('#1d1209')); c.restore()
    # налобный фонарь, висящий на шее
    strap = smooth([(-66, top - 4), (-76, top + 70), (-30, top + 128), (30, top + 128), (76, top + 70), (66, top - 4)], False)
    c.drawPath(strap, P('#0d0f0e', 1, 'stroke', 14)); c.drawPath(strap, P('#5b655f', .35, 'stroke', 2))
    lx, ly = 56, top + 118 + br * 2
    c.drawRoundRect(rect(lx - 30, ly - 22, lx + 30, ly + 22), 10, 10, P('#2c3230')); ink(c, skia.Path().addRRect(skia.RRect.MakeRectXY(rect(lx - 30, ly - 22, lx + 30, ly + 22), 10, 10)), 2.4)
    c.drawCircle(lx, ly, 15, P('#0a0d0c')); c.drawCircle(lx, ly, 10.5, P('#7f9488', .85)); c.drawCircle(lx - 3, ly - 3.5, 3.4, P('#fff', .6))

def _gromov_cloth(c, sp, sw, top):
    col = LINE
    for sx in (-1, 1):
        lap = poly([(sx * 74, top - 8), (sx * 24, top + 78), (sx * 6, top + 22)]); c.drawPath(lap, P('#0c0f10')); ink(c, lap, 2.2)
    c.drawPath(poly([(-24, top + 78), (-6, top + 22), (6, top + 22), (24, top + 78), (0, 780)]), P(sp['cloth_s'])); c.drawLine(0, top + 22, 0, 780, P(col, .95, 'stroke', 3))
    for i in range(5):
        c.drawCircle(20, top + 150 + i * 92, 8, P('#8c7a3e')); c.drawCircle(20, top + 150 + i * 92, 8, P(col, .9, 'stroke', 2)); c.drawCircle(18, top + 148 + i * 92, 3, P('#f0dc9c', .8))
    ep = poly([(sw * .52, top + 14), (sw * .8, 168), (sw * .7, 214), (sw * .4, top + 52)]); c.drawPath(ep, P('#0d1011')); ink(c, ep, 2.2)
    c.drawRect(rect(sw * .5, top + 38, sw * .66, top + 50), P('#a6842f')); c.drawRect(rect(sw * .49, top + 60, sw * .62, top + 70), P('#a6842f'))
    c.save(); c.translate(-sw * .58, 290); c.rotate(-3)
    pt = skia.Path().addRRect(skia.RRect.MakeRectXY(rect(-42, -36, 42, 36), 7, 7)); c.drawPath(pt, P('#7b231a')); ink(c, pt, 2.4); c.drawPath(skia.Path().addRRect(skia.RRect.MakeRectXY(rect(-37, -31, 37, 31), 5, 5)), P('#cfa64b', .9, 'stroke', 2.2))
    c.drawPath(poly([(0, -21), (6, -5), (23, -5), (9, 6), (14, 23), (0, 13), (-14, 23), (-9, 6), (-23, -5), (-6, -5)]), P('#d9b050')); c.restore()
    c.drawPath(smooth([(-sw * .52, top + 18), (-sw * .8, 176), (-sw * .98, 240)], False), P(col, .6, 'stroke', 2.2))
    # ремень
    c.drawRect(rect(-sw * 1.06, 690, sw * 1.06, 740), P('#15181a')); c.drawRect(rect(-sw * 1.06, 690, sw * 1.06, 696), P('#4a5250', .7)); c.drawRoundRect(rect(-22, 692, 22, 738), 4, 4, P('#9a8442')); c.drawRoundRect(rect(-14, 700, 14, 730), 3, 3, P(col, .8, 'stroke', 2))

def _mara_cloth(c, sp, sw, top):
    col = LINE
    v = poly([(-30, top + 4), (30, top + 4), (0, top + 120)]); c.drawPath(v, P('#4f8f86')); c.drawPath(v, P('#2d5a54', .5, blur=3)); ink(c, v, 2.0)    # хирургическая форма
    for sx in (-1, 1):
        lap = smooth([(sx * 66, top - 6), (sx * 34, top + 6), (sx * 8, top + 138), (sx * 26, top + 246), (sx * 76, top + 150), (sx * 90, top + 40)]); c.drawPath(lap, P(sp['cloth_h'])); c.drawPath(smooth([(sx * 34, top + 6), (sx * 8, top + 138), (sx * 26, top + 246)], False), P(sp['cloth_s'], .8, 'stroke', 5)); ink(c, lap, 2.2)
    c.drawLine(0, top + 120, 0, 780, P(col, .8, 'stroke', 2.6))
    for i in range(3): c.drawCircle(-3, top + 250 + i * 92, 5.5, P('#aeb3ab')); c.drawCircle(-3, top + 250 + i * 92, 5.5, P(col, .8, 'stroke', 1.6))
    pk = poly([(60, 470), (150, 466), (152, 540), (62, 544)]); c.drawPath(pk, P(sp['cloth_s'], .55)); ink(c, pk, 2.0)
    for (x, y, r, a) in [(-92, 420, 34, .9), (-70, 460, 18, .9), (118, 350, 26, .7), (30, 560, 22, .8)]:
        c.drawPath(smooth([(x - r, y), (x - r * .3, y - r * .8), (x + r * .8, y - r * .5), (x + r, y + r * .3), (x, y + r * .9), (x - r * .7, y + r * .6)]), P('#7a2a20', a)); c.drawCircle(x + 2, y + 2, r * .4, P('#4d150e', a))
    st = smooth([(-56, top), (-70, top + 140), (-40, top + 270), (0, top + 320), (40, top + 270), (66, top + 140), (54, top)], False)
    c.drawPath(st, P('#11181a', 1, 'stroke', 7)); c.drawCircle(0, top + 322, 16, P('#9aa3a0')); c.drawCircle(0, top + 322, 16, P(col, .9, 'stroke', 2.2)); c.drawCircle(-3, top + 319, 5, P('#fff', .5))
    ban = skia.Path().addRRect(skia.RRect.MakeRectXY(rect(-sw * 1.06, 612, -sw * .72, 680), 12, 12)); c.drawPath(ban, P('#d8d2c0')); ink(c, ban, 2.2)
    c.drawLine(-sw * .98, 630, -sw * .8, 664, P('#a89e86', .6, 'stroke', 2))

def _lyosha_cloth(c, sp, sw, top):
    col = LINE
    rb = smooth([(-62, top - 6), (-68, top + 38), (-24, top + 66), (24, top + 66), (68, top + 38), (62, top - 6), (28, top - 14), (-28, top - 14)])
    c.drawPath(rb, P(sp['cloth_s'])); ink(c, rb, 2.4)
    for i in range(7): c.drawLine(-60 + i * 20, top + 4, -52 + i * 20, top + 52, P('#000', .28, 'stroke', 2.4))
    for i in range(16):
        y = 250 + i * 32; c.drawPath(smooth([(-sw * .98, y), (-sw * .3, y + 10), (sw * .3, y + 4), (sw * .98, y + 12)], False), P('#000', .13, 'stroke', 2.4))
    for i in range(10):
        x = -sw * .9 + i * sw * .2; c.drawPath(smooth([(x, 230), (x + 12, 480), (x - 6, 760)], False), P('#000', .1, 'stroke', 2.2))
    c.drawPath(smooth([(-sw * 1.04, 300), (-sw * 1.0, 700)], False), P(sp['cloth_h'], .5, 'stroke', 10, blur=4))
    hd = smooth([(-62, top + 4), (-84, top + 70), (0, top + 120), (84, top + 70), (62, top + 4)], False)
    c.drawPath(hd, P('#17191a', 1, 'stroke', 12)); c.drawPath(hd, P('#5a6460', .35, 'stroke', 2))
    for sx in (-1, 1):
        cx_ = sx * 84; cy_ = top + 84
        cp = skia.Path().addRRect(skia.RRect.MakeRectXY(rect(cx_ - 30, cy_ - 4, cx_ + 30, cy_ + 76), 20, 20)); c.drawPath(cp, P('#2c302e')); ink(c, cp, 2.4)
        c.drawPath(skia.Path().addRRect(skia.RRect.MakeRectXY(rect(cx_ - 22, cy_ + 6, cx_ + 22, cy_ + 68), 15, 15)), P('#59635e')); c.drawPath(skia.Path().addRRect(skia.RRect.MakeRectXY(rect(cx_ - 11, cy_ + 20, cx_ + 11, cy_ + 56), 8, 8)), P('#2c302e', .6))

def bust(c, who, cx, cy, s, t, o=None):
    """Бюст: тело, затем голова. (cx, cy) — центр головы."""
    o = o or {}; br = math.sin(t * 2 * math.pi * .28)
    c.save(); c.translate(cx, cy); c.scale(s * (-1 if o.get('flip') else 1), s)
    torso(c, who, t, o)
    c.save(); c.translate(o.get('hx', 0) + math.sin(t * .9) * 1.6, -br * 2.0 + o.get('hy', 0))
    head(c, who, t, o)
    c.restore()
    if o.get('overlay'): o['overlay'](c)
    c.restore()

# ---------- руки с костями, силуэты, заражённые ----------
def ik(sh, hd, l1, l2, bend=1):
    dx, dy = hd[0] - sh[0], hd[1] - sh[1]; d = max(1e-3, min(math.hypot(dx, dy), l1 + l2 - 1))
    a = math.atan2(dy, dx); cosb = clamp((l1 * l1 + d * d - l2 * l2) / (2 * l1 * d), -1, 1)
    b = math.acos(cosb) * bend
    ex, ey = sh[0] + math.cos(a + b) * l1, sh[1] + math.sin(a + b) * l1
    return (ex, ey), (sh[0] + math.cos(a) * d, sh[1] + math.sin(a) * d)

def _tube(c, x0, y0, x1, y1, r0, r1, fill, shade, lw=2.4):
    """Конечность-трубка: заливка + тень по нижнему краю + контур."""
    pth = capsule(x0, y0, x1, y1, r0, r1); c.drawPath(pth, P(fill))
    c.save(); c.clipPath(pth, doAntiAlias=True)
    d = math.atan2(y1 - y0, x1 - x0); n = d + math.pi / 2
    ax, ay = math.cos(n) * r0 * .2, math.sin(n) * r0 * .2
    c.drawPath(capsule(x0 + ax + math.cos(n) * r0 * 1.0, y0 + ay + math.sin(n) * r0 * 1.0, x1 + ax + math.cos(n) * r1 * 1.0, y1 + ay + math.sin(n) * r1 * 1.0, r0 * .95, r1 * .95), P(shade, .85))
    c.restore(); ink(c, pth, lw)

def arm(c, sh, hd, cloth, skin, l1=240, l2=230, bend=1, w=34, cuff='#222', lcol=None, shade=None):
    shade = shade or mix(cloth, '#000000', .38)
    el, hd2 = ik(sh, hd, l1, l2, bend)
    _tube(c, sh[0], sh[1], el[0], el[1], w, w * .88, cloth, shade, 2.6)
    _tube(c, el[0], el[1], hd2[0], hd2[1], w * .88, w * .72, cloth, shade, 2.6)
    c.drawCircle(el[0], el[1], w * .86, P(cloth)); c.drawPath(smooth([(el[0] - w * .7, el[1] + w * .1), (el[0], el[1] - w * .25), (el[0] + w * .7, el[1] + w * .1)], False), P(shade, .9, 'stroke', 3))
    d = math.atan2(hd2[1] - el[1], hd2[0] - el[0]); ux, uy = math.cos(d), math.sin(d)
    cf = capsule(hd2[0] - ux * w * .55, hd2[1] - uy * w * .55, hd2[0] + ux * w * .1, hd2[1] + uy * w * .1, w * .8, w * .78)
    c.drawPath(cf, P(cuff)); ink(c, cf, 2.4)
    if lcol: c.drawPath(capsule(sh[0], sh[1], el[0], el[1], w * .98, w * .84), P(lcol, .2, 'stroke', 3, blend='add'))
    return el, hd2

def hand(c, x, y, s, rot, pose='fist', skin='#d2a284', shade='#9a6a58', lcol='#7fffb0', a=1.0):
    """Рука кистью вверх (локально): ладонь, четыре пальца с суставами, большой палец; контур и тень."""
    c.save(); c.translate(x, y); c.rotate(rot); c.scale(s, s)
    def seg(x0, y0, x1, y1, w0, w1=None):
        pth = capsule(x0, y0, x1, y1, w0, w1 or w0 * .9); c.drawPath(pth, P(skin))
        c.save(); c.clipPath(pth, doAntiAlias=True); c.drawPath(capsule(x0 + w0 * .55, y0, x1 + w0 * .55, y1, w0 * .7, (w1 or w0 * .9) * .7), P(shade, .7)); c.restore(); ink(c, pth, 2.0)
    def finger(bx, by, ex, ey, w=10.5):
        mx, my = (bx + ex) / 2 + (ex - bx) * .02, (by + ey) / 2
        seg(bx, by, mx, my, w, w * .95); seg(mx, my, ex, ey, w * .95, w * .78)
        c.drawLine(mx - w * .5, my, mx + w * .5, my, P(shade, .9, 'stroke', 1.6))
    palm = smooth([(-32, -26), (-8, -30), (22, -28), (34, -14), (32, 22), (18, 42), (-14, 44), (-30, 24), (-36, -4)])
    # запястье
    c.drawPath(poly([(-18, 38), (20, 38), (22, 80), (-20, 80)]), P(skin)); ink(c, poly([(-18, 38), (-20, 80)], False), 2.0); ink(c, poly([(20, 38), (22, 80)], False), 2.0)
    if pose in ('flat',):
        for i, (bx, ex, ey) in enumerate([(-24, -36, -92), (-8, -12, -104), (8, 10, -100), (24, 34, -86)]): finger(bx, -26, ex, ey, 10.2)
        seg(-30, 8, -62, -34, 11, 9)
    elif pose == 'point':
        for i, bx in enumerate((-4, 10, 24)): c.drawPath(smooth([(bx - 9, -26), (bx + 1, -48), (bx + 10, -26)]), P(shade, .0)); seg(bx, -22, bx + 1, -44, 10, 9)
        finger(-22, -26, -22, -108, 10.5)
        seg(-30, 6, 4, -24, 11, 9)
    elif pose == 'shush':
        finger(-14, -26, -14, -112, 10.5)
        for bx in (4, 18, 30): seg(bx, -22, bx, -42, 10, 9)
        seg(-30, 6, 6, -22, 11, 9)
    else:  # fist
        c.drawPath(palm, P(skin)); ink(c, palm, 2.2)
        for i, bx in enumerate((-24, -8, 8, 24)): seg(bx, -22, bx + 1, -52, 11, 10)
        for i, bx in enumerate((-24, -8, 8, 24)): c.drawLine(bx - 6, -36, bx + 6, -36, P(shade, .9, 'stroke', 1.6))
        seg(-32, 14, 6, -20, 11.5, 10)
    if pose != 'fist': c.drawPath(palm, P(skin)); ink(c, palm, 2.2) if False else None
    if pose != 'fist':
        c.drawPath(palm, P(skin)); c.save(); c.clipPath(palm, doAntiAlias=True); c.drawPath(poly([(10, -40), (50, -40), (50, 60), (10, 60)]), P(shade, .6)); c.restore(); ink(c, palm, 2.2)
    else:
        c.save(); c.clipPath(palm, doAntiAlias=True); c.drawPath(poly([(10, -40), (50, -40), (50, 60), (10, 60)]), P(shade, .55)); c.restore()
    c.restore()

def silhouette(c, x, y, s, t, seed=0, color='#050a0a', rim=None, back=True, sway=1.0):
    """Силуэт человека (голова+плечи+торс) для толпы."""
    ph = t * 1.3 + seed * 2.1; k = 1 + (hash1(seed * 3.3) - .5) * .25
    c.save(); c.translate(x + math.sin(ph) * 4 * sway, y + math.sin(ph * 1.7) * 3 * sway); c.scale(s * k, s * k)
    body = smooth([(-120, 420), (-124, 140), (-96, 70), (-40, 40), (40, 40), (96, 70), (124, 140), (120, 420)])
    c.drawPath(body, P(color)); c.drawPath(oval_path(0, -16, 46, 56), P(color)); c.drawRect(rect(-20, 20, 20, 60), P(color))
    if rim:
        c.drawPath(smooth([(-124, 140), (-96, 70), (-40, 40)], False), P(rim, .3, 'stroke', 3, blend='add'))
    c.restore()

def infected(c, x, y, s, t, pose='stand', seed=0, color='#0a100e', rim='#6bff9e', light=0.5, flip=False):
    """Заражённый: гибкий искривлённый силуэт, пустые глазницы, суставы выгнуты неестественно."""
    c.save(); c.translate(x, y); c.scale(s * (-1 if flip else 1), s)
    tw = math.sin(t * 9 + seed) * 4 + (noise1(t * 6, seed) - .5) * 16
    if pose == 'crouch':
        hip = (0, -70); sh = (60, -190 + tw * .5); head = (150, -190 + tw)
        knee = [(-70, -30), (-10, -20)]; foot = [(-130, 0), (50, 0)]
        elb = [(110, -60), (200, -90)]; hnd = [(130, 0), (240, -10)]
    elif pose == 'lunge':
        hip = (0, -330); sh = (70 + tw, -520); head = (140 + tw, -560)
        knee = [(-120, -170), (120, -190)]; foot = [(-190, 0), (210, -20)]
        elb = [(170, -420), (-30, -380)]; hnd = [(330, -450), (90, -300)]
    else:  # stand, скрюченный
        hip = (0, -330); sh = (-24 + tw * .6, -560); head = (-70 + tw, -640 + abs(tw) * .4)
        knee = [(-60, -170), (60, -170)]; foot = [(-90, 0), (70, 0)]
        elb = [(-100 + tw, -420), (90, -430)]; hnd = [(-30 + tw * 2, -250), (110, -230 + tw)]
    def lim(a, b, w0, w1): c.drawPath(capsule(a[0], a[1], b[0], b[1], w0, w1), P(color))
    for i in (0, 1):
        lim(hip, knee[i], 40, 32); lim(knee[i], foot[i], 32, 20)
        lim(sh, elb[i], 32, 24); lim(elb[i], hnd[i], 24, 15)
        # длинные пальцы
        for k in range(3): c.drawLine(hnd[i][0], hnd[i][1], hnd[i][0] + 26 + k * 5, hnd[i][1] + 18 + k * 14, P(color, 1, 'stroke', 5))
    c.drawPath(capsule(hip[0], hip[1], sh[0], sh[1], 62, 70), P(color))
    c.drawPath(capsule(sh[0], sh[1], head[0], head[1], 34, 26), P(color))
    c.drawPath(oval_path(head[0], head[1], 38, 48), P(color))
    # глазницы и рот (едва видны)
    for sx in (-14, 14):
        c.drawPath(oval_path(head[0] + sx, head[1] - 4, 8, 11), P('#000'))
    c.drawPath(oval_path(head[0], head[1] + 26, 8, 14 + abs(math.sin(t * 5 + seed)) * 6), P('#000'))
    if light:
        c.drawPath(capsule(hip[0] - 40, hip[1], sh[0] - 40, sh[1], 3, 4), P(rim, .3 * light, blend='add'))
        c.drawPath(oval_path(head[0], head[1], 38, 48), P(rim, .28 * light, 'stroke', 3, blend='add'))
    c.restore()

def keys(c, x, y, s, t, ph=0):
    c.save(); c.translate(x, y); c.rotate(math.sin(t * 2.2 + ph) * 3); c.scale(s, s)
    c.drawCircle(0, 0, 26, P('#8d8f86', 1, 'stroke', 7))
    for i in range(5):
        a = math.radians(70 + i * 26); L = 66 + (i % 2) * 18
        px, py = math.cos(a) * 24, math.sin(a) * 24
        c.drawLine(px, py, px + math.cos(a) * L, py + math.sin(a) * L, P('#2a2d29', 1, 'stroke', 14))
        c.drawLine(px, py, px + math.cos(a) * L, py + math.sin(a) * L, P('#9a9a8c' if i % 2 else '#a8864a', 1, 'stroke', 9))
        c.drawRect(rect(px + math.cos(a) * L - 5, py + math.sin(a) * L, px + math.cos(a) * L + 9, py + math.sin(a) * L + 14), P('#6a6a60'))
    c.restore()
