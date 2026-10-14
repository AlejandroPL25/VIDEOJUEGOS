extends CanvasLayer
class_name Hud
## Hud.gd -- Interfaz en pantalla: vidas, chispas, nombre del nivel, mensajes, barra del jefe,
## resumen de nivel y menú de pausa. Se construye por código.

var lives_label: Label
var sparks_label: Label
var name_label: Label
var msg_label: Label
var boss_root: Control
var boss_fill: ColorRect
var summary_root: Control
var summary_label: Label
var pause_root: Control
var _msg_timer := 0.0


func _ready() -> void:
	layer = 10
	process_mode = Node.PROCESS_MODE_ALWAYS     # sigue activo con el juego en pausa

	var heart := TextureRect.new()
	heart.texture = Global.tex("heart.png")
	heart.position = Vector2(8, 8)
	add_child(heart)
	lives_label = _label("x3", Vector2(21, 5), 10)

	var spark := TextureRect.new()
	var at := AtlasTexture.new()
	at.atlas = Global.tex("spark.png")
	at.region = Rect2(0, 0, 8, 8)
	spark.texture = at
	spark.position = Vector2(60, 9)
	add_child(spark)
	sparks_label = _label("0/0", Vector2(71, 5), 10)

	name_label = _label("", Vector2(250, 5), 9)
	name_label.size = Vector2(222, 14)
	name_label.horizontal_alignment = HORIZONTAL_ALIGNMENT_RIGHT
	name_label.add_theme_color_override("font_color", Color(1, 0.85, 0.5))

	msg_label = _label("", Vector2(40, 60), 14)
	msg_label.size = Vector2(400, 30)
	msg_label.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	msg_label.add_theme_color_override("font_color", Color(1, 0.95, 0.7))
	msg_label.visible = false

	# Barra de vida del jefe
	boss_root = Control.new()
	boss_root.visible = false
	add_child(boss_root)
	var bg := ColorRect.new()
	bg.color = Color(0.1, 0.05, 0.12, 0.85)
	bg.position = Vector2(140, 246)
	bg.size = Vector2(200, 12)
	boss_root.add_child(bg)
	boss_fill = ColorRect.new()
	boss_fill.color = Color(0.45, 0.8, 1.0)
	boss_fill.position = Vector2(142, 248)
	boss_fill.size = Vector2(196, 8)
	boss_root.add_child(boss_fill)
	var bl := _label("GÉLIDO", Vector2(140, 232), 9, boss_root)
	bl.size = Vector2(200, 12)
	bl.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER

	# Resumen al terminar el nivel
	summary_root = Control.new()
	summary_root.visible = false
	add_child(summary_root)
	var sbg := ColorRect.new()
	sbg.color = Color(0.1, 0.05, 0.15, 0.9)
	sbg.position = Vector2(100, 50)
	sbg.size = Vector2(280, 170)
	summary_root.add_child(sbg)
	summary_label = _label("", Vector2(112, 58), 10, summary_root)
	summary_label.size = Vector2(256, 150)
	summary_label.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART

	# Pausa
	pause_root = Control.new()
	pause_root.visible = false
	add_child(pause_root)
	var pbg := ColorRect.new()
	pbg.color = Color(0.05, 0.02, 0.08, 0.8)
	pbg.size = Vector2(480, 270)
	pause_root.add_child(pbg)
	var pl := _label("PAUSA\n\nESC / P: continuar\nM: volver al menú", Vector2(0, 90), 14, pause_root)
	pl.size = Vector2(480, 120)
	pl.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER

	Global.lives_changed.connect(set_lives)
	set_lives(Global.lives)


func _label(text: String, pos: Vector2, font_size: int, parent: Node = null) -> Label:
	var l := Label.new()
	l.text = text
	l.position = pos
	l.add_theme_font_size_override("font_size", font_size)
	l.add_theme_color_override("font_color", Color(1, 1, 1))
	l.add_theme_color_override("font_outline_color", Color(0.1, 0.05, 0.12))
	l.add_theme_constant_override("outline_size", 3)
	(parent if parent != null else self).add_child(l)
	return l


func set_lives(n: int) -> void:
	lives_label.text = "x%d" % max(n, 0)


func set_sparks(collected: int, total: int) -> void:
	sparks_label.text = "%d/%d" % [collected, total]


func show_message(text: String, seconds: float = 2.0) -> void:
	msg_label.text = text
	msg_label.visible = true
	_msg_timer = seconds


func show_boss(hp: int, max_hp: int) -> void:
	boss_root.visible = true
	set_boss_hp(hp, max_hp)


func set_boss_hp(hp: int, max_hp: int) -> void:
	boss_fill.size.x = 196.0 * float(hp) / float(max_hp)


func hide_boss() -> void:
	boss_root.visible = false


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
	elif get_tree().paused and event.is_action_pressed("menu"):
		get_tree().paused = false
		Global.stop_music()
		get_tree().change_scene_to_file("res://scenes/main_menu.tscn")
