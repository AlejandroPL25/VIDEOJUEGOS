#!/usr/bin/env python3
"""
Genera los documentos del proyecto en Word (docs/*.docx) para "EMBRA: Bosque de Brasas":
  - Bitacora_de_Desarrollo.docx
  - Biblia_del_Videojuego.docx
  - Reporte_de_Pruebas.docx (una cuartilla + anexo con protocolo)
  - Plan_de_Accion.docx
Uso: python3 tools/make_docs.py
"""
import os
import subprocess
from docx import Document
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_BREAK
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Inches, Pt, RGBColor

BASE = os.path.join(os.path.dirname(__file__), "..")
DOCS = os.path.join(BASE, "docs")
ART = os.path.join(DOCS, "biblia_art")
IMG = os.path.join(DOCS, "img")
GDDM = os.path.join(DOCS, "gdd_media")
NAVY = RGBColor(0x2E, 0x3A, 0x59)
AMBER = RGBColor(0xC9, 0x7F, 0x17)
GREY = RGBColor(0x55, 0x55, 0x55)
HEAD_FILL = "2E3A59"


# ------------------------------------------------------------------ utilidades
def new_doc(margins=1.0, base_size=11):
    d = Document()
    for s in d.sections:
        s.left_margin = s.right_margin = Inches(margins)
        s.top_margin = s.bottom_margin = Inches(margins)
    st = d.styles["Normal"]
    st.font.name = "Calibri"
    st.font.size = Pt(base_size)
    st.element.rPr.rFonts.set(qn("w:eastAsia"), "Calibri")
    st.paragraph_format.space_after = Pt(6)
    for name, size, color in (("Heading 1", 20, NAVY), ("Heading 2", 15, NAVY), ("Heading 3", 12.5, AMBER)):
        h = d.styles[name]
        h.font.name = "Calibri"
        h.font.size = Pt(size)
        h.font.bold = True
        h.font.color.rgb = color
        h.element.rPr.rFonts.set(qn("w:eastAsia"), "Calibri")
        h.paragraph_format.space_before = Pt(14 if name == "Heading 1" else 10)
        h.paragraph_format.space_after = Pt(6)
    add_page_number(d.sections[0])
    return d


def add_page_number(section):
    p = section.footer.paragraphs[0]
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = p.add_run()
    for tag, text in (("begin", None), (None, "PAGE"), ("end", None)):
        if tag:
            el = OxmlElement("w:fldChar")
            el.set(qn("w:fldCharType"), tag)
        else:
            el = OxmlElement("w:instrText")
            el.set(qn("xml:space"), "preserve")
            el.text = text
        run._r.append(el)
    run.font.size = Pt(9)
    run.font.color.rgb = GREY


def shade(cell, hex_color):
    tcPr = cell._tc.get_or_add_tcPr()
    shd = OxmlElement("w:shd")
    shd.set(qn("w:val"), "clear")
    shd.set(qn("w:color"), "auto")
    shd.set(qn("w:fill"), hex_color)
    tcPr.append(shd)


def para(d, text="", bold=False, italic=False, size=None, color=None, align=None, after=None, style=None):
    p = d.add_paragraph(style=style)
    if text:
        r = p.add_run(text)
        r.bold = bold
        r.italic = italic
        if size:
            r.font.size = Pt(size)
        if color:
            r.font.color.rgb = color
    if align:
        p.alignment = align
    if after is not None:
        p.paragraph_format.space_after = Pt(after)
    return p


def rich(d, parts, style=None, after=None):
    p = d.add_paragraph(style=style)
    for text, fmt in parts:
        r = p.add_run(text)
        r.bold = fmt.get("b", False)
        r.italic = fmt.get("i", False)
        if fmt.get("hl"):
            r.font.highlight_color = 7
    if after is not None:
        p.paragraph_format.space_after = Pt(after)
    return p


def bullet(d, text, bold_prefix=None):
    p = d.add_paragraph(style="List Bullet")
    if bold_prefix:
        r = p.add_run(bold_prefix)
        r.bold = True
    p.add_run(text)
    p.paragraph_format.space_after = Pt(3)
    return p


def table(d, header, rows, widths=None, font=9.5, head_fill=HEAD_FILL):
    t = d.add_table(rows=1, cols=len(header))
    t.style = "Table Grid"
    t.alignment = WD_TABLE_ALIGNMENT.CENTER
    for i, h in enumerate(header):
        c = t.rows[0].cells[i]
        c.text = ""
        r = c.paragraphs[0].add_run(h)
        r.bold = True
        r.font.size = Pt(font)
        r.font.color.rgb = RGBColor(255, 255, 255)
        shade(c, head_fill)
    for row in rows:
        cells = t.add_row().cells
        for i, val in enumerate(row):
            cells[i].text = ""
            p = cells[i].paragraphs[0]
            p.paragraph_format.space_after = Pt(2)
            r = p.add_run(str(val))
            r.font.size = Pt(font)
    if widths:
        t.autofit = False
        for i, w in enumerate(widths):
            t.columns[i].width = Inches(w)
        for row in t.rows:
            for i, w in enumerate(widths):
                row.cells[i].width = Inches(w)
    d.add_paragraph().paragraph_format.space_after = Pt(2)
    return t


def picture(d, path, width=6.3, caption=None):
    if not os.path.exists(path):
        raise FileNotFoundError(path)
    p = d.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.add_run().add_picture(path, width=Inches(width))
    p.paragraph_format.space_after = Pt(2)
    if caption:
        para(d, caption, italic=True, size=9, color=GREY, align=WD_ALIGN_PARAGRAPH.CENTER, after=8)


def page_break(d):
    d.add_paragraph().add_run().add_break(WD_BREAK.PAGE)


def title_block(d, title, subtitle, lines):
    para(d, title, bold=True, size=26, color=NAVY, align=WD_ALIGN_PARAGRAPH.CENTER, after=2)
    para(d, subtitle, italic=True, size=13, color=AMBER, align=WD_ALIGN_PARAGRAPH.CENTER, after=10)
    for ln in lines:
        para(d, ln, size=10.5, color=GREY, align=WD_ALIGN_PARAGRAPH.CENTER, after=0)
    d.add_paragraph()


def git_log():
    out = subprocess.run(["git", "log", "--reverse", "--format=%h|%ad|%s", "--date=format:%d/%m/%Y"],
                         cwd=BASE, capture_output=True, text=True).stdout
    return [tuple(ln.split("|", 2)) for ln in out.strip().splitlines()]


