"""Фоны: коридор шлюза, гермодверь, вентшахта, кладовая, город, тоннель."""
from .core import *

GREEN = '#3cff8a'; ORANGE = '#ff7a2a'
def persp(hor, fw=300, fh=420):
    NL, NR, NT, NB = -170, W + 170, -230, H + 230
    FL, FR = W / 2 - fw / 2, W / 2 + fw / 2
    FT, FB = hor - fh * 0.56, hor + fh * 0.44
    def at(u):
        return (lerp(NL, FL, u), lerp(NR, FR, u), lerp(NT, FT, u), lerp(NB, FB, u))
    return at, (FL, FR, FT, FB)

def rivets(c, cx, cy, r, n, rr, color, a=0.9, rot=0):
    for i in range(n):
        ang = rot + i * 2 * math.pi / n
        x, y = cx + math.cos(ang) * r, cy + math.sin(ang) * r
        c.drawCircle(x, y, rr, P('#05080a', .8)); c.drawCircle(x - rr * .2, y - rr * .25, rr * .75, P(color, a))

def door(c, cx, cy, R, t, open_amt=0.0, wheel=0.0, lamp=GREEN, light=1.0, closed_ind=None, behind=None, bolts=1.0):
    """Круглая гермодверь анфас. open_amt: 0 закрыта .. 1 распахнута."""
    # рамa
    fr = oval_path(cx, cy, R * 1.17, R * 1.17)
    c.drawPath(fr, P('#0b1112')); texture_fill(c, fr, '#2a3430', 'concrete', 1.2, .55)
    c.drawCircle(cx, cy, R * 1.17, P('#000', .9, 'stroke', R * .035))
    rivets(c, cx, cy, R * 1.1, 24, R * .018, '#55635e')
    # проём
    hole = oval_path(cx, cy, R * 1.03, R * 1.03)
    c.save(); c.clipPath(hole, doAntiAlias=True)
    if open_amt > 0.02:
        if behind: behind(c, cx, cy, R * 1.03)
        else:
            c.drawPaint(P('#070b0b'))
            c.drawRect(rect(cx - R, cy - R, cx + R, cy + R), P('#000', 1, shader=rad(cx, cy, R * 1.1, [('#94a79a', .55 * (.6 + .4 * open_amt), 0), ('#33483e', .5, .5), ('#050808', 1, 1)])))
    else:
        c.drawPaint(P('#04070a'))
    # внутренние засовы проёма (за дверью)
    for i in range(8):
        ang = i * math.pi / 4 + .39
        x, y = cx + math.cos(ang) * R * .98, cy + math.sin(ang) * R * .98
        c.save(); c.translate(x, y); c.rotate(math.degrees(ang))
        out = (1 - bolts) * R * .09
        c.drawRect(rect(-R * .11 - out, -R * .05, R * .03, R * .05), P('#46524d'))
        c.restore()
    c.restore()
    # полотно двери
    k = math.cos(open_amt * 1.25)  # сжатие по x при открытии
    k = max(k, 0.07)
    hinge = cx - R
    lcx = hinge + R * k
    c.save()
    c.translate(lcx, cy); c.scale(k, 1)
    leaf = oval_path(0, 0, R, R)
    c.drawPath(leaf, P('#1a2220'))
    c.save(); c.clipPath(leaf, doAntiAlias=True)
    c.drawRect(rect(-R, -R, R, R), P('#6f7d77', 1, shader=tex_shader('metal', 1.4, 0, 0)))
    c.drawRect(rect(-R, -R, R, R), P('#26302d', .72))
    # ржавчина
    c.drawRect(rect(-R, -R, R, R), P('#7a3a14', .5, shader=tex_shader('rust', 1.6, 60, 40)))
    # объём: свет сверху-слева, тень справа-снизу
    c.drawRect(rect(-R, -R, R, R), P('#000', 1, shader=lin(-R, -R, R, R, [('#ffffff', .14 * light, 0), ('#000000', 0, .45), ('#000000', .72, 1)])))
    # кольца
    for rr, w, a in [(.93, .035, .85), (.80, .02, .6), (.52, .03, .7)]:
        c.drawCircle(0, 0, R * rr, P('#05080a', a, 'stroke', R * w))
        c.drawCircle(-R * .008, -R * .012, R * rr, P('#8fa299', .22, 'stroke', R * w * .35))
    # панели-накладки
    for i in range(8):
        a0 = i * 45 + 22.5
        c.save(); c.rotate(a0)
        c.drawRect(rect(R * .56, -R * .012, R * .79, R * .012), P('#05080a', .7))
        c.restore()
    rivets(c, 0, 0, R * .87, 16, R * .024, '#7d8d87')
    # потёки
    for i in range(9):
        sx = -R * .8 + i * R * .2 + noise1(i * 3.1, 5) * R * .1
        ln = R * (.25 + noise1(i * 1.7, 9) * .6)
        c.drawRect(rect(sx, -R * .6 + noise1(i, 3) * R * .3, sx + R * .014, -R * .6 + noise1(i, 3) * R * .3 + ln), P('#3a1a08', .35))
    c.restore()
    # штурвал
    c.save(); c.rotate(wheel)
    wr = R * .27
    c.drawCircle(R * .02, R * .03, wr, P('#000', .45, 'stroke', R * .06, blur=5))
    for i in range(6):
        c.save(); c.rotate(i * 60)
        c.drawRect(rect(-R * .02, -wr, R * .02, 0), P('#2b2f2c'))
        c.drawRect(rect(-R * .008, -wr, R * .004, 0), P('#7d756a', .8))
        c.restore()
    c.drawCircle(0, 0, wr, P('#26211c', 1, 'stroke', R * .05))
    c.drawCircle(-R * .006, -R * .008, wr, P('#a0663a', .75, 'stroke', R * .016))
    c.drawCircle(0, 0, R * .075, P('#1a1d1c')); c.drawCircle(-R * .01, -R * .012, R * .055, P('#6c6f68'))
    c.restore()
    # блики лампы на полотне
    c.drawRect(rect(-R, -R, R, R), P(lamp, 1, shader=rad(-R * .1, -R * .98, R * 1.3, [(lamp, .28 * light, 0), (lamp, 0, 1)]), blend='add'))
    c.restore()
    c.drawPath(leaf, P('#000', .9, 'stroke', R * .02)) if False else None
    c.restore()
    # тень двери на проём при открытии
    # индикатор над дверью
    ic = closed_ind or lamp
    c.drawRoundRect(rect(cx - R * .16, cy - R * 1.36, cx + R * .16, cy - R * 1.2), R * .03, R * .03, P('#050708'))
    c.drawCircle(cx, cy - R * 1.28, R * .05, P(ic, .95))
    glow(c, cx, cy - R * 1.28, R * .5, ic, .55)

