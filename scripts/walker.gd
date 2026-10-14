extends CharacterBody2D
class_name Walker
## Walker.gd -- Escarchín: babosa de hielo que patrulla el suelo.
## Da la vuelta al llegar a una pared o a un borde. Se vence pisándolo o con fuego.

const SPEED := 28.0
const GRAVITY := 900.0

var dir := -1
var dead := false
var level: Level
var sprite: AnimatedSprite2D
var touch_area: Area2D
var edge_ray: RayCast2D
var _turn_cd := 0.0


func _ready() -> void:
	add_to_group("enemy")
	collision_layer = 4
	collision_mask = 1
	var shape := RectangleShape2D.new()
	shape.size = Vector2(12, 10)
	var cs := CollisionShape2D.new()
	cs.shape = shape
	cs.position = Vector2(0, 3)
	add_child(cs)

	sprite = AnimatedSprite2D.new()
	sprite.sprite_frames = Global.make_frames("escarchin_sheet.png", 16, 16, {"walk": {"frames": [0, 1], "fps": 4.0}})
	sprite.play("walk")
	add_child(sprite)

	edge_ray = RayCast2D.new()
	edge_ray.target_position = Vector2(0, 10)
	edge_ray.collision_mask = 1
	edge_ray.position = Vector2(dir * 9, 7)
	add_child(edge_ray)

	# Zona de contacto con el jugador
	touch_area = Area2D.new()
	touch_area.collision_layer = 0
	touch_area.collision_mask = 2
	var ts := RectangleShape2D.new()
	ts.size = Vector2(12, 12)
	var tcs := CollisionShape2D.new()
	tcs.shape = ts
	tcs.position = Vector2(0, 2)
	touch_area.add_child(tcs)
	add_child(touch_area)


func _physics_process(delta: float) -> void:
	if dead:
		return
	_turn_cd = max(_turn_cd - delta, 0.0)
	velocity.y = min(velocity.y + GRAVITY * delta, 400.0)
	velocity.x = dir * SPEED
	move_and_slide()
	if _turn_cd <= 0.0:
		if is_on_wall() or (is_on_floor() and not edge_ray.is_colliding()):
			_turn()
	for b in touch_area.get_overlapping_bodies():
		if b is Player:
			_touch_player(b)


func _turn() -> void:
	dir = -dir
	edge_ray.position.x = dir * 9
	sprite.flip_h = dir > 0
	_turn_cd = 0.25


func _touch_player(p: Player) -> void:
	if p.dead:
		return
	if p.velocity.y > 20.0 and p.global_position.y < global_position.y - 3.0:
		p.bounce()
		_die("stomp")
	else:
		p.hurt()


## Daño por bola de fuego
func hit(_dmg: int) -> void:
	_die("fire")


func _die(kind: String) -> void:
	if dead:
		return
	dead = true
	Global.kills += 1
	Global.add_score(50)
	set_deferred("collision_layer", 0)
	touch_area.set_deferred("monitoring", false)
	if kind == "stomp":
		Global.play_sfx("stomp")
		sprite.scale = Vector2(1.3, 0.4)
		sprite.position.y = 5
		Global.spawn_burst(get_parent(), global_position, Color(0.7, 0.9, 1.0), 8, 45.0, 0.4, 100.0)
	else:
		Global.play_sfx("hit")
		Global.spawn_burst(get_parent(), global_position, Color(1.0, 0.6, 0.25), 12, 60.0, 0.5, 100.0)
		Global.spawn_burst(get_parent(), global_position, Color(0.7, 0.9, 1.0), 8, 45.0, 0.4, 100.0)
	await get_tree().create_timer(0.18 if kind == "stomp" else 0.01).timeout
	queue_free()
