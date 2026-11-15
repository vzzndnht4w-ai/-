"""Сцены серии 0 «Последний поворот»: 34 кадра. scene(c, t, T) — кадр в момент t клипа длиной T."""
from .core import *
from . import bg, bg2, chars
from .chars import bust, hand, arm, silhouette, infected, keys, SPECS
from .bg import GREEN, ORANGE

def blurred(c, fn, sigma=10):
    c.saveLayer(None, skia.Paint(ImageFilter=skia.ImageFilters.Blur(sigma, sigma))); fn(); c.restore()
def vign(c, a=.8, r=1200, cy=960):
    c.drawRect(rect(0, 0, W, H), P('#000', 1, shader=rad(W / 2, cy, r, [('#000', 0, 0), ('#000', .15, .45), ('#000', a, 1)])))
def wallbg(c, t, lamp=GREEN, lx=900, ly=300, base='#1b2a26'):
    c.drawPaint(P('#050a09')); p = poly([(0, 0), (W, 0), (W, H), (0, H)])
    texture_fill(c, p, base, 'concrete', 1.3, .9)
    for i in range(12):
        x = hash1(i * 3.3) * W; c.drawRect(rect(x, 0, x + 8 + hash1(i) * 14, 300 + hash1(i * 2) * 1400), P('#000', .22, blur=4))
    for x in (180, 700): c.drawRect(rect(x, 0, x + 10, H), P('#000', .55))
    glow(c, lx, ly, 1000, lamp, .5); vign(c, .85)
def flicker(t, k=.3, f=18, seed=0): return 1 - k * (1 - noise1(t * f, seed))
def pulse(t, f=7.5): return (math.sin(t * f) + 1) / 2

def recorder(c, x, y, s, t, rot=0):
    c.save(); c.translate(x, y); c.rotate(rot); c.scale(s, s)
    c.drawRoundRect(rect(-70, -100, 70, 100), 12, 12, P('#1c1f1d')); c.drawRoundRect(rect(-70, -100, 70, 100), 12, 12, P('#000', 1, 'stroke', 3))
    c.drawRoundRect(rect(-56, -84, 56, -10), 6, 6, P('#3a3f3a'))
    for sx in (-1, 1):
        c.drawCircle(sx * 26, -47, 20, P('#0d0f0e')); c.drawCircle(sx * 26, -47, 8, P('#a0a29a'))
        for k in range(3):
            a = t * 2.2 * (1 if sx > 0 else -1) + k * 2.09
            c.drawLine(sx * 26, -47, sx * 26 + math.cos(a) * 17, -47 + math.sin(a) * 17, P('#a0a29a', .9, 'stroke', 2.4))
    c.drawRoundRect(rect(-52, 6, 52, 40), 5, 5, P('#2b302c'))
    for i in range(-2, 3): c.drawLine(i * 16, 12, i * 16, 34, P('#000', .6, 'stroke', 2))
    for i in range(4): c.drawRoundRect(rect(-50 + i * 26, 56, -30 + i * 26, 84), 4, 4, P('#5c615a' if i != 0 else '#7a2b22'))
    on = (math.sin(t * 3.3) > -0.2)
    c.drawCircle(46, -92, 5, P('#ff3a2a', 1 if on else .25))
    if on: glow(c, 46, -92, 40, '#ff3a2a', .6)
    c.restore()

def side_shade(c, side=-1, a=.85, w=.9):
    c.drawRect(rect(0, 0, W, H), P('#000', 1, shader=lin(W * (.5 + .05 * side), 0, W * (.5 - side * w * .5), 0, [('#000000', 0, 0), ('#000000', a, 1)])))

def clipboard(c, x, y, rot=-10, s=1.0):
    c.save(); c.translate(x, y); c.rotate(rot); c.scale(s, s)
    c.drawRoundRect(rect(-150, -190, 150, 190), 10, 10, P('#2d3330')); c.drawRoundRect(rect(-132, -170, 132, 170), 4, 4, P('#cfc9b3'))
    for i in range(9): c.drawLine(-110, -130 + i * 30, 70 + (i % 3) * 20, -130 + i * 30, P('#2a2a28', .6, 'stroke', 3))
    c.drawRoundRect(rect(-40, -200, 40, -172), 6, 6, P('#8a8d86')); c.restore()

def runner(c, x, y, s, t, seed, color='#050908', rim=None):
    ph = t * 11 + seed * 2.7; bob = abs(math.sin(ph)) * 10
    c.save(); c.translate(x, y - bob * s); c.scale(s, s)
    for sgn in (-1, 1):
        a = math.sin(ph + (0 if sgn > 0 else math.pi))
        c.drawPath(capsule(sgn * 12, -190, sgn * 12 + a * 50, -90, 17, 13), P(color)); c.drawPath(capsule(sgn * 12 + a * 50, -90, sgn * 12 + a * 80, 0, 13, 10), P(color))
        c.drawPath(capsule(sgn * 36, -330, sgn * 36 - a * 50, -250, 12, 10), P(color)); c.drawPath(capsule(sgn * 36 - a * 50, -250, sgn * 36 - a * 90, -330 + abs(a) * 20, 10, 8), P(color))
    c.drawPath(capsule(0, -190, 0, -340, 36, 42), P(color)); c.drawPath(oval_path(6, -396, 28, 34), P(color))
    c.restore()

