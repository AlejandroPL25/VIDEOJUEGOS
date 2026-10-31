extends Control
## EndScreen.gd -- Pantallas de "Fin del juego" y "Victoria" (según la variable mode).
## Victoria: Embra encendió el altar final y la fogata ancestral vuelve a arder; muestra el resumen
## y la tabla de mejores puntajes por nivel.

@export var mode := "gameover"   # "gameover" | "victory"

const AMBER := Color("F4A62A")
const CREAM := Color("FFF3C4")


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
		title = "¡LA FOGATA ANCESTRAL ARDE DE NUEVO!"
		var minutes := int(Global.play_time) / 60
		var seconds := int(Global.play_time) % 60
		body = "Embra encendió el altar y el Bosque de Brasas volvió a brillar.\n\n"
		body += "Puntaje total: %d\nChispas: %d  ·  Enemigos vencidos: %d\nVidas perdidas: %d  ·  Tiempo: %d:%02d\nEtapa final de Embra: %s\n\n" % [
			Global.total_score, Global.sparks, Global.kills, Global.deaths, minutes, seconds, Global.STAGE_NAMES[Global.stage() - 1]]
		body += "MEJOR PUNTAJE POR NIVEL\n"
		for i in LevelData.LEVELS.size():
			body += "%d. %s: %d\n" % [i + 1, LevelData.LEVELS[i]["name"], Global.best_scores[i]]
		body += "\nENTER: volver al menú   Q: salir"
	else:
		Global.play_sfx("gameover")
		title = "FIN DEL JUEGO"
		body = "La brasa de Embra se apagó... pero siempre queda una chispa.\n\nENTER: reintentar el nivel\nM: menú principal   Q: salir"

	var tl := _label(title, Vector2(0, 24), 15, AMBER)
	tl.size = Vector2(480, 24)
	tl.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	var bl := _label(body, Vector2(60, 58), 10, Color.WHITE)
	bl.size = Vector2(360, 200)
	bl.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	bl.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART


func _label(text: String, pos: Vector2, size: int, color: Color) -> Label:
	var l := Label.new()
	l.text = text
	l.position = pos
	l.add_theme_font_size_override("font_size", size)
	l.add_theme_color_override("font_color", color)
	l.add_theme_color_override("font_outline_color", Color(0.07, 0.08, 0.17))
	l.add_theme_constant_override("outline_size", 3)
	add_child(l)
	return l


func _unhandled_input(event: InputEvent) -> void:
	if event.is_action_pressed("quit_game") and not OS.has_feature("web"):
		Global.quit_game()
	elif event.is_action_pressed("confirm"):
		Global.stop_music()
		if mode == "victory":
			get_tree().change_scene_to_file("res://scenes/main_menu.tscn")
		else:
			Global.lives = Global.START_LIVES
			Global.restore_level_start()
			get_tree().change_scene_to_file("res://scenes/level.tscn")
	elif mode == "gameover" and event.is_action_pressed("menu"):
		Global.stop_music()
		get_tree().change_scene_to_file("res://scenes/main_menu.tscn")
