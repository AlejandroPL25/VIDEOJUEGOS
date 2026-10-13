#!/usr/bin/env python3
"""
Generador de assets en pixel art para "Embra: La Llama Eterna".
Todo el arte es original y se dibuja por código (Pillow), así que no hay problemas de licencia
y se puede regenerar o ajustar cambiando paletas/parámetros.
Uso:  python3 tools/make_assets.py
Salida: assets/sprites/*.png
"""
import math
import os
from PIL import Image, ImageDraw

OUT = os.path.join(os.path.dirname(__file__), "..", "assets", "sprites")
os.makedirs(OUT, exist_ok=True)

def hexc(h, a=255):
    h = h.lstrip("#")
    return (int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16), a)

# ---------- Paleta global ----------
OUTLINE = hexc("#2b1320")
RED = hexc("#c8323c")
ORANGE = hexc("#f4733a")
YELLOW = hexc("#ffc93c")
LIGHT = hexc("#fff1b0")
WHITE = hexc("#ffffff")
CLEAR = (0, 0, 0, 0)

def new(w, h):
    return Image.new("RGBA", (w, h), CLEAR)

def outline(img, color=OUTLINE):
    """Agrega contorno de 1 px alrededor de los píxeles opacos (vecindad 4)."""
    w, h = img.size
    px = img.load()
    src = [[px[x, y][3] > 0 for x in range(w)] for y in range(h)]
    for y in range(h):
        for x in range(w):
            if not src[y][x]:
                for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                    nx, ny = x + dx, y + dy
                    if 0 <= nx < w and 0 <= ny < h and src[ny][nx]:
                        px[x, y] = color
                        break
    return img

def save(img, name):
    img.save(os.path.join(OUT, name))

# ======================================================================
#  EMBRA (protagonista): brasa viva con corona de llama
# ======================================================================
def embra_frame(flame=0, bob=0, legs=0, squash=0, eyes="open", tint=None, tuck=False):
    img = new(16, 16)
    d = ImageDraw.Draw(img)
    cx, cy = 8, 10 + bob
    rx, ry = 5.2 + squash * 0.6, 5.2 - squash * 0.6
    for y in range(16):
        for x in range(16):
            dx, dy = (x + 0.5 - cx) / rx, (y + 0.5 - cy) / ry
            if dx * dx + dy * dy <= 1.0:
                col = ORANGE
                if dy > 0.35:
                    col = RED
                elif dx < -0.2 and dy < 0:
                    col = YELLOW
                img.putpixel((x, y), col)
    # llama (corona)
    tipx = 8 + flame
    top = max(0, 1 + bob)
    d.polygon([(5, 7 + bob), (6, 4 + bob), (6 + (flame > 0), 3 + bob), (tipx, top),
               (10 - (flame < 0), 3 + bob), (10, 4 + bob), (11, 7 + bob)], fill=RED)
    d.polygon([(6, 7 + bob), (7, 4 + bob), (tipx, top + 2), (9, 4 + bob), (10, 7 + bob)], fill=ORANGE)
    d.polygon([(7, 7 + bob), (tipx, top + 3), (9, 7 + bob)], fill=YELLOW)
    # ojos
    ey = 9 + bob
    if eyes == "open":
        for ex in (5, 9):
            d.rectangle([ex, ey, ex + 1, ey + 2], fill=OUTLINE)
            img.putpixel((ex, ey), WHITE)
    elif eyes == "wide":
        for ex in (5, 9):
            d.rectangle([ex, ey - 1, ex + 1, ey + 2], fill=OUTLINE)
            img.putpixel((ex, ey - 1), WHITE)
    elif eyes == "x":
        for ex in (5, 9):
            img.putpixel((ex, ey), OUTLINE); img.putpixel((ex + 1, ey + 1), OUTLINE)
            img.putpixel((ex + 1, ey), OUTLINE); img.putpixel((ex, ey + 1), OUTLINE)
    # piernas
    if tuck:
        d.rectangle([5, 14, 6, 15], fill=RED); d.rectangle([9, 14, 10, 15], fill=RED)
    else:
        l1 = 4 + legs; l2 = 10 - legs
        d.rectangle([l1, 14, l1 + 2, 15], fill=RED)
        d.rectangle([l2, 14, l2 + 2, 15], fill=RED)
    outline(img)
    if tint:
        px = img.load()
        for y in range(16):
            for x in range(16):
                r, g, b, a = px[x, y]
                if a:
                    px[x, y] = (min(255, r + tint), min(255, g + tint), min(255, b + tint), a)
    return img