# ===================== сцены =====================
def s01(c, t, T):
    c.drawPaint(P('#050a09'))
    c.drawRect(rect(0, 0, W, H), P('#000', 1, shader=rad(780, 760, 1100, [('#1f3a30', 1, 0), ('#070d0c', 1, 1)])))
    c.drawRect(rect(0, 0, W, H), P('#fff', 1, shader=tex_shader('concrete', 1.5), blend='mul'))
    bust(c, 'artyom', 500, 760, 4.6, t, dict(lightx=.7, lcol='#6bff9e', hx=-4, tired=1, look=(.4, .2), mouth=0))
    side_shade(c, -1, .86, .9)
    hand(c, 548, 1385 - ease(t / 1.0) * 25, 2.9, 4, 'shush', skin='#d2a284', shade='#9a6a58')
    recorder(c, 250, 1560 + math.sin(t * 2) * 4, 2.1, t, -12)
    c.drawRect(rect(0, 0, W, H), P('#ff3a2a', 1, shader=rad(300, 1500, 420, [('#ff3a2a', .10, 0), ('#ff3a2a', 0, 1)]), blend='add'))

def s02(c, t, T):
    bg.airlock(c, t, hor=1180, fw=420, fh=600, flick=.35)

def s03(c, t, T):
    bg2.vent(c, t, hor=820, fw=330, fh=360, beam=(430, 1330, math.radians(-38)), lamp=GREEN)
    gx, gy, R = 790, 930, 130
    c.drawCircle(gx, gy, R * 1.18, P('#101312')); c.drawCircle(gx, gy, R * 1.18, P('#6a6e66', 1, 'stroke', 8))
    c.drawCircle(gx, gy, R, P('#d6d2bc'))
    for i in range(-6, 7):
        a = math.radians(-90 + i * 16); c.drawLine(gx + math.cos(a) * R * .8, gy + math.sin(a) * R * .8, gx + math.cos(a) * R * .95, gy + math.sin(a) * R * .95, P('#222', 1, 'stroke', 3))
    c.drawPath(skia.Path().arcTo(rect(gx - R * .9, gy - R * .9, gx + R * .9, gy + R * .9), -50, 100, False), P('#a52a1c', .9, 'stroke', 9)) if False else None
    na = math.radians(-90 + 30 + math.sin(t * 7) * 3 + (noise1(t * 5, 2) - .5) * 8)
    c.drawLine(gx, gy, gx + math.cos(na) * R * .85, gy + math.sin(na) * R * .85, P('#a52a1c', 1, 'stroke', 5)); c.drawCircle(gx, gy, 9, P('#1a1a18'))
    c.drawCircle(gx, gy, R, P('#fff', 1, shader=lin(gx - R, gy - R, gx + R, gy + R, [('#ffffff', .35, 0), ('#ffffff', 0, .4)]), blend='add'))
    bust(c, 'artyom', 330, 1400, 2.1, t, dict(lightx=.6, lcol='#ffe8b0', turn=.7, look=(1, -.4), tired=.8))

def s04(c, t, T): bg2.city(c, t)
def s05(c, t, T): bg2.store(c, t)

def s06(c, t, T):
    c.drawPaint(P('#060a09')); p = poly([(0, 0), (W, 0), (W, H), (0, H)])
    texture_fill(c, p, '#26352f', 'concrete', 1.1, .9)
    bg.door(c, W / 2, 940, 470, t, 0.0, 0.0, lamp=GREEN, light=1.0, closed_ind=ORANGE)
    # мощные стальные засовы по краю
    for i in range(10):
        a = i * math.pi / 5 + .3; x, y = W / 2 + math.cos(a) * 640, 940 + math.sin(a) * 640
        c.save(); c.translate(x, y); c.rotate(math.degrees(a))
        c.drawRoundRect(rect(-70, -30, 70, 30), 6, 6, P('#2a302d')); c.drawRoundRect(rect(-70, -30, 70, 30), 6, 6, P('#000', 1, 'stroke', 4)); c.drawRect(rect(-70, -30, 70, -22), P('#889890', .25)); c.restore()
    vign(c, .85)
    bg2.dust_field(c, t, 50, a=.18)