# ================================================================== BITÁCORA
def bitacora():
    d = new_doc()
    title_block(d, "Bitácora de desarrollo", "EMBRA: Bosque de Brasas · prototipo funcional",
                ["Motor: Godot 4.3 (GDScript)  ·  Control de versiones: Git", "Universidad Tecmilenio · Proyecto integrador de videojuegos"])

    d.add_heading("1. Datos del proyecto", 1)
    table(d, ["Concepto", "Detalle"], [
        ("Videojuego", "EMBRA: Bosque de Brasas, plataformas 2D en pixel art (según el GDD de la Fase 2)"),
        ("Motor y lenguaje", "Godot 4.3 con GDScript. Nota: el GDD planteó Unity; para esta actividad el prototipo se reconstruyó en Godot"),
        ("Alcance del prototipo", "3 niveles progresivos más el nivel final \"El Altar\", Rondines, zonas de fuego y humo con partículas, penalizaciones, tabla de mejor puntaje por nivel, música y efectos de sonido"),
        ("Plataformas exportadas", "Windows (.exe) como plataforma principal del GDD; también Linux y Web"),
        ("Código", "Aprox. 1,500 líneas de GDScript, todas comentadas, más herramientas en Python para generar arte, audio y niveles"),
        ("Repositorio", "Git local con un commit por etapa (sección 5)"),
    ], widths=[1.8, 4.7])

    d.add_heading("2. Cómo trabajé", 1)
    para(d, "Mas que nada seguí el GDD y el diagrama de Gantt: primero las mecánicas básicas, luego enemigos y penalizaciones, el sistema de partículas, los niveles, el audio, "
            "las pruebas y la compilación. Cada etapa la cerré con un commit en Git para poder regresar si algo se rompía, y todo el código lleva comentarios en español "
            "para entender qué hace cada parte sin tener que adivinar.")
    para(d, "Siendo completamente honesto, el arte y el audio los generé por código porque los sitios de assets no estaban disponibles desde mi entorno de trabajo: "
            "los sprites están dibujados en pixel art con la paleta del GDD y siguiendo el boceto de Embra, y la música y los efectos se sintetizaron con ondas de 8 bits. "
            "Entonces todo es original, sin problemas de licencia, y si quiero cambiar algo solo corro el script otra vez.")

    d.add_heading("3. Plan (Gantt del GDD) contra lo realizado", 1)
    picture(d, os.path.join(GDDM, "gantt_gdd.png"), 6.0, "Diagrama de Gantt del GDD (24 de agosto al 14 de octubre de 2026).")
    para(d, "Las actividades 1 a 5 (investigación, reporte, propuesta, GDD y arte conceptual) ya estaban hechas en la fase anterior. Las actividades 6 a 12 son las que se plasman en esta bitácora. "
            "Las fechas de la columna \"Fecha real\" son las de los commits del repositorio: el desarrollo en Godot se concentró entre el 13 y el 17 de octubre de 2026, "
            "es decir, más comprimido y un poco después de lo que planteaba el Gantt.", italic=True)
    table(d, ["Actividad del Gantt", "Fecha planeada", "Fecha real", "Entrada de bitácora"], [
        ("6. Prototipo de mecánicas básicas", "14/09 al 18/09", "13/10 al 14/10", "Entradas 1 y 2"),
        ("7. Enemigos y penalizaciones", "21/09 al 23/09", "14/10 y 17/10", "Entradas 2 y 4"),
        ("8. Sistema de partículas (fuego/humo)", "24/09 al 25/09", "17/10", "Entrada 4"),
        ("9. Diseño e integración de niveles", "28/09 al 02/10", "14/10 y 17/10", "Entradas 2 y 4"),
        ("10. Integración de audio", "05/10 al 06/10", "17/10", "Entrada 4"),
        ("11. Pruebas y balanceo", "07/10 al 09/10", "14/10 y 17/10", "Entradas 3 y 5"),
        ("12. Pulido final y compilación", "12/10 al 14/10", "14/10 y 17/10", "Entradas 3 y 6"),
    ], widths=[2.4, 1.2, 1.2, 1.7])

    d.add_heading("4. Registro de avances", 1)
    entradas = [
        ("Entrada 1 · Preparación del entorno (13/10/2026) · Gantt 6",
         "Instalé Godot 4.3 y las plantillas de exportación y comprobé que el motor corre sin ventana (modo headless) para poder probar el juego de forma automática. "
         "Armé la estructura del proyecto: assets, scripts, scenes, tools y docs, y los primeros generadores de arte y audio.",
         "Los sitios de assets no estaban accesibles.", "Generar arte y audio originales con scripts (Pillow y el módulo wave).", "5bc59d5"),
        ("Entrada 2 · Primera versión jugable (14/10/2026) · Gantt 6, 7 y 9",
         "Construí el núcleo (autoload Global, controles, audio), el jugador con salto variable, coyote time y buffer de salto, un primer grupo de enemigos, el HUD, el controlador de nivel, "
         "el menú, el game over y la victoria, y un generador de mapas ASCII para los niveles.",
         "Embra se hundía en el suelo al iniciar; Engine.time_scale hacía que las físicas dejaran de ser fiables; aparecía el error 'Can't change this state while flushing queries'.",
         "Esperar 3 fotogramas de física a que el TileMapLayer cree sus colisiones; usar --fixed-fps 60 en las pruebas; cambiar propiedades con set_deferred cuando el código corre dentro de un callback de colisión.",
         "9ec853a, 0df11e9, deffb84, 4836b6b, 4d9b0de, b67b568"),
        ("Entrada 3 · Pruebas automáticas y exportación (14/10/2026) · Gantt 11 y 12",
         "Hice un bot (scripts/bot.gd) que juega solo y recorre los niveles hasta la meta; con él encontré errores reales de diseño, como un hueco de 4 casillas imposible de saltar. "
         "También agregué un modo de capturas para documentar el juego, el README, el script tools/run_tests.sh y los presets de exportación; exporté Windows, Linux y Web.",
         "Un hueco imposible en un nivel y una etiqueta del menú que se agregaba al nodo equivocado.", "Colocar plataformas con posiciones relativas al inicio de cada tramo y corregir el padre de la etiqueta.",
         "fff8ac7, 0e82896"),
        ("Entrada 4 · Alineación con el GDD (17/10/2026) · Gantt 7, 8, 9 y 10",
         "Al revisar el GDD vi que mi primera versión incluía cosas que no estaban en el diseño (otros enemigos, una bola de fuego, un jefe, otra historia y otra paleta). "
         "Entonces rehíce el juego siguiendo el GDD: Embra con el boceto del documento, el Rondín como único enemigo, las zonas de fuego y humo hechas con partículas que se encienden y se apagan, "
         "las penalizaciones, la tabla de mejor puntaje por nivel, los cuatro niveles (Bosque de Brasas, Cañón Humeante, Ruinas de Carbón y El Altar) y la música de dos capas que se intensifica cerca de enemigos y fuego. "
         "Quité lo que no estaba en el GDD (jefe, bola de fuego, corazones de vida extra y letreros, porque la meta de diseño pide que el Nivel 1 enseñe todo sin tutorial escrito).",
         "En el nivel 2 el altar quedó fuera del mapa porque el ancho estaba mal calculado.", "El generador de niveles ahora recorta el ancho automáticamente al último tile usado.",
         "ad26c16, 266f3fd"),
        ("Entrada 5 · Pruebas con el diseño del GDD (17/10/2026) · Gantt 11",
         "Volví a correr el bot en los 4 niveles ya con las reglas del GDD y todos se completaron. Revisé capturas del juego en una pantalla virtual para comprobar la paleta, los Rondines, las zonas de fuego y la interfaz.",
         "—", "—", "ad26c16"),
        ("Entrada 6 · Compilación y documentación (17/10/2026) · Gantt 12",
         "Exporté de nuevo los ejecutables con el juego final y armé la biblia del videojuego, el reporte de pruebas, el plan de acción y esta bitácora.", "—", "—", "commits finales de documentación"),
    ]
    for titulo, hecho, problema, solucion, commit in entradas:
        d.add_heading(titulo, 3)
        rich(d, [("Qué hice: ", {"b": True}), (hecho, {})], after=3)
        if problema != "—":
            rich(d, [("Problemas: ", {"b": True}), (problema, {})], after=3)
            rich(d, [("Solución: ", {"b": True}), (solucion, {})], after=3)
        rich(d, [("Commits: ", {"b": True}), (commit, {"i": True})], after=6)

    d.add_heading("5. Historial de versiones (Git)", 1)
    para(d, "Salida de git log al momento de redactar esta bitácora (un commit por etapa):")
    table(d, ["Commit", "Fecha", "Mensaje"], git_log(), widths=[0.8, 1.0, 4.7], font=9)

    d.add_heading("6. Trazabilidad: GDD → prototipo", 1)
    table(d, ["Elemento del GDD", "Cómo quedó en el prototipo", "Dónde"], [
        ("Movimiento lateral con flechas y salto con barra espaciadora", "Aceleración corta, salto variable, coyote time y buffer de salto", "player.gd, global.gd"),
        ("Recolección de chispas (monedas) que suma puntos", "+10 puntos por chispa; contador en el HUD", "pickup.gd, global.gd"),
        ("Rondines: criaturas de carbón que patrullan una plataforma", "Caminan de un extremo a otro y dan la vuelta en bordes y paredes", "rondin.gd"),
        ("Colisión con un Rondín: pierde una vida y parte del puntaje", "Se pierde 1 vida y el 20 % del puntaje del nivel", "rondin.gd, global.gd"),
        ("Zonas de fuego y humo con partículas, mismo daño que un enemigo", "Alternan fuego activo, aviso con brasas y fase apagada; solo dañan cuando están activas", "fire_zone.gd"),
        ("Caída al vacío: pierde una vida y reinicia en el último punto de control sin perder puntaje", "Reaparece en el último brasero; no se descuentan puntos", "player.gd, checkpoint.gd"),
        ("Altar final de cada nivel; al terminar el juego se reenciende la fogata", "El altar termina el nivel; tras El Altar aparece la pantalla de victoria", "goal.gd, end_screen.gd"),
        ("Sistema de partículas de fuego y humo", "Estela de Embra y llamas, brasas y humo de las zonas de fuego", "player.gd, fire_zone.gd"),
        ("Música chiptune cálida que se intensifica con enemigos o fuego activo", "Cada nivel tiene pista base y capa de peligro sincronizada que se mezcla por cercanía", "global.gd, level.gd, tools/make_audio.py"),
        ("Efectos: salto, chispa, daño y pérdida de vida", "4 efectos más punto de control, victoria, fin del juego y clic", "assets/audio"),
        ("Tabla de mejor puntaje por nivel", "Se guarda en disco y se muestra en el menú y al terminar un nivel", "global.gd, main_menu.gd"),
        ("3 niveles progresivos más El Altar", "Bosque de Brasas, Cañón Humeante, Ruinas de Carbón y El Altar", "tools/make_levels.py"),
        ("Meta de diseño: entender todo sin tutorial escrito", "El Nivel 1 sigue el boceto del GDD y no tiene letreros", "tools/make_levels.py"),
        ("Paleta y boceto de Embra", "Colores exactos del GDD y sprite de Embra basado en el boceto", "tools/make_assets.py"),
        ("Meta de producto: versión compilada", "Ejecutable de Windows (y Linux/Web)", "build/"),
    ], widths=[2.2, 3.0, 1.3], font=8.5)

    d.add_heading("7. Resultados de las pruebas automáticas", 1)
    table(d, ["Nivel", "Zona", "Resultado del bot", "Tiempo de recorrido"], [
        ("1", "Bosque de Brasas", "Completado", "14.9 s"),
        ("2", "Cañón Humeante", "Completado", "23.7 s"),
        ("3", "Ruinas de Carbón", "Completado", "30.0 s"),
        ("4", "El Altar", "Completado", "29.9 s"),
    ], widths=[0.6, 2.2, 2.4, 1.3])
    para(d, "Importante: el bot es invulnerable, así que estas pruebas confirman que los niveles son físicamente completables, pero no dicen nada de la dificultad ni de la diversión. "
            "Para eso falta la prueba con una persona externa (ver el reporte de pruebas).", italic=True)

    d.add_heading("7b. Entrada 7 · Mejoras posteriores a la prueba con usuarios (v1.1)", 1)
    para(d, "Después de que unas personas probaron el prototipo salieron seis comentarios. No están en el GDD, pero se decidió implementarlos porque mejoran la jugabilidad sin cambiar las reglas del GDD.")
    table(d, ["Comentario del usuario", "Qué se hizo", "Dónde"], [
        ("Falta un botón de salir", "Botón Salir en el menú principal, en el menú de pausa y tecla Q durante la partida", "main_menu.gd, hud.gd, global.gd"),
        ("No se puede matar enemigos saltando encima", "Pisotón: si Embra cae sobre el enemigo lo vence y rebota. Se usa la posición de los pies del fotograma anterior para distinguirlo del contacto lateral", "enemy_base.gd, player.gd"),
        ("Mejor forma de matar enemigos", "Bola de fuego con X o J (con enfriamiento y máximo en pantalla); en la etapa 3 atraviesa y hace doble daño", "fireball.gd, player.gd"),
        ("Que el personaje evolucione", "3 etapas según las chispas acumuladas: Brasa (0), Llama (20) y Fuego ardiente (70), con sprite propio y barra en el HUD", "global.gd, hud.gd, player.gd"),
        ("Mejores enemigos", "Rondín furioso (carga), Rondín gigante (2 de vida) y Ceniza (vuela). Cada enemigo da puntos distintos: 50, 100, 200 y 75", "enemy_base.gd, rondin_*.gd, ceniza.gd"),
        ("Mejorar el diseño de los personajes", "Sprites nuevos de 16x24 para Embra (3 etapas) y para todos los enemigos, con la paleta del GDD", "tools/make_assets.py"),
    ], widths=[1.9, 3.5, 1.4], font=8.5)
    para(d, "Pruebas: el bot sigue completando los 4 niveles y una prueba aparte confirma que el pisotón vence al enemigo sin quitar vidas (la prueba de contacto lateral sí lastima a Embra). "
            "Al ser mejoras fuera del GDD, las reglas de puntaje, vidas y penalización no cambiaron.", italic=True)

    d.add_heading("7c. Entrada 8 · Resultados de la prueba con personas externas (v1.2)", 1)
    para(d, "Dos participantes externos jugaron la versión v1.1 y contestaron el cuestionario. Los controles, la música, el arte y la dificultad salieron bien. "
            "Dificultades encontradas: las primeras chispas de los niveles 3 y 4 obligaban a saltar y no se entendía que el vapor quita puntos.")
    table(d, ["Hallazgo", "Solución implementada", "Dónde"], [
        ("Primeras chispas de los niveles 3 y 4 solo se alcanzaban saltando", "Se bajó una fila el tramo inicial de chispas para recogerlas caminando, como en el nivel 1", "tools/make_levels.py"),
        ("No se entiende que el fuego y el vapor quitan puntos", "Aviso corto la primera vez que Embra se acerca a una zona de fuego y nota en la pantalla de controles", "level.gd, main_menu.gd"),
    ], widths=[2.4, 3.2, 1.2], font=8.5)
    para(d, "Pendiente: repetir la prueba con la v1.2 y dar más identidad al juego con textos breves de historia entre niveles. Los bots volvieron a completar los 4 niveles.", italic=True)

    d.add_heading("8. Pendientes", 1)
    for t in ["Hacer la prueba con al menos una persona externa y llenar el reporte de pruebas.",
              "Ajustar dificultad, vidas y puntos de control según lo que se observe (plan de acción).",
              "Revisar que las fechas de esta bitácora coincidan con las que se entregarán junto al Gantt."]:
        bullet(d, t)
    d.save(os.path.join(DOCS, "Bitacora_Desarrollo.docx"))


