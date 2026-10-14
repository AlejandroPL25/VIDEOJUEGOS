#!/usr/bin/env python3
"""
Generador de niveles de "Embra: La Llama Eterna".
Cada nivel se construye con funciones (suelo, huecos, plataformas) que respetan los límites del salto:
  - Hueco máximo: 3 tiles   - Escalón máximo hacia arriba: 3 tiles (se usan 1-2 casi siempre)
Salida: scripts/level_data.gd  (const LEVELS con filas ASCII) y docs/niveles_ascii.txt

Leyenda:
  #  suelo sólido        S  púas (daño)       o  chispa (moneda)     h  corazón (vida extra)
  P  inicio de Embra     w  Escarchín (patrulla)   b  Humoro (vuela)    c  brasero (checkpoint)
  G  Hoguera Eterna (meta)   B  jefe Gélido     t  letrero con consejo    T  decoración de fondo
"""
import os

HEIGHT = 18

class Lvl:
    def __init__(self, width):
        self.w = width
        self.g = [[" "] * width for _ in range(HEIGHT)]
        self.cur = 0

    def put(self, x, y, ch):
        if 0 <= x < self.w and 0 <= y < HEIGHT:
            self.g[y][x] = ch

    def seg(self, length, top):
        """Suelo de 'length' columnas con superficie en la fila 'top'. Avanza el cursor."""
        for x in range(self.cur, self.cur + length):
            for y in range(top, HEIGHT):
                self.put(x, y, "#")
        start = self.cur
        self.cur += length
        return start

    def gap(self, n):
        self.cur += n

    def plat(self, x0, x1, y):
        for x in range(x0, x1 + 1):
            self.put(x, y, "#")

    def wall(self, x0, x1, y0, y1):
        for x in range(x0, x1 + 1):
            for y in range(y0, y1 + 1):
                self.put(x, y, "#")

    def sparks(self, xs, y):
        for x in xs:
            self.put(x, y, "o")

    def arc(self, x0, x1, ybase, peak=2):
        """Arco de chispas que guía el salto sobre un hueco."""
        n = x1 - x0 + 1
        for i, x in enumerate(range(x0, x1 + 1)):
            t = 0 if n == 1 else i / (n - 1)
            h = int(round(peak * 4 * t * (1 - t)))
            self.put(x, ybase - h, "o")

    def rows(self):
        return ["".join(r) for r in self.g]


# ------------------------------------------------------------------ Nivel 1
def nivel1():
    L = Lvl(152)
    L.seg(24, 14)
    L.put(3, 13, "P"); L.put(6, 13, "t"); L.sparks(range(9, 13), 13)
    L.put(18, 13, "t"); L.put(20, 13, "T"); L.put(14, 13, "T")
    L.seg(12, 13)                         # 24-35
    L.arc(34, 39, 12, 2)
    L.gap(2)                              # 36-37
    L.seg(14, 13)                         # 38-51
    L.put(41, 12, "t"); L.put(47, 12, "w")
    L.arc(50, 56, 12, 2)
    L.gap(3)                              # 52-54
    L.seg(10, 14)                         # 55-64
    L.put(56, 13, "t"); L.put(60, 13, "w"); L.put(63, 13, "c"); L.put(58, 13, "T")
    L.gap(2)                              # 65-66
    L.seg(3, 12)                          # 67-69 pilar
    L.put(68, 10, "h"); L.sparks([67, 69], 10)
    L.seg(3, 13)                          # 70-72
    L.seg(9, 14)                          # 73-81
    L.put(77, 13, "w"); L.put(80, 13, "T")
    L.arc(80, 85, 13, 2)
    L.gap(3)                              # 82-84
    L.seg(10, 14)                         # 85-94
    L.put(88, 9, "b"); L.put(87, 13, "S")
    L.sparks([89, 90], 12)
    L.gap(2)                              # 95-96
    L.seg(16, 13)                         # 97-112
    L.put(98, 12, "c"); L.put(102, 12, "w"); L.put(107, 12, "w"); L.put(110, 12, "T")
    L.sparks([100, 101, 104, 105], 11)
    L.gap(3)                              # 113-115
    L.plat(116, 118, 12); L.sparks([116, 117, 118], 11)
    L.plat(121, 123, 11); L.sparks([121, 122, 123], 10)
    L.plat(126, 128, 12); L.sparks([126, 127, 128], 11)
    L.put(122, 8, "b")
    L.cur = 131
    L.seg(21, 13)                         # 131-151
    L.put(135, 12, "w"); L.put(140, 12, "T")
    L.put(147, 12, "G")
    return dict(
        name="Bosque de Ceniza", theme=0, music="music_bosque", rows=L.rows(),
        hints=["Muévete con A / D o con las flechas",
               "Salta con ESPACIO. Mantén presionado para saltar más alto",
               "Salta sobre los enemigos para vencerlos",
               "Presiona X para lanzar una bola de fuego"])


