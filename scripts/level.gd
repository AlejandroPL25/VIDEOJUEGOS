extends Node2D
class_name Level
## Level.gd -- Construye un nivel a partir del mapa ASCII (ver level_data.gd / tools/make_levels.py)
## y administra la partida: fondo, mapa de tiles, enemigos, objetos, cámara, puntos de control,
## muerte/reaparición, final de nivel y modo de pruebas automáticas.

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
var boss_node: Boss = null

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

	_build_background()
	_build_tilemap()
	_build_borders()

	player = Player.new()
	player.level = self
	add_child(player)
	hud = Hud.new()
	add_child(hud)

	_spawn_entities()
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
	hud.set_sparks(0, sparks_in_level)
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
	var hint_index := 0
	var hints: Array = data["hints"]
	for x in width_tiles:
		for y in height_tiles:
			var ch := cell_char(x, y)
			var center := Vector2(x * TILE + 8, y * TILE + 8)
			var bottom := Vector2(x * TILE + 8, (y + 1) * TILE)
			match ch:
				"P":
					checkpoint_pos = center + Vector2(0, 0)
				"o":
					var p := Pickup.new()
					p.kind = Pickup.Kind.SPARK
					p.level = self
					p.position = center
					add_child(p)
					sparks_in_level += 1
				"h":
					var hp := Pickup.new()
					hp.kind = Pickup.Kind.HEART
					hp.level = self
					hp.position = center
					add_child(hp)
				"S":
					var sp := Spike.new()
					sp.theme = theme
					sp.position = center
					add_child(sp)
				"w":
					if not Global.autotest_no_enemies:
						var w := Walker.new()
						w.level = self
						w.position = center
						add_child(w)
				"b":
					if not Global.autotest_no_enemies:
						var f := Flyer.new()
						f.position = center
						add_child(f)
				"c":
					var c := Checkpoint.new()
					c.level = self
					c.position = bottom + Vector2(0, -12)
					add_child(c)
				"G":
					goal_node = Goal.new()
					goal_node.level = self
					goal_node.position = bottom + Vector2(0, -12)
					add_child(goal_node)
				"B":
					boss_node = Boss.new()
					boss_node.level = self
					boss_node.position = bottom + Vector2(0, -16)
					boss_node.patrol_left = (x - 24) * TILE
					boss_node.patrol_right = (x + 5) * TILE
					add_child(boss_node)
				"t":
					if hint_index < hints.size():
						var s := SignHint.new()
						s.text = hints[hint_index]
						s.position = center
						add_child(s)
					hint_index += 1
				"T":
					var d := Sprite2D.new()
					d.texture = Global.tex("decor_%d.png" % theme)
					d.position = bottom - Vector2(0, d.texture.get_height() / 2.0)
					d.z_index = -5
					add_child(d)
	if boss_node != null:
		boss_node.defeated.connect(_on_boss_defeated)
		if goal_node != null:
			goal_node.set_active(false)


# ---------------------------------------------------------------- Flujo de la partida
func _physics_process(delta: float) -> void:
	if level_done:
		return
	elapsed += delta
	Global.play_time += delta
	if Global.autotest and elapsed > 300.0:
		autotest_fail("Tiempo agotado (el bot no llegó a la meta)")


func on_player_died() -> void:
	if Global.autotest:
		autotest_fail("Embra murió en x=%d y=%d" % [int(player.global_position.x), int(player.global_position.y)])
		return
	Global.deaths += 1
	if Global.lose_life():
		await get_tree().create_timer(1.2).timeout
		Global.stop_music()
		get_tree().change_scene_to_file("res://scenes/game_over.tscn")
	else:
		await get_tree().create_timer(1.0).timeout
		player.respawn(checkpoint_pos)


func _on_boss_defeated() -> void:
	hud.show_message("¡Gélido cayó! Enciende la Hoguera Eterna", 3.0)
	if goal_node != null:
		goal_node.set_active(true)


func complete_level() -> void:
	if level_done:
		return
	level_done = true
	player.freeze()
	Global.play_sfx("win")
	var bonus := 200 + 50 * sparks_collected
	Global.add_score(bonus)
	var last := Global.current_level + 1 >= LevelData.LEVELS.size()
	var txt := "¡%s completado!\n\nChispas: %d / %d\nPuntos: %d\n\n%s" % [
		data["name"], sparks_collected, sparks_in_level, Global.score,
		"ENTER: ver el final" if last else "ENTER: siguiente nivel"]
	hud.show_summary(txt)
	if Global.autotest:
		print("[TEST] PASA nivel %d en %.1f s (chispas %d/%d)" % [Global.current_level + 1, elapsed, sparks_collected, sparks_in_level])
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
