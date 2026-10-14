extends Control
## EndScreen.gd -- Pantallas de "Fin del juego" y "Victoria" (según la variable mode).

@export var mode := "gameover"   # "gameover" | "victory"


func _ready() -> void:
	var sky := "bg_sky_3.png" if mode == "victory" else "bg_sky_0.png"
	var t := TextureRect.new()
	t.texture = Global.tex(sky)
	add_child(t)
	var near := TextureRect.new()
	near.texture = Global.tex("bg_near_3.png" if mode == "victory" else "bg_near_0.png")
	add_child(near)

	var title := ""
	var body := ""
	if mode == "victory":
		Global.play_music("music_menu")
		Global.play_sfx("win")
		title = "¡LA LLAMA ETERNA ARDE DE NUEVO!"
		var minutes := int(Global.play_time) / 60
		var seconds := int(Global.play_time) % 60
		body = ("Embra reavivó la Hoguera Eterna y Cenizal volvió a brillar.\n\n" +
			"Chispas recogidas: %d\nEnemigos vencidos: %d\nVidas perdidas: %d\nTiempo: %d:%02d\n" +
			"PUNTOS: %d\n\nENTER: volver al menú") % [Global.sparks, Global.kills, Global.deaths, minutes, seconds, Global.score]
	else:
		Global.play_sfx("gameover")
		title = "FIN DEL JUEGO"
		body = "La llama de Embra se apagó... pero una brasa nunca muere del todo.\n\nENTER: reintentar el nivel\nM: menú principal"

	var tl := _label(title, Vector2(0, 40), 16, Color(1, 0.85, 0.45))
	tl.size = Vector2(480, 24)
	tl.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	var bl := _label(body, Vector2(60, 80), 10, Color(1, 1, 1))
	bl.size = Vector2(360, 160)
	bl.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	bl.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART


func _label(text: String, pos: Vector2, size: int, color: Color) -> Label:
	var l := Label.new()
	l.text = text
	l.position = pos
	l.add_theme_font_size_override("font_size", size)
	l.add_theme_color_override("font_color", color)
	l.add_theme_color_override("font_outline_color", Color(0.1, 0.05, 0.12))
	l.add_theme_constant_override("outline_size", 3)
	add_child(l)
	return l


func _unhandled_input(event: InputEvent) -> void:
	if event.is_action_pressed("confirm"):
		if mode == "victory":
			Global.stop_music()
			get_tree().change_scene_to_file("res://scenes/main_menu.tscn")
		else:
			Global.lives = Global.START_LIVES
			Global.stop_music()
			get_tree().change_scene_to_file("res://scenes/level.tscn")
	elif mode == "gameover" and event.is_action_pressed("menu"):
		Global.stop_music()
		get_tree().change_scene_to_file("res://scenes/main_menu.tscn")
