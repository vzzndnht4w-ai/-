"""Остальные фоны: вентшахта, кладовая, город, тоннель, поршни."""
from .core import *
from .bg import persp, GREEN, ORANGE, rivets

def dust_field(c, t, n=60, color='#d8f0e0', a=.25, area=(0, 0, W, H), drift=(0, 22), size=2.6):
    x0, y0, x1, y1 = area
    for i in range(n):
        x = x0 + (hash1(i * 7.7) * (x1 - x0) + math.sin(t * .7 + i) * 24 + t * drift[0] * (.3 + hash1(i))) % (x1 - x0)
        y = y0 + (hash1(i * 5.1) * (y1 - y0) + t * drift[1] * (.3 + hash1(i * 1.9))) % (y1 - y0)
        c.drawCircle(x, y, 1 + hash1(i * 2.3) * size, P(color, a * (.3 + .7 * hash1(i * 9.9))))

def vent(c, t, hor=900, fw=300, fh=330, lamp=GREEN, beam=None, grille=False, vib=0.0, rust=1.0, light=1.0):
    """Узкая металлическая шахта (низкий ракурс). beam=(x,y,angle) — луч фонаря."""
    at, (FL, FR, FT, FB) = persp(hor, fw, fh)
    c.drawPaint(P('#020405'))
    nl, nr, nt, nb = at(0)
    far = poly([(FL, FT), (FR, FT), (FR, FB), (FL, FB)])
    c.drawPath(far, P('#040807'))
    quads = {'l': poly([(nl, nt), (FL, FT), (FL, FB), (nl, nb)]), 'r': poly([(nr, nt), (FR, FT), (FR, FB), (nr, nb)]),
             'c': poly([(nl, nt), (nr, nt), (FR, FT), (FL, FT)]), 'f': poly([(nl, nb), (nr, nb), (FR, FB), (FL, FB)])}
    for k, base in [('l', '#1d2220'), ('r', '#1b201e'), ('c', '#111514'), ('f', '#151918')]:
        c.drawPath(quads[k], P(base)); texture_fill(c, quads[k], base, 'metal', 1.0, .9)
        c.save(); c.clipPath(quads[k], doAntiAlias=True)
        c.drawRect(rect(0, 0, W, H), P('#7a3a14', .38 * rust, shader=tex_shader('rust', 1.4, 100, 50)))
        c.restore()
    # рёбра жёсткости
    for i in range(0, 14):
        u = 1 - .78 ** (i + .4); u = clamp(u * 1.1, 0, .97)
        l, r, tp, bt = at(u); wv = 3 + 16 * (1 - u)
        vv = math.sin(t * 40 + i) * vib * (1 - u)
        c.drawPath(poly([(l, tp), (r, tp), (r, bt), (l, bt)]), P('#000', .75, 'stroke', wv))
        c.drawPath(poly([(l + wv, tp + wv), (r - wv, tp + wv), (r - wv, bt - wv), (l + wv, bt - wv)]), P('#8c9a92', .07, 'stroke', max(1, wv * .35)))
        for sx in (l, r):
            for yy in (tp, bt, (tp + bt) / 2):
                c.drawCircle(sx + (8 if sx == l else -8) * (1 - u), yy + vv, 2 + 5 * (1 - u), P('#3a403c'))
    # продольные швы
    for fx in (.25, .5, .75):
        c.drawLine(lerp(nl, nr, fx), nb, lerp(FL, FR, fx), FB, P('#000', .5, 'stroke', 5))
    # решётка вдали
    cx, cy = W / 2, (FT + FB) / 2
    if grille:
        gw, gh = (FR - FL) * .86, (FB - FT) * .86
        c.drawRect(rect(cx - gw / 2, cy - gh / 2, cx + gw / 2, cy + gh / 2), P('#000', 1, shader=rad(cx, cy, gw, [('#9ae6b4', .55, 0), ('#2a6a4a', .5, .6), ('#02100a', 1, 1)])))
        for i in range(9):
            x = cx - gw / 2 + gw * i / 8
            c.drawLine(x, cy - gh / 2, x, cy + gh / 2, P('#050808', 1, 'stroke', 5))
        for i in range(7):
            y = cy - gh / 2 + gh * i / 6
            c.drawLine(cx - gw / 2, y, cx + gw / 2, y, P('#050808', 1, 'stroke', 4))
        c.drawRect(rect(cx - gw / 2, cy - gh / 2, cx + gw / 2, cy + gh / 2), P('#000', 1, 'stroke', 6)) if False else None
        glow(c, cx, cy, 420, lamp, .35)
    else:
        glow(c, cx, cy, 380, lamp, .2 * light)
    # лампа
    for u in (.35, .7):
        l, r, tp, bt = at(u); x, y = W / 2, tp + (bt - tp) * .02; sz = lerp(36, 9, u)
        c.drawRoundRect(rect(x - sz, y, x + sz, y + sz * .5), 4, 4, P(lamp, .9)); glow(c, x, y + 10, sz * 8, lamp, .28 * light)
    # виньетка
    c.drawRect(rect(0, 0, W, H), P('#000', 1, shader=rad(W / 2, hor, 1000, [('#000000', 0, 0), ('#000000', .2, .4), ('#000000', .85, 1)])))
    if beam:
        bx, by, ang = beam
        L = 1900; w = 330
        a0, a1 = ang - math.radians(11), ang + math.radians(11)
        pth = poly([(bx, by), (bx + math.cos(a0) * L, by + math.sin(a0) * L), (bx + math.cos(a1) * L, by + math.sin(a1) * L)])
        c.save(); c.clipPath(pth, doAntiAlias=True)
        c.drawRect(rect(0, 0, W, H), P('#fff3c0', 1, shader=lin(bx, by, bx + math.cos(ang) * L, by + math.sin(ang) * L, [('#fff3c0', .55, 0), ('#fff3c0', .16, .5), ('#fff3c0', 0, 1)]), blend='add'))
        for i in range(90):
            d = hash1(i * 3.1) * L * .8 + 40; off = (hash1(i * 5.9) - .5) * math.tan(math.radians(11)) * d * 1.8
            px = bx + math.cos(ang) * d - math.sin(ang) * off + math.sin(t + i) * 5; py = by + math.sin(ang) * d + math.cos(ang) * off + (t * 14 + hash1(i) * 100) % 30
            c.drawCircle(px, py, 1.4 + hash1(i * 2) * 2.4, P('#fff6d0', .5))
        c.restore()
    dust_field(c, t, 50, a=.15)

