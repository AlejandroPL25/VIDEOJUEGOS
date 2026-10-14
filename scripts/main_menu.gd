extends Control
## MainMenu.gd -- Menú principal: Jugar, Controles y Salir.

var controls_panel: Control
var play_button: Button


func _ready() -> void:
	Global.play_music("music_menu")
	for f in ["bg_sky_0.png", "bg_far_0.png", "bg_near_0.png"]:
		var t := TextureRect.new()
		t.texture = Global.tex(f)
		t.position = Vector2.ZERO
		add_child(t)

	var logo := TextureRect.new()
	logo.texture = Global.tex("logo.png")
	logo.scale = Vector2(1.6, 1.6)
	logo.position = Vector2(240 - 91 * 1.6, 28)
	add_child(logo)

	var sub := _label("LA LLAMA ETERNA", Vector2(0, 108), 14, Color(1, 0.85, 0.5))
	sub.size = Vector2(480, 20)
	sub.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER

	var embra := TextureRect.new()
	embra.texture = Global.make_frames("embra_sheet.png", 16, 16, {"i": {"frames": [0], "fps": 1.0}}).get_frame_texture("i", 0)
	embra.scale = Vector2(3, 3)
	embra.position = Vector2(216, 130)
	add_child(embra)

	play_button = _button("Jugar", Vector2(190, 185))
	play_button.pressed.connect(_on_play)
	var controls := _button("Controles", Vector2(190, 211))
	controls.pressed.connect(func() -> void: controls_panel.visible = not controls_panel.visible)
	var quit := _button("Salir", Vector2(190, 237))
	quit.pressed.connect(func() -> void: get_tree().quit())
	if OS.has_feature("web"):
		quit.visible = false
	play_button.grab_focus()

	controls_panel = ColorRect.new()
	(controls_panel as ColorRect).color = Color(0.1, 0.05, 0.15, 0.93)
	controls_panel.position = Vector2(110, 60)
	controls_panel.size = Vector2(260, 130)
	controls_panel.visible = false
	add_child(controls_panel)
	var cl := _label("CONTROLES\n\nMover: A / D o flechas\nSaltar: ESPACIO (mantén = más alto)\nBola de fuego: X\nPausa: ESC / P\n\nPisa a los enemigos o quémalos.", Vector2(12, 8), 9, Color(1, 1, 1), controls_panel)
	cl.size = Vector2(236, 114)

	var credit := _label("Proyecto escolar - Universidad Tecmilenio", Vector2(0, 258), 8, Color(0.8, 0.75, 0.85))
	credit.size = Vector2(480, 12)
	credit.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER


func _label(text: String, pos: Vector2, size: int, color: Color, parent: Node = null) -> Label:
	var l := Label.new()
	l.text = text
	l.position = pos
	l.add_theme_font_size_override("font_size", size)
	l.add_theme_color_override("font_color", color)
	l.add_theme_color_override("font_outline_color", Color(0.1, 0.05, 0.12))
	l.add_theme_constant_override("outline_size", 3)
	(parent if parent != null else self).add_child(l)
	return l


func _button(text: String, pos: Vector2) -> Button:
	var b := Button.new()
	b.text = text
	b.position = pos
	b.size = Vector2(100, 22)
	b.add_theme_font_size_override("font_size", 10)
	add_child(b)
	return b


func _on_play() -> void:
	Global.play_sfx("click")
	Global.start_new_game()
	Global.stop_music()
	get_tree().change_scene_to_file("res://scenes/level.tscn")