# ================================================================== BIBLIA
def biblia():
    d = new_doc()
    picture(d, os.path.join(ART, "logo_hoja.png"), 5.8)
    title_block(d, "Biblia del videojuego", "EMBRA: Bosque de Brasas",
                ["Videojuego de plataformas 2D en pixel art · Godot 4.3", "Versión 1.0 del prototipo · Universidad Tecmilenio"])

    d.add_heading("1. Resumen del juego", 1)
    table(d, ["Concepto", "Descripción"], [
        ("Nombre", "EMBRA: Bosque de Brasas"),
        ("Tipo", "Videojuego de plataformas 2D (2D Platformer)"),
        ("Género", "Plataformas / acción-aventura casual"),
        ("Plataforma", "PC (Windows). El GDD plantea distribución en Steam"),
        ("Clasificación", "PEGI 7 / ESRB E10+ (violencia de caricatura leve, sin sangre)"),
        ("Estilo visual", "Pixel art 2D con paleta cálida de ámbar y fuego sobre fondos oscuros"),
        ("Tipo de jugador", "Un jugador, perfil casual-core; partidas cortas con progresión y puntaje"),
        ("Premisa", "Una pequeña brasa debe saltar de plataforma en plataforma, recolectar chispas y llegar al altar final para reavivar la fogata ancestral antes de que el bosque se apague."),
    ], widths=[1.5, 5.0])
    d.add_heading("Mecánicas", 3)
    table(d, ["Mecánica", "Control", "Reglas"], [
        ("Movimiento lateral y salto", "Flechas (o A/D) y ESPACIO", "Salto variable: mantener presionado salta más alto. Margen para saltar justo tras dejar un borde y buffer de salto."),
        ("Recolección de chispas", "Tocar la chispa", "Equivalen a las monedas del prototipo original: +10 puntos y desaparecen."),
        ("Colisión con Rondines", "—", "Pierdes una vida y el 20 % del puntaje del nivel."),
        ("Zonas de fuego y humo", "—", "Solo dañan cuando el fuego está activo: mismo daño que un Rondín. Alternan fuego, aviso con brasas y fase apagada."),
        ("Caída al vacío", "—", "Pierdes una vida, no pierdes puntos y reapareces en el último brasero."),
        ("Puntaje", "—", "Chispas +10 por chispa, +100 al terminar el nivel. Se guarda el mejor puntaje de cada nivel."),
    ], widths=[1.6, 1.4, 3.5])

    d.add_heading("2. Historia", 1)
    para(d, "Embra es una pequeña brasa que se separó de la fogata ancestral que mantenía encendido el Bosque de Brasas. Sin su llama el bosque comienza a apagarse, "
            "y los antiguos guardianes del bosque, los Rondines, pierden el control y empiezan a vagar de forma errática entre las plataformas.")
    para(d, "Embra debe saltar de plataforma en plataforma, recolectar chispas para recuperar fuerza y llegar hasta el altar final para volver a encender la fogata "
            "antes de que el bosque se apague por completo.")
    para(d, "Para llegar al altar final tiene que atravesar cuatro lugares: el Bosque de Brasas donde nació, el Cañón Humeante donde el humo ya cubre los caminos, "
            "las Ruinas de Carbón donde los Rondines son más numerosos y El Altar, donde arde la fogata ancestral.")
    d.add_heading("Estructura en cuatro niveles", 3)
    table(d, ["Nivel", "Lugar", "Qué introduce", "Meta"], [
        ("1", "Bosque de Brasas", "Movimiento y salto, chispas, el primer Rondín y una zona de fuego, todo con el diseño del nivel (sin tutorial escrito).", "Altar del nivel 1"),
        ("2", "Cañón Humeante", "Las zonas de fuego y humo, con más combinaciones y menos Rondines.", "Altar del nivel 2"),
        ("3", "Ruinas de Carbón", "Enemigos y zonas de fuego juntos, con plataformas más estrechas y exigentes.", "Altar del nivel 3"),
        ("4", "El Altar", "Combina todas las mecánicas antes de cerrar la historia.", "La fogata ancestral vuelve a arder"),
    ], widths=[0.5, 1.5, 3.4, 1.1])

    d.add_heading("3. Narrativa", 1)
    para(d, "El juego cuenta su historia sin diálogos ni tutorial escrito: el diseño de los niveles y el entorno enseñan y narran. El tono es cálido y esperanzado, con un poco de ternura. "
            "El frío y la oscuridad de la noche son el contexto, y el fuego es la voz de Embra.")
    d.add_heading("Recursos narrativos", 3)
    for pre, t in [("Embra no habla. ", "Se comunica con sus animaciones, su llama y los sonidos de sus saltos y sus chispas."),
                   ("El entorno cuenta la historia. ", "El bosque, el cañón y las ruinas muestran cómo el humo y la oscuridad avanzan cuando falta la fogata; en El Altar aparecen columnas con braseros y el altar final."),
                   ("El Nivel 1 es el tutorial. ", "Sigue el boceto del GDD: una zona de práctica, plataformas que suben, un Rondín por plataforma y una zona de fuego antes de la meta, de modo que el jugador aprende probando."),
                   ("Mensajes cortos. ", "Aparecen al comenzar cada nivel, al activar un punto de control y al perder puntos."),
                   ("Pantallas finales. ", "Una para el fin del juego y otra para la victoria con el resumen y la tabla de mejores puntajes.")]:
        bullet(d, t, pre)
    d.add_heading("Textos del juego", 3)
    table(d, ["Momento", "Texto"], [
        ("Inicio de cada nivel", "Nivel 1: Bosque de Brasas / Nivel 2: Cañón Humeante / Nivel 3: Ruinas de Carbón / Nivel 4: El Altar"),
        ("Punto de control", "Punto de control"),
        ("Penalización", "-N puntos"),
        ("Fin de nivel", "¡[Nivel] completado! Chispas, puntaje del nivel y mejor puntaje (con aviso de nuevo récord)"),
        ("Fin del juego", "La brasa de Embra se apagó... pero siempre queda una chispa."),
        ("Victoria", "¡LA FOGATA ANCESTRAL ARDE DE NUEVO! Embra encendió el altar y el Bosque de Brasas volvió a brillar."),
    ], widths=[1.7, 4.8])

    d.add_heading("4. Personajes y bosquejos", 1)
    para(d, "Los personajes se diseñaron para reconocerse por su silueta y su color. Las láminas muestran el boceto, el arte final del juego, su paleta y sus cuadros de animación. "
            "Para Embra se usa el boceto original del GDD y se explica cómo se trasladó al sprite.")
    picture(d, os.path.join(ART, "char_embra.png"), 6.5, "Embra, protagonista: boceto del GDD y sprite del juego.")
    picture(d, os.path.join(ART, "char_rondin.png"), 6.5, "Rondín, enemigo básico.")
    d.add_heading("Zona de fuego y humo (peligro ambiental)", 3)
    para(d, "No es un personaje, pero se diseñó como uno: una boca de piedra con una grieta de brasa sobre la que se generan llamas, brasas y humo con partículas. "
            "Alterna entre fuego activo, aviso (solo brasas) y apagada (solo humo) para que el jugador pueda medir sus saltos. Se ve en el nivel 1 y en el resto de los niveles.")

    d.add_heading("5. Mundo y niveles", 1)
    zonas = [
        ("Nivel 1 · Bosque de Brasas", "Bosque nocturno con árboles y musgo turquesa sobre las plataformas. Es el nivel de aprendizaje y sigue el boceto del GDD.", "2 Rondines, 1 zona de fuego, 26 chispas.", "music_bosque (96 bpm, cálida y ligera)", "mapa_nivel_1.png"),
        ("Nivel 2 · Cañón Humeante", "Cañón de roca fría con agujas de piedra y bruma de humo. Presenta las zonas de fuego y humo.", "3 Rondines, 6 zonas de fuego, 33 chispas.", "music_canon (104 bpm)", "mapa_nivel_2.png"),
        ("Nivel 3 · Ruinas de Carbón", "Ruinas de ladrillo azul grisáceo con pilares y grietas de brasa. Combina enemigos y fuego con plataformas más estrechas.", "9 Rondines, 6 zonas de fuego, 39 chispas.", "music_ruinas (100 bpm)", "mapa_nivel_3.png"),
        ("Nivel 4 · El Altar", "Templo de piedra con vetas ámbar y columnas con braseros. Es una subida larga hasta el altar donde se enciende la fogata.", "8 Rondines, 8 zonas de fuego, 48 chispas.", "music_altar (112 bpm)", "mapa_nivel_4.png"),
    ]
    for nombre, desc, contenido, musica, mapa in zonas:
        d.add_heading(nombre, 3)
        para(d, desc, after=3)
        rich(d, [("Contenido: ", {"b": True}), (contenido, {}), ("   Música: ", {"b": True}), (musica, {})], after=4)
        picture(d, os.path.join(ART, mapa), 6.5, "Mapa del nivel (se muestra en dos mitades apiladas).")
    d.add_heading("Layout del Nivel 1: boceto del GDD y resultado", 3)
    picture(d, os.path.join(GDDM, "boceto_nivel1_gdd.png"), 5.2, "Boceto del GDD para el Nivel 1.")
    picture(d, os.path.join(IMG, "shot_n1_rondin.png"), 4.6, "El mismo recorrido en el juego: plataformas que suben con Rondines.")
    picture(d, os.path.join(IMG, "shot_n1_fuego.png"), 4.6, "Plataforma con zona de fuego antes de la meta.")

    d.add_heading("6. Arte visual", 1)
    d.add_heading("Dirección de arte", 3)
    for pre, t in [("Estilo: ", "pixel art con sprites de 16 píxeles de ancho (Embra de 16x20) y contorno claro en Embra para que resalte sobre el fondo nocturno; el Rondín lleva contorno naranja como señal de peligro."),
                   ("Color: ", "la paleta del GDD manda: fondo nocturno #1B1F3B, plataformas #2E3A59, ámbar #F4A62A para el personaje, fuego #E8542A para el peligro, brillo #FFF3C4 para partículas y turquesa #4CC9C0 para detalles frescos."),
                   ("Regla: ", "lo cálido (ámbar y fuego) se reserva para Embra, las chispas y los peligros; todo lo demás es frío, así el ojo lo encuentra primero."),
                   ("Fondos: ", "tres capas con parallax (cielo con estrellas y brasas, siluetas lejanas y cercanas) que cambian en cada lugar."),
                   ("Interfaz: ", "HUD mínimo arriba (vidas, chispas, puntaje, nombre del nivel) y mensajes que desaparecen solos."),
                   ("Efectos: ", "partículas de fuego y humo en la estela de Embra y en las zonas de fuego; chispas al recolectar.")]:
        bullet(d, t, pre)
    picture(d, os.path.join(GDDM, "paleta_gdd.png"), 5.8, "Paleta del GDD.")
    picture(d, os.path.join(ART, "paleta_tiles.png"), 6.5, "Paleta aplicada y tilesets por nivel.")
    picture(d, os.path.join(ART, "objetos.png"), 6.5, "Objetos y elementos del mundo.")
    d.add_heading("Audio", 3)
    para(d, "Música de fondo chiptune de 8 bits con un tema cálido y ligero mientras se explora. Cada nivel tiene una pista base y una capa de peligro (arpegios agudos y percusión) "
            "de la misma duración: cuando Embra se acerca a un Rondín o a una zona de fuego activa, la capa de peligro se mezcla suavemente y la música se intensifica, "
            "así se percibe el peligro sin un elemento visual adicional. Efectos: salto, recolección de chispas, daño y pérdida de vida, además de punto de control, victoria, fin del juego y clic de menú.")
    d.add_heading("Capturas del prototipo", 3)
    for f, cap in [("shot_menu.png", "Menú principal."), ("shot_n1_inicio.png", "Nivel 1: Bosque de Brasas."), ("shot_n2.png", "Nivel 2: Cañón Humeante."),
                   ("shot_n3.png", "Nivel 3: Ruinas de Carbón."), ("shot_n4.png", "Nivel 4: El Altar."), ("shot_victoria.png", "Pantalla de victoria.")]:
        picture(d, os.path.join(IMG, f), 4.6, cap)

    d.add_heading("Cambios posteriores a la prueba: evolución y enemigos", 3)
    para(d, "Embra evoluciona al juntar chispas: Brasa (inicio), Llama (20 chispas, desbloquea la bola de fuego) y Fuego ardiente (70 chispas, el fuego atraviesa enemigos y hace doble daño). "
            "Además de los Rondines del GDD aparecen tres variantes: el Furioso carga contra Embra al verlo, el Gigante resiste dos golpes y la Ceniza vuela. Todos se pueden vencer saltándoles encima o con fuego.")
    picture(d, os.path.join(ART, "evolucion.png"), 5.8, "Las tres etapas de Embra.")
    picture(d, os.path.join(ART, "enemigos.png"), 6.5, "Enemigos del juego y puntos que dan.")
    for f, cap in [("shot_evo2.png", "Embra en etapa 2 (Llama) con barra de evolución."), ("shot_evo3.png", "Embra en etapa 3 (Fuego ardiente)."),
                   ("shot_n3_furioso.png", "Rondín furioso."), ("shot_n4_gigante.png", "Rondín gigante.")]:
        picture(d, os.path.join(IMG, f), 4.2, cap)

    d.add_heading("7. Créditos y herramientas", 1)
    para(d, "Diseño, programación, arte y audio del prototipo: proyecto escolar de Universidad Tecmilenio. Herramientas: Godot 4.3, Python con Pillow para el arte, "
            "el módulo wave para el audio y Git para el control de versiones. El arte y el audio fueron creados para este proyecto.")
    d.save(os.path.join(DOCS, "Biblia_Videojuego.docx"))


