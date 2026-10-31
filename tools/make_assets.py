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
#  EMBRA (16x24) en 3 etapas de evolución: Brasa -> Llama -> Fuego ardiente
#  Sigue el boceto del GDD (cuerpo rectangular redondeado ámbar, llama triangular, ojos ovalados,
#  brazos delgados y piernas turquesa) y agrega rasgos de cada etapa.
# ======================================================================
def embra_frame(stage=1, flame=0, bob=0, leg=0, arms="down", eyes="open", tuck=False, flash=False, mouth="smile"):
    W, H = 16, 24
    img = new(W, H)
    d = ImageDraw.Draw(img)
    by = 10 + bob                     # parte superior del cuerpo
    tipx = 8 + flame
    # ---- llama (crece con la evolución)
    if stage == 1:
        d.polygon([(5, by), (tipx, by - 6), (10, by)], fill=FIRE)
        d.polygon([(6, by), (tipx, by - 3), (9, by)], fill=CREAM)
    elif stage == 2:
        d.polygon([(4, by), (5, by - 4), (6, by - 2), (tipx, by - 9), (9, by - 2), (10, by - 4), (11, by)], fill=FIRE)
        d.polygon([(5, by), (tipx, by - 6), (10, by)], fill=AMBER)
        d.polygon([(7, by), (tipx, by - 3), (9, by)], fill=CREAM)
    else:
        d.polygon([(3, by), (3, by - 5), (5, by - 3), (6, by - 8), (tipx, by - 11), (9, by - 8), (10, by - 3), (12, by - 5), (12, by)], fill=FIRE)
        d.polygon([(4, by), (6, by - 5), (tipx, by - 8), (9, by - 5), (11, by)], fill=AMBER)
        d.polygon([(6, by), (tipx, by - 5), (9, by)], fill=CREAM)
        for (x, y) in ((2, by - 8), (13, by - 7), (1, by - 3)):      # brasas flotando alrededor de la llama
            d.point((x + flame, y), fill=AMBER)
    # ---- cuerpo: rectángulo redondeado ámbar con sombra y luz
    d.rounded_rectangle([3, by, 12, by + 9], radius=2, fill=AMBER)
    d.rectangle([4, by + 8, 11, by + 9], fill=AMBER_D)
    d.line([(4, by + 1), (4, by + 5)], fill=hexc("#ffc45a"))
    if stage >= 2:
        d.ellipse([6, by + 6, 9, by + 8], fill=hexc("#ffd36b"))        # brillo de brasa en el vientre
    if stage >= 3:
        d.point((5, by + 1), fill=CREAM); d.point((10, by + 1), fill=CREAM)
    # ---- brazos
    hand = AMBER if stage == 1 else (CREAM if stage == 2 else FIRE)
    def arm(p1, p2, tip):
        d.line([p1, p2], fill=AMBER if stage < 3 else FIRE)
        if stage >= 2:
            img.putpixel(p2, hand if stage == 2 else AMBER)
    if arms == "down":
        arm((2, by + 3), (1, by + 5), 0); arm((13, by + 3), (14, by + 5), 0)
    elif arms == "up":
        arm((2, by + 3), (1, by + 1), 0); arm((13, by + 3), (14, by + 1), 0)
    elif arms == "wide":
        arm((2, by + 3), (0, by + 4), 0); arm((13, by + 3), (15, by + 4), 0)
    elif arms == "swing_a":
        arm((2, by + 3), (1, by + 6), 0); arm((13, by + 3), (14, by + 3), 0)
    elif arms == "swing_b":
        arm((2, by + 3), (1, by + 3), 0); arm((13, by + 3), (14, by + 6), 0)
    elif arms == "shoot":
        arm((2, by + 3), (1, by + 5), 0); arm((13, by + 4), (15, by + 3), 0)
    # ---- ojos ovalados oscuros con brillo
    ey = by + 3
    if eyes in ("open", "wide"):
        top = ey - (1 if eyes == "wide" else 0)
        d.rectangle([5, top, 6, ey + 2], fill=NIGHT); d.rectangle([9, top, 10, ey + 2], fill=NIGHT)
        img.putpixel((5, top), CREAM); img.putpixel((9, top), CREAM)
    elif eyes == "x":
        for ex in (5, 9):
            img.putpixel((ex, ey), NIGHT); img.putpixel((ex + 1, ey + 1), NIGHT)
            img.putpixel((ex + 1, ey), NIGHT); img.putpixel((ex, ey + 1), NIGHT)
    # ---- boca y mejillas
    my = by + 6
    if eyes != "x":
        if mouth == "smile":
            d.line([(7, my), (8, my)], fill=AMBER_D); img.putpixel((6, my - 1), AMBER_D); img.putpixel((9, my - 1), AMBER_D)
        elif mouth == "open":
            d.rectangle([7, my - 1, 8, my + 1], fill=NIGHT)
        d.point((4, my - 1), fill=hexc("#e8863a")); d.point((11, my - 1), fill=hexc("#e8863a"))
    # ---- piernas turquesa con pie
    ly = by + 10
    if tuck:
        d.rectangle([4, ly, 6, ly + 1], fill=TEAL); d.rectangle([9, ly, 11, ly + 1], fill=TEAL)
    else:
        l1 = ly + (1 if leg > 0 else 0)
        l2 = ly + (1 if leg < 0 else 0)
        end = min(H - 1, ly + 3)
        d.rectangle([4, l1, 6, end], fill=TEAL); d.rectangle([9, l2, 11, end], fill=TEAL)
        d.line([(4, end), (6, end)], fill=TEAL_D); d.line([(9, end), (11, end)], fill=TEAL_D)
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
    for stage in (1, 2, 3):
        frames = [
            embra_frame(stage, flame=0, arms="down"),                                      # 0 reposo A
            embra_frame(stage, flame=1, arms="down", bob=1),                                # 1 reposo B
            embra_frame(stage, flame=-1, arms="swing_a", leg=1),                            # 2 correr 1
            embra_frame(stage, flame=1, arms="down", leg=0),                                # 3 correr 2
            embra_frame(stage, flame=-1, arms="swing_b", leg=-1),                           # 4 correr 3
            embra_frame(stage, flame=1, arms="down", leg=0),                                # 5 correr 4
            embra_frame(stage, flame=0, arms="up", tuck=True, eyes="wide"),                 # 6 salto
            embra_frame(stage, flame=-1, arms="wide", tuck=True, eyes="wide"),              # 7 caída
            embra_frame(stage, flame=0, arms="wide", eyes="x", flash=True),                 # 8 herido
            embra_frame(stage, flame=1, arms="shoot", mouth="open"),                        # 9 disparo
        ]
        sheet = new(16 * len(frames), 24)
        for i, f in enumerate(frames):
            sheet.paste(f, (16 * i, 0))
        save(sheet, "embra_sheet.png" if stage == 1 else "embra%d_sheet.png" % stage)

