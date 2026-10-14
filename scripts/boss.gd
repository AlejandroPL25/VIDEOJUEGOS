extends CharacterBody2D
class_name Boss
## Boss.gd -- Gélido, el Rey de Escarcha (jefe final).
## Patrulla la arena y lanza astillas de hielo bajas (se esquivan saltando) y altas (se esquivan
## en el suelo). Con la mitad de vida entra en fase 2: se mueve más rápido y convoca un Escarchín.
## Se daña con bolas de fuego (1) o pisándolo (2).

signal defeated
signal hp_changed(hp: int, max_hp: int)

const MAX_HP := 8
const GRAVITY := 900.0

var hp := MAX_HP
var level: Level
var sprite: AnimatedSprite2D
var touch_area: Area2D
var patrol_left := 0.0
var patrol_right := 0.0
var dir := -1
var active := false
var dying := false
var phase2 := false
var invuln := 0.0
var attack_timer := 2.5
var mouth_timer := 0.0


func _ready() -> void:
	add_to_group("enemy")
	collision_layer = 4
	collision_mask = 1
	var shape := RectangleShape2D.new()
	shape.size = Vector2(20, 28)
	var cs := CollisionShape2D.new()
	cs.shape = shape
	cs.position = Vector2(0, 2)
	add_child(cs)

	sprite = AnimatedSprite2D.new()
	sprite.sprite_frames = Global.make_frames("gelido_sheet.png", 32, 32, {
		"idle": {"frames": [0], "fps": 1.0},
		"attack": {"frames": [1], "fps": 1.0},
		"hurt": {"frames": [2], "fps": 1.0},
	})
	sprite.play("idle")
	add_child(sprite)

	touch_area = Area2D.new()
	touch_area.collision_layer = 0
	touch_area.collision_mask = 2
	var ts := RectangleShape2D.new()
	ts.size = Vector2(24, 30)
	var tcs := CollisionShape2D.new()
	tcs.shape = ts
	tcs.position = Vector2(0, 1)
	touch_area.add_child(tcs)
	add_child(touch_area)


func _physics_process(delta: float) -> void:
	if dying:
		return
	velocity.y = min(velocity.y + GRAVITY * delta, 400.0)
	if not active:
		move_and_slide()
		if level.player != null and level.player.global_position.x > patrol_left - 90.0:
			_activate()
		return

	invuln = max(invuln - delta, 0.0)
	mouth_timer = max(mouth_timer - delta, 0.0)
	var spd := 40.0 if phase2 else 26.0
	velocity.x = dir * spd
	move_and_slide()
	if global_position.x < patrol_left:
		dir = 1
	elif global_position.x > patrol_right:
		dir = -1
	# Mirar hacia el jugador
	if level.player != null:
		sprite.flip_h = level.player.global_position.x > global_position.x

	attack_timer -= delta
	if attack_timer <= 0.0:
		_attack()
		attack_timer = 1.8 if phase2 else 2.6

	# Animación
	if invuln > 0.35:
		sprite.play("hurt")
	elif mouth_timer > 0.0:
		sprite.play("attack")
	else:
		sprite.play("idle")

	for b in touch_area.get_overlapping_bodies():
		if b is Player and not b.dead:
			if b.velocity.y > 20.0 and b.global_position.y < global_position.y - 10.0:
				b.bounce()
				hit(2)
			else:
				b.hurt()


func _activate() -> void:
	active = true
	level.hud.show_boss(hp, MAX_HP)
	level.hud.show_message("¡Gélido, el Rey de Escarcha!", 2.5)


func _attack() -> void:
	mouth_timer = 0.45
	var toward := -1 if (level.player != null and level.player.global_position.x < global_position.x) else 1
	var shots := 2 if phase2 else 1
	for i in shots:
		var low := (randi() % 2 == 0)
		if phase2:
			low = (i == 0)   # en fase 2 lanza una baja y una alta a la vez
		var sh := IceShard.new()
		sh.direction = toward
		sh.speed = 120.0 if phase2 else 90.0
		level.add_child(sh)
		sh.global_position = global_position + Vector2(toward * 14.0, 10.0 if low else -14.0)
	Global.play_sfx("shard")


## Daño (bola de fuego = 1, pisotón = 2)
func hit(dmg: int) -> void:
	if dying or not active or invuln > 0.0:
		return
	hp = max(hp - dmg, 0)
	invuln = 0.6
	Global.play_sfx("hit")
	Global.spawn_burst(get_parent(), global_position, Color(0.8, 0.95, 1.0), 10, 60.0, 0.4, 100.0)
	hp_changed.emit(hp, MAX_HP)
	level.hud.set_boss_hp(hp, MAX_HP)
	if hp <= 0:
		_die()
	elif hp <= MAX_HP / 2 and not phase2:
		_enter_phase2()


func _enter_phase2() -> void:
	phase2 = true
	level.hud.show_message("¡Gélido se enfurece!", 1.8)
	# Se agrega de forma diferida porque esta función puede ejecutarse dentro de un callback de física
	var w := Walker.new()
	w.level = level
	w.position = global_position + Vector2(-24 * dir, 0)
	level.add_child.call_deferred(w)


func _die() -> void:
	dying = true
	set_deferred("collision_layer", 0)
	touch_area.set_deferred("monitoring", false)
	Global.add_score(1000)
	Global.kills += 1
	Global.play_sfx("boss_die")
	for i in 6:
		Global.spawn_burst(get_parent(), global_position + Vector2(randf_range(-12, 12), randf_range(-12, 12)),
				Color(0.8, 0.95, 1.0), 14, 90.0, 0.8, 120.0)
		await get_tree().create_timer(0.18).timeout
	level.hud.hide_boss()
	defeated.emit()
	queue_free()
