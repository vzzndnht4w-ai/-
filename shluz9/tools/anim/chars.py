"""Персонажи: голова + плечи (бюст) с анимацией дыхания, моргания, поворота; руки; силуэты."""
from .core import *

SPECS = {
 'artyom': dict(skin='#c79b7d', shade='#7d5545', hair='#17120f', cloth='#566059', cloth_d='#2c332f', jaw=.74, cheek=.8, brow=1.0, stub=.5, stub_c='#1c1512',
                eye='#4a3a2e', eyew=.9, age=.7, nose=1.0, ear=1.0, hairstyle='short'),
 'gromov': dict(skin='#b78e72', shade='#6f4a3b', hair='#6a6a68', cloth='#262b2c', cloth_d='#101414', jaw=.92, cheek=.9, brow=1.3, stub=.55, stub_c='#8a8d8c',
                eye='#2a2a2a', eyew=.8, age=1.0, nose=1.15, ear=1.0, hairstyle='buzz', scar=True),
 'mara': dict(skin='#e0bfa6', shade='#98715f', hair='#cdb06a', cloth='#d9dcd6', cloth_d='#8b918c', jaw=.68, cheek=.74, brow=.6, stub=0, stub_c='#000',
              eye='#5d7c8a', eyew=1.05, age=.2, nose=.85, ear=.9, hairstyle='ponytail'),
 'lyosha': dict(skin='#d9b296', shade='#8c6652', hair='#2a1d17', cloth='#6b7f6d', cloth_d='#3a4a3d', jaw=.72, cheek=.82, brow=.6, stub=0, stub_c='#000',
                eye='#2d241d', eyew=1.12, age=0, nose=.7, ear=1.0, hairstyle='messy', child=True),
}

def face_path(sp, R=100):
    j = sp['jaw']; ch = sp['cheek']
    pts = [(0, -1.12), (.58, -.98), (.9 * ch + .1, -.52), (.95 * ch, .02), (.82 * ch, .46), (.55 * j + .08, .8), (.24 * j, .98), (0, 1.02),
           (-.24 * j, .98), (-.55 * j - .08, .8), (-.82 * ch, .46), (-.95 * ch, .02), (-(.9 * ch + .1), -.52), (-.58, -.98)]
    return smooth([(x * R * .86, y * R) for x, y in pts])

def eyelid_open(t, seed=0, period=3.6, closed=0.0):
    ph = (t + seed * 1.7) % period
    b = 0.0
    if ph < .16: b = math.sin(ph / .16 * math.pi)
    return clamp(1 - max(b, closed))

