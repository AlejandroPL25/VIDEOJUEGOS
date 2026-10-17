#!/usr/bin/env python3
"""
Generador de assets en pixel art de "EMBRA: Bosque de Brasas".
Sigue el GDD (Fase 2): paleta ámbar/fuego sobre fondos nocturnos, plataformas frías y detalles frescos,
y el boceto de Embra (cuerpo rectangular redondeado ámbar, llama triangular, ojos ovalados,
brazos delgados y piernas turquesa). Todo el arte es original y se dibuja por código (Pillow).
Uso:  python3 tools/make_assets.py   ->  assets/sprites/*.png
"""
import math
import os
from PIL import Image, ImageDraw

OUT = os.path.join(os.path.dirname(__file__), "..", "assets", "sprites")
os.makedirs(OUT, exist_ok=True)

def hexc(h, a=255):
    h = h.lstrip("#")
    return (int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16), a)

# ---------- Paleta del GDD ----------
NIGHT = hexc("#1B1F3B")     # fondo nocturno
SLATE = hexc("#2E3A59")     # plataformas
AMBER = hexc("#F4A62A")     # ámbar (personaje)
FIRE = hexc("#E8542A")      # fuego / peligro
CREAM = hexc("#FFF3C4")     # brillo / partículas
TEAL = hexc("#4CC9C0")      # detalles frescos
# tonos derivados (sombras y luces de la misma paleta)
NIGHT_D = hexc("#12152b")
SLATE_D = hexc("#222c45")
SLATE_L = hexc("#3d4d73")
AMBER_D = hexc("#c97f17")
FIRE_D = hexc("#b13a1c")
TEAL_D = hexc("#3a9c95")
CLEAR = (0, 0, 0, 0)

def new(w, h):
    return Image.new("RGBA", (w, h), CLEAR)

def outline(img, color):
    """Contorno de 1 px alrededor de los píxeles opacos (vecindad 4)."""
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

def noise(seed):
    s = seed
    def r():
        nonlocal s
        s = (s * 1103515245 + 12345) & 0x7FFFFFFF
        return s / 0x7FFFFFFF
    return r

# ======================================================================
#  EMBRA (16x20): sigue el boceto del GDD
# ======================================================================
def embra_frame(flame=0, bob=0, leg=0, arms="down", eyes="open", tuck=False, flash=False):
    W, H = 16, 20
    img = new(W, H)
    d = ImageDraw.Draw(img)
    by = 6 + bob                      # parte superior del cuerpo
    # llama triangular (fuego por fuera, brillo por dentro)
    tipx = 8 + flame
    d.polygon([(5, by), (tipx, max(0, by - 6 + (1 if flame else 0))), (10, by)], fill=FIRE)
    d.polygon([(6, by), (tipx, by - 3), (9, by)], fill=CREAM)
    # cuerpo: rectángulo redondeado ámbar
    d.rounded_rectangle([3, by, 12, by + 9], radius=2, fill=AMBER)
    d.rectangle([4, by + 8, 11, by + 9], fill=AMBER_D)       # sombra inferior
    d.line([(4, by + 1), (4, by + 5)], fill=hexc("#ffc45a"))   # luz lateral
    # brazos delgados
    if arms == "down":
        d.line([(2, by + 3), (1, by + 5)], fill=AMBER); d.line([(13, by + 3), (14, by + 5)], fill=AMBER)
    elif arms == "up":
        d.line([(2, by + 3), (1, by + 1)], fill=AMBER); d.line([(13, by + 3), (14, by + 1)], fill=AMBER)
    elif arms == "wide":
        d.line([(2, by + 3), (0, by + 4)], fill=AMBER); d.line([(13, by + 3), (15, by + 4)], fill=AMBER)
    elif arms == "swing_a":
        d.line([(2, by + 3), (1, by + 6)], fill=AMBER); d.line([(13, by + 3), (14, by + 3)], fill=AMBER)
    elif arms == "swing_b":
        d.line([(2, by + 3), (1, by + 3)], fill=AMBER); d.line([(13, by + 3), (14, by + 6)], fill=AMBER)
    # ojos ovalados oscuros
    ey = by + 3
    if eyes == "open":
        d.rectangle([5, ey, 6, ey + 2], fill=NIGHT); d.rectangle([9, ey, 10, ey + 2], fill=NIGHT)
    elif eyes == "wide":
        d.rectangle([5, ey - 1, 6, ey + 2], fill=NIGHT); d.rectangle([9, ey - 1, 10, ey + 2], fill=NIGHT)
    elif eyes == "x":
        for ex in (5, 9):
            img.putpixel((ex, ey), NIGHT); img.putpixel((ex + 1, ey + 1), NIGHT)
            img.putpixel((ex + 1, ey), NIGHT); img.putpixel((ex, ey + 1), NIGHT)
    # piernas turquesa
    ly = by + 10
    if tuck:
        d.rectangle([4, ly, 6, ly + 1], fill=TEAL); d.rectangle([9, ly, 11, ly + 1], fill=TEAL)
    else:
        l1 = ly + (1 if leg > 0 else 0)
        l2 = ly + (1 if leg < 0 else 0)
        d.rectangle([4, l1, 6, min(H - 1, ly + 3)], fill=TEAL)
        d.rectangle([9, l2, 11, min(H - 1, ly + 3)], fill=TEAL)
    outline(img, CREAM)
    if flash:
        px = img.load()
        for y in range(H):
            for x in range(W):
                r, g, b, a = px[x, y]
                if a:
                    px[x, y] = (min(255, r + 90), min(255, g + 90), min(255, b + 90), a)
    return img

