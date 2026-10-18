#!/usr/bin/env python3
"""
Genera las láminas de arte para la biblia del videojuego (docs/biblia_art/*.png) de
"EMBRA: Bosque de Brasas": hojas de personajes (boceto del GDD + sprite final + paleta),
paleta global y tilesets, objetos, logotipo y mapas de nivel renderizados con los assets del juego.
Uso: python3 tools/make_bible_art.py
"""
import os
import sys
from collections import Counter
from PIL import Image, ImageDraw, ImageFont

BASE = os.path.join(os.path.dirname(__file__), "..")
SPR = os.path.join(BASE, "assets", "sprites")
GDD = os.path.join(BASE, "docs", "gdd_media")
OUT = os.path.join(BASE, "docs", "biblia_art")
os.makedirs(OUT, exist_ok=True)
sys.path.insert(0, os.path.dirname(__file__))
import make_levels  # noqa: E402

# Paleta del GDD
NIGHT = (27, 31, 59, 255)
SLATE = (46, 58, 89, 255)
AMBER = (244, 166, 42, 255)
FIRE = (232, 84, 42, 255)
CREAM = (255, 243, 196, 255)
TEAL = (76, 201, 192, 255)
INK = (18, 21, 43, 255)
GRID = (36, 41, 76, 255)

FONT_DIR = "/usr/share/fonts/truetype/liberation/"
def font(size, bold=False, italic=False):
    name = "LiberationSans-" + ("BoldItalic" if bold and italic else "Bold" if bold else "Italic" if italic else "Regular") + ".ttf"
    return ImageFont.truetype(FONT_DIR + name, size)

def load(name, base=SPR):
    return Image.open(os.path.join(base, name)).convert("RGBA")

def frame(sheet, i, w, h):
    return sheet.crop((i * w, 0, (i + 1) * w, h))

def hexs(c):
    return "#%02X%02X%02X" % c[:3]

def top_colors(img, n=6):
    cnt = Counter()
    for px in (img.get_flattened_data() if hasattr(img, 'get_flattened_data') else img.getdata()):
        if px[3] > 200:
            cnt[px[:3]] += 1
    return [c for c, _ in cnt.most_common(n)]

def sketch_outline(img, scale):
    """Bosquejo a lápiz de un sprite: silueta suavizada + detalles interiores."""
    from PIL import ImageFilter, ImageChops
    pad = Image.new("RGBA", (img.width + 4, img.height + 4), (0, 0, 0, 0))
    pad.paste(img, (2, 2))
    img = pad
    w, h = img.size
    alpha = img.split()[3].point(lambda v: 255 if v > 0 else 0)
    big = alpha.resize((w * scale, h * scale), Image.BICUBIC).filter(ImageFilter.GaussianBlur(scale * 0.55))
    mask = big.point(lambda v: 255 if v > 110 else 0)
    edge = ImageChops.subtract(mask.filter(ImageFilter.MaxFilter(5)), mask.filter(ImageFilter.MinFilter(3)))
    out = Image.new("RGBA", mask.size, (0, 0, 0, 0))
    out.paste(Image.new("RGBA", mask.size, (255, 255, 255, 30)), mask=mask)
    out.paste(Image.new("RGBA", mask.size, CREAM), mask=edge)
    # detalles interiores (ojos, grietas): píxeles de color de brasa/oscuro rodeados por el sprite
    src = img.load()
    detail = Image.new("L", (w * scale, h * scale), 0)
    dd = ImageDraw.Draw(detail)
    marks = {(232, 84, 42), (177, 58, 28), (27, 31, 59)}
    for y in range(h):
        for x in range(w):
            r, g, b, a = src[x, y]
            if a > 0 and (r, g, b) in marks:
                inner = all(0 <= x + dx < w and 0 <= y + dy < h and src[x + dx, y + dy][3] > 0
                            for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)))
                if inner:
                    dd.ellipse([x * scale + 2, y * scale + 2, (x + 1) * scale - 2, (y + 1) * scale - 2], fill=255)
    detail = detail.filter(ImageFilter.GaussianBlur(scale * 0.2)).point(lambda v: 255 if v > 90 else 0)
    out.paste(Image.new("RGBA", mask.size, AMBER), mask=detail)
    return out