def head(c, who, t, o=None):
    """Рисует голову в локальных координатах (радиус ~100), центр (0,0)."""
    o = o or {}; sp = dict(SPECS[who]); R = 100
    if o.get('pale'): sp['skin'] = mix(sp['skin'], '#cfd6cc', o['pale']); sp['shade'] = mix(sp['shade'], '#5a6660', o['pale'])
    turn = o.get('turn', 0.0); look = o.get('look', (0, 0)); eo = o.get('eyes', eyelid_open(t, hash1(len(who)), closed=o.get('squint', 0)))
    mouth = o.get('mouth', 0.0); tilt = o.get('tilt', 0.0); fear = o.get('fear', 0.0); tired = o.get('tired', 0.0)
    lightx = o.get('lightx', -0.6); lcol = o.get('lcol', '#7fffb0'); under = o.get('under', 0.0)
    child = sp.get('child')
    c.save(); c.rotate(tilt)
    fp = face_path(sp)
    # волосы сзади
    if sp['hairstyle'] == 'ponytail':
        c.drawPath(smooth([(-96, -40), (-80, -118), (0, -140), (90, -118), (104, -40), (96, 70), (60, 20), (-60, 20), (-96, 70)]), P(sp['hair']))
    if sp['hairstyle'] == 'messy':
        c.drawPath(smooth([(-98, -30), (-90, -118), (0, -142), (92, -118), (100, -30), (80, 10), (-80, 10)]), P(sp['hair']))
    # шея
    nk = poly([(-.4 * R, .6 * R), (.4 * R, .6 * R), (.5 * R, 1.4 * R), (-.5 * R, 1.4 * R)])
    c.drawPath(nk, P(sp['skin'])); c.drawPath(nk, P(sp['shade'], .9, shader=lin(0, .7 * R, 0, 1.2 * R, [(sp['shade'], .95, 0), (sp['shade'], 0, 1)])))
    # уши
    for sx in (-1, 1):
        ex = sx * (.86 * sp['cheek'] * R * .98 + 4 + turn * -6 * sx * 0)
        c.drawPath(oval_path(ex, .0 + 6, 14 * sp['ear'], 26 * sp['ear']), P(sp['skin']))
        c.drawPath(oval_path(ex + sx * 2, 6, 7, 15), P(sp['shade'], .85))
    # лицо
    c.drawPath(fp, P(sp['skin']))
    c.save(); c.clipPath(fp, doAntiAlias=True)
    # объём: тень со стороны, противоположной свету
    sx = -1 if lightx > 0 else 1
    c.drawRect(rect(-140, -140, 140, 150), P('#000', 1, shader=lin(-lightx * 90, 0, lightx * 90, 0, [(sp['shade'], 0.0, 0), (sp['shade'], .15, .5), (sp['shade'], .88, 1)])))
    if under:
        c.drawRect(rect(-140, -140, 140, 150), P('#000', 1, shader=lin(0, 110, 0, -110, [(lcol, .5 * under, 0), (lcol, 0, .6), ('#000000', .5 * under, 1)])))
    # тень под бровями / в глазницах
    for ex in (-1, 1):
        c.drawPath(oval_path(ex * (37 + turn * 7), -14, 28, 17), P(sp['shade'], .5 + .3 * tired, blur=6))
    # тень под подбородком/шея
    c.drawRect(rect(-120, 80, 120, 130), P(sp['shade'], .6, blur=9))
    # румянец/усталость
    if sp.get('age', 0) > 0.3:
        for ex in (-1, 1):
            c.drawPath(oval_path(ex * (36 + turn * 7), 14, 24, 9), P('#4a3340', .38 + .25 * tired, blur=5))
    # щетина
    if sp['stub'] > 0:
        stub = poly([(-90, 12), (-60, 6), (-30, 30), (0, 28), (30, 30), (60, 6), (90, 12), (110, 130), (-110, 130)])
        c.drawPath(stub, P(sp['stub_c'], sp['stub'] * .75, blur=3))
        # зерно щетины
        for i in range(260):
            x = (hash1(i * 3.7) - .5) * 190; y = 10 + hash1(i * 6.1) * 105
            if y > 38 and abs(x) < 80 - (y - 20) * .35 and hash1(i * 1.7) > .45:
                c.drawCircle(x, y, 1.2, P(sp['stub_c'], .5))
    c.restore()
    # лицевые детали (сдвигаются при повороте)
    ox = turn * 9
    # нос
    nose = smooth([(ox * 1.4 - 4, -26), (ox * 1.6 - 9 * sp['nose'], 20), (ox * 1.6 + 0, 30 * sp['nose'] + 4), (ox * 1.6 + 9 * sp['nose'], 20), (ox * 1.4 + 4, -26)])
    c.drawPath(nose, P(sp['shade'], .35, blur=3))
    c.drawPath(poly([(ox * 1.5 + 2, -22), (ox * 1.7 + 12 * sp['nose'], 26 * sp['nose']), (ox * 1.5 + 2, 28 * sp['nose'])]), P(sp['shade'], .55))
    c.drawPath(smooth([(ox * 1.5 - 12 * sp['nose'], 31 * sp['nose']), (ox * 1.5, 36 * sp['nose']), (ox * 1.5 + 12 * sp['nose'], 31 * sp['nose'])], False), P('#2a1710', .7, 'stroke', 3))
    # глаза
    for ex in (-1, 1):
        cx_ = ex * 37 + ox + (0 if ex == 1 else 0); cy_ = -12
        w = 20 * sp['eyew'] * (1 + fear * .15); h_ = (9 + 5 * fear) * eo * sp['eyew'] * (1.1 if child else 1)
        if child: h_ *= 1.1
        eye = smooth([(cx_ - w, cy_ + 1), (cx_ - w * .4, cy_ - h_), (cx_ + w * .5, cy_ - h_ * 1.0), (cx_ + w, cy_ + 1), (cx_ + w * .45, cy_ + h_ * .85), (cx_ - w * .45, cy_ + h_ * .9)])
        c.drawPath(eye, P('#e8e2d4'))
        c.save(); c.clipPath(eye, doAntiAlias=True)
        px = cx_ + look[0] * 6 + ox * .3; py = cy_ + look[1] * 4
        ir = 8.5 * (1.15 if child else 1)
        c.drawCircle(px, py, ir, P(sp['eye'])); c.drawCircle(px, py, ir * .5, P('#050505'))
        c.drawCircle(px - 3, py - 3, 2.2, P('#ffffff', .9))
        c.drawRect(rect(cx_ - w, cy_ - h_ - 2, cx_ + w, cy_ - h_ * .2), P('#000', .25, blur=3))
        c.restore()
        c.drawPath(eye, P('#120a08', .95, 'stroke', 2.6))
        # верхнее веко (тяжёлое)
        c.drawPath(smooth([(cx_ - w * 1.05, cy_ - 1), (cx_, cy_ - h_ * 1.25 - 3), (cx_ + w * 1.05, cy_ - 1)], False), P('#120a08', .9, 'stroke', 3.2))
        # мешки под глазами
        if sp.get('age', 0) > 0.3:
            c.drawPath(smooth([(cx_ - w * .9, cy_ + h_ + 6), (cx_, cy_ + h_ + 12), (cx_ + w * .9, cy_ + h_ + 5)], False), P('#2b1d26', .5, 'stroke', 5, blur=2))
        # брови
        bt = sp['brow'] * (9 if not child else 5)
        inner_up = (fear * 9 + (o.get('worry', 0)) * 8)
        ang_in = -(ex) * 0
        bx0 = cx_ - ex * 26 - 0; bx1 = cx_ + ex * 22
        inner = (cx_ - ex * 24, cy_ - 24 - inner_up - (o.get('frown', 0)) * -7)
        outer = (cx_ + ex * 26, cy_ - 26 - fear * 4 + o.get('frown', 0) * 0)
        mid = ((inner[0] + outer[0]) / 2, min(inner[1], outer[1]) - 4 + tired * 2)
        bp = smooth([inner, mid, outer], False)
        c.drawPath(bp, P(sp['hair'] if sp['hairstyle'] != 'ponytail' else '#9b8044', 1, 'stroke', bt))
        if sp.get('scar') and ex == 1:
            c.drawPath(smooth([(cx_ - 8, cy_ - 44), (cx_ + 8, cy_ - 24), (cx_ + 22, cy_ - 4)], False), P('#c98b86', .85, 'stroke', 3.2))
            for k in range(4):
                tx = cx_ - 3 + k * 7; ty = cy_ - 38 + k * 9
                c.drawLine(tx - 4, ty + 2, tx + 4, ty - 2, P('#c98b86', .7, 'stroke', 1.6))
    # рот
    my = 62 + (4 if child else 0)
    mw = 21 * (1.0 if not child else .8)
    mo = mouth * 14
    if mo > 1.5:
        c.drawPath(smooth([(ox - mw, my), (ox, my - 3), (ox + mw, my), (ox, my + 3 + mo)]), P('#1c0a0a', 1))
        c.drawRect(rect(ox - mw * .7, my - 2, ox + mw * .7, my + 3), P('#d8d0c0', .8))
    else:
        c.drawPath(smooth([(ox - mw, my + (1 if sp.get('age', 0) > .3 else 0)), (ox, my - 1 + o.get('smile', 0) * -3), (ox + mw, my + 1)], False), P('#2a100c', .9, 'stroke', 3.4))
        c.drawPath(smooth([(ox - mw * .6, my + 7), (ox, my + 9), (ox + mw * .6, my + 7)], False), P(sp['shade'], .55, 'stroke', 3, blur=1.5))
    # носогубные
    if sp.get('age', 0) > .5:
        for ex in (-1, 1):
            c.drawPath(smooth([(ex * 24 + ox, 20), (ex * 30 + ox, 46), (ex * 26 + ox, 62)], False), P(sp['shade'], .55, 'stroke', 2.2))
    # волосы
    hc = sp['hair']; hs = sp['hairstyle']
    if hs in ('short', 'buzz'):
        h_h = 1.0 if hs == 'short' else .6
        hp = smooth([(-92, -22), (-96, -84), (-52, -122), (0, -128), (54, -122), (96, -84), (92, -22), (76, -56), (40, -82 * h_h - 8), (-6, -88 * h_h - 6), (-44, -78 * h_h - 8), (-78, -52)])
        c.drawPath(hp, P(hc))
        c.save(); c.clipPath(hp, doAntiAlias=True)
        c.drawRect(rect(-120, -150, 120, 0), P('#000', 1, shader=lin(-lightx * 80, 0, lightx * 80, 0, [('#000000', 0, 0), ('#000000', .65, 1)])))
        for i in range(40):
            x = -90 + hash1(i * 4.1) * 180; y = -125 + hash1(i * 2.3) * 60
            c.drawLine(x, y, x + (hash1(i * 7) - .5) * 18, y + 14 + hash1(i) * 10, P('#ffffff', .07 if hs == 'short' else .12, 'stroke', 1.4))
        c.restore()
    elif hs == 'ponytail':
        hp = smooth([(-94, -10), (-92, -90), (-46, -126), (6, -130), (60, -118), (96, -84), (94, -8), (82, -50), (40, -86), (-6, -96), (-60, -78), (-80, -46)])
        c.drawPath(hp, P(hc)); c.drawPath(hp, P('#ffffff', .1, shader=lin(-60, -130, 60, -60, [('#ffffff', .25, 0), ('#ffffff', 0, 1)])))
        c.drawPath(smooth([(-70, -88), (-20, -110), (30, -100), (74, -70)], False), P('#8a7236', .4, 'stroke', 5))
    elif hs == 'messy':
        pts = [(-98, -10), (-100, -70), (-80, -110), (-40, -128), (-10, -112), (22, -134), (56, -116), (84, -104), (102, -64), (96, -8), (84, -50), (52, -76), (24, -62), (-6, -80), (-36, -62), (-70, -56)]
        c.drawPath(smooth(pts), P(hc))
        for i in range(14):
            x = -90 + i * 13; c.drawLine(x, -112, x + (hash1(i) - .5) * 40, -66 + hash1(i * 3) * 30, P('#ffffff', .06, 'stroke', 2))
    # свет-обводка по кромке
    c.save(); c.clipPath(fp, doAntiAlias=True)
    sg = 1 if lightx > 0 else -1
    c.drawRect(rect(-140, -140, 140, 150), P(lcol, 1, shader=lin(sg * 98, 0, sg * 70, 0, [(lcol, .38, 0), (lcol, 0, 1)]), blend='add'))
    c.restore()
    c.restore()