# ======================================================================
#  ENEMIGOS: Rondín, Rondín furioso, Rondín gigante y Ceniza (volador)
# ======================================================================
CARBON = hexc("#3a3d52")
CARBON_D = hexc("#262938")

def rondin(step=0):
    img = new(16, 16)
    d = ImageDraw.Draw(img)
    sq = 1 if step else 0
    d.rounded_rectangle([2, 4 + sq, 13, 13], radius=3, fill=CARBON)
    d.rectangle([3, 11, 12, 13], fill=CARBON_D)
    d.polygon([(3, 5 + sq), (4, 1 + sq), (6, 4 + sq)], fill=CARBON)               # trozos de carbón
    d.polygon([(8, 4 + sq), (10, 0 + sq), (12, 5 + sq)], fill=CARBON)
    d.point((4, 2 + sq), fill=AMBER); d.point((10, 1 + sq), fill=AMBER)           # brasas en los cuernos
    d.line([(4, 9), (6, 10), (5, 12)], fill=FIRE_D)                               # grietas de brasa
    d.line([(11, 8), (10, 10), (12, 11)], fill=FIRE_D)
    d.line([(4, 5 + sq), (6, 6 + sq)], fill=NIGHT_D); d.line([(11, 5 + sq), (9, 6 + sq)], fill=NIGHT_D)   # ceño
    d.rectangle([4, 7, 6, 8], fill=FIRE); d.rectangle([9, 7, 11, 8], fill=FIRE)   # ojos encendidos
    img.putpixel((5, 7), CREAM); img.putpixel((10, 7), CREAM)
    d.line([(6, 11), (9, 11)], fill=FIRE_D)                                       # boca
    if step == 0:
        d.rectangle([3, 14, 5, 15], fill=CARBON_D); d.rectangle([10, 14, 12, 15], fill=CARBON_D)
    else:
        d.rectangle([4, 14, 6, 15], fill=CARBON_D); d.rectangle([9, 14, 11, 15], fill=CARBON_D)
    outline(img, FIRE)
    return img