def s07(c, t, T):
    def behind(cv, cx, cy, r):
        cv.drawPaint(P('#0d1210'))
        cv.drawRect(rect(cx - r, cy - r, cx + r, cy + r), P('#000', 1, shader=rad(cx, cy, r * 1.2, [('#ffb070', .9, 0), ('#b0522a', .6, .4), ('#1a0f0a', 1, 1)])))
        for i in range(40):
            x = cx - r + (hash1(i * 4.7) * 2 * r); y = (cy - r + hash1(i * 2.3) * 2 * r + t * 90 * hash1(i)) % (2 * r) + cy - r
            cv.drawCircle(x, y, 2 + hash1(i * 1.3) * 3, P('#d8d0c0', .5))
    bg.airlock(c, t, hor=860, alarm=True, flick=.25, door_open=min(.95, .6 + ease(t / 1.2) * .35), behind=behind, lamp=ORANGE, light=.7)

def s08(c, t, T):
    blurred(c, lambda: bg.airlock(c, t, hor=800, alarm=True, flick=.25, door_open=.9, lamp=ORANGE, light=.6), 14)
    p = pulse(t)
    bust(c, 'artyom', 470, 1010, 3.2, t, dict(lightx=.8, lcol=ORANGE, turn=.8, look=(1, 0), fear=.85, breath=2.0, tired=1, mouth=.25))
    c.drawRect(rect(0, 0, W, H), P(ORANGE, 1, shader=rad(W, 500, 1200, [(ORANGE, .35 * p, 0), (ORANGE, 0, 1)]), blend='add'))
    vign(c, .7)

def s09(c, t, T):
    c.save(); c.translate((noise1(t * 25, 3) - .5) * 14, (noise1(t * 25, 4) - .5) * 14)
    bg.airlock(c, t, hor=860, alarm=True, flick=.7, lamp=GREEN, light=.9)
    c.restore()
    for i in range(110):
        x = hash1(i * 6.1) * W; y = ((hash1(i * 3.3) * H) + t * (300 + 400 * hash1(i * 7.7))) % H; r = 2 + hash1(i * 5) * 5
        c.drawCircle(x, y, r, P('#b8b8a8', .35 + .3 * hash1(i)))
    for k in range(3):
        ph = (t * .9 + k * .33) % 1; x = 220 + k * 320
        c.drawPath(poly([(x, -10), (x + 28, 0), (x + 12, 90 + ph * 400), (x - 8, 0)]), P('#2a2a26', .5 * (1 - ph)))

def s10(c, t, T):
    bg2.tunnel(c, t, lamp='#8fd0a8')
    for i in range(14):
        u = ((t * .16 + hash1(i * 5.3)) % 1)
        x = lerp(540 + (hash1(i * 3.1) - .5) * 600, 540 + (hash1(i * 3.1) - .5) * 1700, u ** 1.4); y = lerp(1040, 1750, u ** 1.4)
        runner(c, x, y, lerp(.25, 1.35, u ** 1.4), t, i, color='#040706', rim='#bfe8cc')
    vign(c, .8, 1150, 900)

def corridor_crowd(c, t, rows, alarm=True, lamp=ORANGE, facing='back', hor=860, door_open=0.0):
    bg.airlock(c, t, hor=hor, alarm=alarm, flick=.4, lamp=lamp, light=.8, door_open=door_open)
    for (y, s, n, seed) in rows:
        for i in range(n):
            x = (i + .5) * W / n + (hash1(i * 4.1 + seed) - .5) * 120 * s
            silhouette(c, x, y + hash1(i * 3.3 + seed) * 40 * s, s, t, seed * 10 + i, color='#030606', rim=lamp, sway=1.6)

def s11(c, t, T):
    corridor_crowd(c, t, [(1180, .62, 8, 1), (1420, .9, 6, 2), (1700, 1.35, 4, 3)])
    for i in range(10):  # поднятые руки
        x = 120 + hash1(i * 7.7) * 840; y = 1250 + hash1(i * 2.1) * 400; ph = math.sin(t * 6 + i) * 18
        c.drawPath(capsule(x, y + 140, x + ph, y - 60, 14, 10), P('#030606')); c.drawCircle(x + ph, y - 70, 14, P('#030606'))
    vign(c, .8)

def s12(c, t, T):
    bg.airlock(c, t, hor=820, flick=.2)
    bust(c, 'gromov', 540, 1000, 3.0, t, dict(lightx=-.4, lcol='#6bff9e', under=.25, look=(math.sin(t * .7), 0)))
    clipboard(c, 250, 1560, -10)

def s13(c, t, T):
    wallbg(c, t, GREEN, 540, 1500)
    bust(c, 'gromov', 540, 870, 5.0, t, dict(lightx=0, lcol='#6bff9e', under=1.0, frown=1, tired=.6, brow=1))
    vign(c, .9, 1000, 900)