def airlock(c, t, hor=860, fw=380, fh=540, lamp=GREEN, flick=0.0, door_open=0.0, wheel=0.0, alarm=False,
            dust=True, behind=None, light=1.0, door_ind=None, rumble=0.0, ash=False):
    at, (FL, FR, FT, FB) = persp(hor, fw, fh)
    fl = 1 - flick * (1 - noise1(t * 22.0, 7)) if flick else 1.0
    c.drawPaint(P('#020405'))
    # дальняя стена
    wall = poly([(FL, FT), (FR, FT), (FR, FB), (FL, FB)])
    texture_fill(c, wall, '#22342e', 'concrete', .5, .8)
    # стены
    nl, nr, nt, nb = at(0); 
    cols = {'left': poly([(nl, nt), (FL, FT), (FL, FB), (nl, nb)]), 'right': poly([(nr, nt), (FR, FT), (FR, FB), (nr, nb)]),
            'ceil': poly([(nl, nt), (nr, nt), (FR, FT), (FL, FT)]), 'floor': poly([(nl, nb), (nr, nb), (FR, FB), (FL, FB)])}
    for name, base in [('left', '#1b2a26'), ('right', '#1b2a26'), ('ceil', '#0d1613'), ('floor', '#0f1a1c')]:
        texture_fill(c, cols[name], base, 'concrete', .9 if name in 'leftright' else 1.1, .55, ox=hash1(len(name)) * 90)
    # швы панелей
    for i in range(1, 9):
        u = 1 - 0.80 ** i * 1.0
        u = clamp(u * 1.08 - .05, 0, 1)
        l, r, tp, bt = at(u)
        for (x0, y0, x1, y1) in [(l, tp, l, bt), (r, tp, r, bt)]:
            c.drawLine(x0, y0, x1, y1, P('#000', .55 * (1 - u * .4), 'stroke', 3 + 7 * (1 - u)))
        c.drawLine(l, tp, r, tp, P('#000', .5, 'stroke', 2 + 6 * (1 - u)))
        c.drawLine(l, bt, r, bt, P('#000', .4, 'stroke', 2 + 5 * (1 - u)))
    # потёки на стенах
    for side in (0, 1):
        for i in range(16):
            u = noise1(i * 5.3 + side * 9, 2) * .95
            l, r, tp, bt = at(u)
            x = l if side == 0 else r
            h = (bt - tp) * (.12 + .5 * noise1(i * 2.2, 8)); y0 = tp + (bt - tp) * .12 * noise1(i, 4)
            w = 4 + 10 * (1 - u)
            xx = x + (1 if side == 0 else -1) * (8 + 70 * (1 - u) * noise1(i * 1.3, 6))
            c.drawRect(rect(xx, y0, xx + w, y0 + h), P('#02070a', .35, blur=3))
    # трубы вдоль потолка
    for off, rr in [(.1, 22), (.16, 14)]:
        for side in (0, 1):
            x0 = lerp(nl, nr, off if side == 0 else 1 - off) if False else None
        # левая/правая трубы
    for sgn in (-1, 1):
        for k, (yo, rr, colr) in enumerate([(.07, 26, '#26322e'), (.14, 15, '#3a2a1e')]):
            def pt(u):
                l, r, tp, bt = at(u)
                x = (l if sgn < 0 else r) - sgn * (r - l) * (.06 + k * .05)
                y = tp + (bt - tp) * yo
                return x, y, rr * (1 - u * .85)
            pts = [pt(u / 10) for u in range(0, 11)]
            pa = skia.Path(); pa.moveTo(pts[0][0], pts[0][1])
            for p_ in pts[1:]: pa.lineTo(p_[0], p_[1])
            c.drawPath(pa, P('#000', .8, 'stroke', pts[0][2] * 2 + 4))
            c.drawPath(pa, P(colr, 1, 'stroke', pts[0][2] * 2))
            c.drawPath(pa, P('#fff', .08, 'stroke', pts[0][2] * .5))
    # пол: лужа-отражение
    # дверь
    dcx, dcy = W / 2, (FT + FB) / 2 + 6
    R = min(fw, fh) * .4
    door(c, dcx, dcy, R, t, door_open, wheel, lamp=lamp, light=light * fl, closed_ind=door_ind, behind=behind)
    # лампы в потолке
    lamps = []
    for i, u in enumerate([.08, .38, .62, .78]):
        l, r, tp, bt = at(u)
        x, y = W / 2, tp + (bt - tp) * .015
        sz = lerp(46, 10, u)
        lamps.append((x, y, sz, u))
    for (x, y, sz, u) in lamps:
        c.drawRoundRect(rect(x - sz * 1.3, y - sz * .3, x + sz * 1.3, y + sz * .7), sz * .2, sz * .2, P('#070a0a'))
        c.drawRoundRect(rect(x - sz, y, x + sz, y + sz * .5), sz * .15, sz * .15, P(lamp, .95 * fl))
        glow(c, x, y + sz * .3, sz * 7 * (1 - u * .4), lamp, .32 * fl * light)
        # пятно на полу
        l, r, tp, bt = at(u)
        glow_ell(c, x, bt - (bt - tp) * .02, sz * 6, sz * 1.6, lamp, .28 * fl * light)
    # настенные лампы
    for sgn in (-1, 1):
        for u in (.2, .5):
            l, r, tp, bt = at(u)
            x = (l if sgn < 0 else r) - sgn * 8; y = tp + (bt - tp) * .3
            sz = lerp(30, 8, u)
            c.drawCircle(x, y, sz * .7, P(lamp, .9 * fl))
            glow(c, x, y, sz * 7, lamp, .3 * fl * light)
    # световая дымка у двери
    glow(c, dcx, dcy, 480, lamp, .16 * light * fl)
    glow_ell(c, dcx, FB + 80, 520, 160, lamp, .16 * light)
    # лёгкий туман
    c.drawRect(rect(0, 0, W, H), P('#000', 1, shader=rad(W / 2, hor, 1100, [('#000000', 0, 0), ('#000000', .0, .35), ('#000000', .78, 1)])))
    c.drawRect(rect(0, 0, W, H), P('#000', 1, shader=rad(W / 2, hor, 700, [('#2a5a45', .07, 0), ('#2a5a45', 0, 1)]), blend='add'))
    # сигнальный маяк
    if alarm:
        ph = (math.sin(t * 7.5) + 1) / 2
        c.drawRect(rect(0, 0, W, H), P(ORANGE, 1, shader=rad(W / 2, 180, 1300, [(ORANGE, .38 * ph, 0), (ORANGE, 0, 1)]), blend='add'))
        for sgn in (-1, 1):
            l, r, tp, bt = at(.15)
            x = (l if sgn < 0 else r) - sgn * 10; y = tp + (bt - tp) * .2
            c.drawCircle(x, y, 18, P(ORANGE, .5 + .5 * ph)); glow(c, x, y, 360, ORANGE, .55 * ph)
    # пыль
    if dust:
        for i in range(70):
            sp = .02 + hash1(i * 3.3) * .05
            x = (hash1(i * 7.7) * W + math.sin(t * .6 + i) * 26 + t * 8 * (hash1(i) - .5) * 4) % W
            y = (hash1(i * 5.1) * H + t * 22 * (.3 + hash1(i * 1.9))) % H
            c.drawCircle(x, y, 1.2 + hash1(i * 2.3) * 2.2, P('#c8e8d6', .05 + .18 * hash1(i * 9.9)))
    if rumble:
        pass