def paper(w, h):
    img = Image.new("RGBA", (w, h), NIGHT)
    d = ImageDraw.Draw(img)
    for x in range(0, w, 32):
        d.line([(x, 0), (x, h)], fill=GRID)
    for y in range(0, h, 32):
        d.line([(0, y), (w, y)], fill=GRID)
    return img

def wrap(d, text, fnt, maxw):
    words, lines, cur = text.split(), [], ""
    for wd in words:
        t = (cur + " " + wd).strip()
        if d.textlength(t, font=fnt) <= maxw:
            cur = t
        else:
            lines.append(cur); cur = wd
    if cur:
        lines.append(cur)
    return lines

def header(d, W, title, subtitle=None):
    d.rectangle([0, 0, W, 70], fill=SLATE)
    d.rectangle([0, 66, W, 70], fill=AMBER)
    d.text((28, 12), title, font=font(38, True), fill=CREAM)
    if subtitle:
        d.text((W - 28, 26), subtitle, font=font(22, italic=True), fill=AMBER, anchor="ra")

def character_sheet(fname, sheet_file, fw, fh, title, subtitle, left_img, left_caption, desc, scale, anim_idx, notes):
    W, H = 1400, 1150
    img = paper(W, H)
    d = ImageDraw.Draw(img)
    header(d, W, title, subtitle)

    # --- izquierda: boceto
    d.text((40, 92), left_caption, font=font(21, True), fill=AMBER)
    if left_img is None:
        sheet = load(sheet_file)
        base = frame(sheet, 0, fw, fh)
        left = sketch_outline(base, 20)
        panel = Image.new("RGBA", (left.width + 40, left.height + 40), (20, 24, 50, 255))
        panel.alpha_composite(left, (20, 20))
    else:
        panel = left_img
    img.alpha_composite(panel, (40, 125))
    # anotaciones
    for (text, lx, ly) in notes:
        fnt = font(17, italic=True)
        for i, ln in enumerate(wrap(d, text, fnt, 230)):
            d.text((lx, ly + i * 21), ln, font=fnt, fill=CREAM)

    # --- derecha: arte final del juego
    d.text((830, 92), "ARTE FINAL (sprite del juego)", font=font(21, True), fill=AMBER)
    sheet = load(sheet_file)
    base = frame(sheet, 0, fw, fh)
    big = base.resize((fw * scale, fh * scale), Image.NEAREST)
    pn = Image.new("RGBA", (big.width + 40, big.height + 40), (20, 24, 50, 255))
    pn.alpha_composite(big, (20, 20))
    img.alpha_composite(pn, (830, 125))
    cols = top_colors(base, 6)
    px0, py0 = 830, 125 + pn.height + 16
    d.text((px0, py0), "Colores usados", font=font(18, True), fill=AMBER)
    for i, c in enumerate(cols):
        x = px0 + i * 92
        d.rectangle([x, py0 + 26, x + 80, py0 + 60], fill=c + (255,), outline=CREAM)
        d.text((x, py0 + 64), hexs(c), font=font(14), fill=CREAM)

    ty = py0 + 100
    for ln_title, ln_text in desc:
        d.text((830, ty), ln_title, font=font(18, True), fill=AMBER)
        ty += 22
        for ln in wrap(d, ln_text, font(16), 520):
            d.text((830, ty), ln, font=font(16), fill=CREAM)
            ty += 20
        ty += 6

    # --- tira de animación
    d.text((40, H - 190), "Cuadros de animación", font=font(18, True), fill=AMBER)
    x = 40
    for i in anim_idx:
        f = frame(sheet, i, fw, fh)
        s = 5
        b = f.resize((fw * s, fh * s), Image.NEAREST)
        bg = Image.new("RGBA", (b.width + 16, b.height + 16), (20, 24, 50, 255))
        bg.alpha_composite(b, (8, 8))
        if x + bg.width > 800:
            break
        img.alpha_composite(bg, (x, H - 160))
        x += bg.width + 10
    img.convert("RGB").save(os.path.join(OUT, fname))