def make_embra():
    frames = [
        embra_frame(flame=0, arms="down"),                               # 0 idle A
        embra_frame(flame=1, arms="down", bob=1),                         # 1 idle B
        embra_frame(flame=-1, arms="swing_a", leg=1),                     # 2 correr 1
        embra_frame(flame=1, arms="down", leg=0),                         # 3 correr 2
        embra_frame(flame=-1, arms="swing_b", leg=-1),                    # 4 correr 3
        embra_frame(flame=1, arms="down", leg=0),                         # 5 correr 4
        embra_frame(flame=0, arms="up", tuck=True, eyes="wide"),          # 6 salto
        embra_frame(flame=-1, arms="wide", tuck=True, eyes="wide"),       # 7 caída
        embra_frame(flame=0, arms="wide", eyes="x", flash=True),          # 8 herido
    ]
    sheet = new(16 * len(frames), 20)
    for i, f in enumerate(frames):
        sheet.paste(f, (16 * i, 0))
    save(sheet, "embra_sheet.png")

# ======================================================================
#  RONDÍN (enemigo): criatura de carbón con grietas de brasa
# ======================================================================
def rondin(step=0):
    img = new(16, 16)
    d = ImageDraw.Draw(img)
    carbon = hexc("#3a3d52")
    carbon_d = hexc("#262938")
    d.rounded_rectangle([2, 4, 13, 13], radius=3, fill=carbon)
    d.rectangle([3, 11, 12, 13], fill=carbon_d)
    d.polygon([(3, 5), (4, 1), (6, 4)], fill=carbon)                 # trozos de carbón
    d.polygon([(8, 4), (10, 0), (12, 5)], fill=carbon)
    d.line([(4, 8), (6, 9), (5, 11)], fill=FIRE_D)                   # grietas de brasa
    d.line([(11, 6), (10, 8), (12, 9)], fill=FIRE_D)
    d.rectangle([4, 6, 6, 8], fill=FIRE); d.rectangle([9, 6, 11, 8], fill=FIRE)   # ojos encendidos
    img.putpixel((5, 7), CREAM); img.putpixel((10, 7), CREAM)
    if step == 0:
        d.rectangle([3, 14, 5, 15], fill=carbon_d); d.rectangle([10, 14, 12, 15], fill=carbon_d)
    else:
        d.rectangle([4, 14, 6, 15], fill=carbon_d); d.rectangle([9, 14, 11, 15], fill=carbon_d)
    outline(img, FIRE)
    return img

