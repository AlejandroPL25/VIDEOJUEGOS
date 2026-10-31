#!/usr/bin/env python3
"""
Generador de niveles de "EMBRA: Bosque de Brasas" (según el GDD de la Fase 2):
  Nivel 1  Bosque de Brasas   introduce movimiento, salto, chispas, Rondines y una zona de fuego (boceto del GDD)
  Nivel 2  Cañón Humeante     introduce las zonas de fuego y humo
  Nivel 3  Ruinas de Carbón   enemigos + zonas de fuego con plataformas más exigentes
  Nivel 4  El Altar           nivel final que combina todas las mecánicas
Cada nivel se construye con funciones (suelo, huecos, plataformas) que respetan los límites del salto:
  - Hueco máximo: 3 tiles   - Escalón máximo hacia arriba: 2-3 tiles
Las posiciones se dan RELATIVAS al inicio de cada tramo para evitar errores de conteo.
Salida: scripts/level_data.gd y docs/niveles_ascii.txt

Leyenda:
  #  suelo / plataforma     o  chispa (moneda)     P  inicio de Embra    
  R  Rondín furioso (carga)  B  Rondín gigante (2 de vida)  a  Ceniza (enemigo volador)
  R  Rondín furioso (carga)  B  Rondín gigante (2 de vida)  a  Ceniza (enemigo volador)
  F  zona de fuego y humo   c  brasero (punto de control)    G  altar (meta)    T  decoración de fondo
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
        """Suelo que llega hasta el fondo del mapa. Devuelve la columna de inicio y avanza el cursor."""
        start = self.cur
        for x in range(start, start + length):
            for y in range(top, HEIGHT):
                self.put(x, y, "#")
        self.cur += length
        return start

    def plat(self, length, top, thick=2):
        """Plataforma flotante de 'thick' filas (queda vacío por debajo: hay vacío)."""
        start = self.cur
        for x in range(start, start + length):
            for y in range(top, top + thick):
                self.put(x, y, "#")
        self.cur += length
        return start

    def gap(self, n):
        self.cur += n

    def sparks(self, xs, y):
        for x in xs:
            self.put(x, y, "o")

    def arc(self, x0, x1, ybase, peak=2):
        """Arco de chispas que guía el salto."""
        n = x1 - x0 + 1
        for i, x in enumerate(range(x0, x1 + 1)):
            t = 0 if n == 1 else i / (n - 1)
            self.put(x, ybase - int(round(peak * 4 * t * (1 - t))), "o")

    def fire(self, x, top, w):
        """Zona de fuego y humo de w tiles de ancho sobre una superficie cuyo borde superior es 'top'."""
        for i in range(w):
            self.put(x + i, top - 1, "F")

    def rows(self):
        """Devuelve las filas recortadas al último tile usado (así el ancho nunca queda corto ni sobrado)."""
        last = max(x for y in range(HEIGHT) for x in range(self.w) if self.g[y][x] != " ")
        return ["".join(r[: last + 1]) for r in self.g]


# ------------------------------------------------------------------ Nivel 1
def nivel1():
    """Sigue el boceto del GDD: inicio, plataforma con chispa, plataformas con Rondín, zona de fuego y meta."""
    L = Lvl(300)
    a = L.seg(22, 14)                              # tramo inicial para aprender a moverse
    L.put(a + 3, 13, "P"); L.put(a + 5, 13, "T"); L.put(a + 16, 13, "T")
    L.sparks(range(a + 8, a + 14), 13)
    L.gap(2)                                       # primer salto, un hueco pequeño
    L.arc(a + 20, a + 27, 12, 2)
    b = L.seg(6, 14)                               # isla corta
    L.sparks([b + 2, b + 3], 12)
    L.gap(3)
    p1 = L.plat(8, 13)                             # plataforma 1 (baja) con chispa
    L.put(p1 + 4, 10, "o")
    L.gap(3)
    p2 = L.plat(9, 11)                             # plataforma 2: primer Rondín + chispa
    L.put(p2 + 2, 10, "r"); L.put(p2 + 7, 8, "o")
    L.sparks([p2 + 4, p2 + 5], 8)
    L.gap(3)
    p3 = L.plat(10, 9)                             # plataforma 3 (alta): Rondín, brasero y chispa
    L.put(p3 + 2, 8, "r"); L.put(p3 + 8, 8, "c"); L.put(p3 + 6, 5, "o")
    L.gap(3)
    p4 = L.plat(11, 11)                            # plataforma 4: zona de fuego y chispa encima
    L.fire(p4 + 4, 11, 3); L.put(p4 + 5, 7, "o"); L.sparks([p4 + 2, p4 + 9], 9)
    L.gap(3)
    m = L.seg(18, 14)                              # plataforma de la meta
    L.put(m + 1, 13, "c"); L.put(m + 4, 13, "T"); L.sparks([m + 6, m + 7, m + 8], 12)
    L.put(m + 13, 13, "G")
    return dict(name="Bosque de Brasas", theme=0, music="music_bosque", rows=L.rows())


# ------------------------------------------------------------------ Nivel 2
def nivel2():
    """Cañón Humeante: aquí se presentan las zonas de fuego y humo."""
    L = Lvl(300)
    a = L.seg(34, 13)
    L.put(a + 3, 12, "P"); L.sparks(range(a + 6, a + 11), 12); L.put(a + 8, 12, "T")
    L.fire(a + 16, 13, 3)                          # primera zona de fuego, en suelo plano
    L.arc(a + 13, a + 21, 11, 3)
    L.put(a + 27, 12, "T")
    L.gap(3)
    b = L.seg(16, 12)                              # dos zonas de fuego con un espacio seguro en medio
    L.fire(b + 3, 12, 2); L.fire(b + 8, 12, 2)
    L.sparks([b + 5, b + 6], 9)
    L.put(b + 14, 11, "c")
    L.seg(4, 11)                                   # escalones hacia arriba
    L.seg(4, 10)
    c = L.seg(14, 9)                               # cornisa alta con un Rondín
    L.put(c + 3, 8, "r"); L.sparks([c + 8, c + 9, c + 10], 6)
    L.put(c + 12, 8, "T")
    L.gap(3)
    d = L.plat(6, 11)                              # cruce del cañón en plataformas
    L.sparks([d + 2, d + 3], 8)
    L.put(d + 5, 6, "a")                           # Ceniza voladora sobre el cruce
    L.put(d + 5, 6, "a")                           # Ceniza voladora sobre el cruce
    L.gap(3)
    e = L.plat(9, 12)
    L.fire(e + 3, 12, 2); L.put(e + 3, 8, "o"); L.put(e + 4, 8, "o")
    L.gap(3)
    f = L.plat(6, 11)
    L.put(f + 3, 7, "o"); L.put(f + 1, 5, "a")
    L.gap(3)
    g = L.seg(20, 13)                              # segundo tramo: brasero, Rondín y zonas de fuego
    L.put(g + 1, 12, "c"); L.put(g + 8, 12, "r")
    L.fire(g + 5, 13, 2); L.fire(g + 14, 13, 3)
    L.arc(g + 12, g + 18, 11, 3)
    L.put(g + 10, 12, "T")
    L.gap(3)
    h = L.seg(24, 13)
    L.put(h + 3, 12, "r"); L.sparks([h + 6, h + 7, h + 8], 10)
    L.put(h + 12, 12, "T")
    L.put(h + 19, 12, "G")
    return dict(name="Cañón Humeante", theme=1, music="music_canon", rows=L.rows())


# ------------------------------------------------------------------ Nivel 3
def nivel3():
    """Ruinas de Carbón: más Rondines y zonas de fuego sobre plataformas más estrechas."""
    L = Lvl(300)
    a = L.seg(16, 14)
    L.put(a + 3, 13, "P"); L.sparks(range(a + 6, a + 11), 12); L.put(a + 12, 13, "T")
    L.gap(3)
    b = L.plat(7, 13)                              # Rondín en plataforma pequeña
    L.put(b + 2, 12, "r"); L.sparks([b + 4, b + 5], 9)
    L.gap(3)
    c = L.plat(9, 12)
    L.fire(c + 3, 12, 2); L.put(c + 3, 8, "o"); L.put(c + 4, 8, "o"); L.put(c + 7, 6, "a")
    L.gap(3)
    d = L.seg(14, 13)
    L.put(d + 1, 12, "c"); L.put(d + 5, 12, "R"); L.put(d + 11, 12, "T")
    L.sparks([d + 8, d + 9, d + 10], 10)
    L.seg(3, 11)                                   # torre de escalones
    L.seg(3, 9)
    t = L.seg(8, 7)                                # parte alta con zona de fuego
    L.fire(t + 3, 7, 2); L.sparks([t + 2, t + 5, t + 6], 4)
    L.put(t + 7, 6, "T")
    L.seg(3, 9)
    L.seg(3, 11)
    e = L.seg(12, 13)
    L.put(e + 3, 12, "R"); L.put(e + 8, 12, "r"); L.sparks([e + 5, e + 6], 10)
    L.gap(3)
    f = L.plat(6, 12)
    L.put(f + 3, 11, "r")
    L.gap(3)
    g = L.plat(6, 11)
    L.fire(g + 2, 11, 2)
    L.put(g + 2, 7, "o"); L.put(g + 3, 7, "o")
    L.gap(3)
    h = L.plat(6, 12)
    L.put(h + 3, 8, "o")
    L.gap(3)
    i = L.seg(18, 14)
    L.put(i + 1, 13, "c"); L.fire(i + 5, 14, 3); L.put(i + 11, 13, "r"); L.put(i + 15, 13, "T")
    L.arc(i + 3, i + 9, 12, 3)
    L.gap(3)
    j = L.seg(9, 13)
    L.fire(j + 3, 13, 3); L.arc(j + 1, j + 7, 11, 3)
    L.gap(3)
    k = L.seg(12, 13)
    L.put(k + 3, 12, "r"); L.put(k + 8, 12, "R"); L.sparks([k + 5, k + 6], 10); L.put(k + 5, 7, "a")
    L.seg(2, 12)
    L.seg(2, 10)
    m = L.seg(26, 14)
    L.put(m + 1, 13, "c"); L.fire(m + 8, 14, 2); L.put(m + 12, 13, "r"); L.put(m + 16, 13, "T")
    L.sparks([m + 4, m + 5, m + 6], 11)
    L.put(m + 22, 13, "G")
    return dict(name="Ruinas de Carbón", theme=2, music="music_ruinas", rows=L.rows())


# ------------------------------------------------------------------ Nivel 4
def nivel4():
    """El Altar: combina plataformas, Rondines, zonas de fuego y vacíos en la subida final al altar."""
    L = Lvl(300)
    a = L.seg(14, 14)
    L.put(a + 3, 13, "P"); L.sparks(range(a + 6, a + 11), 12)
    L.gap(3)
    b = L.plat(8, 13)
    L.put(b + 2, 12, "r"); L.sparks([b + 5, b + 6], 10)
    L.gap(3)
    c = L.plat(8, 12)
    L.fire(c + 3, 12, 2); L.put(c + 3, 8, "o"); L.put(c + 4, 8, "o")
    L.gap(3)
    d = L.seg(16, 13)
    L.put(d + 1, 12, "c"); L.put(d + 6, 12, "R"); L.fire(d + 10, 13, 3); L.arc(d + 8, d + 14, 11, 3)
    L.put(d + 14, 12, "T")
    L.gap(3)
    e = L.plat(7, 12)
    L.put(e + 3, 8, "o")
    L.gap(3)
    f = L.plat(8, 11)
    L.put(f + 2, 10, "r"); L.sparks([f + 5, f + 6], 8)
    L.gap(3)
    g = L.plat(8, 10)
    L.fire(g + 3, 10, 2); L.put(g + 3, 6, "o"); L.put(g + 4, 6, "o")
    L.gap(3)
    h = L.seg(14, 12)
    L.put(h + 1, 11, "c"); L.put(h + 6, 11, "B"); L.put(h + 12, 11, "T"); L.put(h + 9, 6, "a")
    L.sparks([h + 3, h + 4], 9)
    L.seg(3, 10)                                   # subida por escalones
    L.seg(3, 8)
    i = L.seg(10, 6)
    L.fire(i + 3, 6, 3); L.arc(i + 1, i + 8, 4, 2)
    L.gap(3)
    j = L.plat(6, 7)
    L.put(j + 3, 6, "r")
    L.gap(3)
    k = L.plat(8, 8)
    L.fire(k + 3, 8, 2); L.put(k + 3, 4, "o"); L.put(k + 4, 4, "o")
    L.gap(3)
    l = L.seg(16, 9)
    L.put(l + 1, 8, "c"); L.put(l + 6, 8, "B"); L.fire(l + 10, 9, 3); L.arc(l + 8, l + 14, 6, 3)
    L.put(l + 14, 8, "T")
    L.seg(3, 8)
    L.seg(3, 7)
    m = L.seg(26, 6)                               # tramo final hasta el altar
    L.put(m + 1, 5, "c"); L.put(m + 6, 5, "R"); L.fire(m + 10, 6, 2); L.fire(m + 15, 6, 2); L.put(m + 12, 1, "a")
    L.sparks([m + 3, m + 4], 3); L.arc(m + 8, m + 13, 3, 2)
    L.put(m + 19, 5, "T"); L.put(m + 22, 5, "G")
    return dict(name="El Altar", theme=3, music="music_altar", rows=L.rows())


LEVELS = [nivel1(), nivel2(), nivel3(), nivel4()]


def to_gd():
    out = ["# Generado por tools/make_levels.py -- NO editar a mano (edita el generador y vuelve a correrlo)",
           "# Leyenda: # suelo, o chispa, P inicio, r Rondín, F zona de fuego y humo, c brasero (punto de control),",
           "#          G altar (meta), T decoración",
           "class_name LevelData", "", "const LEVELS := ["]
    for lv in LEVELS:
        out.append("\t{")
        out.append(f'\t\t"name": "{lv["name"]}",')
        out.append(f'\t\t"theme": {lv["theme"]},')
        out.append(f'\t\t"music": "{lv["music"]}",')
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
        print(f"Nivel {i}: {len(lv['rows'][0])} cols | chispas={flat.count('o')} Rondines={flat.count('r')} furiosos={flat.count('R')} gigantes={flat.count('B')} Cenizas={flat.count('a')} fuego={flat.count('F')} puntos_control={flat.count('c')}")
    print("level_data.gd generado")
