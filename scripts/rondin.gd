extends EnemyBase
class_name Rondin
## Rondin.gd -- Rondín: criatura de carbón que perdió el control y patrulla una plataforma de un
## extremo a otro (GDD). Da la vuelta al llegar a un borde o a una pared. Se vence pisándolo o con fuego.

const GRAVITY := 900.0

var speed := 30.0
var dir := -1
var edge_ray: RayCast2D
var _turn_cd := 0.0
# Parámetros que cambian en las variantes (furioso y gigante)
var sheet_file := "rondin_sheet.png"
var frame_w := 16
var frame_h := 16
var hitbox := Vector2(12, 12)
var body_offset := Vector2(0, 2)


func _setup() -> void:
	var shape := RectangleShape2D.new()
	shape.size = hitbox
	var cs := CollisionShape2D.new()
	cs.shape = shape
	cs.position = body_offset
	add_child(cs)

	sprite = AnimatedSprite2D.new()
	sprite.sprite_frames = _make_sprite_frames()
	sprite.play("walk")
	add_child(sprite)

	edge_ray = RayCast2D.new()
	edge_ray.target_position = Vector2(0, 10)
	edge_ray.collision_mask = 1
	edge_ray.position = Vector2(dir * (hitbox.x / 2.0 + 1.0), body_offset.y + hitbox.y / 2.0 - 1.0)
	add_child(edge_ray)

	_make_touch(hitbox, body_offset)


func _make_sprite_frames() -> SpriteFrames:
	return Global.make_frames(sheet_file, frame_w, frame_h, {"walk": {"frames": [0, 1], "fps": 4.0}})


func _speed_multiplier() -> float:
	return 1.0


func _behave(delta: float) -> void:
	_turn_cd = max(_turn_cd - delta, 0.0)
	velocity.y = min(velocity.y + GRAVITY * delta, 400.0)
	velocity.x = 0.0 if Global.freeze_enemies else dir * speed * _speed_multiplier()
	move_and_slide()
	if _turn_cd <= 0.0:
		if is_on_wall() or (is_on_floor() and not edge_ray.is_colliding()):
			_turn()


func _turn() -> void:
	dir = -dir
	edge_ray.position.x = dir * (hitbox.x / 2.0 + 1.0)
	sprite.flip_h = dir > 0
	_turn_cd = 0.25