# ------------------------------------------------------------------ Nivel 2
def nivel2():
    L = Lvl(176)
    L.seg(12, 13)
    L.put(3, 12, "P"); L.put(8, 12, "t"); L.sparks(range(5, 11), 11)
    L.seg(6, 13)                          # 12-17
    L.put(15, 12, "S"); L.sparks([14, 15, 16], 10)
    L.seg(9, 13)                          # 18-26
    L.put(22, 7, "b"); L.put(25, 12, "T")
    L.gap(3)                              # 27-29
    L.arc(26, 31, 11, 2)
    L.seg(7, 12)                          # 30-36
    L.put(34, 11, "w")
    L.seg(10, 12)                         # 37-46
    L.put(40, 11, "S"); L.put(41, 11, "S"); L.put(42, 11, "S")
    L.sparks([40, 41, 42], 8)
    L.put(45, 11, "c")
    L.gap(3)                              # 47-49
    L.seg(8, 10)                          # 50-57
    L.put(53, 9, "T"); L.sparks([51, 52, 54, 55], 8)
    L.put(54, 4, "b")
    L.seg(3, 11)                          # 58-60
    L.seg(3, 12)                          # 61-63
    L.seg(12, 13)                         # 64-75
    L.put(68, 12, "w"); L.put(72, 12, "w"); L.put(66, 12, "h")
    L.gap(3)                              # 76-78
    L.plat(79, 81, 12); L.sparks([79, 80, 81], 11)
    L.plat(84, 86, 11); L.sparks([84, 85, 86], 10)
    L.plat(89, 91, 10); L.sparks([89, 90, 91], 9)
    L.plat(94, 96, 11); L.sparks([94, 95, 96], 10)
    L.put(87, 6, "b"); L.put(92, 5, "b")
    L.cur = 99
    L.seg(14, 12)                         # 99-112
    L.put(100, 11, "c"); L.put(105, 11, "w"); L.put(108, 11, "S"); L.put(109, 11, "S")
    L.sparks([105, 106, 107], 9)
    L.gap(3)                              # 113-115
    L.seg(9, 12)                          # 116-124
    L.put(119, 11, "w"); L.put(122, 11, "t")
    L.seg(2, 10)                          # 125-126
    L.seg(2, 8)                           # 127-128 (escalón 2)
    L.sparks([127, 128], 6)
    L.seg(10, 12)                         # 129-138 (caída)
    L.put(133, 11, "w"); L.put(136, 7, "b"); L.put(131, 11, "S")
    L.sparks([131, 132, 133, 134], 9)
    L.gap(3)                              # 139-141
    L.seg(6, 12)                          # 142-147
    L.put(144, 11, "h"); L.put(146, 11, "T")
    L.seg(2, 12)
    L.seg(1, 12)
    L.gap(2)                              # 151-152
    L.seg(25, 13)                         # 153-177 (ajusta ancho)
    L.put(156, 12, "c"); L.put(160, 12, "w"); L.put(165, 12, "w")
    L.put(172, 12, "G")
    return dict(
        name="Cuevas de Escarcha", theme=1, music="music_cuevas", rows=L.rows(),
        hints=["Las púas lastiman: salta sobre ellas. Los braseros guardan tu avance",
               "Los Humoros vuelan en ondas: espera el momento y pasa por debajo"])


