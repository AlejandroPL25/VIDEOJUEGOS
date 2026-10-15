#!/usr/bin/env python3
"""
Genera las láminas de arte para la biblia del videojuego (docs/biblia_art/*.png):
hojas de personajes con bosquejo + versión final + paleta, tilesets por zona, paleta global y
mapas de nivel renderizados con los mismos assets del juego.
Uso: python3 tools/make_bible_art.py
"""
import os
import sys
from collections import Counter
from PIL import Image, ImageDraw, ImageFont

BASE = os.path.join(os.path.dirname(__file__), "..")
SPR = os.path.join(BASE, "assets", "sprites")
OUT = os.path.join(BASE, "docs", "biblia_art")
os.makedirs(OUT, exist_ok=True)
sys.path.insert(0, os.path.dirname(__file__))
import make_levels  # noqa: E402

PAPER = (239, 227, 200, 255)
GRID = (222, 208, 176, 255)
GRAPHITE = (74, 70, 84, 255)
INK = (43, 19, 32, 255)
MAROON = (109, 34, 55, 255)
GOLD = (176, 141, 87, 255)

FONT_DIR = "/usr/share/fonts/truetype/liberation/"
def font(size, bold=False, italic=False):
    name = "LiberationSans-" + ("BoldItalic" if bold and italic else "Bold" if bold else "Italic" if italic else "Regular") + ".ttf"
    return ImageFont.truetype(FONT_DIR + name, size)

def load(name):
    return Image.open(os.path.join(SPR, name)).convert("RGBA")

def frame(sheet, i, w, h):
    return sheet.crop((i * w, 0, (i + 1) * w, h))

def hexs(c):
    return "#%02x%02x%02x" % c[:3]

def top_colors(img, n=6):
    cnt = Counter()
    for px in img.get_flattened_data() if hasattr(img, 'get_flattened_data') else img.getdata():
        if px[3] > 200:
            cnt[px[:3]] += 1
    return [c for c, _ in cnt.most_common(n)]

def sketch_outline(img, scale):
    """Convierte un sprite en un 'bosquejo' a lápiz: silueta suavizada + detalles interiores."""
    from PIL import ImageFilter, ImageChops
    pad = Image.new("RGBA", (img.width + 4, img.height + 4), (0, 0, 0, 0))   # margen para no cortar el contorno
    pad.paste(img, (2, 2))
    img = pad
    w, h = img.size
    alpha = img.split()[3].point(lambda v: 255 if v > 0 else 0)
    big = alpha.resize((w * scale, h * scale), Image.BICUBIC).filter(ImageFilter.GaussianBlur(scale * 0.55))
    mask = big.point(lambda v: 255 if v > 110 else 0)
    edge = ImageChops.subtract(mask.filter(ImageFilter.MaxFilter(5)), mask.filter(ImageFilter.MinFilter(3)))
    out = Image.new("RGBA", mask.size, (0, 0, 0, 0))
    out.paste(Image.new("RGBA", mask.size, (255, 255, 255, 45)), mask=mask)
    out.paste(Image.new("RGBA", mask.size, GRAPHITE), mask=edge)
    # detalles interiores: píxeles de contorno oscuro que no tocan el borde (ojos, boca, grietas)
    src = img.load()
    detail = Image.new("L", (w * scale, h * scale), 0)
    dd = ImageDraw.Draw(detail)
    for y in range(h):
        for x in range(w):
            r, g, b, a = src[x, y]
            if a > 0 and (r, g, b) in ((43, 19, 32),):
                inner = all(0 <= x + dx < w and 0 <= y + dy < h and src[x + dx, y + dy][3] > 0
                            for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)))
                if inner:
                    dd.ellipse([x * scale + 1, y * scale + 1, (x + 1) * scale - 1, (y + 1) * scale - 1], fill=255)
    detail = detail.filter(ImageFilter.GaussianBlur(scale * 0.25)).point(lambda v: 255 if v > 90 else 0)
    out.paste(Image.new("RGBA", mask.size, GRAPHITE), mask=detail)
    return out

def paper(w, h):
    img = Image.new("RGBA", (w, h), PAPER)
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

