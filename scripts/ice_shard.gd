extends Area2D
class_name IceShard
## IceShard.gd -- Astilla de hielo que lanza Gélido. Lastima a Embra y se rompe contra las paredes.

var direction := -1
var speed := 90.0
var _life := 4.0
var _used := false


func _ready() -> void:
	collision_layer = 0
	collision_mask = 1 | 2        # mundo + jugador
	var shape := CircleShape2D.new()
	shape.radius = 3.0
	var cs := CollisionShape2D.new()
	cs.shape = shape
	add_child(cs)
	var spr := Sprite2D.new()
	spr.texture = Global.tex("iceshard.png")
	spr.flip_h = direction < 0
	add_child(spr)
	body_entered.connect(_on_body_entered)
	z_index = 6


func _physics_process(delta: float) -> void:
	position.x += direction * speed * delta
	_life -= delta
	if _life <= 0.0:
		_break()


func _on_body_entered(body: Node) -> void:
	if _used:
		return
	if body is Player:
		body.hurt()
		_break()
	elif body is TileMapLayer or body is StaticBody2D:
		_break()


func _break() -> void:
	if _used:
		return
	_used = true
	Global.spawn_burst(get_parent(), global_position, Color(0.75, 0.92, 1.0), 6, 40.0, 0.35, 80.0)
	queue_free()