def s14(c, t, T):
    bg.airlock(c, t, hor=780, alarm=True, flick=.3, lamp=GREEN, light=.8)
    bust(c, 'gromov', 360, 960, 2.7, t, dict(lightx=.5, lcol=ORANGE, turn=.7, look=(1, 0), under=.2, mouth=.3 * (math.sin(t * 6) > .3), frown=1))
    sh = (840, 1500); hd = (840 + math.sin(t * 3) * 4, 1050 - ease(t / .8) * 40)
    arm(c, sh, hd, '#2b3234', '#c49a7c', 270, 270, bend=1, w=48)
    hand(c, hd[0], hd[1], 2.3, 8, 'point', skin='#c49a7c', shade='#8e6150')
    keys(c, 330, 1780, 2.0, t)

def s15(c, t, T):
    gap = lerp(.85, .08, ease(t / T))
    def behind(cv, cx, cy, r):
        cv.drawPaint(P('#0a0e0c'))
        cv.drawRect(rect(cx - r, cy - r, cx + r, cy + r), P('#000', 1, shader=rad(cx, cy, r * 1.25, [('#ffb070', .95, 0), ('#a8502a', .6, .45), ('#120a08', 1, 1)])))
        for i in range(7):
            ys = cy - r * .6 + i * r * .22; xs = cx + r * .9; reach = (1 - gap) * 0 + gap * r * 1.3 + 60 * math.sin(t * 5 + i)
            cv.drawPath(capsule(xs, ys + 90, xs - reach, ys + math.sin(t * 4 + i) * 20, 22, 16), P('#050403'))
            for f in range(4): cv.drawLine(xs - reach, ys, xs - reach - 26, ys - 18 + f * 12 + math.sin(t * 9 + f) * 4, P('#050403', 1, 'stroke', 8))
    c.drawPaint(P('#060a09')); texture_fill(c, poly([(0, 0), (W, 0), (W, H), (0, H)]), '#26352f', 'concrete', 1.1, .9)
    bg.door(c, W / 2 + 40, 960, 520, t, gap * 1.0, 0, lamp=ORANGE, light=.9, behind=behind)
    vign(c, .8)

def s16(c, t, T):
    wallbg(c, t, ORANGE, 300, 200, '#1b2420')
    bust(c, 'mara', 400, 700, 2.3, t, dict(lightx=.5, lcol=ORANGE, tilt=11, eyes=.1, worry=1, tired=.8, hx=-10))
    bust(c, 'lyosha', 560, 1180, 2.1, t, dict(lightx=.5, lcol=ORANGE, tilt=-6, eyes=.3, fear=.4, breath=2.4))
    hand(c, 372, 1262, 1.8, -10, 'flat', skin='#ebcab3', shade='#b98a78'); hand(c, 748, 1262, 1.8, 10, 'flat', skin='#ebcab3', shade='#b98a78')
    c.drawRect(rect(0, 0, W, H), P(ORANGE, 1, shader=rad(W, 100, 1300, [(ORANGE, .22 * pulse(t), 0), (ORANGE, 0, 1)]), blend='add')); vign(c, .75)

def s17(c, t, T):
    blurred(c, lambda: bg.airlock(c, t, hor=800, alarm=True, flick=.4, lamp=GREEN, light=.8), 8)
    pull = ease(t / T)
    bust(c, 'artyom', 400, 1020, 2.7, t, dict(lightx=.6, lcol=ORANGE, squint=.55, frown=1, tired=1, tilt=-4, mouth=.25, breath=2.5, hy=pull * 12))
    # рычаг
    bx, by = 820, 660
    c.drawRoundRect(rect(bx - 80, by + 360, bx + 80, by + 420), 8, 8, P('#2a2f2c')); c.drawRect(rect(bx - 14, by + 140, bx + 14, by + 400), P('#1a1e1c')) if False else None
    ang = math.radians(-18 + pull * 48)
    hx_, hy_ = bx + math.sin(ang) * 380, by + 380 - math.cos(ang) * 380 + 40
    c.drawLine(bx, by + 380, hx_, hy_, P('#101312', 1, 'stroke', 30)); c.drawLine(bx - 3, by + 380, hx_ - 3, hy_, P('#8a928c', 1, 'stroke', 14))
    c.drawCircle(bx, by + 380, 36, P('#1d211f')); c.drawCircle(bx, by + 380, 18, P('#707a73'))
    c.drawRoundRect(rect(hx_ - 42, hy_ - 28, hx_ + 42, hy_ + 28), 14, 14, P('#a52a1c')); c.drawRoundRect(rect(hx_ - 42, hy_ - 28, hx_ + 42, hy_ + 28), 14, 14, P('#000', .8, 'stroke', 4))
    sh = (400 + 215 * .88 * 2.7 * .75, 1020 + 190 * 2.7 * .85)
    arm(c, sh, (hx_, hy_ + 10), '#5a655e', '#d2a284', 340, 340, bend=1, w=46)
    hand(c, hx_, hy_ + 10, 2.0, 0, 'fist', skin='#d2a284', shade='#9a6a58')
    c.drawRect(rect(0, 0, W, H), P(ORANGE, 1, shader=rad(W, 200, 1300, [(ORANGE, .28 * pulse(t), 0), (ORANGE, 0, 1)]), blend='add')); vign(c, .7)