def make_embra():
    frames = [
        embra_frame(flame=0, legs=0),            # 0 idle A
        embra_frame(flame=1, legs=0, bob=1),     # 1 idle B
        embra_frame(flame=-1, legs=-1, bob=0),   # 2 run 1
        embra_frame(flame=1, legs=0, bob=-1),    # 3 run 2
        embra_frame(flame=-1, legs=1, bob=0),    # 4 run 3
        embra_frame(flame=1, legs=0, bob=-1),    # 5 run 4
        embra_frame(flame=0, squash=-1.2, tuck=True, eyes="wide"),   # 6 jump (estirado)
        embra_frame(flame=-1, squash=0.6, tuck=True, eyes="wide"),   # 7 fall
        embra_frame(flame=0, eyes="x", tint=70),                      # 8 hurt
    ]
    sheet = new(16 * len(frames), 16)
    for i, f in enumerate(frames):
        sheet.paste(f, (16 * i, 0))
    save(sheet, "embra_sheet.png")

# ======================================================================
#  ENEMIGOS
# ======================================================================
def escarchin(squash=0):
    """Babosa de hielo (patrulla)."""
    img = new(16, 16)
    d = ImageDraw.Draw(img)
    cx, cy = 8, 11
    rx, ry = 6.5 + squash, 4.8 - squash * 0.8
    for y in range(16):
        for x in range(16):
            dx, dy = (x + 0.5 - cx) / rx, (y + 0.5 - cy) / ry
            if dx * dx + dy * dy <= 1.0:
                col = hexc("#8fd3ff")
                if dy > 0.3:
                    col = hexc("#3a86c8")
                elif dx < -0.25 and dy < -0.1:
                    col = hexc("#e8f8ff")
                img.putpixel((x, y), col)
    # picos de hielo
    d.polygon([(4, 7), (5, 3), (7, 7)], fill=hexc("#cfeeff"))
    d.polygon([(8, 7), (10, 2), (12, 7)], fill=hexc("#cfeeff"))
    # ojos enojados
    d.rectangle([5, 9, 6, 11], fill=OUTLINE); d.rectangle([9, 9, 10, 11], fill=OUTLINE)
    img.putpixel((5, 9), WHITE); img.putpixel((9, 9), WHITE)
    d.line([(4, 8), (6, 9)], fill=OUTLINE); d.line([(11, 8), (9, 9)], fill=OUTLINE)
    outline(img)
    return img

def humoro(wing=0):
    """Fantasma de humo (vuela)."""
    img = new(16, 16)
    d = ImageDraw.Draw(img)
    d.ellipse([3, 3, 12, 11], fill=hexc("#aab0b8"))
    d.ellipse([4, 4, 9, 8], fill=hexc("#d7dbe0"))
    # cola ondulada
    d.polygon([(3, 9), (4, 14), (6, 12), (8, 15), (10, 12), (12, 14), (12, 9)], fill=hexc("#7e848c"))
    # alas
    wy = 4 + wing * 3
    d.polygon([(0, 6 + wing), (3, 6), (3, 9)], fill=hexc("#6a7078"))
    d.polygon([(15, 6 + wing), (12, 6), (12, 9)], fill=hexc("#6a7078"))
    d.rectangle([5, 6, 6, 7], fill=hexc("#ff3b3b")); d.rectangle([9, 6, 10, 7], fill=hexc("#ff3b3b"))
    outline(img)
    return img

def gelido(open_mouth=False, hurt=False):
    """Jefe: Gélido, el Rey de Escarcha (32x32)."""
    img = new(32, 32)
    d = ImageDraw.Draw(img)
    ice = hexc("#8fd3ff") if not hurt else hexc("#ffd6d6")
    ice2 = hexc("#3a86c8") if not hurt else hexc("#c86a6a")
    ice3 = hexc("#e8f8ff")
    # capa / cuerpo
    d.polygon([(6, 30), (9, 14), (23, 14), (26, 30)], fill=ice2)
    d.polygon([(9, 30), (11, 15), (21, 15), (23, 30)], fill=ice)
    # brazos
    d.polygon([(2, 22), (8, 16), (10, 20), (5, 26)], fill=ice)
    d.polygon([(30, 22), (24, 16), (22, 20), (27, 26)], fill=ice)
    # cabeza
    d.rectangle([10, 5, 21, 15], fill=ice3)
    d.rectangle([10, 12, 21, 15], fill=ice)
    # corona
    for x in (10, 14, 18):
        d.polygon([(x, 6), (x + 2, 0), (x + 4, 6)], fill=hexc("#ffe27a"))
    # ojos y boca
    d.rectangle([12, 8, 14, 10], fill=hexc("#ff3b3b")); d.rectangle([17, 8, 19, 10], fill=hexc("#ff3b3b"))
    if open_mouth:
        d.rectangle([14, 12, 18, 14], fill=OUTLINE)
    else:
        d.line([(13, 13), (19, 13)], fill=OUTLINE)
    # cristales del pecho
    d.polygon([(14, 20), (16, 17), (18, 20), (16, 25)], fill=ice3)
    outline(img)
    return img

