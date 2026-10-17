extends CharacterBody2D
class_name Rondin
## Rondin.gd -- Rondín: criatura de carbón que perdió el control y patrulla una plataforma de un
## extremo a otro (GDD). Da la vuelta al llegar a un borde o a una pared. El contacto con Embra
## cuesta una vida y parte del puntaje; no se puede vencer: hay que esquivarlo.

const SPEED := 30.0
const GRAVITY := 900.0

var dir := -1
var level: Level
var sprite: AnimatedSprite2D
var touch_area: Area2D
var edge_ray: RayCast2D
var _turn_cd := 0.0


func _ready() -> void:
	add_to_group("danger")
	collision_layer = 4
	collision_mask = 1
	var shape := RectangleShape2D.new()
	shape.size = Vector2(12, 12)
	var cs := CollisionShape2D.new()
	cs.shape = shape
	cs.position = Vector2(0, 2)
	add_child(cs)

	sprite = AnimatedSprite2D.new()
	sprite.sprite_frames = Global.make_frames("rondin_sheet.png", 16, 16, {"walk": {"frames": [0, 1], "fps": 4.0}})
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
	_turn_cd = max(_turn_cd - delta, 0.0)
	velocity.y = min(velocity.y + GRAVITY * delta, 400.0)
	velocity.x = dir * SPEED
	move_and_slide()
	if _turn_cd <= 0.0:
		if is_on_wall() or (is_on_floor() and not edge_ray.is_colliding()):
			_turn()
	for b in touch_area.get_overlapping_bodies():
		if b is Player:
			b.hurt()


func _turn() -> void:
	dir = -dir
	edge_ray.position.x = dir * 9
	sprite.flip_h = dir > 0
	_turn_cd = 0.25
