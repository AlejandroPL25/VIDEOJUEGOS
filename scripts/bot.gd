extends RefCounted
class_name Bot
## Bot.gd -- Jugador automático para las pruebas del prototipo (modo --autotest).
## Camina hacia la derecha leyendo el mapa con una pequeña "mirada hacia adelante" y salta cuando
## hay pared o hueco. En pruebas Embra es invulnerable a enemigos y fuego (solo se verifica que la
## geometría de cada nivel se puede recorrer hasta el altar).

var level: Level
var _stuck_timer := 0.0
var _last_x := 0.0


func fill(p: Player) -> void:
	var tile := Level.TILE
	var px := p.global_position.x
	var feet_row := int(floor((p.global_position.y + 8.0) / tile))   # fila que ocupan los pies
	var ground_row := feet_row + 1
	var dir := 1.0
	p.in_dir = dir

	var jump := false
	if p.is_on_floor():
		# Pared adelante
		var wx := int(floor((px + 8.5) / tile))
		if level.is_solid(wx, feet_row):
			jump = true
		# Hueco adelante (a ~6 px del borde)
		var gx := int(floor((px + 6.0) / tile))
		if not level.is_solid(gx, ground_row) and not level.is_solid(gx, ground_row + 1):
			jump = true
	p.in_jump_pressed = jump
	p.in_jump_held = jump or not p.is_on_floor()

	# Detector de atasco
	if absf(px - _last_x) < 0.2:
		_stuck_timer += 1.0 / 60.0
	else:
		_stuck_timer = 0.0
	_last_x = px
	if _stuck_timer > 5.0:
		level.autotest_fail("Bot atascado en x=%d (tile %d)" % [int(px), int(px / tile)])