def make_rondin():
    sheet = new(32, 16)
    sheet.paste(rondin(0), (0, 0)); sheet.paste(rondin(1), (16, 0))
    save(sheet, "rondin_sheet.png")

# ======================================================================
#  TILES (2 columnas × 4 filas: [superficie, interior] por zona)
# ======================================================================
def base_tile(body, dark, light, top, top_dark, seed, with_top, strata=False):
    t = new(16, 16)
    r = noise(seed)
    for y in range(16):
        for x in range(16):
            t.putpixel((x, y), body)
    for _ in range(24):
        x, y = int(r() * 16), int(r() * 16)
        t.putpixel((x, y), dark if r() < 0.6 else light)
    if strata:
        for y in (5, 11):
            for x in range(16):
                if r() < 0.8:
                    t.putpixel((x, y), dark)
    if with_top:
        for x in range(16):
            for y in range(0, 4):
                t.putpixel((x, y), top)
            if r() < 0.5:
                t.putpixel((x, 4), top)
            t.putpixel((x, 3 if r() < 0.5 else 4), top_dark)
    return t

def brick_tile(body, line, top, seed, with_top, accent=None):
    t = new(16, 16)
    r = noise(seed)
    for y in range(16):
        for x in range(16):
            t.putpixel((x, y), body)
    for y in (0, 5, 10, 15):
        for x in range(16):
            t.putpixel((x, y), line)
    for row, y0 in enumerate((0, 5, 10)):
        off = 0 if row % 2 == 0 else 4
        for bx in range(off, 16, 8):
            for y in range(y0, y0 + 5):
                t.putpixel((bx % 16, y), line)
    for _ in range(10):
        t.putpixel((int(r() * 16), int(r() * 16)), line)
    if accent:
        for _ in range(4):
            t.putpixel((int(r() * 16), int(r() * 16)), accent)
    if with_top:
        for x in range(16):
            for y in range(0, 3):
                t.putpixel((x, y), top)
    return t

def make_tiles():
    sheet = new(32, 64)
    zonas = [
        # 0: Bosque de Brasas (musgo turquesa sobre pizarra)
        (base_tile(SLATE, SLATE_D, SLATE_L, TEAL_D, TEAL, 11, True),
         base_tile(SLATE, SLATE_D, SLATE_L, TEAL_D, TEAL, 12, False)),
        # 1: Cañón Humeante (estratos de roca fría)
        (base_tile(hexc("#34405f"), SLATE_D, SLATE_L, hexc("#5a6a92"), hexc("#46557c"), 21, True, True),
         base_tile(hexc("#34405f"), SLATE_D, SLATE_L, hexc("#5a6a92"), hexc("#46557c"), 22, False, True)),
        # 2: Ruinas de Carbón (ladrillo azul grisáceo)
        (brick_tile(hexc("#2a3350"), hexc("#1d2440"), hexc("#4a5a85"), 31, True),
         brick_tile(hexc("#2a3350"), hexc("#1d2440"), hexc("#4a5a85"), 32, False)),
        # 3: El Altar (piedra con vetas ámbar)
        (brick_tile(hexc("#3b4a6f"), hexc("#27365a"), hexc("#7280ab"), 41, True, AMBER_D),
         brick_tile(hexc("#3b4a6f"), hexc("#27365a"), hexc("#7280ab"), 42, False, AMBER_D)),
    ]
    for row, (top, inner) in enumerate(zonas):
        sheet.paste(top, (0, row * 16))
        sheet.paste(inner, (16, row * 16))
    save(sheet, "tiles.png")