def s18(c, t, T):
    c.drawPaint(P('#060a09')); texture_fill(c, poly([(0, 0), (W, 0), (W, H), (0, H)]), '#22302b', 'concrete', 1.1, .9)
    ang = t * 36 + 20
    bg.door(c, W / 2, 900, 640, t, 0, ang, lamp=ORANGE, light=.8)
    wr = 640 * .27 * 1.12
    for k, sgn in enumerate((-1, 1)):
        a = math.radians(ang + 90 + sgn * 70); wx, wy = W / 2 + math.cos(a) * wr * 1.0, 900 + math.sin(a) * wr * 1.0
        arm(c, (W / 2 + sgn * 400, 2080), (wx, wy), '#5a655e', '#d2a284', 545, 545, bend=sgn, w=46)
        hand(c, wx, wy, 1.8, 0, 'fist', skin='#d2a284', shade='#9a6a58')
    bust(c, 'artyom', 540, 1560 + math.sin(t * 5) * 4, 1.5, t, dict(lightx=.6, lcol=ORANGE, squint=.7, frown=1, mouth=.3, tired=1, breath=2.5))
    c.drawRect(rect(0, 0, W, H), P(ORANGE, 1, shader=rad(W / 2, 100, 1300, [(ORANGE, .2 * pulse(t), 0), (ORANGE, 0, 1)]), blend='add')); vign(c, .8)

def s19(c, t, T):
    k = ease(t / (T * .85))
    c.drawPaint(P('#070a09')); texture_fill(c, poly([(0, 0), (W, 0), (W, H), (0, H)]), '#1e2a26', 'concrete', 1.2, .9)
    for i, y in enumerate((300, 560, 820, 1080, 1340, 1600)):
        # гнездо в раме
        c.drawRoundRect(rect(720, y - 62, W + 20, y + 62), 10, 10, P('#05080a')); c.drawRoundRect(rect(720, y - 62, W + 20, y + 62), 10, 10, P('#000', 1, 'stroke', 6))
        # цилиндр поршня
        c.drawRoundRect(rect(-20, y - 78, 380, y + 78), 18, 18, P('#2a302d')); c.drawRoundRect(rect(-20, y - 78, 380, y + 78), 18, 18, P('#fff', 1, shader=lin(0, y - 78, 0, y + 78, [('#ffffff', .22, 0), ('#000000', 0, .5), ('#000000', .5, 1)])))
        for xx in (60, 150, 240, 330): c.drawRect(rect(xx, y - 80, xx + 14, y + 80), P('#0c0f0e'))
        # шток
        ext = 380 + k * 360 * (.85 + .15 * math.sin(i * 1.7)); 
        c.drawRect(rect(380, y - 26, ext, y + 26), P('#9aa6a0')); c.drawRect(rect(380, y - 26, ext, y - 8), P('#fff', .35)); c.drawRect(rect(380, y + 10, ext, y + 26), P('#000', .4))
        c.drawRoundRect(rect(ext, y - 52, ext + 90, y + 52), 10, 10, P('#3a403c')); c.drawRoundRect(rect(ext, y - 52, ext + 90, y + 52), 10, 10, P('#000', 1, 'stroke', 5))
        if ext + 90 > 700: glow(c, 740, y, 150, ORANGE, .45 * clamp((ext + 90 - 700) / 120))
        # пар
        for j in range(5):
            ph = (t * .8 + j * .2 + i * .13) % 1
            c.drawCircle(120 + j * 60, y - 80 - ph * 70, 18 + ph * 50, P('#d8e8e0', .14 * (1 - ph), blur=14))
    c.drawRect(rect(0, 0, W, H), P(ORANGE, 1, shader=lin(W, 0, 400, 0, [(ORANGE, .12, 0), (ORANGE, 0, 1)]), blend='add')); vign(c, .8)
    if k > .97: c.drawRect(rect(0, 0, W, H), P('#fff', .06 * math.sin((t - T * .8) * 20) ** 2))

def s20(c, t, T):
    k = ease(t / (T * .55)); ind = ORANGE if t < T * .55 else GREEN
    c.drawPaint(P('#060a09')); texture_fill(c, poly([(0, 0), (W, 0), (W, H), (0, H)]), '#26352f', 'concrete', 1.1, .9)
    bg.door(c, W / 2, 940, 470, t, 0, 0, lamp=GREEN, light=.9, closed_ind=ind, bolts=k)
    for i in range(10):
        a = i * math.pi / 5 + .3; x, y = W / 2 + math.cos(a) * 640, 940 + math.sin(a) * 640
        c.save(); c.translate(x, y); c.rotate(math.degrees(a)); out = (1 - k) * 60
        c.drawRoundRect(rect(-70 - out, -30, 70 - out, 30), 6, 6, P('#2a302d')); c.drawRoundRect(rect(-70 - out, -30, 70 - out, 30), 6, 6, P('#000', 1, 'stroke', 4)); c.restore()
    if abs(t - T * .55) < .12: c.drawRect(rect(0, 0, W, H), P('#d8ffe8', .22 * (1 - abs(t - T * .55) / .12)))
    vign(c, .85); bg2.dust_field(c, t, 40, a=.15)