# ------------------------------------------------------------------ Nivel 3
def nivel3():
    """Ruinas de Humo. Las posiciones se dan RELATIVAS al inicio de cada tramo (evita errores de conteo)."""
    L = Lvl(200)
    a = L.seg(14, 14)
    L.put(3, 13, "P"); L.sparks(range(6, 12), 12)
    L.put(10, 13, "T")
    b = L.seg(6, 14)                      # tramo corto con un Escarchín
    L.put(b + 3, 13, "w")
    L.gap(3)
    s = L.cur                             # tres plataformas flotantes
    L.plat(s, s + 2, 12); L.sparks([s, s + 1, s + 2], 11)
    L.plat(s + 5, s + 7, 11); L.sparks([s + 5, s + 6, s + 7], 10)
    L.plat(s + 10, s + 12, 12)
    L.put(s + 6, 6, "b")
    L.cur = s + 15
    g = L.seg(12, 14)                     # primer brasero y púas
    L.put(g + 2, 13, "c"); L.put(g + 6, 13, "S"); L.put(g + 7, 13, "S"); L.put(g + 9, 13, "w")
    L.sparks([g + 6, g + 7], 11)
    L.gap(3)
    L.seg(3, 12)                          # torre en escalones de 2
    L.seg(3, 10)
    t3 = L.seg(3, 8)
    L.sparks([t3, t3 + 1, t3 + 2], 7); L.put(t3 + 1, 5, "b")
    L.seg(3, 10)
    L.seg(3, 12)
    g = L.seg(10, 14)
    L.put(g + 3, 13, "w"); L.put(g + 7, 13, "w"); L.put(g + 1, 13, "T")
    L.gap(3)
    g = L.seg(5, 13)
    L.put(g + 2, 12, "h")
    L.seg(2, 13)
    L.gap(2)
    g = L.seg(9, 14)                      # púas, Escarchín y brasero antes del puente
    L.put(g + 2, 13, "S"); L.put(g + 3, 13, "S"); L.put(g + 5, 13, "w"); L.put(g + 7, 13, "c")
    L.sparks([g + 2, g + 3], 11)
    L.put(g + 4, 8, "b")
    L.gap(3)
    s = L.cur                             # puente de plataformas
    L.plat(s, s + 2, 12); L.plat(s + 5, s + 7, 11); L.plat(s + 10, s + 12, 10)
    L.plat(s + 15, s + 17, 11); L.plat(s + 20, s + 22, 12)
    L.sparks([s, s + 1, s + 2, s + 5, s + 6, s + 7, s + 10, s + 11, s + 12, s + 15, s + 16, s + 17], 8)
    L.put(s + 3, 6, "b"); L.put(s + 13, 6, "b")
    L.cur = s + 25
    g = L.seg(12, 14)
    L.put(g + 2, 13, "c"); L.put(g + 6, 13, "w"); L.put(g + 9, 13, "S")
    L.seg(2, 12)
    L.seg(2, 10)
    L.seg(2, 12)
    g = L.seg(8, 14)
    L.put(g + 2, 13, "w"); L.put(g + 5, 13, "T"); L.put(g + 5, 8, "b")
    L.gap(3)
    g = L.seg(7, 14)
    for i in (2, 3, 4):
        L.put(g + i, 13, "S")
    L.sparks([g + 2, g + 3, g + 4], 10)
    L.gap(2)
    g = L.seg(30, 14)
    L.put(g + 1, 13, "c"); L.put(g + 7, 13, "w"); L.put(g + 12, 13, "w"); L.put(g + 17, 13, "w")
    L.put(g + 10, 8, "b"); L.put(g + 21, 13, "h")
    L.put(g + 25, 13, "G")
    return dict(
        name="Ruinas de Humo", theme=2, music="music_ruinas", rows=L.rows(),
        hints=[])