# ======================================================================
#  OBJETOS
# ======================================================================
def make_items():
    # chispas (2 cuadros) 8x8
    sheet = new(16, 8)
    for i in range(2):
        t = new(8, 8)
        d = ImageDraw.Draw(t)
        arm = 3 if i == 0 else 2
        d.line([(3, 3 - arm), (3, 3 + arm)], fill=AMBER)
        d.line([(3 - arm, 3), (3 + arm, 3)], fill=AMBER)
        d.rectangle([2, 2, 4, 4], fill=CREAM)
        t.putpixel((3, 3), hexc("#ffffff"))
        outline(t, AMBER_D)
        sheet.paste(t, (8 * i, 0))
    save(sheet, "spark.png")

    # brasero (punto de control): apagado / encendido 16x24
    sheet = new(32, 24)
    for i, lit in enumerate((False, True)):
        t = new(16, 24)
        d = ImageDraw.Draw(t)
        d.rectangle([7, 12, 8, 22], fill=SLATE_L)
        d.polygon([(2, 8), (13, 8), (11, 13), (4, 13)], fill=hexc("#51628e"))
        d.rectangle([3, 22, 12, 23], fill=SLATE_L)
        if lit:
            d.polygon([(4, 8), (5, 3), (7, 5), (8, 0), (10, 5), (11, 3), (12, 8)], fill=FIRE)
            d.polygon([(6, 8), (8, 3), (10, 8)], fill=AMBER)
            d.polygon([(7, 8), (8, 5), (9, 8)], fill=CREAM)
        else:
            d.polygon([(5, 8), (8, 5), (11, 8)], fill=hexc("#3a3f58"))
        outline(t, NIGHT_D)
        sheet.paste(t, (16 * i, 0))
    save(sheet, "checkpoint.png")

    # altar (meta): apagado / encendido 24x28 con banderín turquesa (como en el boceto del GDD)
    sheet = new(48, 28)
    for i, lit in enumerate((False, True)):
        t = new(24, 28)
        d = ImageDraw.Draw(t)
        d.polygon([(2, 27), (4, 17), (18, 17), (20, 27)], fill=hexc("#51628e"))
        d.rectangle([4, 15, 17, 17], fill=hexc("#7280ab"))
        d.rectangle([7, 11, 14, 15], fill=hexc("#3a3f58"))
        d.rectangle([21, 3, 21, 20], fill=CREAM)                          # mástil
        d.polygon([(22, 3), (23, 3), (23, 8), (22, 8)], fill=TEAL)        # banderín turquesa
        d.polygon([(22, 4), (23, 5), (22, 7)], fill=TEAL)
        if lit:
            d.polygon([(6, 15), (8, 7), (10, 10), (11, 3), (13, 10), (15, 7), (17, 15)], fill=FIRE)
            d.polygon([(8, 15), (11, 8), (14, 15)], fill=AMBER)
            d.polygon([(10, 15), (11, 11), (12, 15)], fill=CREAM)
        else:
            d.polygon([(8, 11), (11, 8), (14, 11)], fill=hexc("#2a2d40"))
        outline(t, NIGHT_D)
        sheet.paste(t, (24 * i, 0))
    save(sheet, "altar.png")

    # boca de fuego (base de las zonas de fuego y humo) 16x8
    t = new(16, 8)
    d = ImageDraw.Draw(t)
    d.rectangle([0, 3, 15, 7], fill=hexc("#3b2a3a"))
    d.rectangle([1, 2, 14, 3], fill=hexc("#51628e"))
    d.rectangle([3, 3, 12, 4], fill=FIRE_D)
    d.line([(4, 3), (11, 3)], fill=FIRE)
    outline(t, NIGHT_D)
    save(t, "fire_vent.png")

    # partícula: punto suave 6x6
    t = new(6, 6)
    for y in range(6):
        for x in range(6):
            dd = math.hypot(x - 2.5, y - 2.5)
            if dd < 2.9:
                a = int(255 * max(0.0, 1 - dd / 3.0))
                t.putpixel((x, y), (255, 255, 255, a))
    save(t, "particle.png")

    # icono de vida (mini Embra) 8x8 para el HUD
    t = new(8, 8)
    d = ImageDraw.Draw(t)
    d.polygon([(2, 3), (4, 0), (5, 3)], fill=FIRE)
    d.rectangle([1, 3, 6, 7], fill=AMBER)
    t.putpixel((2, 5), NIGHT); t.putpixel((5, 5), NIGHT)
    outline(t, CREAM)
    save(t, "life_icon.png")

