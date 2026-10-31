extends Area2D
class_name Fireball
## Fireball.gd -- Bola de fuego de Embra (desde la etapa "Llama"). Daña enemigos y se apaga contra el
## suelo y las paredes. En la etapa "Fuego ardiente" es más grande, hace doble daño y atraviesa enemigos.

const LIFETIME := 1.1

var direction := 1
var damage := 1
var pierce := false
var speed := 210.0
var _life := LIFETIME
var _used := false


func _ready() -> void:
	add_to_group("fireball")
	collision_layer = 0
	collision_mask = 1 | 4        # mundo + enemigos
	var shape := CircleShape2D.new()
	shape.radius = 4.5 if pierce else 3.0
	var cs := CollisionShape2D.new()
	cs.shape = shape
	add_child(cs)
	var spr := AnimatedSprite2D.new()
	spr.sprite_frames = Global.make_frames("fireball.png", 8, 8, {"fly": {"frames": [0, 1], "fps": 12.0}})
	spr.flip_h = direction < 0
	if pierce:
		spr.scale = Vector2(1.5, 1.5)
	spr.play("fly")
	add_child(spr)
	body_entered.connect(_on_body_entered)
	z_index = 6


func _physics_process(delta: float) -> void:
	position.x += direction * speed * delta
	_life -= delta
	if _life <= 0.0:
		_explode()


func _on_body_entered(body: Node) -> void:
	if _used:
		return
	if body.has_method("hit"):
		body.hit(damage, "fire")
		if not pierce:
			_explode()
	elif body is TileMapLayer or body is StaticBody2D:
		_explode()


func _explode() -> void:
	if _used:
		return
	_used = true
	Global.spawn_burst(get_parent(), global_position, Color("F4A62A"), 8, 50.0, 0.35, 60.0)
	queue_free()
