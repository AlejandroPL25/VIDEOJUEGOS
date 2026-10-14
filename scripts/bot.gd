extends RefCounted
class_name Bot
## Bot.gd -- Jugador automático para las pruebas del prototipo (modo --autotest).
## Lee el mapa del nivel con una pequeña "mirada hacia adelante": camina a la derecha y salta
## cuando hay pared, hueco o púas. En el nivel del jefe se detiene a distancia y dispara.
## Sirve para comprobar que cada nivel se puede completar físicamente.

var level: Level
var _stuck_timer := 0.0
var _last_x := 0.0


func fill(p: Player) -> void:
	var tile := Level.TILE
	var px := p.global_position.x
	var feet_row := int(floor((p.global_position.y + 6.0) / tile))   # fila que ocupan los pies
	var ground_row := feet_row + 1
	p.in_fire = false

	# ---- Objetivo: jefe (si sigue vivo) o la Hoguera Eterna ----
	var dir := 1.0
	var boss := level.boss_node
	if boss != null and is_instance_valid(boss) and not boss.dying:
		var dist: float = boss.global_position.x - px
		if dist < 150.0:
			dir = 0.0
			p.facing = 1
			p.in_fire = true
	elif level.goal_node != null and level.goal_node.active:
		var gx: float = level.goal_node.global_position.x
		if px > gx + 3.0:
			dir = -1.0
		elif px < gx - 3.0:
			dir = 1.0
		else:
			dir = 0.0
	p.in_dir = dir

	var jump := false
	if p.is_on_floor() and dir != 0.0:
		var s := int(dir)
		# Pared adelante
		var wx := int(floor((px + s * 8.5) / tile))
		if level.is_solid(wx, feet_row):
			jump = true
		# Hueco adelante (a ~6 px del borde)
		var gx := int(floor((px + s * 6.0) / tile))
		if not level.is_solid(gx, ground_row) and not level.is_solid(gx, ground_row + 1):
			jump = true
		# Púas adelante
		for dx in range(0, 3):
			var cx := int(floor(px / tile)) + dx * s
			if level.cell_char(cx, feet_row) == "S":
				var edge := float(cx * tile) if s > 0 else float(cx * tile + tile)
				if absf(edge - px) < 22.0:
					jump = true
	p.in_jump_pressed = jump
	p.in_jump_held = jump or not p.is_on_floor()

	# Detector de atasco
	if absf(px - _last_x) < 0.2 and dir != 0.0:
		_stuck_timer += 1.0 / 60.0
	else:
		_stuck_timer = 0.0
	_last_x = px
	if _stuck_timer > 5.0:
		level.autotest_fail("Bot atascado en x=%d (tile %d)" % [int(px), int(px / tile)])