def s21(c, t, T):
    wallbg(c, t, GREEN, 950, 250)
    slide = ease(t / T) * 30
    bust(c, 'artyom', 400, 980 + slide, 3.1, t, dict(lightx=.6, lcol='#6bff9e', tilt=-15, squint=.55, tired=1, breath=3.2, turn=.4, hx=-20))
    side_shade(c, -1, .4, .8)

def s22(c, t, T):
    corridor_crowd(c, t, [(1120, .55, 9, 4), (1330, .8, 7, 5), (1620, 1.25, 5, 6)], alarm=False, lamp=GREEN)
    vign(c, .85)

def s23(c, t, T):
    hits = [.35, .9, 1.3, 2.2, 2.55, 3.4, 3.7, 4.3]
    imp = max([math.exp(-(t - h) * 9) for h in hits if t >= h] + [0])
    c.save(); c.translate((noise1(t * 40, 5) - .5) * 30 * imp, (noise1(t * 40, 6) - .5) * 20 * imp)
    c.drawPaint(P('#060a09')); texture_fill(c, poly([(0, 0), (W, 0), (W, H), (0, H)]), '#26352f', 'concrete', 1.1, .9)
    bg.door(c, W / 2, 940, 470, t, 0, 0, lamp=GREEN, light=.9 + imp)
    c.restore()
    for i in range(int(imp * 40)): c.drawCircle(hash1(i * 3.1 + t) * W, hash1(i * 7.1 + t) * H * .6 + t * 0, 2 + hash1(i) * 4, P('#c0c0b0', .5))
    c.drawRect(rect(0, 0, W, H), P(ORANGE, 1, shader=rad(W / 2, 940, 800, [(ORANGE, .18 * imp, 0), (ORANGE, 0, 1)]), blend='add'))
    if t > 4.5: c.drawPaint(P('#000', min(1, (t - 4.5) * 3) * 0))
    vign(c, .85)

def s24(c, t, T):
    blurred(c, lambda: bg.airlock(c, t, hor=800, flick=.3, lamp=GREEN), 12)
    bust(c, 'gromov', 320, 1000, 2.1, t, dict(lightx=.7, lcol='#6bff9e', turn=.8, look=(1, 0), tired=.7, frown=1))
    bust(c, 'mara', 770, 1030, 2.0, t, dict(lightx=-.7, lcol='#6bff9e', turn=.6, look=(1, 0), worry=1, flip=True, fear=.5))
    vign(c, .85)

def s25(c, t, T):
    bg2.vent(c, t, hor=860, fw=330, fh=360, grille=True, lamp=GREEN)
    ph = (t / T)
    x = lerp(560, 520, ph); 
    c.save(); c.translate(0, 0)
    c.save(); c.clipRect(rect(W / 2 - 150, 790, W / 2 + 150, 1020))
    infected(c, 430 + ph * 220, 1010, .34, t, 'stand', 1, color='#010302', light=0)
    c.restore(); c.restore()
    for i in range(9): c.drawLine(W / 2 - 150 + i * 37.5, 790, W / 2 - 150 + i * 37.5, 1020, P('#050808', 1, 'stroke', 6))

def s26(c, t, T):
    bg2.tunnel(c, t, lamp='#8fd0a8')
    infected(c, 540 + math.sin(t * .7) * 20, 1500, 1.5, t, 'stand', 2, color='#050807', rim='#9ae6b4', light=.9)
    vign(c, .8, 1150, 900)

def s27(c, t, T):
    bg2.tunnel(c, t, lamp='#6fa890', dark=.5)
    c.drawPaint(P('#000', .15))
    infected(c, 620, 1560, 2.2, t, 'crouch', 3, color='#030504', rim='#9ae6b4', light=.6)
    vign(c, .9, 1100, 1000)

def s28(c, t, T):
    c.drawPaint(P('#060a09')); texture_fill(c, poly([(0, 0), (W, 0), (W, H), (0, H)]), '#22302b', 'concrete', 1.1, .9)
    bg.door(c, 920, 960, 640, t, 0, 0, lamp=GREEN, light=.9)
    bust(c, 'artyom', 360, 1000, 2.9, t, dict(lightx=.8, lcol='#6bff9e', tilt=16, turn=.9, eyes=.1, tired=1, breath=1.5, hx=40, hy=10))
    hand(c, 640, 1330, 2.4, 78, 'flat', skin='#d2a284', shade='#9a6a58')
    vign(c, .85)