def furioso(step=0, charge=False):
    img = new(16, 16)
    d = ImageDraw.Draw(img)
    lean = 1 if charge else 0
    body = hexc("#5a2f35")
    d.rounded_rectangle([2 + lean, 5, 13, 13], radius=3, fill=body)
    d.rectangle([3 + lean, 11, 12, 13], fill=hexc("#3b1f26"))
    for x in (3, 6, 9):                                                         # púas ardientes en el lomo
        d.polygon([(x + lean, 5), (x + 1 + lean, 0 + (1 if step else 0)), (x + 3 + lean, 5)], fill=FIRE)
    d.line([(4, 9), (7, 10), (5, 12)], fill=AMBER)
    d.line([(10, 8), (9, 10), (12, 11)], fill=AMBER)
    d.rectangle([4 + lean, 7, 6 + lean, 8], fill=CREAM); d.rectangle([9 + lean, 7, 11 + lean, 8], fill=CREAM)
    img.putpixel((6 + lean, 8), FIRE); img.putpixel((11 + lean, 8), FIRE)
    d.line([(4 + lean, 6), (7 + lean, 7)], fill=NIGHT_D); d.line([(11 + lean, 6), (8 + lean, 7)], fill=NIGHT_D)
    if charge:
        d.rectangle([6, 11, 10, 12], fill=NIGHT_D)
        d.rectangle([2, 14, 5, 15], fill=hexc("#3b1f26")); d.rectangle([9, 14, 13, 15], fill=hexc("#3b1f26"))
    elif step == 0:
        d.rectangle([3, 14, 5, 15], fill=hexc("#3b1f26")); d.rectangle([10, 14, 12, 15], fill=hexc("#3b1f26"))
    else:
        d.rectangle([4, 14, 6, 15], fill=hexc("#3b1f26")); d.rectangle([9, 14, 11, 15], fill=hexc("#3b1f26"))
    outline(img, AMBER)
    return img

def gigante(step=0):
    img = new(24, 24)
    d = ImageDraw.Draw(img)
    sq = 1 if step else 0
    d.rounded_rectangle([2, 6 + sq, 21, 20], radius=4, fill=CARBON)
    d.rectangle([4, 17, 19, 20], fill=CARBON_D)
    d.polygon([(3, 7 + sq), (5, 1 + sq), (8, 6 + sq)], fill=CARBON)               # cuernos grandes
    d.polygon([(15, 6 + sq), (19, 1 + sq), (21, 7 + sq)], fill=CARBON)
    d.point((5, 2 + sq), fill=AMBER); d.point((19, 2 + sq), fill=AMBER)
    d.rectangle([5, 9, 8, 11], fill=FIRE); d.rectangle([15, 9, 18, 11], fill=FIRE)   # ojos
    img.putpixel((6, 9), CREAM); img.putpixel((16, 9), CREAM)
    d.line([(5, 8), (9, 9)], fill=NIGHT_D); d.line([(18, 8), (14, 9)], fill=NIGHT_D)
    d.ellipse([9, 13, 14, 18], fill=FIRE_D)                                         # núcleo de brasa en el pecho
    d.ellipse([10, 14, 13, 17], fill=AMBER); d.point((11, 15), fill=CREAM)
    d.line([(4, 12), (6, 15), (4, 17)], fill=FIRE_D); d.line([(19, 12), (17, 15), (19, 17)], fill=FIRE_D)
    if step == 0:
        d.rectangle([4, 21, 9, 23], fill=CARBON_D); d.rectangle([14, 21, 19, 23], fill=CARBON_D)
    else:
        d.rectangle([5, 21, 10, 23], fill=CARBON_D); d.rectangle([13, 21, 18, 23], fill=CARBON_D)
    outline(img, FIRE)
    return img