# ================================================================== REPORTE DE PRUEBAS
def reporte():
    d = new_doc(margins=0.9, base_size=10.5)
    para(d, "Reporte de pruebas del prototipo", bold=True, size=17, color=NAVY, after=0)
    para(d, "EMBRA: Bosque de Brasas · Universidad Tecmilenio", italic=True, size=10.5, color=AMBER, after=6)
    table(d, ["Dato", "Registro"], [
        ("Fecha de la prueba", "[COMPLETAR]"),
        ("Persona que probó", "[COMPLETAR: nombre o iniciales, edad aproximada, experiencia con videojuegos]"),
        ("Versión y plataforma", "Prototipo v1.0, ejecutable de Windows"),
        ("Duración de la sesión", "[COMPLETAR] minutos, sin explicaciones previas más allá de abrir el juego"),
    ], widths=[1.8, 4.9], font=9.5)

    rich(d, [("Objetivo. ", {"b": True}),
             ("Comprobar con una persona ajena al proyecto la meta de diseño del GDD (que entienda las mecánicas sin tutorial escrito, solo con el Nivel 1), si la dificultad es razonable y si el juego es claro y divertido.", {})], after=4)
    rich(d, [("Método. ", {"b": True}),
             ("La persona jugó sin ayuda mientras yo observaba y anotaba (hoja de observación en el anexo). Al terminar respondió un cuestionario corto de 8 preguntas.", {})], after=4)
    rich(d, [("Pruebas internas previas. ", {"b": True}),
             ("Un bot automático completó los 4 niveles hasta el altar. Esto confirma que se pueden terminar, pero no mide la dificultad (el bot es invulnerable).", {})], after=4)

    rich(d, [("Resultados. ", {"b": True}), ("[COMPLETAR después de la prueba con los datos reales]", {"hl": True})], after=2)
    table(d, ["Aspecto", "Qué observé"], [
        ("Nivel 1 sin tutorial", "[COMPLETAR: ¿entendió mover, saltar, juntar chispas y esquivar Rondines y fuego sin ayuda?]"),
        ("Dificultad", "[COMPLETAR: nivel donde perdió más vidas, ¿llegó a El Altar?]"),
        ("Rondines y zonas de fuego", "[COMPLETAR: ¿entendió el ciclo del fuego y que los Rondines no se pueden vencer?]"),
        ("Penalizaciones", "[COMPLETAR: ¿se entendió la pérdida de vida y de puntos y el reinicio en el brasero?]"),
        ("Audio y claridad visual", "[COMPLETAR: ¿notó que la música se intensifica? ¿distinguió peligros y chispas?]"),
        ("Diversión y comentarios", "[COMPLETAR: calificación del 1 al 5 y comentarios textuales]"),
        ("Errores o fallas", "[COMPLETAR: cualquier bug o confusión]"),
    ], widths=[1.9, 4.8], font=9.5)
    rich(d, [("Conclusión. ", {"b": True}), ("[COMPLETAR: 2 o 3 líneas con lo más importante que se aprendió y qué cambios se proponen en el plan de acción.]", {"hl": True})], after=0)

    page_break(d)
    d.add_heading("Anexo A · Protocolo de la prueba", 2)
    for t in ["Abrir el ejecutable y llegar al menú. No explicar los controles: que los descubra con el diseño del Nivel 1.",
              "Pedir que juegue entre 10 y 15 minutos pensando en voz alta.",
              "No ayudar salvo que se bloquee por más de un minuto; anotar cuándo ocurre.",
              "Al terminar, aplicar el cuestionario y preguntar qué cambiaría."]:
        bullet(d, t)
    d.add_heading("Hoja de observación", 3)
    table(d, ["Momento", "Qué ocurrió", "Vidas perdidas", "Anotación"], [
        ("Menú y controles", "", "", ""), ("Nivel 1 Bosque de Brasas", "", "", ""), ("Nivel 2 Cañón Humeante", "", "", ""),
        ("Nivel 3 Ruinas de Carbón", "", "", ""), ("Nivel 4 El Altar", "", "", ""), ("Fin del juego / victoria", "", "", ""),
    ], widths=[1.8, 2.4, 1.2, 1.3], font=9)
    d.add_heading("Cuestionario (1 = muy mal, 5 = muy bien)", 3)
    table(d, ["#", "Pregunta", "Respuesta"], [
        ("1", "¿Se entienden los controles?", ""), ("2", "¿Entendiste cómo funcionan los Rondines y el fuego sin que nadie te explicara?", ""),
        ("3", "¿La dificultad es adecuada?", ""), ("4", "¿Se ve bien lo que pasa en pantalla?", ""),
        ("5", "¿El sonido y la música acompañan?", ""), ("6", "¿Qué tan divertido fue?", ""),
        ("7", "¿Qué fue lo mejor del juego?", ""), ("8", "¿Qué cambiarías primero?", ""),
    ], widths=[0.4, 4.6, 1.7], font=9.5)
    d.add_heading("Anexo B · Hallazgos de la primera prueba (usuarios externos)", 2)
    table(d, ["#", "Hallazgo", "Qué se hizo (v1.1)"], [
        ("1", "No hay forma de salir del juego", "Botón Salir en menú y pausa, tecla Q"),
        ("2", "No se puede matar enemigos saltando encima", "Pisotón con rebote"),
        ("3", "Hace falta otra forma de vencer enemigos", "Bola de fuego (X o J)"),
        ("4", "El personaje no evoluciona", "3 etapas por chispas acumuladas"),
        ("5", "Los enemigos son todos iguales", "Furioso, Gigante y Ceniza"),
        ("6", "El diseño de los personajes puede mejorar", "Sprites nuevos de Embra y enemigos"),
    ], widths=[0.4, 3.4, 2.9], font=9.5)
    para(d, "Pendiente: repetir la prueba con la v1.1 para confirmar que los cambios ayudaron (datos de la persona, tiempo y calificación en la plantilla de arriba).", italic=True)
    d.save(os.path.join(DOCS, "Reporte_de_Pruebas.docx"))