def s29(c, t, T):
    blurred(c, lambda: bg.airlock(c, t, hor=800, flick=.4, lamp=GREEN, light=.7), 16)
    tr = (noise1(t * 20, 8) - .5) * 5
    bust(c, 'lyosha', 540 + tr, 940, 4.2, t, dict(lightx=.7, lcol='#6bff9e', fear=1.0, look=(0, 0), tired=.2, breath=2.0))
    vign(c, .85, 1000)

def prof_head(c, t, scale=1.0, twitch=0.0, col='#5d675f', rim='#9ae6b4'):
    """Голова заражённого в профиль (лицом вправо): серая кожа, пустая глазница, дёргающееся ухо."""
    c.save(); c.scale(scale, scale)
    head = smooth([(-70, -310), (80, -320), (200, -250), (232, -160), (226, -100), (300, 10), (262, 46), (270, 92), (246, 112), (258, 142), (238, 218),
                   (150, 300), (40, 340), (-30, 420), (-250, 420), (-210, 120), (-220, -100), (-170, -240)])
    c.drawPath(head, P(col)); c.save(); c.clipPath(head, doAntiAlias=True)
    c.drawRect(rect(-300, -400, 400, 460), P('#000', 1, shader=lin(-220, 0, 300, 0, [('#000', .8, 0), ('#000', .2, .65), ('#000', 0, 1)])))
    tp_ = P('#fff', 1, blend='mul', shader=tex_shader('rust', 1.3, 30, 10)); tp_.setAlphaf(.8); c.drawRect(rect(-300, -400, 400, 460), tp_)
    for i in range(18):
        x = -120 + hash1(i * 3.1) * 340; y = -200 + hash1(i * 5.3) * 420
        c.drawPath(smooth([(x, y), (x + 30, y + 20 * hash1(i)), (x + 70, y + 12)], False), P('#0e1a14', .6, 'stroke', 3))
    # глазница
    c.drawPath(oval_path(150, -110, 52, 44), P('#020504')); c.drawPath(oval_path(158, -108, 28, 24), P('#000'))
    c.drawPath(smooth([(100, -170), (160, -190), (210, -160)], False), P('#0a120e', .9, 'stroke', 12))
    # скула, рот
    c.drawPath(smooth([(90, 30), (160, 60), (230, 70)], False), P('#0e1a14', .6, 'stroke', 5))
    c.drawPath(smooth([(210, 136), (252, 134), (262, 146)], False), P('#000', .95, 'stroke', 5))
    c.restore()
    c.drawPath(head, P(rim, .32, 'stroke', 5, blend='add'))
    c.save(); c.translate(-40, 20); c.rotate(twitch * 10)
    ear = smooth([(10, -90), (-50, -130), (-104, -30), (-60, 90), (4, 80)]); c.drawPath(ear, P(col)); c.drawPath(ear, P('#000', .55, 'stroke', 4))
    c.drawPath(smooth([(-20, -60), (-62, -70), (-70, 10), (-34, 46)], False), P('#000', .6, 'stroke', 7)); c.drawPath(ear, P(rim, .3, 'stroke', 3, blend='add')); c.restore()
    c.restore()

def s30(c, t, T):
    wallbg(c, t, GREEN, 900, 300, '#10181a'); c.drawPaint(P('#000', .25))
    tw = max(0, math.sin(t * 9) * (math.sin(t * 2.2) > .55))
    c.save(); c.translate(470, 980); prof_head(c, t, 2.0, tw); c.restore()
    vign(c, .9, 1000)

def s31(c, t, T):
    bg2.vent(c, t, hor=860, fw=330, fh=360, vib=3, lamp=GREEN)
    # вибрирующая труба на переднем плане
    for k in range(18):
        amp = 8 * math.sin(t * 60 + k) * (.5 + .5 * math.sin(t * 5))
        y = 1000 + k * 0
    py = 1080 + math.sin(t * 70) * 6 * (.6 + .4 * math.sin(t * 4))
    c.drawRect(rect(-40, py - 110, W + 40, py + 110), P('#1d2a26'))
    c.drawRect(rect(-40, py - 110, W + 40, py + 110), P('#fff', 1, shader=lin(0, py - 110, 0, py + 110, [('#ffffff', .3, 0), ('#000000', 0, .35), ('#000000', .6, 1)])))
    c.drawRect(rect(-40, py - 110, W + 40, py + 110), P('#7a3a14', .35, shader=tex_shader('rust', 1.2, 10, 10)))
    for x in (160, 620, 940): c.drawRect(rect(x, py - 120, x + 38, py + 120), P('#0e1110')); c.drawRect(rect(x + 3, py - 120, x + 10, py + 120), P('#889890', .4))
    for r in range(3): c.drawLine(-40, py - 70 + r * 70 + math.sin(t * 80 + r) * 5, W + 40, py - 70 + r * 70, P('#9ae6b4', .1, 'stroke', 3))
    for i in range(60):
        x = hash1(i * 3.1) * W; y = (py + 110 + (t * 160 * (.4 + hash1(i)) + hash1(i * 9) * 800) % 700)
        c.drawCircle(x, y, 1.5 + hash1(i * 2) * 2.5, P('#c9d2c8', .5))
    vign(c, .8)