def store(c, t, swing=True):
    """Кладовая: полки с консервами, одна лампа, ржаво-оранжевый свет."""
    c.drawPaint(P('#0a0705'))
    wall = rect(0, 0, W, 1450)
    c.drawRect(wall, P('#2a1d15')); texture_fill(c, poly([(0, 0), (W, 0), (W, 1450), (0, 1450)]), '#2e2018', 'concrete', 1.0, .8)
    c.drawRect(rect(0, 1450, W, H), P('#150f0b')); texture_fill(c, poly([(0, 1450), (W, 1450), (W, H), (0, H)]), '#1a120d', 'concrete', 1.2, .8)
    # колонна по центру
    c.drawRect(rect(430, 0, 650, 1450), P('#3a2c22')); texture_fill(c, poly([(430, 0), (650, 0), (650, 1450), (430, 1450)]), '#3c2e24', 'concrete', .8, .8)
    c.drawRect(rect(430, 0, 650, 1450), P('#000', 1, shader=lin(430, 0, 650, 0, [('#000', .5, 0), ('#000', 0, .4), ('#000', .55, 1)])))
    # шаблонная надпись 200
    f = skia.Font(skia.Typeface('DejaVu Sans', skia.FontStyle.Bold()), 92)
    c.drawSimpleText('200', 458, 800, f, P('#d8d0bc', .88))
    for sx in (0, 1):
        for yy in (630, 840): c.drawCircle(446 + sx * 188, yy + 40, 6, P('#000', .5))
    # стеллажи с банками
    def shelf(x0, x1, depth_dark=.0):
        c.drawRect(rect(x0, 200, x1, 1450), P('#161a1a'))
        for i in range(6):
            y = 330 + i * 190
            c.drawRect(rect(x0, y, x1, y + 22), P('#4a5250')); c.drawRect(rect(x0, y + 22, x1, y + 36), P('#000', .5))
            x = x0 + 8
            k = 0
            while x < x1 - 40:
                w = 40 + hash1(i * 9 + k * 3.3 + x0) * 18; h = 70 + hash1(i * 5 + k * 1.7) * 60
                if hash1(i * 13 + k * 2.1 + x0) > .12:
                    cc = ['#8a6a3a', '#6a7a5a', '#7a3a2a', '#8e8a72'][int(hash1(k + i * 7 + x0) * 4)]
                    if hash1(i + k * 5.5 + x0) > .8:
                        c.drawRect(rect(x, y - h * .9, x + w * 1.8, y), P('#4a3a2a')); c.drawRect(rect(x, y - h * .9, x + w * 1.8, y), P('#000', .3, 'stroke', 3)); x += w * 1.8 + 4
                    else:
                        c.drawRoundRect(rect(x, y - h, x + w, y), 6, 6, P(cc)); c.drawRect(rect(x + 4, y - h * .62, x + w - 4, y - h * .3), P('#d8cfb0', .75))
                        c.drawRoundRect(rect(x, y - h, x + w, y), 6, 6, P('#000', 1, shader=lin(x, 0, x + w, 0, [('#fff', .16, 0), ('#000', 0, .5), ('#000', .5, 1)])))
                        x += w + 4
                else: x += 34
                k += 1
        c.drawRect(rect(x0, 200, x1, 1450), P('#000', 1, shader=lin(x0, 0, x1, 0, [('#000', .6 * depth_dark, 0), ('#000', .0, 1)]) if depth_dark else lin(x0, 0, x1, 0, [('#000', 0, 0), ('#000', 0, 1)])))
    shelf(-20, 410, .3); shelf(670, 1100, .0)
    # ящики на полу
    for (x, y, w, h) in [(40, 1330, 220, 120), (230, 1370, 160, 80), (730, 1320, 250, 130), (880, 1250, 160, 110)]:
        c.drawRect(rect(x, y, x + w, y + h), P('#5c452c')); texture_fill(c, poly([(x, y), (x + w, y), (x + w, y + h), (x, y + h)]), '#5a432b', 'rust', 1.0, .6)
        c.drawRect(rect(x, y, x + w, y + h), P('#000', .8, 'stroke', 4)); c.drawLine(x, y + h * .35, x + w, y + h * .35, P('#000', .6, 'stroke', 3))
    # лампа на проводе
    sw = math.sin(t * 1.3) * 22 if swing else 0
    bx, by = W / 2 + sw, 360
    c.drawLine(W / 2, -10, bx, by - 40, P('#050505', 1, 'stroke', 5))
    c.drawPath(poly([(bx - 40, by - 46), (bx + 40, by - 46), (bx + 64, by - 8), (bx - 64, by - 8)]), P('#1a1a18'))
    c.drawCircle(bx, by + 6, 24, P('#ffd8a0'))
    fl = .85 + .15 * noise1(t * 11, 3)
    glow(c, bx, by + 10, 900, '#ff8a2a', .62 * fl); glow(c, bx, by + 10, 300, '#ffc070', .55 * fl)
    c.drawRect(rect(0, 0, W, H), P('#000', 1, shader=rad(W / 2, 700, 1200, [('#000', 0, 0), ('#000', .25, .45), ('#000', .85, 1)])))
    dust_field(c, t, 50, '#ffdcb0', .18, (200, 200, 900, 1300))