# ------------------------------------------------------------------ Nivel 4 (jefe)
def nivel4():
    L = Lvl(100)
    L.seg(16, 13)
    L.put(3, 12, "P"); L.put(6, 12, "t"); L.sparks(range(8, 14), 11)
    L.seg(8, 13)                          # 16-23
    L.put(20, 12, "S"); L.put(21, 12, "S"); L.put(22, 12, "w")
    L.gap(3)                              # 24-26
    L.seg(9, 12)                          # 27-35
    L.put(30, 11, "w"); L.put(33, 6, "b"); L.put(29, 11, "c")
    L.gap(3)                              # 36-38
    L.plat(39, 41, 11); L.sparks([39, 40, 41], 10)
    L.plat(44, 46, 10); L.sparks([44, 45, 46], 9)
    L.put(43, 6, "b")
    L.cur = 49
    L.seg(8, 12)                          # 49-56
    L.put(51, 11, "h"); L.put(54, 11, "c"); L.put(55, 11, "t")
    L.seg(43, 13)                         # 57-99 (arena)
    L.wall(98, 99, 0, 12)                 # pared del fondo
    L.plat(68, 71, 10)
    L.plat(84, 87, 10)
    L.put(77, 12, "G")
    L.put(90, 12, "B")
    L.sparks([69, 70], 9); L.sparks([85, 86], 9)
    return dict(
        name="Fortaleza Gélida", theme=3, music="music_fortaleza", rows=L.rows(),
        hints=["Gélido guarda la última chispa. Pronto lo enfrentarás",
               "Dispárale con X y esquiva sus astillas: salta las bajas y quédate en el suelo ante las altas"])


LEVELS = [nivel1(), nivel2(), nivel3(), nivel4()]

def to_gd():
    out = ["# Generado por tools/make_levels.py -- NO editar a mano (edita el generador y vuelve a correrlo)",
           "# Leyenda: # suelo, S púas, o chispa, h corazón, P inicio, w Escarchín, b Humoro,",
           "#          c brasero, G Hoguera Eterna, B jefe Gélido, t letrero, T decoración",
           "class_name LevelData", "", "const LEVELS := ["]
    for lv in LEVELS:
        out.append("\t{")
        out.append(f'\t\t"name": "{lv["name"]}",')
        out.append(f'\t\t"theme": {lv["theme"]},')
        out.append(f'\t\t"music": "{lv["music"]}",')
        hints = ", ".join('"%s"' % h for h in lv["hints"])
        out.append(f'\t\t"hints": [{hints}],')
        out.append('\t\t"rows": [')
        for r in lv["rows"]:
            out.append(f'\t\t\t"{r}",')
        out.append("\t\t],")
        out.append("\t},")
    out.append("]")
    return "\n".join(out) + "\n"

if __name__ == "__main__":
    base = os.path.join(os.path.dirname(__file__), "..")
    with open(os.path.join(base, "scripts", "level_data.gd"), "w", encoding="utf-8") as f:
        f.write(to_gd())
    with open(os.path.join(base, "docs", "niveles_ascii.txt"), "w", encoding="utf-8") as f:
        for i, lv in enumerate(LEVELS, 1):
            f.write(f"=== Nivel {i}: {lv['name']} ({len(lv['rows'][0])}x{len(lv['rows'])}) ===\n")
            f.write("\n".join(lv["rows"]) + "\n\n")
    for i, lv in enumerate(LEVELS, 1):
        flat = "".join(lv["rows"])
        print(f"Nivel {i}: {len(lv['rows'][0])} cols | chispas={flat.count('o')} enemigos={flat.count('w')+flat.count('b')} púas={flat.count('S')}")
    print("level_data.gd generado")