# ================================================================== PLAN DE ACCIÓN
def plan():
    d = new_doc(margins=0.8, base_size=10)
    para(d, "Plan de acción", bold=True, size=18, color=NAVY, after=0)
    para(d, "Respuesta a los resultados de la prueba · EMBRA: Bosque de Brasas", italic=True, size=11, color=AMBER, after=8)

    d.add_heading("1. Cómo se decide qué corregir", 2)
    para(d, "Cada hallazgo de la prueba se clasifica por impacto en la experiencia (alto, medio, bajo) y por esfuerzo de corregirlo (alto, medio, bajo). "
            "Se atiende primero lo de alto impacto y bajo esfuerzo, después lo de alto impacto y alto esfuerzo, y al final lo demás. "
            "Después de cada corrección se vuelve a correr el bot (tools/run_tests.sh) y se registra el cambio en un commit y en la bitácora.")

    d.add_heading("2. Mejoras ya identificadas por el equipo", 2)
    para(d, "Salieron de la revisión del propio prototipo, antes de la prueba con usuarios; la prueba servirá para confirmar su prioridad.", italic=True)
    table(d, ["#", "Mejora", "Por qué", "Cómo", "Prio."], [
        ("1", "Ajustar la dificultad", "El bot solo prueba que los niveles se pueden terminar; no mide dificultad.", "Según la prueba: más puntos de control, o menos Rondines y fuego en el nivel donde más se pierdan vidas.", "Alta"),
        ("2", "Revisar el tiempo de las zonas de fuego", "Tiempos de fuego, aviso y apagado definidos a ojo (1.8 s, 0.5 s y 1.5 s).", "Ajustar los tiempos en fire_zone.gd según cómo los viva el jugador.", "Alta"),
        ("3", "Confirmar la penalización de puntos", "Se interpretó \"parte del puntaje acumulado\" como el 20 % del puntaje del nivel.", "Probar otros porcentajes en global.gd (PENALTY_RATIO).", "Media"),
        ("4", "Más variedad de enemigos", "El GDD solo define al Rondín; puede sentirse repetitivo.", "Ya se agregaron Furioso, Gigante y Ceniza en la v1.1; falta ver en la prueba si se sienten bien.", "Hecha"),
        ("5", "Ajustes de volumen y pantalla de opciones", "El sonido no se puede bajar desde el juego.", "Agregar una pantalla de opciones con volumen de música y efectos.", "Media"),
        ("6", "Mejorar los menús para control de consola", "El menú se maneja mejor con teclado y ratón.", "Agregar navegación con D-pad y botón A en menús y pantallas finales.", "Baja"),
        ("7", "Tipografía pixel art", "La fuente por defecto no combina del todo con el arte.", "Incluir una fuente pixelada con licencia libre en el tema de la interfaz.", "Baja"),
    ], widths=[0.3, 1.5, 1.8, 2.5, 0.5], font=9)

    d.add_heading("3. Acciones a partir de la prueba con usuario", 2)
    para(d, "Llenar esta tabla con los hallazgos del reporte de pruebas.", italic=True)
    table(d, ["Hallazgo observado", "Impacto", "Acción propuesta", "Prioridad", "Responsable", "Criterio de éxito"], [
        ("Sin botón de salir", "Alto", "Botón Salir en menú y pausa, tecla Q", "Alta", "Programación", "Hecho (v1.1)"),
        ("No se mata saltando sobre el enemigo", "Alto", "Pisotón con rebote", "Alta", "Programación", "Hecho (v1.1)"),
        ("Pocas formas de vencer enemigos", "Medio", "Bola de fuego con enfriamiento", "Media", "Programación", "Hecho (v1.1)"),
        ("El personaje no evoluciona", "Medio", "3 etapas según chispas acumuladas", "Media", "Programación y arte", "Hecho (v1.1)"),
        ("Enemigos poco variados", "Medio", "Furioso, Gigante y Ceniza", "Media", "Programación y arte", "Hecho (v1.1)"),
        ("Diseño de personajes mejorable", "Medio", "Sprites nuevos con la paleta del GDD", "Media", "Arte", "Hecho (v1.1)"),
        ("Repetir la prueba con la v1.1", "Medio", "Probar con otra persona externa y llenar el reporte", "Alta", "Equipo", "Pendiente"),
    ], widths=[1.6, 0.7, 1.7, 0.7, 0.9, 1.1], font=9)

    d.add_heading("4. Seguimiento", 2)
    for t in ["Revisión de resultados y priorización: una sesión corta apenas termine la prueba.",
              "Implementar las acciones de prioridad alta y registrar cada una en la bitácora.",
              "Repetir la prueba con otra persona externa para confirmar que los cambios ayudaron.",
              "Exportar de nuevo el ejecutable y actualizar el README con la nueva versión."]:
        bullet(d, t)
    d.save(os.path.join(DOCS, "Plan_de_Accion.docx"))


