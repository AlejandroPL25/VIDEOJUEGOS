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
	logo.scale = Vector2(1.6, 1.6)
	logo.position = Vector2(240 - 91 * 1.6, 22)
	add_child(logo)

	var sub := _label("BOSQUE DE BRASAS", Vector2(0, 100), 14, AMBER)
	sub.size = Vector2(480, 20)
	sub.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER

	var embra := TextureRect.new()
	embra.texture = Global.make_frames("embra_sheet.png", 16, 20, {"i": {"frames": [0], "fps": 1.0}}).get_frame_texture("i", 0)
	embra.scale = Vector2(3, 3)
	embra.position = Vector2(216, 124)
	add_child(embra)

	play_button = _button("Jugar", Vector2(190, 188))
	play_button.pressed.connect(_on_play)
	var scores := _button("Mejores puntajes", Vector2(190, 212))
	scores.pressed.connect(func() -> void:
		controls_panel.visible = false
		scores_panel.visible = not scores_panel.visible)
	var controls := _button("Controles", Vector2(190, 236))
	controls.pressed.connect(func() -> void:
		scores_panel.visible = false
		controls_panel.visible = not controls_panel.visible)
	play_button.grab_focus()

	controls_panel = _panel("CONTROLES\n\nMover: flechas izquierda / derecha (o A / D)\nSaltar: ESPACIO\nPausa: ESC o P\n\nLlega al altar de cada nivel, recoge chispas\ny evita a los Rondines y al fuego.")
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
	p.position = Vector2(95, 62)
	p.size = Vector2(290, 120)
	p.visible = false
	add_child(p)
	var l := _label(text, Vector2(12, 8), 9, Color.WHITE, p)
	l.size = Vector2(266, 106)
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


func _button(text: String, pos: Vector2) -> Button:
	var b := Button.new()
	b.text = text
	b.position = pos
	b.size = Vector2(100, 20)
	b.add_theme_font_size_override("font_size", 9)
	add_child(b)
	return b


func _on_play() -> void:
	Global.play_sfx("click")
	Global.start_new_game()
	Global.stop_music()
	get_tree().change_scene_to_file("res://scenes/level.tscn")
