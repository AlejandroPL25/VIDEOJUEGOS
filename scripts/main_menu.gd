extends Control
## MainMenu.gd -- Menú principal de EMBRA: Bosque de Brasas.
## Botones: Jugar, Mejores puntajes (tabla por nivel del GDD), Controles y Salir.

const AMBER := Color("F4A62A")
const CREAM := Color("FFF3C4")

var controls_panel: Control
var scores_panel: Control
var play_button: Button


func _ready() -> void:
	Global.play_music("music_menu")
	for f in ["bg_sky_0.png", "bg_far_0.png", "bg_near_0.png"]:
		var t := TextureRect.new()
		t.texture = Global.tex(f)
		add_child(t)

	var logo := TextureRect.new()
	logo.texture = Global.tex("logo.png")
	logo.scale = Vector2(1.4, 1.4)
	logo.position = Vector2(240 - 91 * 1.4, 8)
	add_child(logo)

	var sub := _label("BOSQUE DE BRASAS", Vector2(0, 80), 13, AMBER)
	sub.size = Vector2(480, 20)
	sub.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER

	# Las tres etapas de Embra, de la brasa al fuego ardiente
	var xs := [190, 232, 274]
	var files := ["embra_sheet.png", "embra2_sheet.png", "embra3_sheet.png"]
	for i in 3:
		var e := TextureRect.new()
		e.texture = Global.make_frames(files[i], 16, 24, {"i": {"frames": [0], "fps": 1.0}}).get_frame_texture("i", 0)
		e.scale = Vector2(1.6, 1.6)
		e.position = Vector2(xs[i], 106)
		add_child(e)

	# Botones centrados en una columna
	var box := VBoxContainer.new()
	box.position = Vector2(165, 150)
	box.add_theme_constant_override("separation", 4)
	add_child(box)
	play_button = _button("Jugar", box)
	play_button.pressed.connect(_on_play)
	var scores := _button("Mejores puntajes", box)
	scores.pressed.connect(func() -> void:
		controls_panel.visible = false
		scores_panel.visible = not scores_panel.visible)
	var controls := _button("Controles", box)
	controls.pressed.connect(func() -> void:
		scores_panel.visible = false
		controls_panel.visible = not controls_panel.visible)
	var quit := _button("Salir", box)
	quit.pressed.connect(func() -> void: Global.quit_game())
	if OS.has_feature("web"):
		quit.visible = false      # en el navegador no se puede cerrar la pestaña desde el juego
	play_button.grab_focus()

	controls_panel = _panel("CONTROLES\n\nMover: flechas izquierda / derecha (o A / D)\nSaltar: ESPACIO\nBola de fuego: X (desde la etapa Llama)\nPausa: ESC o P    Salir: Q (en pausa)\n\nPisa a los enemigos o quémalos. Junta chispas\npara evolucionar: Brasa, Llama y Fuego ardiente.")
	var lines := "MEJORES PUNTAJES\n\n"
	for i in LevelData.LEVELS.size():
		lines += "%d. %s: %d\n" % [i + 1, LevelData.LEVELS[i]["name"], Global.best_scores[i]]
	scores_panel = _panel(lines)

	var credit := _label("Proyecto escolar - Universidad Tecmilenio", Vector2(0, 258), 8, Color(0.8, 0.78, 0.9))
	credit.size = Vector2(480, 12)
	credit.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER


func _panel(text: String) -> Control:
	var p := ColorRect.new()
	p.color = Color(0.1, 0.12, 0.23, 0.95)
	p.position = Vector2(90, 50)
	p.size = Vector2(300, 130)
	p.visible = false
	add_child(p)
	var l := _label(text, Vector2(12, 8), 9, Color.WHITE, p)
	l.size = Vector2(276, 116)
	return p


func _label(text: String, pos: Vector2, size: int, color: Color, parent: Node = null) -> Label:
	var l := Label.new()
	l.text = text
	l.position = pos
	l.add_theme_font_size_override("font_size", size)
	l.add_theme_color_override("font_color", color)
	l.add_theme_color_override("font_outline_color", Color(0.07, 0.08, 0.17))
	l.add_theme_constant_override("outline_size", 3)
	(parent if parent != null else self).add_child(l)
	return l


func _button(text: String, parent: Node) -> Button:
	var b := Button.new()
	b.text = text
	b.custom_minimum_size = Vector2(150, 22)
	Global.style_button(b, 10)
	parent.add_child(b)
	return b


func _on_play() -> void:
	Global.play_sfx("click")
	Global.start_new_game()
	Global.stop_music()
	get_tree().change_scene_to_file("res://scenes/level.tscn")