def torso(c, who, t, o=None, scale_w=1.0):
    """Плечи/одежда в локальных координатах: шея начинается около y=100."""
    o = o or {}; sp = SPECS[who]; br = math.sin(t * 2 * math.pi * .28) * (o.get('breath', 1.0))
    lcol = o.get('lcol', '#7fffb0'); lightx = o.get('lightx', -.6)
    sw = 215 * scale_w * (0.74 if sp.get('child') else 1.0) ; top = 128 - br * 2
    body = smooth([(-sw * .98, 760), (-sw * 1.02, 280), (-sw * .88, 190), (-sw * .5, top + 6), (-62, top - 6), (0, top - 12), (62, top - 6), (sw * .5, top + 6), (sw * .88, 190), (sw * 1.02, 280), (sw * .98, 760)])
    body = skia.Path(body)
    c.drawPath(body, P(sp['cloth']))
    c.save(); c.clipPath(body, doAntiAlias=True)
    tp_ = P('#ffffff', 1, blend='mul', shader=tex_shader('metal', .8, 0, 0)); tp_.setAlphaf(.75); c.drawRect(rect(-sw * 1.2, 0, sw * 1.2, 800), tp_)
    c.drawRect(rect(-sw * 1.2, 0, sw * 1.2, 800), P('#000', 1, shader=lin(-lightx * sw, 0, lightx * sw, 0, [('#000000', 0, 0), ('#000000', .1, .5), ('#000000', .6, 1)])))
    # складки
    for i in range(6):
        x0 = -sw * .7 + i * sw * .28
        c.drawPath(smooth([(x0, 240), (x0 + 12 + 8 * (i % 2), 400), (x0 - 10, 560)], False), P('#000', .22, 'stroke', 5, blur=2))
    # воротник/молния
    if who == 'artyom':
        c.drawPath(poly([(-62, top - 6), (0, top + 70), (62, top - 6), (30, top - 14), (0, top + 20), (-30, top - 14)]), P(sp['cloth_d'], .9))
        c.drawLine(0, top + 66, 0, 700, P('#161a18', .9, 'stroke', 4))
        for k in range(10): c.drawLine(-4, top + 80 + k * 22, 4, top + 80 + k * 22, P('#8b8a80', .6, 'stroke', 2))
        # нашивка
        px, py = -sw * .62, 250
        c.save(); c.translate(px, py); c.rotate(-4)
        c.drawRoundRect(rect(-52, -22, 52, 22), 4, 4, P('#b8661f')); c.drawRoundRect(rect(-48, -18, 48, 18), 3, 3, P('#2a2018', .9, 'stroke', 2))
        f = skia.Font(skia.Typeface('DejaVu Sans', skia.FontStyle.Bold()), 9)
        c.drawSimpleText('VENT', -16, -4, f, P('#1d1510')); c.drawSimpleText('MAINTENANCE', -39, 12, skia.Font(skia.Typeface('DejaVu Sans', skia.FontStyle.Bold()), 7.2), P('#1d1510'))
        c.restore()
        # налобный фонарь на шее
        c.drawPath(smooth([(-64, top - 2), (-70, top + 70), (0, top + 126), (70, top + 70), (64, top - 2)], False), P('#0e1110', 1, 'stroke', 13))
        c.drawPath(smooth([(-64, top - 2), (-70, top + 70), (0, top + 126), (70, top + 70), (64, top - 2)], False), P('#505a54', .35, 'stroke', 2))
        lx, ly = 48, top + 106 + br * 2
        c.drawRoundRect(rect(lx - 26, ly - 20, lx + 26, ly + 20), 9, 9, P('#232826')); c.drawRoundRect(rect(lx - 26, ly - 20, lx + 26, ly + 20), 9, 9, P('#111', 1, 'stroke', 2))
        c.drawCircle(lx, ly, 13, P('#0b0e0d')); c.drawCircle(lx, ly, 9, P('#6a7a70', .8)); c.drawCircle(lx - 3, ly - 3, 3, P('#fff', .5))
    elif who == 'gromov':
        c.drawPath(poly([(-70, top - 8), (-24, top + 64), (-4, top + 20)]), P('#0b0e0f')); c.drawPath(poly([(70, top - 8), (24, top + 64), (4, top + 20)]), P('#0b0e0f'))
        c.drawPath(poly([(-24, top + 64), (-4, top + 20), (0, top + 140), (-14, 700)]), P('#1a1f20')); c.drawLine(0, top + 20, 0, 720, P('#07090a', .9, 'stroke', 4))
        for k in range(5): c.drawCircle(18, top + 150 + k * 90, 7, P('#7a6a3c')), c.drawCircle(17, top + 148 + k * 90, 3, P('#e6d390', .7))
        # погон и нашивка коменданта
        c.drawPath(poly([(sw * .5, top + 6), (sw * .88, 190), (sw * .74, 232), (sw * .38, top + 48)]), P('#0d1011'))
        c.drawRect(rect(sw * .5, top + 38, sw * .66, top + 52), P('#9c7a2a')); c.drawRect(rect(sw * .5, top + 60, sw * .62, top + 70), P('#9c7a2a'))
        c.save(); c.translate(-sw * .6, 260); c.rotate(-3)
        c.drawRoundRect(rect(-40, -34, 40, 34), 6, 6, P('#7e2418')); c.drawRoundRect(rect(-36, -30, 36, 30), 4, 4, P('#caa24b', .9, 'stroke', 2.4))
        c.drawPath(poly([(0, -20), (6, -4), (22, -4), (9, 6), (14, 22), (0, 12), (-14, 22), (-9, 6), (-22, -4), (-6, -4)]), P('#caa24b'))
        c.restore()
    elif who == 'mara':
        c.drawPath(poly([(-70, top - 8), (-22, top + 100), (0, top + 10)]), P('#c9ccc6')); c.drawPath(poly([(70, top - 8), (22, top + 100), (0, top + 10)]), P('#c9ccc6'))
        c.drawPath(poly([(-22, top + 100), (0, top + 10), (22, top + 100), (0, 740)]), P('#445049'))
        c.drawLine(0, top + 60, 0, 720, P('#9ea39d', .8, 'stroke', 3))
        # пятна на халате
        for (x, y, r, a) in [(-90, 400, 40, .5), (-70, 440, 22, .5), (120, 330, 30, .35), (60, 520, 26, .4)]:
            c.drawCircle(x, y, r, P('#6e2a1d', a, blur=6)); c.drawCircle(x + 3, y + 3, r * .5, P('#4a1810', a * .8, blur=3))
        # стетоскоп
        c.drawPath(smooth([(-55, top), (-60, top + 130), (-20, top + 250), (20, top + 150), (55, top)], False), P('#151819', 1, 'stroke', 7))
    elif who == 'lyosha':
        # крупный вязаный свитер
        c.drawPath(smooth([(-70, top - 4), (-62, top + 46), (0, top + 70), (62, top + 46), (70, top - 4)], False), P('#46564a', 1, 'stroke', 34))
        for k in range(18):
            c.drawLine(-sw + k * sw / 8.5, 220, -sw + k * sw / 8.5 + 10, 760, P('#000', .17, 'stroke', 3))
        for k in range(24):
            y = 220 + k * 24; c.drawPath(smooth([(-sw * 1.0, y), (0, y + 8), (sw * 1.0, y)], False), P('#000', .12, 'stroke', 2))
        # наушники на шее
        c.drawPath(smooth([(-92, 60), (-110, 150), (0, 210), (110, 150), (92, 60)], False), P('#1a1b1a', 1, 'stroke', 14))
        for sx in (-1, 1):
            c.drawRoundRect(rect(sx * 112 - 24, 70, sx * 112 + 24, 150), 20, 20, P('#2a2c2b')); c.drawRoundRect(rect(sx * 112 - 18, 78, sx * 112 + 18, 142), 14, 14, P('#505a55'))
    c.restore()
    # тень от головы на одежду
    # rim
    c.save(); c.clipPath(body, doAntiAlias=True)
    sg = 1 if lightx > 0 else -1
    c.drawRect(rect(-sw * 1.2, 0, sw * 1.2, 800), P(lcol, 1, shader=lin(sg * sw * 1.0, 0, sg * sw * .8, 0, [(lcol, .35, 0), (lcol, 0, 1)]), blend='add'))
    c.restore()