def make_enemies():
    sheet = new(32, 16)
    sheet.paste(escarchin(0), (0, 0)); sheet.paste(escarchin(1), (16, 0))
    save(sheet, "escarchin_sheet.png")
    sheet = new(32, 16)
    sheet.paste(humoro(0), (0, 0)); sheet.paste(humoro(1), (16, 0))
    save(sheet, "humoro_sheet.png")
    sheet = new(96, 32)
    sheet.paste(gelido(False), (0, 0)); sheet.paste(gelido(True), (32, 0)); sheet.paste(gelido(False, True), (64, 0))
    save(sheet, "gelido_sheet.png")

# ======================================================================
#  TILES (2 columnas × 4 filas: [superficie, interior] por zona)
# ======================================================================
def noise(seed):
    s = seed
    def r():
        nonlocal s
        s = (s * 1103515245 + 12345) & 0x7FFFFFFF
        return s / 0x7FFFFFFF
    return r

def tile_base(top_col, mid_col, dark_col, seed, with_top, speck):
    t = new(16, 16)
    r = noise(seed)
    for y in range(16):
        for x in range(16):
            t.putpixel((x, y), mid_col)
    for _ in range(26):
        x, y = int(r() * 16), int(r() * 16)
        t.putpixel((x, y), dark_col if r() < 0.6 else speck)
    if with_top:
        for x in range(16):
            for y in range(0, 4):
                t.putpixel((x, y), top_col)
            if r() < 0.5:
                t.putpixel((x, 4), top_col)
            t.putpixel((x, 3 if r() < 0.5 else 4), dark_col)
    return t

def brick_tile(base, line, seed, with_top, top_col):
    t = new(16, 16)
    r = noise(seed)
    for y in range(16):
        for x in range(16):
            t.putpixel((x, y), base)
    for y in (0, 5, 10, 15):
        for x in range(16):
            t.putpixel((x, y), line)
    for row, y0 in enumerate((0, 5, 10)):
        off = 0 if row % 2 == 0 else 4
        for bx in range(off, 16, 8):
            for y in range(y0, y0 + 5):
                t.putpixel((bx % 16, y), line)
    for _ in range(14):
        t.putpixel((int(r() * 16), int(r() * 16)), top_col if r() < 0.4 else line)
    if with_top:
        for x in range(16):
            for y in range(0, 3):
                t.putpixel((x, y), top_col)
    return t

def make_tiles():
    sheet = new(32, 64)
    zonas = [
        # 0: Bosque de Ceniza
        (tile_base(hexc("#7a8a6a"), hexc("#4a3b4f"), hexc("#362a3b"), 11, True, hexc("#6b5a70")),
         tile_base(hexc("#7a8a6a"), hexc("#4a3b4f"), hexc("#362a3b"), 12, False, hexc("#6b5a70"))),
        # 1: Cuevas de Escarcha
        (tile_base(hexc("#e8f8ff"), hexc("#4f8fc9"), hexc("#356da0"), 21, True, hexc("#a9dcff")),
         tile_base(hexc("#e8f8ff"), hexc("#4f8fc9"), hexc("#356da0"), 22, False, hexc("#a9dcff"))),
        # 2: Ruinas de Humo
        (brick_tile(hexc("#6d6a73"), hexc("#3f3c45"), 31, True, hexc("#8e8a96")),
         brick_tile(hexc("#6d6a73"), hexc("#3f3c45"), 32, False, hexc("#8e8a96"))),
        # 3: Fortaleza Gélida
        (brick_tile(hexc("#3d5a8a"), hexc("#27365a"), 41, True, hexc("#a9dcff")),
         brick_tile(hexc("#3d5a8a"), hexc("#27365a"), 42, False, hexc("#a9dcff"))),
    ]
    for row, (top, inner) in enumerate(zonas):
        sheet.paste(top, (0, row * 16))
        sheet.paste(inner, (16, row * 16))
    save(sheet, "tiles.png")

    # púas (una por zona, 4 en fila)
    sp = new(64, 16)
    colores = ["#b9c0c9", "#e8f8ff", "#c9c4d0", "#a9dcff"]
    for i, c in enumerate(colores):
        t = new(16, 16)
        d = ImageDraw.Draw(t)
        for x0 in (0, 5, 10):
            d.polygon([(x0, 15), (x0 + 3, 6), (x0 + 6, 15)], fill=hexc(c))
        outline(t)
        sp.paste(t, (i * 16, 0))
    save(sp, "spikes.png")