def make_characters():
    gdd_sketch = Image.open(os.path.join(GDD, "boceto_embra_gdd.png")).convert("RGBA")
    gdd_sketch = gdd_sketch.resize((int(gdd_sketch.width * 0.82), int(gdd_sketch.height * 0.82)), Image.LANCZOS)
    character_sheet(
        "char_embra.png", "embra_sheet.png", 16, 20, "EMBRA", "Protagonista · elemental de brasa",
        gdd_sketch, "BOCETO ORIGINAL DEL GDD",
        [("Rol", "Personaje jugable. Es una pequeña brasa separada de la fogata ancestral que debe llegar al altar de cada nivel."),
         ("Personalidad", "Curiosa, valiente y optimista. No habla: se expresa con saltos, chispas y los movimientos de su llama."),
         ("Habilidades", "Moverse a izquierda y derecha y saltar entre plataformas. Recoge chispas para ganar puntos."),
         ("Debilidades", "El contacto con un Rondín o con fuego activo le cuesta una vida y parte de su puntaje; caer al vacío le cuesta una vida."),
         ("Del boceto al sprite", "Se respetó el cuerpo rectangular redondeado ámbar, la llama triangular (fuego y brillo), los ojos ovalados oscuros, los brazos delgados y las piernas turquesa.")],
        20, [0, 1, 2, 3, 4, 5, 6, 7, 8], [])
    character_sheet(
        "char_rondin.png", "rondin_sheet.png", 16, 16, "RONDÍN", "Enemigo · criatura de carbón", None, "BOSQUEJO",
        [("Rol", "Enemigo del Bosque de Brasas. Antes guardaba el bosque; al faltar la fogata perdió el control."),
         ("Comportamiento", "Patrulla una plataforma de un extremo a otro y da la vuelta en los bordes y las paredes."),
         ("Cómo se enfrenta", "No se puede vencer: hay que esquivarlo saltando. El contacto cuesta una vida y parte del puntaje."),
         ("Diseño", "Silueta de carbón con grietas de brasa y ojos encendidos. El contorno naranja lo marca como peligro, igual que el fuego.")],
        20, [0, 1], [("Trozos de carbón en la cabeza", 480, 150), ("Grietas y ojos de brasa", 480, 330), ("Patitas cortas que alternan al caminar", 480, 480)])

# ----------------------------------------------------------------------------------------------
def make_palette_and_tiles():
    W, H = 1400, 880
    img = paper(W, H)
    d = ImageDraw.Draw(img)
    header(d, W, "PALETA Y TILESETS", "Según el GDD")
    pal = [("#1B1F3B", "Fondo nocturno"), ("#2E3A59", "Plataformas"), ("#F4A62A", "Ámbar (personaje)"),
           ("#E8542A", "Fuego / peligro"), ("#FFF3C4", "Brillo / partículas"), ("#4CC9C0", "Detalles frescos")]
    d.text((30, 90), "Paleta del GDD", font=font(22, True), fill=AMBER)
    for i, (h, n) in enumerate(pal):
        x = 30 + i * 225
        d.rectangle([x, 125, x + 200, 205], fill=h, outline=CREAM, width=2)
        d.text((x, 212), h, font=font(20, True), fill=CREAM)
        d.text((x, 238), n, font=font(16), fill=CREAM)
    zonas = [("1 · Bosque de Brasas", 0), ("2 · Cañón Humeante", 1), ("3 · Ruinas de Carbón", 2), ("4 · El Altar", 3)]
    tiles = load("tiles.png")
    for i, (name, row) in enumerate(zonas):
        x0 = 30 + i * 340
        d.text((x0, 290), name, font=font(20, True), fill=AMBER)
        top = tiles.crop((0, row * 16, 16, row * 16 + 16)).resize((100, 100), Image.NEAREST)
        inner = tiles.crop((16, row * 16, 32, row * 16 + 16)).resize((100, 100), Image.NEAREST)
        sky = load("bg_sky_%d.png" % row).resize((300, 169), Image.NEAREST)
        near = load("bg_near_%d.png" % row).resize((300, 169), Image.NEAREST)
        sky.alpha_composite(near, (0, 0))
        img.alpha_composite(sky, (x0, 325))
        for k in range(3):
            img.alpha_composite(top, (x0 + k * 100, 505))
            img.alpha_composite(inner, (x0 + k * 100, 605))
        d.text((x0, 712), "fondo · superficie · interior", font=font(15, italic=True), fill=CREAM)
    d.text((30, 760), "Regla de color: el ámbar y el fuego solo se usan en el personaje, las chispas y los peligros; todo lo demás es frío.", font=font(18, italic=True), fill=CREAM)
    img.convert("RGB").save(os.path.join(OUT, "paleta_tiles.png"))