def s32(c, t, T):
    bg.airlock(c, t, hor=800, flick=.5, lamp=GREEN, light=.8)
    k = ease(t / 1.2)
    bust(c, 'gromov', 470, 1020, 2.9, t, dict(lightx=-.5, lcol='#6bff9e', pale=.55, fear=.3, tired=1, frown=1, look=(.3, 0)))
    hd = (840, 1500 - k * 740)
    arm(c, (840, 1650), (hd[0], hd[1] + 70), '#2b3234', '#c49a7c', 480, 480, bend=1, w=50)
    hand(c, hd[0], hd[1], 2.6, 0, 'fist', skin=mix('#c49a7c', '#cfd6cc', .5), shade=mix('#8e6150', '#5a6660', .5))
    vign(c, .85)

def s33(c, t, T):
    wallbg(c, t, GREEN, 540, 1500); c.drawPaint(P('#000', .25))
    mo = .18 + .14 * abs(math.sin(t * 7)) * (math.sin(t * 1.8) > -.2)
    bust(c, 'gromov', 540, 810, 8.8, t, dict(lightx=0, lcol='#6bff9e', under=1.0, mouth=mo, pale=.5, frown=1, tired=1, eyes=.9))
    c.drawRect(rect(0, 0, W, 420), P('#000', 1, shader=lin(0, 0, 0, 420, [('#000', 1, 0), ('#000', 0, 1)])))
    c.drawRect(rect(0, 1500, W, H), P('#000', 1, shader=lin(0, 1500, 0, H, [('#000', 0, 0), ('#000', 1, 1)])))
    vign(c, .85)

def s34(c, t, T):
    cut = T - .55
    if t > cut: c.drawPaint(P('#000')); return
    k = clamp(t / cut)
    beat = (math.sin(t * 38) ** 2) * (math.sin(t * 7.3) > -.2)
    imp = beat * k ** 1.5
    c.save(); c.translate((noise1(t * 50, 5) - .5) * 44 * k, (noise1(t * 50, 6) - .5) * 30 * k)
    c.drawPaint(P('#060a09')); texture_fill(c, poly([(0, 0), (W, 0), (W, H), (0, H)]), '#26352f', 'concrete', 1.1, .9)
    bg.door(c, W / 2, 940, 470, t, 0, 0, lamp=GREEN, light=.8 + imp * .5, closed_ind=ORANGE)
    # вмятины от ударов с той стороны
    c.save(); c.clipPath(oval_path(W / 2, 940, 430, 430), doAntiAlias=True)
    for i in range(9):
        if k * 1.15 > i / 9:
            ox = W / 2 + (hash1(i * 7.3) - .5) * 600; oy = 940 + (hash1(i * 3.9) - .5) * 600; a = (math.sin(t * (22 + i * 3) + i) ** 2) * .5
            c.drawCircle(ox, oy, 90 + 30 * a, P('#000', 1, shader=rad(ox, oy, 110, [('#000', .55 * a + .15, 0), ('#000', 0, 1)])))
            c.drawCircle(ox - 20, oy - 24, 70, P('#fff', 1, shader=rad(ox - 20, oy - 24, 80, [('#fff', .10 * a, 0), ('#fff', 0, 1)]), blend='add'))
    c.restore()
    c.restore()
    # свет сквозь щель вокруг двери и тени бегущих тел
    ring = oval_path(W / 2, 940, 482, 482)
    c.drawPath(ring, P(ORANGE, .55 * (.5 + .5 * imp), 'stroke', 14, blur=6, blend='add'))
    for i in range(14):
        a0 = (hash1(i * 5.1) * 360 + t * (60 + 40 * hash1(i))) % 360; ln = 18 + 40 * hash1(i * 2.2) * k
        c.save(); c.translate(W / 2, 940); c.rotate(a0)
        c.drawRect(rect(470, -ln, 500, ln), P('#000', .8 * k)); c.restore()
    c.drawRect(rect(0, 0, W, H), P('#000', 1, shader=rad(W / 2, 940, 480, [('#000', 0, 0), ('#000', .2 * k, 1)])))
    c.drawRect(rect(0, 0, W, H), P(ORANGE, 1, shader=rad(W / 2, 940, 900, [(ORANGE, .22 * imp, 0), (ORANGE, 0, 1)]), blend='add'))
    vign(c, .85)

SCENES = {i: globals()['s%02d' % i] for i in range(1, 35)}