# ======================================================================
#  OBJETOS
# ======================================================================
def make_items():
    # chispas (2 frames de brillo) 8x8
    sheet = new(16, 8)
    for i in range(2):
        t = new(8, 8)
        d = ImageDraw.Draw(t)
        c = (3, 3)
        arm = 3 if i == 0 else 2
        d.line([(c[0], c[1] - arm), (c[0], c[1] + arm)], fill=YELLOW)
        d.line([(c[0] - arm, c[1]), (c[0] + arm, c[1])], fill=YELLOW)
        d.rectangle([2, 2, 4, 4], fill=LIGHT)
        t.putpixel((3, 3), WHITE)
        outline(t)
        sheet.paste(t, (8 * i, 0))
    save(sheet, "spark.png")

    # corazón (vida extra) 10x10
    t = new(10, 10)
    d = ImageDraw.Draw(t)
    d.ellipse([0, 1, 5, 6], fill=hexc("#ff4d6d")); d.ellipse([4, 1, 9, 6], fill=hexc("#ff4d6d"))
    d.polygon([(0, 5), (9, 5), (5, 9)], fill=hexc("#ff4d6d"))
    t.putpixel((2, 2), WHITE)
    outline(t)
    save(t, "heart.png")

    # brasero (checkpoint): apagado / encendido 16x24
    sheet = new(32, 24)
    for i, lit in enumerate((False, True)):
        t = new(16, 24)
        d = ImageDraw.Draw(t)
        d.rectangle([7, 12, 8, 22], fill=hexc("#5b4a42"))
        d.polygon([(2, 8), (13, 8), (11, 13), (4, 13)], fill=hexc("#7b6a60"))
        d.rectangle([3, 22, 12, 23], fill=hexc("#5b4a42"))
        if lit:
            d.polygon([(4, 8), (5, 3), (7, 5), (8, 0), (10, 5), (11, 3), (12, 8)], fill=ORANGE)
            d.polygon([(6, 8), (8, 3), (10, 8)], fill=YELLOW)
        else:
            d.polygon([(5, 8), (8, 5), (11, 8)], fill=hexc("#4a4a50"))
        outline(t)
        sheet.paste(t, (16 * i, 0))
    save(sheet, "checkpoint.png")

    # Hoguera Eterna (meta): apagada / encendida 24x24
    sheet = new(48, 24)
    for i, lit in enumerate((False, True)):
        t = new(24, 24)
        d = ImageDraw.Draw(t)
        d.polygon([(2, 23), (4, 14), (20, 14), (22, 23)], fill=hexc("#6d6a73"))
        d.rectangle([4, 12, 19, 14], fill=hexc("#8e8a96"))
        d.rectangle([7, 8, 16, 12], fill=hexc("#4f3b2e"))
        if lit:
            d.polygon([(6, 12), (8, 4), (10, 7), (12, 0), (14, 7), (16, 4), (18, 12)], fill=RED)
            d.polygon([(8, 12), (10, 6), (12, 2), (14, 6), (16, 12)], fill=ORANGE)
            d.polygon([(10, 12), (12, 5), (14, 12)], fill=YELLOW)
        else:
            d.polygon([(8, 8), (12, 5), (16, 8)], fill=hexc("#3a3a40"))
        outline(t)
        sheet.paste(t, (24 * i, 0))
    save(sheet, "hearth.png")

    # bola de fuego 8x8 (2 frames)
    sheet = new(16, 8)
    for i in range(2):
        t = new(8, 8)
        d = ImageDraw.Draw(t)
        d.ellipse([1, 1, 6, 6], fill=ORANGE)
        d.ellipse([2, 2, 5, 5], fill=YELLOW)
        t.putpixel((3 + i, 3), WHITE)
        d.polygon([(0, 3), (2, 2), (2, 5)], fill=RED)
        outline(t)
        sheet.paste(t, (8 * i, 0))
    save(sheet, "fireball.png")

    # astilla de hielo 8x8
    t = new(8, 8)
    d = ImageDraw.Draw(t)
    d.polygon([(0, 4), (5, 1), (7, 4), (5, 6)], fill=hexc("#cfeeff"))
    d.line([(1, 4), (6, 4)], fill=hexc("#6ec6ff"))
    outline(t)
    save(t, "iceshard.png")

    # partículas: punto suave 6x6
    t = new(6, 6)
    for y in range(6):
        for x in range(6):
            dd = math.hypot(x - 2.5, y - 2.5)
            if dd < 2.9:
                a = int(255 * max(0.0, 1 - dd / 3.0))
                t.putpixel((x, y), (255, 255, 255, a))
    save(t, "particle.png")

    # letrero 16x16
    t = new(16, 16)
    d = ImageDraw.Draw(t)
    d.rectangle([7, 9, 8, 15], fill=hexc("#6b4a2e"))
    d.rectangle([1, 2, 14, 9], fill=hexc("#a8794a"))
    d.line([(3, 4), (12, 4)], fill=hexc("#6b4a2e")); d.line([(3, 7), (10, 7)], fill=hexc("#6b4a2e"))
    outline(t)
    save(t, "sign.png")

    # corazones/chispa UI 8x8 (icono de chispa) ya es spark; icono de vida = heart