def city(c, t):
    """Руины города ночью, ядерное зарево на горизонте, падающий пепел."""
    c.drawRect(rect(0, 0, W, H), P('#000', 1, shader=lin(0, 0, 0, H, [('#0b0706', 1, 0), ('#2a1209', 1, .55), ('#6a2a10', 1, .8), ('#140a06', 1, 1)])))
    # зарево и гриб
    gx, gy = 640, 1250; pu = 1 + math.sin(t * 1.5) * .03
    glow(c, gx, gy, 1100, '#ff6a20', .55 * pu)
    c.save(); c.translate(gx, gy)
    stem = smooth([(-46, 0), (-58, -160), (-40, -340), (-90, -440), (-180, -480), (-230, -560), (-170, -690), (-60, -740), (60, -750), (180, -690), (240, -560), (190, -480), (100, -440), (52, -340), (64, -160), (50, 0)])
    c.drawPath(stem, P('#000', 1, shader=lin(0, -760, 0, 0, [('#ffb870', .95, 0), ('#e0591c', .9, .35), ('#6a1e0c', .95, .8), ('#2a0e08', .95, 1)])))
    c.save(); c.clipPath(stem, doAntiAlias=True)
    for i in range(14):
        a = i * .9 + t * .25
        c.drawCircle(math.cos(a) * 120, -600 + math.sin(a) * 90, 60 + 20 * math.sin(a * 2), P('#fff0c0', .09, blur=14))
    c.restore(); c.restore()
    # слои зданий
    def skyline(base, hmin, hmax, col, seed, step, a=1.0, gap=0.0):
        pts = [(-20, H)]; x = -20
        while x < W + 40:
            h = hmin + hash1(x * .013 + seed) * (hmax - hmin); w = step * (.7 + hash1(x * .027 + seed * 2) * .9)
            top = base - h; broken = hash1(x * .05 + seed * 3) > .55
            pts += [(x, top), (x + w * .4, top + (h * .12 if broken else 0)), (x + w, top + (h * .3 if broken else 0))]
            x += w
        pts.append((x, H)); c.drawPath(poly(pts), P(col, a))
    skyline(1420, 120, 420, '#3a1a0e', 1.1, 90, 1)
    skyline(1560, 180, 640, '#1c0e08', 2.7, 110, 1)
    skyline(1760, 240, 820, '#0a0605', 4.3, 140, 1)
    # окна/огни
    for i in range(30):
        x = hash1(i * 4.3) * W; y = 1200 + hash1(i * 8.1) * 500
        if (math.sin(t * 3 + i) + 1) > .5: c.drawCircle(x, y, 3, P('#ff8a2a', .35 + .3 * hash1(i * 2)))
    # земля, обломки
    c.drawPath(poly([(0, 1800), (200, 1760), (380, 1810), (700, 1770), (1000, 1820), (W, 1780), (W, H), (0, H)]), P('#050303'))
    # пепел
    for i in range(170):
        sp = .5 + hash1(i * 2.3) * 1.2; x = (hash1(i * 7.1) * W + math.sin(t * .8 + i) * 40 + t * 18) % W; y = (hash1(i * 3.7) * H + t * 120 * sp) % H
        r = 1.5 + hash1(i * 6.1) * 3.5
        c.drawCircle(x, y, r, P('#1a1210', .85)); c.drawCircle(x, y, r + 1.5, P('#ff9a40', .1))
    c.drawRect(rect(0, 0, W, H), P('#000', 1, shader=rad(W / 2, 960, 1250, [('#000', 0, 0), ('#000', .7, 1)])))

