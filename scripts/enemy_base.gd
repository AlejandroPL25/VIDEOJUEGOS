extends CharacterBody2D
class_name EnemyBase
## EnemyBase.gd -- Base común de todos los enemigos (mejora posterior a la prueba con usuarios).
## Un enemigo se puede vencer de dos formas: PISÁNDOLO desde arriba (Embra rebota) o con la BOLA DE
## FUEGO (desde la etapa "Llama"). Si Embra lo toca de lado, de frente o desde abajo, recibe el daño
## del GDD: pierde una vida y parte del puntaje. Cada tipo de enemigo define su comportamiento en _behave().

var hp := 1
var points := 50
var level: Level
var sprite: AnimatedSprite2D
var touch_area: Area2D
var dead := false
var stomp_line := 6.0        # los pies de Embra deben estar por encima de (centro + stomp_line) para contar como pisotón
var _flash := 0.0
var _invuln := 0.0


func _ready() -> void:
	add_to_group("danger")
	collision_layer = 4
	collision_mask = 1
	_setup()


## Cada enemigo crea aquí su colisión, su sprite y su zona de contacto.
func _setup() -> void:
	pass


## Cada enemigo define aquí cómo se mueve.
func _behave(_delta: float) -> void:
	pass


func _make_touch(size: Vector2, offset: Vector2) -> void:
	touch_area = Area2D.new()
	touch_area.collision_layer = 0
	touch_area.collision_mask = 2
	var ts := RectangleShape2D.new()
	ts.size = size
	var tcs := CollisionShape2D.new()
	tcs.shape = ts
	tcs.position = offset
	touch_area.add_child(tcs)
	add_child(touch_area)


func _physics_process(delta: float) -> void:
	if dead:
		return
	_invuln = max(_invuln - delta, 0.0)
	if _flash > 0.0:
		_flash -= delta
		sprite.modulate = Color(2.2, 2.2, 2.2) if int(_flash * 30.0) % 2 == 0 else Color.WHITE
		if _flash <= 0.0:
			sprite.modulate = Color.WHITE
	_behave(delta)
	for b in touch_area.get_overlapping_bodies():
		if b is Player:
			_touch_player(b)


func _touch_player(p: Player) -> void:
	if p.dead or p.frozen:
		return
	# Pisotón: en el fotograma anterior los pies de Embra estaban por encima de la cabeza del enemigo
	# y no va subiendo. Si estaba a la altura del suelo (caminando contra el enemigo) es contacto lateral.
	if p.velocity.y >= -20.0 and p.prev_feet_y <= global_position.y + stomp_line:
		p.bounce()
		hit(1, "stomp")
	else:
		p.hurt()


## Daño recibido. kind = "stomp" (pisotón) o "fire" (bola de fuego).
func hit(dmg: int, kind: String) -> void:
	if dead or _invuln > 0.0:
		return
	hp -= dmg
	_invuln = 0.35 if kind == "stomp" else 0.12
	if hp <= 0:
		_die(kind)
	else:
		_flash = 0.3
		Global.play_sfx("tick")
		Global.spawn_burst(get_parent(), global_position, Color("FFF3C4"), 6, 50.0, 0.3, 80.0)


func _die(kind: String) -> void:
	dead = true
	Global.add_kill(points)
	level.hud.set_score(Global.level_score)
	set_deferred("collision_layer", 0)
	touch_area.set_deferred("monitoring", false)
	remove_from_group("danger")
	if kind == "stomp":
		Global.play_sfx("stomp")
		sprite.scale = Vector2(1.3, 0.35)
		sprite.position.y += sprite.sprite_frames.get_frame_texture(sprite.animation, 0).get_height() * 0.3
	else:
		Global.play_sfx("enemydie")
	Global.spawn_burst(get_parent(), global_position, Color("E8542A"), 12, 70.0, 0.5, 100.0)
	Global.spawn_burst(get_parent(), global_position, Color("F4A62A"), 8, 55.0, 0.45, 80.0)
	level.show_points(global_position, points)
	await get_tree().create_timer(0.2 if kind == "stomp" else 0.01).timeout
	queue_free()