def ceniza(wing=0):
    img = new(16, 16)
    d = ImageDraw.Draw(img)
    ash = hexc("#8a90b0"); ash_l = hexc("#b3b9d4"); ash_d = hexc("#5f6585")
    d.ellipse([3, 3, 12, 11], fill=ash)
    d.ellipse([4, 4, 9, 8], fill=ash_l)
    d.polygon([(3, 9), (4, 14), (6, 12), (8, 15), (10, 12), (12, 14), (12, 9)], fill=ash_d)   # cola de ceniza
    wy = 5 - wing * 2
    d.polygon([(0, wy), (3, 6), (3, 10)], fill=ash_d)
    d.polygon([(15, wy), (12, 6), (12, 10)], fill=ash_d)
    d.rectangle([5, 6, 6, 8], fill=FIRE); d.rectangle([9, 6, 10, 8], fill=FIRE)
    img.putpixel((5, 6), CREAM); img.putpixel((9, 6), CREAM)
    d.point((8, 3), fill=AMBER); d.point((4, 5), fill=AMBER)                                    # brasas dentro de la ceniza
    outline(img, FIRE_D)
    return img

def make_enemies():
    sheet = new(32, 16)
    sheet.paste(rondin(0), (0, 0)); sheet.paste(rondin(1), (16, 0))
    save(sheet, "rondin_sheet.png")
    sheet = new(48, 16)
    sheet.paste(furioso(0), (0, 0)); sheet.paste(furioso(1), (16, 0)); sheet.paste(furioso(0, True), (32, 0))
    save(sheet, "furioso_sheet.png")
    sheet = new(48, 24)
    sheet.paste(gigante(0), (0, 0)); sheet.paste(gigante(1), (24, 0))
    save(sheet, "gigante_sheet.png")
    sheet = new(32, 16)
    sheet.paste(ceniza(0), (0, 0)); sheet.paste(ceniza(1), (16, 0))
    save(sheet, "ceniza_sheet.png")
    # bola de fuego 8x8 (2 cuadros)
    sheet = new(16, 8)
    for i in range(2):
        t = new(8, 8)
        d = ImageDraw.Draw(t)
        d.ellipse([1, 1, 6, 6], fill=FIRE)
        d.ellipse([2, 2, 5, 5], fill=AMBER)
        t.putpixel((3 + i, 3), CREAM)
        d.polygon([(0, 3), (2, 2), (2, 5)], fill=FIRE_D)
        outline(t, NIGHT_D)
        sheet.paste(t, (8 * i, 0))
    save(sheet, "fireball.png")

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
    f = embra_frame(2)
    big = f.resize((48, 72), Image.NEAREST)
    bg = Image.new("RGBA", (64, 64), NIGHT)
    bg.alpha_composite(big.crop((0, 4, 48, 68)).resize((48, 64), Image.NEAREST), (8, 0))
    save(bg, "icon.png")

def clean_obsolete():
    """Elimina assets del diseño anterior que ya no están en el GDD."""
    for f in ("escarchin_sheet.png", "humoro_sheet.png", "gelido_sheet.png", "iceshard.png",
              "spikes.png", "heart.png", "hearth.png", "sign.png"):
        p = os.path.join(OUT, f)
        if os.path.exists(p):
            os.remove(p)

def main():
    clean_obsolete()
    make_embra()
    make_enemies()
    make_tiles()
    make_items()
    make_decor()
    make_backgrounds()
    make_logo()
    make_icon()
    print("Assets generados en", os.path.abspath(OUT))

if __name__ == "__main__":
    main()