def bust(c, who, cx, cy, s, t, o=None):
    """Полный бюст: тело, затем голова. (cx,cy) — центр головы."""
    o = o or {}; br = math.sin(t * 2 * math.pi * .28)
    c.save(); c.translate(cx, cy); c.scale(s * (-1 if o.get('flip') else 1), s)
    torso(c, who, t, o)
    c.save(); c.translate(o.get('hx', 0) + math.sin(t * .9) * 2, -br * 2.5 + o.get('hy', 0))
    head(c, who, t, o)
    if who == 'lyosha' or who == 'artyom':
        pass
    c.restore()
    if o.get('overlay'): o['overlay'](c)
    c.restore()

def hand(c, x, y, s, rot, pose='fist', skin='#c79b7d', shade='#7d5545', lcol='#7fffb0', a=1.0):
    c.save(); c.translate(x, y); c.rotate(rot); c.scale(s, s)
    sk, sh = skin, shade
    def finger(x0, y0, x1, y1, w):
        c.drawPath(capsule(x0, y0, x1, y1, w, w * .88), P(sk))
        c.drawPath(capsule(x0 + w * .3, y0, x1 + w * .3, y1, w * .45, w * .4), P(sh, .55))
    c.drawPath(skia.Path().addRRect(skia.RRect.MakeRectXY(rect(-34, -26, 34, 40), 20, 20)), P(sk))
    if pose == 'fist':
        for i in range(4): finger(-26 + i * 17, -22, -26 + i * 17 + 2, -52, 11)
        c.drawPath(oval_path(-38, 6, 12, 24), P(sk))
        c.drawPath(capsule(-30, 10, 8, -30, 11, 10), P(sk))
        for i in range(4): c.drawLine(-26 + i * 17, -38, -26 + i * 17, -22, P(sh, .6, 'stroke', 2))
    elif pose == 'point':
        for i in range(1, 4): finger(-26 + i * 17, -22, -26 + i * 17 + 2, -46, 11)
        finger(-24, -24, -22, -100, 11)
        c.drawPath(capsule(-30, 10, 6, -30, 11, 10), P(sk))
    elif pose == 'flat':
        for i in range(4): finger(-26 + i * 17, -22, -26 + i * 17 + (i - 1.5) * 2, -86 + abs(i - 1.5) * 8, 10)
        c.drawPath(capsule(-30, 10, -62, -40, 11, 9), P(sk))
    elif pose == 'shush':
        finger(-14, -24, -14, -108, 11)
        for i in (0, 2, 3): finger(-26 + i * 17 + 6, -22, -26 + i * 17 + 6, -46 + i * 2, 11)
        c.drawPath(capsule(-30, 10, 10, -30, 11, 10), P(sk))
    c.drawPath(skia.Path().addRRect(skia.RRect.MakeRectXY(rect(-34, -26, 34, 40), 20, 20)), P('#000', 1, shader=lin(-34, 0, 34, 0, [('#000', 0, 0), ('#000', .5, 1)])))
    c.restore()