# ======================================================================
#  DECORACIÓN y FONDOS
# ======================================================================
def make_decor():
    # árbol del Bosque de Brasas 32x48 (follaje frío con brasas)
    t = new(32, 48)
    d = ImageDraw.Draw(t)
    d.rectangle([14, 22, 17, 47], fill=hexc("#232a45"))
    for (x, y, r) in [(16, 13, 11), (8, 21, 8), (24, 21, 8), (16, 25, 8)]:
        d.ellipse([x - r, y - r, x + r, y + r], fill=hexc("#2b4660"))
    for (x, y, r) in [(13, 10, 5), (22, 19, 4)]:
        d.ellipse([x - r, y - r, x + r, y + r], fill=hexc("#356a78"))
    for (x, y) in [(10, 12), (20, 8), (24, 22), (12, 26), (17, 17)]:
        t.putpixel((x, y), AMBER)
    outline(t, NIGHT_D)
    t.save(os.path.join(OUT, "decor_0.png"))
    # aguja de roca del Cañón 24x40 con vena ámbar
    t = new(24, 40)
    d = ImageDraw.Draw(t)
    d.polygon([(2, 39), (6, 14), (10, 2), (14, 14), (17, 24), (22, 39)], fill=hexc("#34405f"))
    d.polygon([(10, 2), (14, 14), (17, 24), (12, 39), (10, 20)], fill=hexc("#2a3350"))
    d.line([(9, 8), (11, 22), (9, 33)], fill=FIRE_D)
    d.line([(10, 10), (11, 20)], fill=AMBER)
    outline(t, NIGHT_D)
    t.save(os.path.join(OUT, "decor_1.png"))
    # pilar en ruinas 16x48 con grietas de brasa
    t = new(16, 48)
    d = ImageDraw.Draw(t)
    d.rectangle([2, 6, 13, 47], fill=hexc("#2f3a5c"))
    d.rectangle([0, 0, 15, 6], fill=hexc("#46557c"))
    for y in range(10, 47, 8):
        d.line([(2, y), (13, y)], fill=hexc("#1d2440"))
    d.line([(6, 18), (8, 24), (6, 30)], fill=FIRE_D)
    d.line([(7, 20), (8, 24)], fill=AMBER)
    outline(t, NIGHT_D)
    t.save(os.path.join(OUT, "decor_2.png"))
    # columna del Altar con brasero 16x48
    t = new(16, 48)
    d = ImageDraw.Draw(t)
    d.rectangle([3, 14, 12, 47], fill=hexc("#3b4a6f"))
    d.rectangle([1, 10, 14, 14], fill=hexc("#7280ab"))
    d.polygon([(3, 10), (4, 5), (6, 7), (8, 1), (10, 7), (12, 5), (13, 10)], fill=FIRE)
    d.polygon([(5, 10), (8, 4), (11, 10)], fill=AMBER)
    d.polygon([(7, 10), (8, 7), (9, 10)], fill=CREAM)
    for y in range(20, 47, 9):
        d.line([(3, y), (12, y)], fill=hexc("#27365a"))
    outline(t, NIGHT_D)
    t.save(os.path.join(OUT, "decor_3.png"))

def lerp(a, b, t):
    return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))

