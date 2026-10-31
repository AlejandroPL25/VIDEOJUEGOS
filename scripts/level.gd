extends Node2D
class_name Level
## Level.gd -- Construye un nivel a partir del mapa ASCII (ver level_data.gd / tools/make_levels.py)
## y administra la partida: fondo nocturno, plataformas, Rondines, zonas de fuego, chispas, puntos de
## control, penalizaciones, final de nivel con mejor puntaje y modo de pruebas automáticas.

const TILE := 16

var data: Dictionary
var grid: Array = []
var width_tiles := 0
var height_tiles := 0
var theme := 0

var player: Player
var hud: Hud
var tilemap: TileMapLayer
var goal_node: Goal = null

var checkpoint_pos := Vector2.ZERO
var sparks_in_level := 0
var sparks_collected := 0
var level_done := false
var waiting_confirm := false
var elapsed := 0.0
var bot: Bot = null


func _ready() -> void:
	data = LevelData.LEVELS[Global.current_level]
	theme = data["theme"]
	for r in data["rows"]:
		grid.append(String(r))
	height_tiles = grid.size()
	width_tiles = String(grid[0]).length()
	Global.start_level()

	_build_background()
	_build_tilemap()
	_build_borders()

	player = Player.new()
	player.level = self
	add_child(player)
	hud = Hud.new()
	add_child(hud)

	_spawn_entities()
	player.set_stage(Global.stage(), false)
	Global.stage_changed.connect(_on_stage_changed)
	player.global_position = checkpoint_pos
	player.camera.limit_left = 0
	player.camera.limit_right = width_tiles * TILE
	player.camera.limit_top = 0
	player.camera.limit_bottom = height_tiles * TILE
	player.camera.reset_smoothing()

	# Opción de desarrollo: --tp=x,y (en tiles) coloca a Embra para tomar capturas
	for a in OS.get_cmdline_user_args():
		if a.begins_with("--tp="):
			var parts := a.substr(5).split(",")
			player.global_position = Vector2(float(parts[0]) * TILE + 8, float(parts[1]) * TILE + 8)
			checkpoint_pos = player.global_position
			player.camera.reset_smoothing()

	hud.name_label.text = "%d. %s" % [Global.current_level + 1, data["name"]]
	refresh_hud()
	hud.show_message("Nivel %d: %s" % [Global.current_level + 1, data["name"]], 2.5)
	Global.play_music(data["music"])

	# El mapa de tiles crea sus cuerpos físicos en los primeros fotogramas: se espera antes de soltar a Embra
	player.set_physics_process(false)
	if Global.autotest:
		bot = Bot.new()
		bot.level = self
		player.bot = bot
		print("[TEST] Nivel %d '%s' (%dx%d, chispas=%d)" % [Global.current_level + 1, data["name"], width_tiles, height_tiles, sparks_in_level])
	for i in 3:
		await get_tree().physics_frame
	player.set_physics_process(true)


# ---------------------------------------------------------------- Interfaz y evolución
## Actualiza chispas, puntaje y barra de evolución del HUD.
func refresh_hud() -> void:
	hud.set_sparks(sparks_collected, sparks_in_level)
	hud.set_score(Global.level_score)
	hud.set_evolution(Global.stage(), Global.stage_progress(), Global.sparks_to_next())


func _on_stage_changed(new_stage: int) -> void:
	player.set_stage(new_stage, true)
	refresh_hud()
	var extra := " Ahora lanzas fuego con X." if new_stage == 2 else " Tu fuego atraviesa enemigos."
	hud.show_message("¡Embra evolucionó: %s!%s" % [Global.STAGE_NAMES[new_stage - 1], extra], 3.0)
	if Global.autotest:
		print("[TEST] Evolución a etapa %d (%s) con %d chispas" % [new_stage, Global.STAGE_NAMES[new_stage - 1], Global.sparks])


## Texto flotante "+puntos" al vencer a un enemigo.
func show_points(pos: Vector2, points: int) -> void:
	var l := Label.new()
	l.text = "+%d" % points
	l.add_theme_font_size_override("font_size", 9)
	l.add_theme_color_override("font_color", Color("FFF3C4"))
	l.add_theme_color_override("font_outline_color", Color(0.07, 0.08, 0.17))
	l.add_theme_constant_override("outline_size", 3)
	l.position = pos + Vector2(-8, -22)
	l.z_index = 30
	add_child(l)
	var tw := create_tween()
	tw.tween_property(l, "position:y", l.position.y - 14.0, 0.7)
	tw.parallel().tween_property(l, "modulate:a", 0.0, 0.7)
	tw.tween_callback(l.queue_free)