# ----------------------------------------------------------------------------------------------
def draw_flames(canvas, px, py):
    """Dibuja unas llamas sencillas sobre una boca de fuego (solo para las láminas de la biblia)."""
    d = ImageDraw.Draw(canvas)
    base_y = py + 9
    d.polygon([(px + 2, base_y), (px + 4, base_y - 14), (px + 7, base_y)], fill=FIRE)
    d.polygon([(px + 6, base_y), (px + 9, base_y - 18), (px + 12, base_y)], fill=FIRE)
    d.polygon([(px + 11, base_y), (px + 13, base_y - 12), (px + 15, base_y)], fill=FIRE)
    d.polygon([(px + 4, base_y), (px + 6, base_y - 8), (px + 8, base_y)], fill=AMBER)
    d.polygon([(px + 8, base_y), (px + 10, base_y - 11), (px + 12, base_y)], fill=AMBER)

def render_level(idx):
    lv = make_levels.LEVELS[idx]
    rows = lv["rows"]
    wt, ht = len(rows[0]), len(rows)
    theme = lv["theme"]
    T = 16
    canvas = Image.new("RGBA", (wt * T, ht * T), (0, 0, 0, 255))
    sky = load("bg_sky_%d.png" % theme).resize((480, 288), Image.NEAREST)
    far = load("bg_far_%d.png" % theme).resize((480, 288), Image.NEAREST)
    near = load("bg_near_%d.png" % theme).resize((480, 288), Image.NEAREST)
    for x in range(0, wt * T, 480):
        canvas.alpha_composite(sky, (x, 0))
        canvas.alpha_composite(far, (x, 0))
        canvas.alpha_composite(near, (x, 0))
    tiles = load("tiles.png")
    spark = frame(load("spark.png"), 0, 8, 8)
    chk = frame(load("checkpoint.png"), 0, 16, 24)
    altar = frame(load("altar.png"), 1, 24, 28)
    rondin = frame(load("rondin_sheet.png"), 0, 16, 16)
    emb = frame(load("embra_sheet.png"), 0, 16, 20)
    vent = load("fire_vent.png")
    decor = load("decor_%d.png" % theme)

    def solid(x, y):
        return 0 <= y < ht and 0 <= x < wt and rows[y][x] == "#"

    for y in range(ht):
        for x in range(wt):
            ch = rows[y][x]
            px, py = x * T, y * T
            cx, cy = px + 8, py + 8
            if ch == "#":
                col = 0 if not solid(x, y - 1) else 1
                canvas.alpha_composite(tiles.crop((col * 16, theme * 16, col * 16 + 16, theme * 16 + 16)), (px, py))
            elif ch == "F":
                canvas.alpha_composite(vent, (px, py + 8))
                draw_flames(canvas, px, py)
            elif ch == "o":
                canvas.alpha_composite(spark, (cx - 4, cy - 4))
            elif ch == "c":
                canvas.alpha_composite(chk, (px, py + 16 - 24))
            elif ch == "G":
                canvas.alpha_composite(altar, (px - 4, py + 16 - 28))
            elif ch == "r":
                canvas.alpha_composite(rondin, (px, py))
            elif ch == "P":
                canvas.alpha_composite(emb, (px, py + 16 - 20))
            elif ch == "T":
                canvas.alpha_composite(decor, (px + 8 - decor.width // 2, py + 16 - decor.height))
    half = (wt + 1) // 2
    a = canvas.crop((0, 0, half * T, ht * T))
    b = canvas.crop((half * T, 0, wt * T, ht * T))
    out = Image.new("RGBA", (half * T, ht * T * 2 + 10), (12, 14, 30, 255))
    out.alpha_composite(a, (0, 0))
    out.alpha_composite(b, (0, ht * T + 10))
    out.convert("RGB").save(os.path.join(OUT, "mapa_nivel_%d.png" % (idx + 1)))

def make_logo():
    logo = load("logo.png")
    img = paper(900, 340)
    big = logo.resize((logo.width * 3, logo.height * 3), Image.NEAREST)
    img.alpha_composite(big, ((900 - big.width) // 2, 30))
    d = ImageDraw.Draw(img)
    d.text((450, 250), "BOSQUE DE BRASAS", font=font(34, True), fill=AMBER, anchor="ma")
    d.text((450, 298), "Logotipo con letras pixeladas de 5x7 y degradado de brasa (brillo → ámbar → fuego)", font=font(16, italic=True), fill=CREAM, anchor="ma")
    img.convert("RGB").save(os.path.join(OUT, "logo_hoja.png"))

def make_items_sheet():
    img = paper(1400, 430)
    d = ImageDraw.Draw(img)
    header(d, 1400, "OBJETOS Y ELEMENTOS DEL MUNDO")
    items = [("Chispa", frame(load("spark.png"), 0, 8, 8), 8, "Moneda: +10 puntos"),
             ("Brasero", frame(load("checkpoint.png"), 1, 16, 24), 5, "Punto de control"),
             ("Altar", frame(load("altar.png"), 1, 24, 28), 4, "Meta de cada nivel"),
             ("Zona de fuego y humo", load("fire_vent.png"), 8, "Base de las llamas hechas con partículas"),
             ("Icono de vida", load("life_icon.png"), 8, "Vidas en el HUD"),
             ("Aguja de roca", load("decor_1.png"), 3, "Decoración del Cañón"),
             ("Árbol", load("decor_0.png"), 3, "Decoración del Bosque"),
             ("Pilar", load("decor_2.png"), 3, "Decoración de las Ruinas")]
    x = 30
    for name, im, s, desc in items:
        big = im.resize((im.width * s, im.height * s), Image.NEAREST)
        if big.height > 150 or big.width > 160:
            big = big.resize((int(big.width * min(150 / big.height, 160 / big.width)), int(big.height * min(150 / big.height, 160 / big.width))), Image.NEAREST)
        bg = Image.new("RGBA", (165, 200), (20, 24, 50, 255))
        bg.alpha_composite(big, ((165 - big.width) // 2, (190 - big.height) // 2))
        img.alpha_composite(bg, (x, 90))
        d.text((x + 82, 300), name, font=font(16, True), fill=AMBER, anchor="ma")
        for i, ln in enumerate(wrap(d, desc, font(14), 155)):
            d.text((x + 82, 326 + i * 18), ln, font=font(14), fill=CREAM, anchor="ma")
        x += 170
    img.convert("RGB").save(os.path.join(OUT, "objetos.png"))

if __name__ == "__main__":
    make_characters()
    make_palette_and_tiles()
    for i in range(4):
        render_level(i)
    make_logo()
    make_items_sheet()
    print("Láminas generadas en", os.path.abspath(OUT))