# ================================================================== REPORTE (una cuartilla) Y PLAN, VERSIÓN DE ENTREGA
HALLAZGOS = [
    ("Falta un botón de salir (comentario de los probadores)", "Agregar una forma clara de salir del juego", "Botón Salir en el menú principal y en la pausa; tecla Q", "Alta", "Cualquier persona puede cerrar el juego sin usar el sistema", "Hecho en v1.1"),
    ("No se podía vencer a los enemigos saltándoles encima", "Pisotón con rebote", "Detectar el pisotón con la posición de los pies del cuadro anterior; vence al enemigo y rebota", "Alta", "La mayoría de los jugadores vence a su primer Rondín sin morir", "Hecho en v1.1"),
    ("Solo había una forma de matar enemigos", "Segunda forma de ataque", "Bola de fuego con X o J, con enfriamiento y máximo en pantalla", "Media", "El jugador elige entre pisar o quemar según la situación", "Hecho en v1.1"),
    ("El personaje no evolucionaba", "Evolución de Embra", "Tres etapas por chispas acumuladas (0, 20 y 70) con sprite propio y barra en el HUD", "Media", "Juntar chispas se siente como progreso, no solo como puntos", "Hecho en v1.1"),
    ("Los enemigos eran todos iguales y el diseño de personajes era mejorable", "Más variedad y mejor arte", "Rondín furioso, Rondín gigante y Ceniza voladora; sprites nuevos con la paleta del GDD", "Media", "Cada nivel presenta un reto distinto sin romper las reglas del GDD", "Hecho en v1.1"),
    ("Participante 1: las primeras chispas de los niveles 3 y 4 obligaban a saltar, a diferencia del nivel 1", "Chispas iniciales al alcance caminando", "Bajar una fila las chispas del tramo inicial de los niveles 3 y 4 en make_levels.py", "Media", "El jugador recoge las primeras chispas de cada nivel sin saltar", "Hecho en v1.2"),
    ("Participante 2: no se entiende que el vapor (humo) quita puntos", "Explicar el peligro sin un tutorial largo", "Aviso corto la primera vez que Embra se acerca a una zona de fuego y nota en la pantalla de controles", "Alta", "El jugador evita las zonas de fuego desde la primera vez, sin perder vidas por no saberlo", "Hecho en v1.2"),
    ("Participante 2: el juego se siente genérico, aunque con buena esencia", "Dar más identidad al juego", "Reforzar la historia de Embra (reencender la fogata) con textos breves entre niveles", "Baja", "Los jugadores describen el juego con su propia identidad, no como genérico", "Pendiente"),
    ("Participante 2: los Rondines se entienden \"más o menos\"", "Repetir la prueba con la v1.2", "Probar con otra persona externa y comparar con esta ronda", "Alta", "Los Rondines y el fuego se entienden sin explicación", "Pendiente"),
]