def make_backgrounds():
    W, H = 480, 270
    cfg = [
        # (cielo arriba, cielo abajo, lejos, cerca, brillo)
        ("#1B1F3B", "#26305a", "#242b4f", "#1f2547", "#FFF3C4"),
        ("#1B1F3B", "#2f2a52", "#2a2a50", "#222446", "#F4A62A"),
        ("#1B1F3B", "#222c52", "#262d52", "#1e2346", "#FFF3C4"),
        ("#151937", "#2b2f63", "#262c58", "#1b2048", "#F4A62A"),
    ]
    for i, (c1, c2, far, near, spark) in enumerate(cfg):
        sky = Image.new("RGBA", (W, H))
        a, b = hexc(c1)[:3], hexc(c2)[:3]
        d = ImageDraw.Draw(sky)
        for y in range(H):
            d.line([(0, y), (W, y)], fill=lerp(a, b, y / H) + (255,))
        r = noise(100 + i)
        for _ in range(70):
            x, y = int(r() * W), int(r() * H * 0.75)
            d.point((x, y), fill=hexc("#FFF3C4", 200))
        for _ in range(26):                       # brasas flotando en el aire
            x, y = int(r() * W), int(r() * H)
            d.point((x, y), fill=hexc(spark, 150))
        if i == 1:                                # bruma de humo del cañón
            for k in range(6):
                y0 = 150 + k * 18
                d.ellipse([k * 90 - 40, y0, k * 90 + 120, y0 + 26], fill=(70, 62, 96, 40))
        sky.save(os.path.join(OUT, f"bg_sky_{i}.png"))
        far_img = new(W, H)
        d = ImageDraw.Draw(far_img)
        pts = [(0, H)]
        for x in range(0, W + 1, 4):
            y = 150 + 28 * math.sin(2 * math.pi * x / W * 2) + 14 * math.sin(2 * math.pi * x / W * 5 + i)
            pts.append((x, y))
        pts.append((W, H))
        d.polygon(pts, fill=hexc(far))
        far_img.save(os.path.join(OUT, f"bg_far_{i}.png"))
        near_img = new(W, H)
        d = ImageDraw.Draw(near_img)
        pts = [(0, H)]
        for x in range(0, W + 1, 4):
            y = 205 + 12 * math.sin(2 * math.pi * x / W * 3 + 1) + 6 * math.sin(2 * math.pi * x / W * 8)
            pts.append((x, y))
        pts.append((W, H))
        d.polygon(pts, fill=hexc(near))
        for k in range(8):
            bx = int((k + 0.5) * W / 8)
            if i == 0:   # árboles del bosque
                d.rectangle([bx - 2, 175, bx + 2, 215], fill=hexc(near))
                d.ellipse([bx - 12, 152, bx + 12, 182], fill=hexc(near))
            elif i == 1:  # paredes del cañón
                d.polygon([(bx - 14, 215), (bx - 6, 150 - (k % 3) * 10), (bx + 6, 160), (bx + 14, 215)], fill=hexc(near))
            elif i == 2:  # columnas rotas
                d.rectangle([bx - 6, 170 + (k % 2) * 10, bx + 6, 215], fill=hexc(near))
            else:         # columnas del templo
                d.rectangle([bx - 5, 140, bx + 5, 215], fill=hexc(near))
                d.rectangle([bx - 8, 136, bx + 8, 142], fill=hexc(near))
        near_img.save(os.path.join(OUT, f"bg_near_{i}.png"))

# ======================================================================
#  LOGO (fuente 5x7 propia) e ícono
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
                    col = CREAM if gy < 1 else (AMBER if gy < 4 else (hexc("#f08a2a") if gy < 6 else FIRE))
                    for sy in range(scale):
                        for sx in range(scale):
                            px[x0 + gx * scale + sx, 4 + gy * scale + sy] = col
        x0 += 6 * scale
    base = img.copy()
    for _ in range(2):
        outline(base, NIGHT_D)
    save(base, "logo.png")

def make_icon():
    f = embra_frame()
    big = f.resize((48, 60), Image.NEAREST)
    bg = Image.new("RGBA", (64, 64), NIGHT)
    bg.alpha_composite(big, (8, 2))
    save(bg, "icon.png")

def clean_obsolete():
    """Elimina assets del diseño anterior que ya no están en el GDD."""
    for f in ("escarchin_sheet.png", "humoro_sheet.png", "gelido_sheet.png", "fireball.png", "iceshard.png",
              "spikes.png", "heart.png", "hearth.png", "sign.png"):
        p = os.path.join(OUT, f)
        if os.path.exists(p):
            os.remove(p)

def main():
    clean_obsolete()
    make_embra()
    make_rondin()
    make_tiles()
    make_items()
    make_decor()
    make_backgrounds()
    make_logo()
    make_icon()
    print("Assets generados en", os.path.abspath(OUT))

if __name__ == "__main__":
    main()