# ---------- руки с костями, силуэты, заражённые ----------
def ik(sh, hd, l1, l2, bend=1):
    dx, dy = hd[0] - sh[0], hd[1] - sh[1]; d = max(1e-3, min(math.hypot(dx, dy), l1 + l2 - 1))
    a = math.atan2(dy, dx); cosb = clamp((l1 * l1 + d * d - l2 * l2) / (2 * l1 * d), -1, 1)
    b = math.acos(cosb) * bend
    ex, ey = sh[0] + math.cos(a + b) * l1, sh[1] + math.sin(a + b) * l1
    return (ex, ey), (sh[0] + math.cos(a) * d, sh[1] + math.sin(a) * d)

def arm(c, sh, hd, cloth, skin, l1=240, l2=230, bend=1, w=34, cuff='#222', lcol=None):
    el, hd2 = ik(sh, hd, l1, l2, bend)
    c.drawPath(capsule(sh[0], sh[1], el[0], el[1], w, w * .88), P(cloth))
    c.drawPath(capsule(el[0], el[1], hd2[0], hd2[1], w * .88, w * .7), P(cloth))
    c.drawPath(capsule(el[0], el[1], hd2[0], hd2[1], w * .6, w * .5), P('#000', .2))
    c.drawPath(capsule(hd2[0] - (hd2[0] - el[0]) * .1, hd2[1] - (hd2[1] - el[1]) * .1, hd2[0], hd2[1], w * .72, w * .72), P(cuff))
    if lcol: c.drawPath(capsule(sh[0], sh[1], el[0], el[1], w * .98, w * .84), P(lcol, .22, 'stroke', 3, blend='add'))
    return el, hd2

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