def character_sheet(fname, sheet_file, fw, fh, frames_idx, title, subtitle, notes, desc, scale, anim_idx):
    W, H = 1400, 1020
    img = paper(W, H)
    d = ImageDraw.Draw(img)
    d.rectangle([0, 0, W, 70], fill=MAROON)
    d.text((28, 12), title, font=font(38, True), fill=(255, 240, 200))
    d.text((W - 28, 26), subtitle, font=font(22, italic=True), fill=(240, 210, 160), anchor="ra")

    sheet = load(sheet_file)
    base = frame(sheet, frames_idx, fw, fh)
    # --- bosquejo (izquierda)
    d.text((40, 90), "BOSQUEJO", font=font(22, True), fill=GRAPHITE)
    sk = sketch_outline(base, scale)
    sx, sy = 60, 135
    img.alpha_composite(sk, (sx - 2 * scale, sy - 2 * scale))
    bw, bh = fw * scale, fh * scale
    # líneas guía
    d.line([(sx + bw // 2, sy - 12), (sx + bw // 2, sy + bh + 12)], fill=(150, 150, 170, 255), width=1)
    d.rectangle([sx, sy, sx + bw, sy + bh], outline=(150, 150, 170, 255))
    for (tx, ty, text, lx, ly) in notes:
        px_, py_ = sx + tx * scale, sy + ty * scale
        d.line([(px_, py_), (lx, ly)], fill=MAROON, width=2)
        d.ellipse([px_ - 4, py_ - 4, px_ + 4, py_ + 4], fill=MAROON)
        fnt = font(17, italic=True)
        for i, ln in enumerate(wrap(d, text, fnt, 190)):
            d.text((lx + 6, ly - 10 + i * 20), ln, font=fnt, fill=INK)

    # --- arte final (derecha)
    d.text((830, 90), "ARTE FINAL (sprite del juego)", font=font(22, True), fill=GRAPHITE)
    fscale = scale
    big = base.resize((fw * fscale, fh * fscale), Image.NEAREST)
    panel = Image.new("RGBA", (big.width + 40, big.height + 40), (60, 48, 80, 255))
    panel.alpha_composite(big, (20, 20))
    img.alpha_composite(panel, (830, 125))
    # paleta
    cols = top_colors(base, 6)
    px0, py0 = 830, 125 + panel.height + 18
    d.text((px0, py0), "Paleta", font=font(18, True), fill=GRAPHITE)
    for i, c in enumerate(cols):
        x = px0 + i * 92
        d.rectangle([x, py0 + 26, x + 80, py0 + 62], fill=c + (255,), outline=INK)
        d.text((x, py0 + 66), hexs(c), font=font(14), fill=INK)

    # --- ficha de texto
    ty = py0 + 100
    for ln_title, ln_text in desc:
        d.text((830, ty), ln_title, font=font(18, True), fill=MAROON)
        ty += 22
        for ln in wrap(d, ln_text, font(16), 520):
            d.text((830, ty), ln, font=font(16), fill=INK)
            ty += 20
        ty += 6

    # --- tira de animación
    d.text((40, H - 175), "Cuadros de animación", font=font(18, True), fill=GRAPHITE)
    x = 40
    for i in anim_idx:
        f = frame(sheet, i, fw, fh)
        s = 5 if fw <= 16 else 3
        big = f.resize((fw * s, fh * s), Image.NEAREST)
        bg = Image.new("RGBA", (big.width + 16, big.height + 16), (60, 48, 80, 255))
        bg.alpha_composite(big, (8, 8))
        if x + bg.width > 800:
            break
        img.alpha_composite(bg, (x, H - 145))
        x += bg.width + 10
    img.convert("RGB").save(os.path.join(OUT, fname))

def make_characters():
    character_sheet(
        "char_embra.png", "embra_sheet.png", 16, 16, 0,
        "EMBRA", "Protagonista · la última brasa de Cenizal",
        [(8, 1, "Corona de llama en 3 capas (rojo, naranja, amarillo) que se mece al moverse", 480, 130),
         (6, 10, "Ojos grandes y oscuros con un brillo: transmiten curiosidad y valentía", 480, 250),
         (11, 13, "Cuerpo redondo de brasa: se lee bien incluso a 16 px", 480, 370),
         (5, 15, "Piernas cortas para correr y saltar", 480, 480)],
        [("Rol", "Héroe jugable. Debe recorrer cuatro zonas y reavivar la Hoguera Eterna."),
         ("Personalidad", "Pequeña, terca y optimista. No habla, se expresa con saltos, chispas y parpadeos de su llama."),
         ("Habilidades", "Correr, saltar (variable), lanzar bolas de fuego (X) y rebotar al pisar enemigos."),
         ("Debilidad", "Una sola herida apaga su llama: pierde una vida y reaparece en el último brasero.")],
        24, [0, 1, 2, 3, 4, 5, 6, 7, 8])
    character_sheet(
        "char_escarchin.png", "escarchin_sheet.png", 16, 16, 0,
        "ESCARCHÍN", "Enemigo común · babosa de hielo",
        [(5, 4, "Picos de hielo en la espalda (silueta fácil de reconocer)", 480, 130),
         (6, 10, "Ojos enojados: se lee como peligro de inmediato", 480, 270),
         (11, 14, "Cuerpo gelatinoso que se aplasta al caminar", 480, 400)],
        [("Rol", "Enemigo básico del Bosque, las Cuevas y la Fortaleza."),
         ("Comportamiento", "Patrulla el suelo a velocidad lenta y da la vuelta al llegar a un borde o pared."),
         ("Cómo vencerlo", "Pisándolo (rebote) o con una bola de fuego. Vale 50 puntos."),
         ("Intención de diseño", "Enseña al jugador que pisar y disparar son dos respuestas válidas.")],
        24, [0, 1])
    character_sheet(
        "char_humoro.png", "humoro_sheet.png", 16, 16, 0,
        "HUMORO", "Enemigo volador · fantasma de humo",
        [(8, 5, "Cabeza de humo claro; el color gris lo separa del fondo de ceniza", 480, 130),
         (6, 7, "Ojos rojos brillantes: lo único cálido de su cuerpo", 480, 250),
         (1, 7, "Alas pequeñas que aletean", 480, 350),
         (8, 13, "Cola ondulada de humo en lugar de piernas", 480, 460)],
        [("Rol", "Enemigo volador presente en las cuatro zonas."),
         ("Comportamiento", "Flota en ondas horizontales y verticales alrededor de su punto de origen."),
         ("Cómo vencerlo", "Pisándolo desde arriba o con una bola de fuego. Vale 75 puntos."),
         ("Intención de diseño", "Obliga a mirar hacia arriba y a medir el tiempo del salto.")],
        24, [0, 1])
    character_sheet(
        "char_gelido.png", "gelido_sheet.png", 32, 32, 0,
        "GÉLIDO", "Jefe final · el Rey de Escarcha",
        [(16, 2, "Corona dorada de tres puntas: símbolo del trono robado", 510, 130),
         (13, 9, "Ojos rojos que brillan como brasas apagadas a la fuerza", 510, 250),
         (16, 22, "Cristal en el pecho: guarda la última chispa", 510, 380),
         (3, 22, "Brazos largos para lanzar astillas de hielo", 510, 500)],
        [("Rol", "Jefe de la Fortaleza Gélida. Robó la última chispa de Cenizal."),
         ("Ataques", "Lanza astillas de hielo bajas (se saltan) y altas (se esquivan en el suelo)."),
         ("Fase 2", "Al llegar a la mitad de su vida se enfurece: se mueve más rápido y convoca un Escarchín."),
         ("Cómo vencerlo", "8 puntos de vida: bolas de fuego (1) o pisotón (2). Al caer, aparece la Hoguera Eterna.")],
        13, [0, 1, 2])

# ----------------------------------------------------------------------------------------------
def make_palette_and_tiles():
    W, H = 1400, 700
    img = paper(W, H)
    d = ImageDraw.Draw(img)
    d.rectangle([0, 0, W, 70], fill=MAROON)
    d.text((28, 12), "PALETA Y TILESETS", font=font(38, True), fill=(255, 240, 200))
    zonas = [("1 · Bosque de Ceniza", 0), ("2 · Cuevas de Escarcha", 1), ("3 · Ruinas de Humo", 2), ("4 · Fortaleza Gélida", 3)]
    tiles = load("tiles.png")
    spikes = load("spikes.png")
    for i, (name, row) in enumerate(zonas):
        x0 = 30 + i * 340
        d.text((x0, 95), name, font=font(20, True), fill=MAROON)
        top = tiles.crop((0, row * 16, 16, row * 16 + 16)).resize((96, 96), Image.NEAREST)
        inner = tiles.crop((16, row * 16, 32, row * 16 + 16)).resize((96, 96), Image.NEAREST)
        sp = spikes.crop((row * 16, 0, row * 16 + 16, 16)).resize((96, 96), Image.NEAREST)
        sky = load("bg_sky_%d.png" % row).resize((300, 169), Image.NEAREST)
        img.alpha_composite(sky, (x0, 130))
        # tira de suelo para ver el tile en contexto
        for k in range(3):
            img.alpha_composite(top.resize((100, 100), Image.NEAREST), (x0 + k * 100, 230))
            img.alpha_composite(inner.resize((100, 100), Image.NEAREST), (x0 + k * 100, 330))
        img.alpha_composite(sp.resize((100, 100), Image.NEAREST), (x0 + 100, 130))
        d.text((x0, 440), "superficie · interior · púas", font=font(15, italic=True), fill=INK)
        cols = top_colors(Image.alpha_composite(top, Image.new("RGBA", top.size, (0, 0, 0, 0))), 4)
        for j, c in enumerate(cols):
            d.rectangle([x0 + j * 75, 465, x0 + j * 75 + 66, 500], fill=c + (255,), outline=INK)
            d.text((x0 + j * 75, 504), hexs(c), font=font(13), fill=INK)
    # paleta de personajes
    d.text((30, 545), "Colores de los personajes", font=font(20, True), fill=MAROON)
    base = [("#2b1320", "Contorno"), ("#c8323c", "Rojo brasa"), ("#f4733a", "Naranja"), ("#ffc93c", "Amarillo"), ("#fff1b0", "Luz"),
            ("#8fd3ff", "Hielo"), ("#3a86c8", "Hielo oscuro"), ("#aab0b8", "Humo")]
    for i, (h, n) in enumerate(base):
        x = 30 + i * 170
        d.rectangle([x, 580, x + 150, 640], fill=h, outline=INK)
        d.text((x, 646), "%s %s" % (n, h), font=font(15), fill=INK)
    img.convert("RGB").save(os.path.join(OUT, "paleta_tiles.png"))

# ----------------------------------------------------------------------------------------------
def render_level(idx):
    lv = make_levels.LEVELS[idx]
    rows = lv["rows"]
    wt, ht = len(rows[0]), len(rows)
    theme = lv["theme"]
    T = 16
    canvas = Image.new("RGBA", (wt * T, ht * T), (0, 0, 0, 255))
    sky = load("bg_sky_%d.png" % theme).resize((480, 288), Image.NEAREST)
    far = load("bg_far_%d.png" % theme)
    near = load("bg_near_%d.png" % theme)
    for x in range(0, wt * T, 480):
        canvas.alpha_composite(sky, (x, 0))
        canvas.alpha_composite(far.resize((480, 288), Image.NEAREST), (x, 0))
        canvas.alpha_composite(near.resize((480, 288), Image.NEAREST), (x, 0))
    tiles = load("tiles.png")
    spikes = load("spikes.png")
    spark = frame(load("spark.png"), 0, 8, 8)
    heart = load("heart.png")
    chk = frame(load("checkpoint.png"), 0, 16, 24)
    hearth = frame(load("hearth.png"), 1, 24, 24)
    walker = frame(load("escarchin_sheet.png"), 0, 16, 16)
    flyer = frame(load("humoro_sheet.png"), 0, 16, 16)
    boss = frame(load("gelido_sheet.png"), 0, 32, 32)
    emb = frame(load("embra_sheet.png"), 0, 16, 16)
    sign = load("sign.png")
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
            elif ch == "S":
                canvas.alpha_composite(spikes.crop((theme * 16, 0, theme * 16 + 16, 16)), (px, py))
            elif ch == "o":
                canvas.alpha_composite(spark, (cx - 4, cy - 4))
            elif ch == "h":
                canvas.alpha_composite(heart, (cx - 5, cy - 5))
            elif ch == "c":
                canvas.alpha_composite(chk, (px, py + 16 - 24))
            elif ch == "G":
                canvas.alpha_composite(hearth, (px - 4, py + 16 - 24))
            elif ch == "w":
                canvas.alpha_composite(walker, (px, py))
            elif ch == "b":
                canvas.alpha_composite(flyer, (px, py))
            elif ch == "B":
                canvas.alpha_composite(boss, (px - 8, py + 16 - 32))
            elif ch == "P":
                canvas.alpha_composite(emb, (px, py))
            elif ch == "t":
                canvas.alpha_composite(sign, (px, py))
            elif ch == "T":
                canvas.alpha_composite(decor, (px + 8 - decor.width // 2, py + 16 - decor.height))
    # dos mitades apiladas para que se pueda leer en un documento
    half = (wt + 1) // 2
    a = canvas.crop((0, 0, half * T, ht * T))
    b = canvas.crop((half * T, 0, wt * T, ht * T))
    out = Image.new("RGBA", (half * T, ht * T * 2 + 10), (30, 20, 40, 255))
    out.alpha_composite(a, (0, 0))
    out.alpha_composite(b, (0, ht * T + 10))
    out.convert("RGB").save(os.path.join(OUT, "mapa_nivel_%d.png" % (idx + 1)))

def make_logo():
    logo = load("logo.png")
    img = paper(900, 330)
    big = logo.resize((logo.width * 3, logo.height * 3), Image.NEAREST)
    img.alpha_composite(big, ((900 - big.width) // 2, 30))
    d = ImageDraw.Draw(img)
    d.text((450, 245), "LA LLAMA ETERNA", font=font(34, True), fill=MAROON, anchor="ma")
    d.text((450, 292), "Logotipo con letras pixeladas de 5x7 y degradado de brasa (amarillo → naranja → rojo)", font=font(16, italic=True), fill=INK, anchor="ma")
    img.convert("RGB").save(os.path.join(OUT, "logo_hoja.png"))

def make_items_sheet():
    img = paper(1400, 420)
    d = ImageDraw.Draw(img)
    d.rectangle([0, 0, 1400, 60], fill=MAROON)
    d.text((28, 8), "OBJETOS Y ELEMENTOS DEL MUNDO", font=font(34, True), fill=(255, 240, 200))
    items = [("Chispa", frame(load("spark.png"), 0, 8, 8), 8, "Moneda: +10 puntos"),
             ("Corazón", load("heart.png"), 8, "Vida extra (máx. 5)"),
             ("Brasero", frame(load("checkpoint.png"), 1, 16, 24), 5, "Punto de control"),
             ("Hoguera Eterna", frame(load("hearth.png"), 1, 24, 24), 4, "Meta de cada nivel"),
             ("Bola de fuego", frame(load("fireball.png"), 0, 8, 8), 8, "Ataque de Embra (X)"),
             ("Astilla de hielo", load("iceshard.png"), 8, "Ataque de Gélido"),
             ("Púas", load("spikes.png").crop((0, 0, 16, 16)), 5, "Daño al contacto"),
             ("Letrero", load("sign.png"), 5, "Consejos del juego")]
    x = 30
    for name, im, s, desc in items:
        big = im.resize((im.width * s, im.height * s), Image.NEAREST)
        bg = Image.new("RGBA", (170, 200), (60, 48, 80, 255))
        bg.alpha_composite(big, ((170 - big.width) // 2, (140 - big.height) // 2 + 10))
        img.alpha_composite(bg, (x, 90))
        d.text((x + 85, 300), name, font=font(18, True), fill=MAROON, anchor="ma")
        for i, ln in enumerate(wrap(d, desc, font(15), 160)):
            d.text((x + 85, 328 + i * 18), ln, font=font(15), fill=INK, anchor="ma")
        x += 172
    img.convert("RGB").save(os.path.join(OUT, "objetos.png"))

if __name__ == "__main__":
    make_characters()
    make_palette_and_tiles()
    for i in range(4):
        render_level(i)
    make_logo()
    make_items_sheet()
    print("Láminas generadas en", os.path.abspath(OUT))