# ---------------------------------------------------------------- Consulta del mapa
func cell_char(x: int, y: int) -> String:
	if y < 0 or y >= height_tiles or x < 0 or x >= width_tiles:
		return " "
	return String(grid[y])[x]


func is_solid(x: int, y: int) -> bool:
	if x < 0 or x >= width_tiles:
		return true
	return cell_char(x, y) == "#"


# ---------------------------------------------------------------- Construcción
func _build_background() -> void:
	var pb := ParallaxBackground.new()
	add_child(pb)
	var layers := [["bg_sky_%d.png" % theme, Vector2(0, 0)],
			["bg_far_%d.png" % theme, Vector2(0.12, 0)],
			["bg_near_%d.png" % theme, Vector2(0.3, 0)]]
	for l in layers:
		var pl := ParallaxLayer.new()
		pl.motion_scale = l[1]
		pl.motion_mirroring = Vector2(480, 0) if l[1].x > 0.0 else Vector2.ZERO
		var spr := Sprite2D.new()
		spr.texture = Global.tex(l[0])
		spr.centered = false
		pl.add_child(spr)
		pb.add_child(pl)


func _make_tileset() -> TileSet:
	var ts := TileSet.new()
	ts.tile_size = Vector2i(TILE, TILE)
	ts.add_physics_layer()
	ts.set_physics_layer_collision_layer(0, 1)
	ts.set_physics_layer_collision_mask(0, 0)
	var src := TileSetAtlasSource.new()
	src.texture = Global.tex("tiles.png")
	src.texture_region_size = Vector2i(TILE, TILE)
	ts.add_source(src, 0)
	var h := TILE / 2.0
	var poly := PackedVector2Array([Vector2(-h, -h), Vector2(h, -h), Vector2(h, h), Vector2(-h, h)])
	for ax in 2:
		for ay in 4:
			var coords := Vector2i(ax, ay)
			src.create_tile(coords)
			var td := src.get_tile_data(coords, 0)
			td.add_collision_polygon(0)
			td.set_collision_polygon_points(0, 0, poly)
	return ts


func _build_tilemap() -> void:
	tilemap = TileMapLayer.new()
	tilemap.tile_set = _make_tileset()
	add_child(tilemap)
	for y in height_tiles:
		for x in width_tiles:
			if cell_char(x, y) == "#":
				var surface := not is_solid(x, y - 1) if y > 0 else true
				tilemap.set_cell(Vector2i(x, y), 0, Vector2i(0 if surface else 1, theme))


## Paredes invisibles en los extremos del nivel.
func _build_borders() -> void:
	for side in [-1, 1]:
		var wall := StaticBody2D.new()
		wall.collision_layer = 1
		var shape := RectangleShape2D.new()
		shape.size = Vector2(16, height_tiles * TILE * 3)
		var cs := CollisionShape2D.new()
		cs.shape = shape
		wall.add_child(cs)
		wall.position = Vector2(-8 if side < 0 else width_tiles * TILE + 8, height_tiles * TILE / 2.0)
		add_child(wall)


func _spawn_entities() -> void:
	var fire_done := {}     # celdas de fuego ya agrupadas en una zona
	for x in width_tiles:
		for y in height_tiles:
			var ch := cell_char(x, y)
			var center := Vector2(x * TILE + 8, y * TILE + 8)
			var bottom := Vector2(x * TILE + 8, (y + 1) * TILE)
			match ch:
				"P":
					checkpoint_pos = Vector2(bottom.x, bottom.y - Player.HALF_HEIGHT)
				"o":
					var p := Pickup.new()
					p.level = self
					p.position = center
					add_child(p)
					sparks_in_level += 1
				"r":
					var r := Rondin.new()
					r.level = self
					r.position = center
					add_child(r)
				"R":
					var rf := RondinFurioso.new()
					rf.level = self
					rf.position = center
					add_child(rf)
				"B":
					var rg := RondinGigante.new()
					rg.level = self
					rg.position = bottom + Vector2(0, -12)
					add_child(rg)
				"a":
					var cz := Ceniza.new()
					cz.level = self
					cz.position = center
					add_child(cz)
				"F":
					if not fire_done.has(Vector2i(x, y)):
						var n := 0
						while cell_char(x + n, y) == "F":
							fire_done[Vector2i(x + n, y)] = true
							n += 1
						var fz := FireZone.new()
						fz.width_px = n * TILE
						fz.position = Vector2(x * TILE + n * TILE / 2.0, (y + 1) * TILE)
						add_child(fz)
				"c":
					var c := Checkpoint.new()
					c.level = self
					c.position = bottom + Vector2(0, -12)
					add_child(c)
				"G":
					goal_node = Goal.new()
					goal_node.level = self
					goal_node.position = bottom + Vector2(0, -14)
					add_child(goal_node)
				"T":
					var d := Sprite2D.new()
					d.texture = Global.tex("decor_%d.png" % theme)
					d.position = bottom - Vector2(0, d.texture.get_height() / 2.0)
					d.z_index = -5
					add_child(d)