def tunnel(c, t, view='out', lamp='#8fd0a8', ash=True, dark=0.0):
    """Бетонный тоннель-выход наружу: арка, пепельный свет, склон."""
    c.drawRect(rect(0, 0, W, H), P('#000', 1, shader=lin(0, 0, 0, H, [('#1c2a26', 1, 0), ('#566a60', 1, .5), ('#2a3a33', 1, 1)])))
    glow(c, W / 2, 830, 900, lamp, .55 * (1 - dark))
    # землей и обломки
    c.drawPath(poly([(0, 1050), (300, 1010), (560, 1040), (820, 1000), (W, 1030), (W, H), (0, H)]), P('#1b2420'))
    c.drawPath(poly([(0, 1260), (W, 1200), (W, H), (0, H)]), P('#0d1210'))
    # далёкие руины
    for i in range(7):
        x = 60 + i * 150; h = 90 + hash1(i * 4.2) * 200
        c.drawPath(poly([(x, 1030), (x, 1030 - h), (x + 70, 1030 - h * .8), (x + 100, 1030 - h * .95), (x + 120, 1030)]), P('#33443d', .8))
    # арка/портал
    arch = skia.Path(); arch.addRect(rect(-40, -40, W + 40, H + 40)); inner = skia.Path(); inner.moveTo(150, H + 40); inner.lineTo(150, 760); inner.cubicTo(150, 330, 930, 330, 930, 760); inner.lineTo(930, H + 40); inner.close()
    arch.addPath(inner); arch.setFillType(skia.PathFillType.kEvenOdd)
    c.drawPath(arch, P('#0b0f0e')); texture_fill(c, arch, '#161d1b', 'concrete', 1.1, .9)
    c.drawPath(inner, P('#000', .9, 'stroke', 16))
    c.drawPath(inner, P(lamp, .22, 'stroke', 3, blend='add'))
    if ash:
        for i in range(210):
            sp = .5 + hash1(i * 2.3) * 1.1; x = (hash1(i * 7.1) * W + math.sin(t * .8 + i) * 30) % W; y = (hash1(i * 3.7) * H + t * 130 * sp) % H
            r = 1.8 + hash1(i * 6.1) * 4.4; a = .25 + hash1(i * 4.1) * .5
            c.drawCircle(x, y, r, P('#c9d2c8', a * .7))
    c.drawRect(rect(0, 0, W, H), P('#000', 1, shader=rad(W / 2, 900, 1250, [('#000', 0, 0), ('#000', .75, 1)])))