# ======================================================================
#  DECORACIÓN y FONDOS
# ======================================================================
def make_decor():
    # árbol de ceniza 32x48
    t = new(32, 48)
    d = ImageDraw.Draw(t)
    d.rectangle([14, 20, 17, 47], fill=hexc("#3a2f3f"))
    for (x, y, r) in [(16, 12, 11), (8, 20, 8), (24, 20, 8), (16, 24, 8)]:
        d.ellipse([x - r, y - r, x + r, y + r], fill=hexc("#554a5c"))
    for (x, y, r) in [(13, 9, 5), (22, 18, 4)]:
        d.ellipse([x - r, y - r, x + r, y + r], fill=hexc("#6c6074"))
    outline(t)
    t.save(os.path.join(OUT, "decor_0.png"))
    # cristal 16x28
    t = new(16, 28)
    d = ImageDraw.Draw(t)
    d.polygon([(1, 27), (4, 8), (7, 27)], fill=hexc("#7cc4f5"))
    d.polygon([(6, 27), (9, 0), (13, 27)], fill=hexc("#a9dcff"))
    d.polygon([(9, 27), (12, 12), (15, 27)], fill=hexc("#4f8fc9"))
    d.line([(9, 2), (9, 24)], fill=hexc("#e8f8ff"))
    outline(t)
    t.save(os.path.join(OUT, "decor_1.png"))
    # pilar en ruinas 16x48
    t = new(16, 48)
    d = ImageDraw.Draw(t)
    d.rectangle([2, 6, 13, 47], fill=hexc("#5d5a63"))
    d.rectangle([0, 0, 15, 6], fill=hexc("#77737d"))
    for y in range(10, 47, 8):
        d.line([(2, y), (13, y)], fill=hexc("#3f3c45"))
    d.polygon([(2, 20), (7, 26), (4, 34)], fill=hexc("#3f3c45"))
    outline(t)
    t.save(os.path.join(OUT, "decor_2.png"))
    # estandarte de la fortaleza 16x40
    t = new(16, 40)
    d = ImageDraw.Draw(t)
    d.rectangle([0, 0, 15, 3], fill=hexc("#27365a"))
    d.polygon([(1, 3), (14, 3), (14, 34), (7, 39), (1, 34)], fill=hexc("#3d5a8a"))
    d.polygon([(7, 10), (8, 8), (9, 10), (8, 16)], fill=hexc("#cfeeff"))
    outline(t)
    t.save(os.path.join(OUT, "decor_3.png"))

def lerp(a, b, t):
    return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))

