extends CanvasLayer
class_name Hud
## Hud.gd -- Interfaz en pantalla: vidas, chispas, puntaje del nivel, nombre del nivel, mensajes,
## resumen de nivel y menú de pausa. Se construye por código con la paleta del GDD.

const AMBER := Color("F4A62A")
const CREAM := Color("FFF3C4")
const NIGHT := Color("1B1F3B")
const FIRE := Color("E8542A")

var lives_label: Label
var sparks_label: Label
var score_label: Label
var stage_label: Label
var bar_fill: ColorRect
var name_label: Label
var msg_label: Label
var summary_root: Control
var summary_label: Label
var _pause_resume_button: Button
var pause_root: Control
var _msg_timer := 0.0


func _ready() -> void:
	layer = 10
	process_mode = Node.PROCESS_MODE_ALWAYS     # sigue activo con el juego en pausa

	var life := TextureRect.new()
	life.texture = Global.tex("life_icon.png")
	life.position = Vector2(8, 8)
	add_child(life)
	lives_label = _label("x3", Vector2(20, 5), 10)

	var spark := TextureRect.new()
	var at := AtlasTexture.new()
	at.atlas = Global.tex("spark.png")
	at.region = Rect2(0, 0, 8, 8)
	spark.texture = at
	spark.position = Vector2(58, 8)
	add_child(spark)
	sparks_label = _label("0/0", Vector2(69, 5), 10)

	score_label = _label("Puntos: 0", Vector2(125, 5), 10)
	score_label.add_theme_color_override("font_color", AMBER)

	# Barra de evolución de Embra (mejora posterior a la prueba con usuarios)
	stage_label = _label("Brasa", Vector2(8, 18), 8)
	stage_label.add_theme_color_override("font_color", CREAM)
	var bar_bg := ColorRect.new()
	bar_bg.color = Color(NIGHT, 0.9)
	bar_bg.position = Vector2(8, 31)
	bar_bg.size = Vector2(110, 6)
	add_child(bar_bg)
	bar_fill = ColorRect.new()
	bar_fill.color = AMBER
	bar_fill.position = Vector2(9, 32)
	bar_fill.size = Vector2(0, 4)
	add_child(bar_fill)

	name_label = _label("", Vector2(250, 5), 9)
	name_label.size = Vector2(222, 14)
	name_label.horizontal_alignment = HORIZONTAL_ALIGNMENT_RIGHT
	name_label.add_theme_color_override("font_color", CREAM)

	msg_label = _label("", Vector2(40, 60), 14)
	msg_label.size = Vector2(400, 30)
	msg_label.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	msg_label.add_theme_color_override("font_color", CREAM)
	msg_label.visible = false

	# Resumen al terminar el nivel
	summary_root = Control.new()
	summary_root.visible = false
	add_child(summary_root)
	var sbg := ColorRect.new()
	sbg.color = Color(NIGHT, 0.93)
	sbg.position = Vector2(100, 50)
	sbg.size = Vector2(280, 170)
	summary_root.add_child(sbg)
	summary_label = _label("", Vector2(112, 58), 10, summary_root)
	summary_label.size = Vector2(256, 150)
	summary_label.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART

	# Pausa: Continuar, Menú principal y Salir del juego
	pause_root = Control.new()
	pause_root.visible = false
	add_child(pause_root)
	var pbg := ColorRect.new()
	pbg.color = Color(NIGHT, 0.88)
	pbg.size = Vector2(480, 270)
	pause_root.add_child(pbg)
	var pl := _label("PAUSA", Vector2(0, 70), 16, pause_root)
	pl.size = Vector2(480, 24)
	pl.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	var box := VBoxContainer.new()
	box.position = Vector2(165, 108)
	box.add_theme_constant_override("separation", 5)
	pause_root.add_child(box)
	var resume := _pause_button("Continuar", box)
	resume.pressed.connect(_resume)
	var menu := _pause_button("Menú principal", box)
	menu.pressed.connect(_go_menu)
	var quit := _pause_button("Salir del juego", box)
	quit.pressed.connect(func() -> void: Global.quit_game())
	if OS.has_feature("web"):
		quit.visible = false
	_pause_resume_button = resume

	Global.lives_changed.connect(set_lives)
	set_lives(Global.lives)


func _label(text: String, pos: Vector2, font_size: int, parent: Node = null) -> Label:
	var l := Label.new()
	l.text = text
	l.position = pos
	l.add_theme_font_size_override("font_size", font_size)
	l.add_theme_color_override("font_color", Color.WHITE)
	l.add_theme_color_override("font_outline_color", Color(0.07, 0.08, 0.17))
	l.add_theme_constant_override("outline_size", 3)
	(parent if parent != null else self).add_child(l)
	return l


func _pause_button(text: String, parent: Node) -> Button:
	var b := Button.new()
	b.text = text
	b.custom_minimum_size = Vector2(150, 24)
	Global.style_button(b, 10)
	parent.add_child(b)
	return b


func _resume() -> void:
	get_tree().paused = false
	pause_root.visible = false


func _go_menu() -> void:
	get_tree().paused = false
	Global.stop_music()
	get_tree().change_scene_to_file("res://scenes/main_menu.tscn")


func set_evolution(stage: int, progress: float, to_next: int) -> void:
	var name_text: String = Global.STAGE_NAMES[stage - 1]
	if stage >= Global.STAGE_NAMES.size():
		stage_label.text = "%s (máxima)" % name_text
	else:
		stage_label.text = "%s · %d chispas para evolucionar" % [name_text, to_next]
	bar_fill.size.x = 108.0 * progress
	bar_fill.color = AMBER if stage < 3 else FIRE


func set_lives(n: int) -> void:
	lives_label.text = "x%d" % max(n, 0)


func set_sparks(collected: int, total: int) -> void:
	sparks_label.text = "%d/%d" % [collected, total]


func set_score(points: int) -> void:
	score_label.text = "Puntos: %d" % points


func show_message(text: String, seconds: float = 2.0) -> void:
	msg_label.text = text
	msg_label.visible = true
	_msg_timer = seconds


func show_summary(text: String) -> void:
	summary_label.text = text
	summary_root.visible = true


func _process(delta: float) -> void:
	if _msg_timer > 0.0:
		_msg_timer -= delta
		if _msg_timer <= 0.0:
			msg_label.visible = false


func _unhandled_input(event: InputEvent) -> void:
	if summary_root.visible:
		return
	if event.is_action_pressed("pause"):
		var now_paused := not get_tree().paused
		get_tree().paused = now_paused
		pause_root.visible = now_paused
		if now_paused:
			_pause_resume_button.grab_focus()
	elif get_tree().paused and event.is_action_pressed("menu"):
		_go_menu()
	elif get_tree().paused and event.is_action_pressed("quit_game"):
		Global.quit_game()
