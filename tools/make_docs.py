#!/usr/bin/env python3
"""
Genera los documentos del proyecto en Word (docs/*.docx):
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
MAROON = RGBColor(0x6D, 0x22, 0x37)
GOLD = RGBColor(0xB0, 0x8D, 0x57)
GREY = RGBColor(0x55, 0x55, 0x55)


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
    for name, size, color in (("Heading 1", 20, MAROON), ("Heading 2", 15, MAROON), ("Heading 3", 12.5, GOLD)):
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
    """parts = [(texto, {'b':True,'i':True}), ...]"""
    p = d.add_paragraph(style=style)
    for text, fmt in parts:
        r = p.add_run(text)
        r.bold = fmt.get("b", False)
        r.italic = fmt.get("i", False)
        if fmt.get("hl"):
            r.font.highlight_color = 7   # amarillo
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


def table(d, header, rows, widths=None, font=9.5, head_fill="6D2237"):
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
        c = para(d, caption, italic=True, size=9, color=GREY, align=WD_ALIGN_PARAGRAPH.CENTER, after=8)
        return c


def page_break(d):
    d.add_paragraph().add_run().add_break(WD_BREAK.PAGE)


def title_block(d, title, subtitle, lines):
    para(d, title, bold=True, size=26, color=MAROON, align=WD_ALIGN_PARAGRAPH.CENTER, after=2)
    para(d, subtitle, italic=True, size=13, color=GOLD, align=WD_ALIGN_PARAGRAPH.CENTER, after=10)
    for ln in lines:
        para(d, ln, size=10.5, color=GREY, align=WD_ALIGN_PARAGRAPH.CENTER, after=0)
    d.add_paragraph()


def git_log():
    out = subprocess.run(["git", "log", "--reverse", "--format=%h|%ad|%s", "--date=format:%d/%m/%Y %H:%M"],
                         cwd=BASE, capture_output=True, text=True).stdout
    rows = []
    for ln in out.strip().splitlines():
        h, dt, msg = ln.split("|", 2)
        rows.append((h, dt, msg))
    return rows


# ================================================================== BITÁCORA
def bitacora():
    d = new_doc()
    title_block(d, "Bitácora de desarrollo", "Embra: La Llama Eterna · prototipo funcional",
                ["Motor: Godot 4.3 (GDScript)  ·  Control de versiones: Git", "Universidad Tecmilenio · Desarrollo de videojuegos"])

    d.add_heading("1. Datos del proyecto", 1)
    table(d, ["Concepto", "Detalle"], [
        ("Videojuego", "Embra: La Llama Eterna, plataformas 2D en pixel art"),
        ("Motor y lenguaje", "Godot 4.3, GDScript (renderizador Compatibilidad, funciona también en navegador)"),
        ("Alcance del prototipo", "4 niveles (3 zonas más la fortaleza del jefe), 2 tipos de enemigo, 1 jefe con dos fases, menú, pausa, game over y pantalla de victoria"),
        ("Plataformas exportadas", "Windows (.exe), Linux (x86_64) y Web (HTML5)"),
        ("Líneas de código", "Aprox. 1,900 líneas de GDScript, todas comentadas, más 4 herramientas en Python para generar arte, audio y niveles"),
        ("Repositorio", "Git local con un commit por etapa (ver sección 4)"),
    ], widths=[1.8, 4.7])

    d.add_heading("2. Cómo trabajé", 1)
    para(d, "Mas que nada seguí la idea del diagrama de Gantt y del GDD: primero lo que hace que el juego sea jugable (movimiento y niveles), "
            "luego los enemigos y el jefe, después la interfaz y al final las pruebas y la exportación. Cada etapa la cerré con un commit en Git "
            "para poder regresar si algo se rompía, y todo el código lleva comentarios en español para entender qué hace cada parte sin tener que adivinar.")
    para(d, "Siendo completamente honesto, una decisión importante fue generar el arte y el audio por código: los sitios de assets que quería usar "
            "no estaban disponibles desde mi entorno de trabajo, entonces dibujé los sprites en pixel art con un script de Python y sinteticé los efectos y la "
            "música tipo chiptune. Eso me dio arte original, sin problemas de licencia, y si quiero cambiarlo solo corro el script otra vez.")

    d.add_heading("3. Registro de avances", 1)
    entradas = [
        ("Entrada 1 · Preparación del entorno (13/10/2026)",
         "Instalé Godot 4.3 y las plantillas de exportación, y comprobé que el motor corre sin ventana (modo headless) para poder probar el juego de forma automática. "
         "Revisé la estructura del proyecto: carpetas assets, scripts, scenes, tools y docs.",
         "Los sitios de assets no estaban accesibles.", "Generar arte y audio originales con scripts (Pillow y el módulo wave).",
         "5bc59d5"),
        ("Entrada 2 · Arte y audio",
         "Hice el generador de pixel art: Embra (9 cuadros de animación), Escarchín, Humoro, el jefe Gélido, 4 tilesets, púas, objetos, decoración, fondos con parallax y el logotipo. "
         "También el generador de audio: 12 efectos de sonido y 5 pistas de música en loop.",
         "Al principio los contornos de los sprites se veían desiguales.", "Agregué una función que dibuja el contorno de 1 px automáticamente alrededor de cada sprite.",
         "5bc59d5"),
        ("Entrada 3 · Diseño de niveles (14/10/2026)",
         "Escribí un generador de mapas ASCII con funciones de suelo, huecos y plataformas que respetan los límites del salto (huecos de máximo 3 casillas y escalones de máximo 3). "
         "Salieron 4 niveles: Bosque de Ceniza, Cuevas de Escarcha, Ruinas de Humo y Fortaleza Gélida.",
         "Calcular a mano las posiciones de cada plataforma era muy propenso a errores.", "Usar posiciones relativas al inicio de cada tramo y validar con el bot (entrada 9).",
         "9ec853a"),
        ("Entrada 4 · Núcleo del juego",
         "Configuré project.godot (pantalla de 480x270 con escala entera para que el pixel art no se deforme), el autoload Global con vidas, chispas, puntos, el registro de controles "
         "por código (teclado y control de consola), el reproductor de audio y una función de partículas reutilizable.",
         "—", "—", "0df11e9"),
        ("Entrada 5 · Jugador",
         "Programé a Embra: aceleración, salto variable (mantener = más alto), coyote time y buffer de salto para que los controles se sientan justos, bola de fuego con enfriamiento, "
         "rebote al pisar enemigos y la estela de fuego y humo con dos sistemas de partículas.",
         "El método amount_ratio no existe en CPUParticles2D y el juego no compilaba.", "Cambié a speed_scale para variar la intensidad de la estela.",
         "deffb84"),
        ("Entrada 6 · Enemigos y jefe",
         "Escarchín (patrulla y da la vuelta en bordes con un RayCast2D), Humoro (vuela en ondas) y el jefe Gélido: patrulla la arena, lanza astillas bajas y altas, "
         "entra en fase 2 con la mitad de la vida y convoca un Escarchín.",
         "Al vencer enemigos con la bola de fuego aparecía el error 'Can't change this state while flushing queries'.", "Cambiar propiedades de física con set_deferred y agregar nodos con call_deferred cuando el código corre dentro de un callback de colisión.",
         "4836b6b"),
        ("Entrada 7 · Objetos e interfaz",
         "Chispas, corazones de vida extra, púas, braseros de punto de control, la Hoguera Eterna como meta, letreros con consejos y el HUD (vidas, chispas, nombre del nivel, "
         "mensajes, barra de vida del jefe, resumen de nivel y menú de pausa).",
         "—", "—", "4d9b0de"),
        ("Entrada 8 · Flujo del juego",
         "El controlador de nivel construye todo el mapa desde el ASCII (TileMapLayer con colisiones, parallax, enemigos, objetos), maneja la muerte y reaparición, el final de nivel "
         "con resumen, el menú principal, la pantalla de fin del juego y la de victoria.",
         "—", "—", "b67b568"),
        ("Entrada 9 · Pruebas automáticas",
         "Hice un bot (scripts/bot.gd) que juega solo: camina a la derecha, salta ante paredes, huecos y púas, y en el nivel del jefe se detiene a distancia y dispara. "
         "Con él verifiqué que los 4 niveles se pueden terminar, y de paso encontró varios errores reales:",
         "(a) Embra se hundía en el suelo al iniciar. (b) Con Engine.time_scale las físicas dejaban de ser fiables. (c) El nivel 3 tenía un hueco de 4 casillas imposible de saltar. "
         "(d) En el nivel 1 un salto sobre púas caía justo al borde de un hueco.",
         "(a) Esperar 3 fotogramas de física a que el TileMapLayer cree sus colisiones. (b) Usar --fixed-fps 60, que corre más rápido que el tiempo real sin alterar la física. "
         "(c) Reescribir el nivel con posiciones relativas. (d) Mover las púas.",
         "fff8ac7"),
        ("Entrada 10 · Capturas, exportación y README",
         "Agregué un modo de capturas (--shot) para documentar el juego, el script tools/run_tests.sh, el README y los presets de exportación. Exporté Windows, Linux y Web "
         "y comprobé que el ejecutable de Linux abre el menú y renderiza.",
         "Un error en el menú: una etiqueta se agregaba al nodo equivocado y el panel de controles quedaba vacío.", "Pasar el padre como parámetro de la función que crea las etiquetas.",
         "0e82896"),
        ("Entrada 11 · Documentación",
         "Biblia del videojuego (arte, narrativa, historia y personajes con bosquejos), reporte de pruebas, plan de acción y esta bitácora.",
         "—", "—", "ver commits finales"),
    ]
    for titulo, hecho, problema, solucion, commit in entradas:
        d.add_heading(titulo, 3)
        rich(d, [("Qué hice: ", {"b": True}), (hecho, {})], after=3)
        if problema != "—":
            rich(d, [("Problemas: ", {"b": True}), (problema, {})], after=3)
            rich(d, [("Solución: ", {"b": True}), (solucion, {})], after=3)
        rich(d, [("Commit: ", {"b": True}), (commit, {"i": True})], after=6)

    d.add_heading("4. Historial de versiones (Git)", 1)
    para(d, "Salida de git log al momento de redactar esta bitácora (un commit por etapa):")
    table(d, ["Commit", "Fecha", "Mensaje"], git_log(), widths=[0.8, 1.3, 4.4], font=9)

    d.add_heading("5. Resultados de las pruebas automáticas", 1)
    table(d, ["Nivel", "Zona", "Resultado del bot", "Tiempo de recorrido"], [
        ("1", "Bosque de Ceniza", "Completado", "23.1 s"),
        ("2", "Cuevas de Escarcha", "Completado", "27.4 s"),
        ("3", "Ruinas de Humo", "Completado", "30.6 s"),
        ("4", "Fortaleza Gélida (jefe)", "Completado: el bot derrota a Gélido y llega a la Hoguera", "28.7 s"),
    ], widths=[0.6, 2.0, 2.8, 1.1])
    para(d, "Importante: estas pruebas confirman que los niveles son físicamente completables, pero no dicen nada de la dificultad ni de la diversión. "
            "Para eso falta la prueba con una persona externa (ver el reporte de pruebas).", italic=True)

    d.add_heading("6. Pendientes y siguientes pasos", 1)
    for t in ["Hacer la prueba con al menos una persona externa y llenar el reporte de pruebas.",
              "Ajustar dificultad, vidas y checkpoints según lo que se observe (plan de acción).",
              "Revisar que las fechas y fases de esta bitácora coincidan con las del diagrama de Gantt entregado."]:
        bullet(d, t)
    d.save(os.path.join(DOCS, "Bitacora_de_Desarrollo.docx"))


# ================================================================== BIBLIA
def biblia():
    d = new_doc()
    picture(d, os.path.join(ART, "logo_hoja.png"), 5.8)
    title_block(d, "Biblia del videojuego", "Embra: La Llama Eterna",
                ["Plataformas 2D en pixel art · Godot 4.3", "Versión 1.0 del prototipo · Universidad Tecmilenio"])

    d.add_heading("1. Resumen del juego", 1)
    table(d, ["Concepto", "Descripción"], [
        ("Título", "Embra: La Llama Eterna"),
        ("Género", "Plataformas 2D de acción con jefe final"),
        ("Plataformas", "PC (Windows y Linux) y navegador web"),
        ("Público", "Jugadores casuales de 8 años en adelante; partidas de 10 a 15 minutos"),
        ("Premisa", "Una brasa diminuta debe cruzar cuatro zonas, vencer al Rey de Escarcha y reavivar la Hoguera Eterna que mantiene vivo al pueblo."),
        ("Pilares de diseño", "Controles justos y ágiles · lectura clara a 16 px · calidez frente al frío · desafío que se aprende jugando"),
    ], widths=[1.5, 5.0])
    d.add_heading("Mecánicas principales", 3)
    table(d, ["Acción", "Control", "Reglas"], [
        ("Mover", "A / D o flechas", "Aceleración corta; más control en el suelo que en el aire."),
        ("Saltar", "ESPACIO (W, flecha arriba, Z)", "Salto variable: mantener presionado salta más alto. Margen de salto tras dejar un borde (coyote time) y buffer de salto."),
        ("Bola de fuego", "X (J, Shift)", "Enfriamiento de 0.4 s y máximo 3 bolas en pantalla. Daña enemigos y al jefe."),
        ("Pisotón", "Caer sobre un enemigo", "Vence al enemigo y rebota. Al jefe le quita 2 de vida."),
        ("Vidas", "—", "3 vidas al inicio (máx. 5). Una herida apaga a Embra; reaparece en el último brasero."),
        ("Puntos", "—", "Chispa +10 · Escarchín +50 · Humoro +75 · Gélido +1000 · bonus de nivel."),
    ], widths=[1.1, 1.9, 3.5])

    d.add_heading("2. Historia", 1)
    para(d, "Cenizal es una aldea de piedra que vive al borde del Bosque de Ceniza. Desde antes de que nadie lo recuerde, en el centro del pueblo arde la Hoguera Eterna: "
            "su calor mantiene lejos al invierno y sus chispas dan vida a todo lo que brilla en Cenizal.")
    para(d, "Una noche sin luna, Gélido, el Rey de Escarcha, bajó de su Fortaleza Gélida con un ejército de Escarchines y robó la última chispa de la hoguera. "
            "La llama se apagó, el frío cubrió los caminos y los Humoros, los fantasmas de las llamas que alguna vez se apagaron, comenzaron a rondar las ruinas.")
    para(d, "Pero de entre las cenizas todavía tibias saltó una brasa tan pequeña que nadie la había visto: Embra. No sabe hablar y no sabe rendirse. "
            "Su misión es llegar hasta la Fortaleza Gélida, recuperar la chispa y encender de nuevo la Hoguera Eterna.")
    d.add_heading("Estructura en cuatro actos", 3)
    table(d, ["Acto", "Zona", "Qué pasa", "Altar"], [
        ("1", "Bosque de Ceniza", "Embra aprende a moverse, saltar y quemar. Encuentra a los primeros Escarchines y Humoros.", "Primer altar de la Hoguera Eterna"),
        ("2", "Cuevas de Escarcha", "El frío de Gélida ya llegó hasta las cuevas: hay púas de hielo y más Humoros. Aparecen los braseros que guardan el avance.", "Segundo altar"),
        ("3", "Ruinas de Humo", "Un templo antiguo de los guardianes de la llama. Los saltos son más exigentes y los Humoros vigilan desde arriba.", "Tercer altar"),
        ("4", "Fortaleza Gélida", "Un último tramo helado y la pelea contra Gélido. Al vencerlo aparece la Hoguera principal.", "La Hoguera Eterna se enciende"),
    ], widths=[0.5, 1.4, 3.3, 1.3])

    d.add_heading("3. Narrativa", 1)
    para(d, "El juego cuenta su historia sin diálogos largos: usa el entorno, los letreros y mensajes cortos para que el jugador entienda sin leer demasiado. "
            "El tono es cálido y esperanzado, con un poco de humor suave; el frío es el antagonista y el fuego es la voz de Embra.")
    d.add_heading("Recursos narrativos", 3)
    for pre, t in [("Embra no habla. ", "Se comunica con sus animaciones, su llama y los sonidos de sus saltos y sus chispas."),
                   ("El entorno cuenta la historia. ", "El bosque pasa de tonos cálidos a hielo, humo y luego a la fortaleza: se ve cómo avanza el invierno de Gélido."),
                   ("Letreros. ", "Pequeños carteles de madera enseñan los controles y dan pistas."),
                   ("Mensajes en pantalla. ", "Anuncian cada nivel, los puntos de control, las vidas extra y el jefe."),
                   ("Pantallas finales. ", "Una para la derrota y otra para la victoria con el resumen de la partida.")]:
        bullet(d, t, pre)
    d.add_heading("Textos del juego", 3)
    table(d, ["Momento", "Texto"], [
        ("Inicio del nivel 1", "Nivel 1: Bosque de Ceniza"),
        ("Letrero 1", "Muévete con A / D o con las flechas"),
        ("Letrero 2", "Salta con ESPACIO. Mantén presionado para saltar más alto"),
        ("Letrero 3", "Salta sobre los enemigos para vencerlos"),
        ("Letrero 4", "Presiona X para lanzar una bola de fuego"),
        ("Cuevas de Escarcha", "Las púas lastiman: salta sobre ellas. Los braseros guardan tu avance"),
        ("Cuevas de Escarcha", "Los Humoros vuelan en ondas: espera el momento y pasa por debajo"),
        ("Punto de control", "¡Punto de control!"),
        ("Vida extra", "¡Vida extra!"),
        ("Antes del jefe", "Gélido guarda la última chispa. Pronto lo enfrentarás"),
        ("Antes del jefe", "Dispárale con X y esquiva sus astillas: salta las bajas y quédate en el suelo ante las altas"),
        ("Aparece el jefe", "¡Gélido, el Rey de Escarcha!"),
        ("Fase 2 del jefe", "¡Gélido se enfurece!"),
        ("Jefe vencido", "¡Gélido cayó! Enciende la Hoguera Eterna"),
        ("Fin del juego", "La llama de Embra se apagó... pero una brasa nunca muere del todo."),
        ("Victoria", "¡LA LLAMA ETERNA ARDE DE NUEVO! Embra reavivó la Hoguera Eterna y Cenizal volvió a brillar."),
    ], widths=[1.7, 4.8])

    d.add_heading("4. Personajes y bosquejos", 1)
    para(d, "Cada personaje se diseñó para reconocerse por su silueta y su color incluso a 16 píxeles. Las láminas muestran el bosquejo con las decisiones de diseño, "
            "el arte final tal como aparece en el juego, su paleta y sus cuadros de animación.")
    for fname, cap in [("char_embra.png", "Embra, protagonista."), ("char_escarchin.png", "Escarchín, enemigo común."),
                       ("char_humoro.png", "Humoro, enemigo volador."), ("char_gelido.png", "Gélido, el Rey de Escarcha (jefe final).")]:
        picture(d, os.path.join(ART, fname), 6.5, cap)

    d.add_heading("5. Mundo y niveles", 1)
    zonas = [
        ("Nivel 1 · Bosque de Ceniza", "Tutorial. Tonos púrpura y grises cálidos, árboles de ceniza y un cielo de atardecer. Enseña movimiento, salto, pisotón y fuego.", "Escarchín, un Humoro.", "music_bosque (100 bpm, tono tranquilo)", "mapa_nivel_1.png"),
        ("Nivel 2 · Cuevas de Escarcha", "Cuevas azules con cristales de hielo y púas. Introduce los braseros y más Humoros.", "Escarchín, Humoro, púas.", "music_cuevas (112 bpm, tono misterioso)", "mapa_nivel_2.png"),
        ("Nivel 3 · Ruinas de Humo", "Ruinas grises de ladrillo con pilares y plataformas flotantes. El nivel de plataformas más exigente.", "Escarchín, Humoro, púas.", "music_ruinas (108 bpm, tono tenso)", "mapa_nivel_3.png"),
        ("Nivel 4 · Fortaleza Gélida", "Fortaleza azul oscuro con estandartes. Un tramo corto de preparación y la arena del jefe con dos plataformas para esquivar astillas.", "Escarchín, Humoro y el jefe Gélido.", "music_fortaleza (132 bpm, tono épico)", "mapa_nivel_4.png"),
    ]
    for nombre, desc, enem, musica, mapa in zonas:
        d.add_heading(nombre, 3)
        para(d, desc, after=3)
        rich(d, [("Enemigos: ", {"b": True}), (enem, {}), ("   Música: ", {"b": True}), (musica, {})], after=4)
        picture(d, os.path.join(ART, mapa), 6.5, "Mapa del nivel (se muestra en dos mitades apiladas).")

    d.add_heading("6. Arte visual", 1)
    d.add_heading("Dirección de arte", 3)
    for pre, t in [("Estilo: ", "pixel art con sprites de 16x16 píxeles (el jefe de 32x32) y contorno oscuro de 1 px para separar a los personajes del fondo."),
                   ("Color: ", "cada zona tiene su propia paleta (púrpura cálido, azul glacial, gris humo y azul fortaleza). Embra es siempre lo más cálido de la pantalla, así el ojo lo encuentra primero."),
                   ("Fondos: ", "tres capas con parallax (cielo, montañas lejanas y siluetas cercanas) que cambian según la zona."),
                   ("Interfaz: ", "HUD mínimo arriba (vidas, chispas, nombre del nivel) y mensajes centrados que desaparecen solos."),
                   ("Efectos: ", "partículas de fuego y humo en la estela de Embra, explosiones de chispas al recolectar y vencer enemigos.")]:
        bullet(d, t, pre)
    picture(d, os.path.join(ART, "paleta_tiles.png"), 6.5, "Paleta y tilesets por zona.")
    picture(d, os.path.join(ART, "objetos.png"), 6.5, "Objetos y elementos del mundo.")
    d.add_heading("Audio", 3)
    para(d, "Todo el audio es original y está sintetizado con ondas cuadradas y triangulares para mantener el aire retro: 12 efectos de sonido (salto, chispa, pisotón, fuego, daño, "
            "vida extra, punto de control, impacto, derrota del jefe, astilla, victoria y fin del juego) y 5 pistas de música en bucle (menú y una por zona).")
    d.add_heading("Capturas del prototipo", 3)
    for f, cap in [("shot_menu.png", "Menú principal."), ("shot_n1_inicio.png", "Nivel 1: Bosque de Ceniza."), ("shot_n2_puas.png", "Nivel 2: Cuevas de Escarcha."),
                   ("shot_n3_puente.png", "Nivel 3: Ruinas de Humo."), ("shot_boss_950.png", "Pelea contra Gélido."), ("shot_victoria.png", "Pantalla de victoria.")]:
        picture(d, os.path.join(IMG, f), 4.6, cap)

    d.add_heading("7. Créditos y herramientas", 1)
    para(d, "Diseño, programación, arte y audio del prototipo: proyecto escolar de Universidad Tecmilenio. Herramientas: Godot 4.3, Python con Pillow para el arte, "
            "el módulo wave para el audio, Git para el control de versiones. Todo el arte y el audio fueron creados para este proyecto.")
    d.save(os.path.join(DOCS, "Biblia_del_Videojuego.docx"))


# ================================================================== REPORTE DE PRUEBAS
def reporte():
    d = new_doc(margins=0.9, base_size=10.5)
    para(d, "Reporte de pruebas del prototipo", bold=True, size=17, color=MAROON, after=0)
    para(d, "Embra: La Llama Eterna · Universidad Tecmilenio", italic=True, size=10.5, color=GOLD, after=6)
    table(d, ["Dato", "Registro"], [
        ("Fecha de la prueba", "[COMPLETAR]"),
        ("Persona que probó", "[COMPLETAR: nombre o iniciales, edad aproximada, experiencia con videojuegos]"),
        ("Versión y plataforma", "Prototipo v1.0, ejecutable de [Windows / Linux / navegador]"),
        ("Duración de la sesión", "[COMPLETAR] minutos, sin explicaciones previas más allá de abrir el juego"),
    ], widths=[1.8, 4.9], font=9.5)

    rich(d, [("Objetivo. ", {"b": True}),
             ("Comprobar con una persona ajena al proyecto si los controles se entienden, si la dificultad es razonable y si el juego es divertido y claro de principio a fin.", {})], after=4)
    rich(d, [("Método. ", {"b": True}),
             ("La persona jugó sin ayuda mientras yo observaba y anotaba (ver hoja de observación en el anexo). Al terminar respondió un cuestionario corto de 8 preguntas.", {})], after=4)
    rich(d, [("Pruebas internas previas. ", {"b": True}),
             ("Un bot automático completó los 4 niveles, incluida la pelea contra Gélido. Esto confirma que los niveles se pueden terminar, pero no mide la dificultad.", {})], after=4)

    rich(d, [("Resultados. ", {"b": True}), ("[COMPLETAR después de la prueba con los datos reales]", {"hl": True})], after=2)
    table(d, ["Aspecto", "Qué observé"], [
        ("Controles y primeros 2 minutos", "[COMPLETAR: ¿entendió mover, saltar y disparar sin ayuda? ¿leyó los letreros?]"),
        ("Dificultad", "[COMPLETAR: nivel donde murió más veces, vidas perdidas, ¿llegó al jefe?]"),
        ("Enemigos y jefe", "[COMPLETAR: ¿entendió que se pisan o se queman? ¿cómo reaccionó al jefe?]"),
        ("Claridad visual y sonido", "[COMPLETAR: ¿distinguió peligros, objetos y puntos de control?]"),
        ("Diversión y comentarios", "[COMPLETAR: calificación del 1 al 5 y comentarios textuales]"),
        ("Errores o fallas", "[COMPLETAR: cualquier bug o confusión]"),
    ], widths=[1.9, 4.8], font=9.5)
    rich(d, [("Conclusión. ", {"b": True}), ("[COMPLETAR: 2 o 3 líneas con lo más importante que se aprendió y qué cambios se proponen en el plan de acción.]", {"hl": True})], after=0)

    page_break(d)
    d.add_heading("Anexo A · Protocolo de la prueba", 2)
    for t in ["Preparar el ejecutable y abrir el menú. No explicar los controles: que los descubra con los letreros.",
              "Pedir que juegue entre 10 y 15 minutos pensando en voz alta.",
              "No ayudar salvo que se bloquee por más de un minuto; anotar cuándo ocurre.",
              "Al terminar, aplicar el cuestionario y preguntar qué cambiaría."]:
        bullet(d, t)
    d.add_heading("Hoja de observación", 3)
    table(d, ["Momento", "Qué ocurrió", "Muertes / intentos", "Anotación"], [
        ("Controles (letreros)", "", "", ""), ("Nivel 1", "", "", ""), ("Nivel 2", "", "", ""),
        ("Nivel 3", "", "", ""), ("Nivel 4 / jefe", "", "", ""), ("Fin del juego", "", "", ""),
    ], widths=[1.6, 2.6, 1.2, 1.3], font=9)
    d.add_heading("Cuestionario (1 = muy mal, 5 = muy bien)", 3)
    table(d, ["#", "Pregunta", "Respuesta"], [
        ("1", "¿Se entienden los controles?", ""), ("2", "¿La dificultad es adecuada?", ""),
        ("3", "¿Quedó claro qué hacen los enemigos y cómo vencerlos?", ""), ("4", "¿Se ve bien lo que pasa en pantalla?", ""),
        ("5", "¿El sonido y la música acompañan?", ""), ("6", "¿Qué tan divertido fue?", ""),
        ("7", "¿Qué fue lo mejor del juego?", ""), ("8", "¿Qué cambiarías primero?", ""),
    ], widths=[0.4, 4.6, 1.7], font=9.5)
    d.save(os.path.join(DOCS, "Reporte_de_Pruebas.docx"))


# ================================================================== PLAN DE ACCIÓN
def plan():
    d = new_doc(margins=0.8, base_size=10)
    para(d, "Plan de acción", bold=True, size=18, color=MAROON, after=0)
    para(d, "Respuesta a los resultados de la prueba · Embra: La Llama Eterna", italic=True, size=11, color=GOLD, after=8)

    d.add_heading("1. Cómo se decide qué corregir", 2)
    para(d, "Cada hallazgo de la prueba se clasifica por impacto en la experiencia (alto, medio, bajo) y por esfuerzo de corregirlo (alto, medio, bajo). "
            "Se atiende primero lo de alto impacto y bajo esfuerzo, después lo de alto impacto y alto esfuerzo, y al final lo demás. "
            "Después de cada corrección se vuelve a correr el bot (tools/run_tests.sh) y se registra el cambio en un commit y en la bitácora.")

    d.add_heading("2. Mejoras ya identificadas por el equipo", 2)
    para(d, "Estas mejoras salieron de la revisión del propio prototipo, antes de la prueba con usuarios; la prueba servirá para confirmar su prioridad.", italic=True)
    table(d, ["#", "Mejora", "Por qué", "Cómo", "Prio."], [
        ("1", "Ajustar la dificultad", "El bot solo prueba que los niveles se pueden terminar; no mide dificultad.", "Según la prueba: más vidas o braseros, o menos púas/enemigos en el nivel donde más se muera.", "Alta"),
        ("2", "Salud en lugar de una sola vida por golpe", "Una herida apaga a Embra; puede frustrar.", "Agregar 2 puntos de corazón por vida y un breve retroceso al ser golpeado.", "Media"),
        ("3", "Ajustes de volumen", "El sonido no se puede bajar desde el juego.", "Pantalla de opciones con volumen de música y efectos.", "Media"),
        ("4", "Guardar el progreso", "Cada partida empieza desde el nivel 1.", "Guardar el nivel alcanzado y la mejor puntuación con ConfigFile.", "Media"),
        ("5", "Mejorar los menús para control de consola", "El menú se maneja mejor con teclado y ratón.", "Agregar navegación con D-pad y botón A en menús y pantallas finales.", "Baja"),
        ("6", "Más variedad de música y arte", "Las pistas son cortas y se repiten.", "Alargar los loops y agregar variaciones por nivel.", "Baja"),
        ("7", "Tipografía pixel art", "La fuente por defecto no combina del todo con el arte.", "Incluir una fuente pixelada con licencia libre en el tema de la interfaz.", "Baja"),
    ], widths=[0.3, 1.5, 1.8, 2.5, 0.5], font=9)

    d.add_heading("3. Acciones a partir de la prueba con usuario", 2)
    para(d, "Llenar esta tabla con los hallazgos del reporte de pruebas.", italic=True)
    table(d, ["Hallazgo observado", "Impacto", "Acción propuesta", "Prioridad", "Responsable", "Criterio de éxito"], [
        ("[COMPLETAR]", "", "", "", "", ""),
        ("[COMPLETAR]", "", "", "", "", ""),
        ("[COMPLETAR]", "", "", "", "", ""),
        ("[COMPLETAR]", "", "", "", "", ""),
    ], widths=[1.6, 0.7, 1.7, 0.7, 0.9, 1.1], font=9)

    d.add_heading("4. Seguimiento", 2)
    for t in ["Revisión de resultados y priorización: una sesión corta apenas termine la prueba.",
              "Implementar las acciones de prioridad alta en la siguiente iteración y registrar cada una en la bitácora.",
              "Repetir la prueba con otra persona externa para confirmar que los cambios ayudaron.",
              "Exportar de nuevo el ejecutable y actualizar el README con la nueva versión."]:
        bullet(d, t)
    d.save(os.path.join(DOCS, "Plan_de_Accion.docx"))


if __name__ == "__main__":
    bitacora()
    biblia()
    reporte()
    plan()
    print("Documentos generados en", os.path.abspath(DOCS))