def reporte():
    d = new_doc(margins=0.75, base_size=9.5)
    para(d, "Reporte de pruebas del prototipo", bold=True, size=15, color=NAVY, after=0)
    para(d, "EMBRA: Bosque de Brasas · Universidad Tecmilenio · Actividad 3", italic=True, size=9.5, color=AMBER, after=4)
    rich(d, [("Objetivo. ", {"b": True}), ("Comprobar con personas ajenas al equipo que se entienden los controles y las reglas del GDD (Rondines, fuego y humo) solo jugando, que la dificultad es razonable y que el juego es claro y divertido.", {})], after=3)
    rich(d, [("Actividad realizada. ", {"b": True}), ("Dos participantes externos jugaron el ejecutable de Windows sin explicación previa y contestaron un cuestionario de 8 preguntas. No se incluyen datos personales. "
             "Las respuestas completas están en la carpeta de evidencias (Evidencia_Respuestas.pdf).", {})], after=3)
    rich(d, [("Resultados observados.", {"b": True})], after=1)
    table(d, ["Pregunta", "Participante 1", "Participante 2"], [
        ("Controles", "Se entienden y son fáciles", "Se entienden"),
        ("Rondines y fuego sin explicación", "Sí, los entendió jugando", "Más o menos, pero lo vio normal"),
        ("Dificultad", "Adecuada; sube poco a poco", "Adecuada"),
        ("Se ve bien en pantalla", "Sí, se distingue todo", "Se ve muy bien"),
        ("Sonido y música", "Acompañan bien", "La música lo mejora"),
        ("Diversión", "Bastante divertido", "Bastante; genérico pero con buena esencia"),
        ("Lo mejor", "Juntar chispas y pasar niveles", "Morir mientras saltaba (le dio risa)"),
        ("Qué cambiaría primero", "Poder recoger las primeras chispas caminando en todos los niveles", "Explicar que el vapor quita puntos"),
    ], widths=[1.6, 2.8, 2.6], font=8.5)
    rich(d, [("Problemas detectados. ", {"b": True}),
             ("(1) En los niveles 3 y 4 las primeras chispas estaban una fila más arriba que en el nivel 1 y obligaban a saltar. (2) No queda claro que el vapor y el fuego activos quitan puntos. "
              "(3) Un participante percibe el juego como genérico. Además, en una primera ronda los probadores pidieron un botón de salir, matar enemigos al saltar encima, otra forma de atacar, evolución del personaje, enemigos más variados y mejor diseño de personajes.", {})], after=3)
    rich(d, [("Conclusiones. ", {"b": True}),
             ("Los controles, la música, el arte y la dificultad funcionan: los dos participantes los calificaron bien y se divirtieron. Los problemas son de claridad (el fuego) y de consistencia (las chispas iniciales). "
              "Todo lo anterior se corrigió en las versiones v1.1 y v1.2 (ver Plan_Accion.pdf), salvo dar más identidad al juego y repetir la prueba con la nueva versión.", {})], after=0)
    d.save(os.path.join(DOCS, "Reporte_Pruebas.docx"))

    e = new_doc(margins=0.9, base_size=10.5)
    para(e, "Evidencia de la prueba: respuestas de los participantes", bold=True, size=15, color=NAVY, after=2)
    para(e, "Transcripción de las respuestas escritas del cuestionario. Sin datos personales.", italic=True, size=10, color=GREY)
    P1 = ["Sí, los controles se entienden y son fáciles de usar.", "Sí, pude entender cómo funcionan mientras jugaba.",
          "Sí, me pareció adecuada. A medida que avanzaba por los niveles se volvía un poco más difícil.", "Sí, se ve bien y se puede distinguir lo que está pasando durante el juego.",
          "Sí, la música y los sonidos acompañan bien al juego.", "Me pareció bastante divertido, me gustó jugarlo y pasar los diferentes niveles.",
          "Me gustó tener que juntar las chispas y superar los diferentes niveles.",
          "Cambiaría que se puedan recoger las chispas que aparecen al principio de cada nivel simplemente caminando, como pasaba en el primer nivel, porque en los siguientes tenía que saltar para poder recogerlas."]
    P2 = ["Sí, sí se entienden.", "Más o menos, pero es normal.", "Sí, es la adecuada.", "Se ve muy bien en pantalla.", "La musiquita lo hace mejor.",
          "Bastante, es genérico pero tiene esencia buena.", "Morir mientras saltaba.", "Quizás la explicación de que esas cosas de vapor te quitan puntos."]
    Q = ["¿Se entienden los controles?", "¿Entendiste cómo funcionan los Rondines y el fuego sin que nadie te explicara?", "¿La dificultad es adecuada?", "¿Se ve bien lo que pasa en pantalla?",
         "¿El sonido y la música acompañan?", "¿Qué tan divertido fue?", "¿Qué fue lo mejor del juego?", "¿Qué cambiarías primero?"]
    table(e, ["#", "Pregunta", "Participante 1", "Participante 2"], [(str(i + 1), Q[i], P1[i], P2[i]) for i in range(8)], widths=[0.3, 1.9, 2.6, 1.9], font=9)
    e.save(os.path.join(DOCS, "Evidencia_Respuestas.docx"))


def plan():
    d = new_doc(margins=0.7, base_size=10)
    para(d, "Plan de acción", bold=True, size=17, color=NAVY, after=0)
    para(d, "EMBRA: Bosque de Brasas · cada acción se relaciona con un hallazgo de las pruebas del prototipo", italic=True, size=10, color=AMBER, after=6)
    table(d, ["Problema detectado", "Mejora propuesta", "Acción concreta", "Prioridad", "Resultado esperado", "Estado"],
          HALLAZGOS, widths=[1.6, 1.1, 1.7, 0.6, 1.5, 0.7], font=8.5)
    d.add_heading("Seguimiento", 2)
    for tx in ["Repetir la prueba con otra persona externa usando la v1.2 y comparar contra esta ronda.",
               "Registrar cada cambio en la bitácora y en el historial de commits.",
               "Si el fuego sigue sin entenderse, hacer más visible la fase de aviso de las zonas."]:
        bullet(d, tx)
    d.save(os.path.join(DOCS, "Plan_Accion.docx"))


if __name__ == "__main__":
    bitacora()
    biblia()
    reporte()
    plan()
    print("Documentos generados en", os.path.abspath(DOCS))