# ---------------------------------------------------------------- Flujo de la partida
func _physics_process(delta: float) -> void:
	if level_done:
		Global.set_danger(0.0)
		return
	elapsed += delta
	Global.play_time += delta
	# Prueba del pisotón (desarrollo): godot -- --stomptest --tp=x,y  deja caer a Embra sobre un enemigo
	if "--stomptest" in OS.get_cmdline_user_args() and elapsed > 1.6:
		print("[TEST] Pisotón: enemigos vencidos = %d, Embra vivo = %s, vidas = %d" % [Global.kills, str(not player.dead), Global.lives])
		get_tree().quit(0 if Global.kills > 0 and not player.dead else 1)
	_update_music_danger()
	if Global.autotest and elapsed > 300.0:
		autotest_fail("Tiempo agotado (el bot no llegó a la meta)")


## La música se intensifica cuando Embra está cerca de un Rondín o de una zona de fuego activa (GDD).
func _update_music_danger() -> void:
	if player == null or player.dead:
		Global.set_danger(0.0)
		return
	var closest := 9999.0
	for n in get_tree().get_nodes_in_group("danger"):
		closest = minf(closest, (n as Node2D).global_position.distance_to(player.global_position))
	for n in get_tree().get_nodes_in_group("hazard"):
		if n.is_active():
			closest = minf(closest, (n as Node2D).global_position.distance_to(player.global_position))
	Global.set_danger(clampf(1.0 - (closest - 50.0) / 110.0, 0.0, 1.0))


## kind = "hit" (enemigo o fuego) o "void" (vacío)
func on_player_died(kind: String) -> void:
	if Global.autotest:
		autotest_fail("Embra murió (%s) en x=%d y=%d" % [kind, int(player.global_position.x), int(player.global_position.y)])
		return
	Global.deaths += 1
	if kind == "hit":
		var lost := Global.apply_hit_penalty()
		hud.set_score(Global.level_score)
		if lost > 0:
			hud.show_message("-%d puntos" % lost, 1.8)
	if Global.lose_life():
		await get_tree().create_timer(1.2).timeout
		Global.stop_music()
		get_tree().change_scene_to_file("res://scenes/game_over.tscn")
	else:
		await get_tree().create_timer(1.0).timeout
		player.respawn(checkpoint_pos)


func complete_level() -> void:
	if level_done:
		return
	level_done = true
	player.freeze()
	Global.play_sfx("win")
	var record := Global.finish_level()
	hud.set_score(Global.level_score)
	var last := Global.current_level + 1 >= LevelData.LEVELS.size()
	var txt := "¡%s completado!\n\nChispas: %d / %d\nPuntaje del nivel: %d\nMejor puntaje del nivel: %d%s\n\n%s" % [
		data["name"], sparks_collected, sparks_in_level, Global.level_score,
		Global.best_scores[Global.current_level], "  ¡NUEVO RÉCORD!" if record else "",
		"ENTER: ver el final" if last else "ENTER: siguiente nivel"]
	hud.show_summary(txt)
	if Global.autotest:
		print("[TEST] PASA nivel %d en %.1f s (chispas %d/%d, enemigos vencidos en total: %d, etapa %d)" % [Global.current_level + 1, elapsed, sparks_collected, sparks_in_level, Global.kills, Global.stage()])
		await get_tree().create_timer(0.3).timeout
		_advance()
		return
	await get_tree().create_timer(0.8).timeout
	waiting_confirm = true


func _unhandled_input(event: InputEvent) -> void:
	if waiting_confirm and event.is_action_pressed("confirm"):
		waiting_confirm = false
		_advance()


func _advance() -> void:
	if Global.current_level + 1 >= LevelData.LEVELS.size():
		Global.stop_music()
		if Global.autotest:
			print("[TEST] TODOS LOS NIVELES COMPLETADOS")
			get_tree().quit(0)
			return
		get_tree().change_scene_to_file("res://scenes/victory.tscn")
	else:
		Global.current_level += 1
		get_tree().change_scene_to_file("res://scenes/level.tscn")


func autotest_fail(reason: String) -> void:
	print("[TEST] FALLA nivel %d: %s" % [Global.current_level + 1, reason])
	get_tree().quit(1)