def make_backgrounds():
    W, H = 480, 270
    cfg = [
        # (cielo arriba, cielo abajo, lejos, cerca, brasas)
        ("#2a2038", "#6b3f5a", "#3a2c48", "#2a2038", "#ffb35a"),
        ("#0f2a4a", "#2c6aa8", "#1f4a7c", "#173a63", "#e8f8ff"),
        ("#26262e", "#5e4a4a", "#3a3640", "#2a2730", "#ff9a52"),
        ("#0b1230", "#2a3f7a", "#1c2a58", "#121c42", "#cfeeff"),
    ]
    for i, (c1, c2, far, near, spark) in enumerate(cfg):
        # cielo
        sky = Image.new("RGBA", (W, H))
        a, b = hexc(c1)[:3], hexc(c2)[:3]
        d = ImageDraw.Draw(sky)
        for y in range(H):
            d.line([(0, y), (W, y)], fill=lerp(a, b, y / H) + (255,))
        r = noise(100 + i)
        for _ in range(70):
            x, y = int(r() * W), int(r() * H * 0.8)
            d.point((x, y), fill=hexc(spark, 200))
        sky.save(os.path.join(OUT, f"bg_sky_{i}.png"))
        # montañas lejanas (tileables horizontalmente)
        far_img = new(W, H)
        d = ImageDraw.Draw(far_img)
        pts = [(0, H)]
        for x in range(0, W + 1, 4):
            y = 150 + 28 * math.sin(2 * math.pi * x / W * 2) + 14 * math.sin(2 * math.pi * x / W * 5 + i)
            pts.append((x, y))
        pts.append((W, H))
        d.polygon(pts, fill=hexc(far))
        far_img.save(os.path.join(OUT, f"bg_far_{i}.png"))
        # siluetas cercanas
        near_img = new(W, H)
        d = ImageDraw.Draw(near_img)
        pts = [(0, H)]
        for x in range(0, W + 1, 4):
            y = 205 + 12 * math.sin(2 * math.pi * x / W * 3 + 1) + 6 * math.sin(2 * math.pi * x / W * 8)
            pts.append((x, y))
        pts.append((W, H))
        d.polygon(pts, fill=hexc(near))
        # adornos de silueta según zona
        for k in range(8):
            bx = int((k + 0.5) * W / 8)
            if i == 0:   # árboles
                d.rectangle([bx - 2, 175, bx + 2, 215], fill=hexc(near))
                d.ellipse([bx - 12, 152, bx + 12, 182], fill=hexc(near))
            elif i == 1 or i == 3:  # cristales / torres
                d.polygon([(bx - 8, 215), (bx, 160 - (k % 3) * 8), (bx + 8, 215)], fill=hexc(near))
            else:        # columnas
                d.rectangle([bx - 6, 170 + (k % 2) * 10, bx + 6, 215], fill=hexc(near))
        near_img.save(os.path.join(OUT, f"bg_near_{i}.png"))

# ======================================================================
#  LOGO (fuente 5x7 propia para no depender de fuentes del sistema)
# ======================================================================
GLYPHS = {
    "E": ["#####", "#....", "#....", "####.", "#....", "#....", "#####"],
    "M": ["#...#", "##.##", "#.#.#", "#.#.#", "#...#", "#...#", "#...#"],
    "B": ["####.", "#...#", "#...#", "####.", "#...#", "#...#", "####."],
    "R": ["####.", "#...#", "#...#", "####.", "#.#..", "#..#.", "#...#"],
    "A": [".###.", "#...#", "#...#", "#####", "#...#", "#...#", "#...#"],
}

def make_logo():
    scale = 6
    word = "EMBRA"
    w = (5 * len(word) + (len(word) - 1)) * scale
    h = 7 * scale
    img = new(w + 8, h + 8)
    px = img.load()
    x0 = 4
    for ch in word:
        g = GLYPHS[ch]
        for gy, row in enumerate(g):
            for gx, c in enumerate(row):
                if c == "#":
                    col = YELLOW if gy < 2 else (ORANGE if gy < 5 else RED)
                    for sy in range(scale):
                        for sx in range(scale):
                            px[x0 + gx * scale + sx, 4 + gy * scale + sy] = col
        x0 += 6 * scale
    # contorno grueso
    base = img.copy()
    for _ in range(2):
        outline(base)
    save(base, "logo.png")

def main():
    make_embra()
    make_enemies()
    make_tiles()
    make_items()
    make_decor()
    make_backgrounds()
    make_logo()
    print("Assets generados en", os.path.abspath(OUT))

if __name__ == "__main__":
    main()
