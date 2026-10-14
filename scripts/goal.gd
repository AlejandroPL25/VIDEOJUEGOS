extends Area2D
class_name Goal
## Goal.gd -- Hoguera Eterna: meta de cada nivel. En el nivel del jefe aparece al vencer a Gélido.

var level: Level
var active := true
var sprite: AnimatedSprite2D


func _ready() -> void:
	collision_layer = 0
	collision_mask = 2
	sprite = AnimatedSprite2D.new()
	sprite.sprite_frames = Global.make_frames("hearth.png", 24, 24, {
		"off": {"frames": [0], "fps": 1.0},
		"on": {"frames": [1], "fps": 1.0},
	})
	sprite.play("off")
	add_child(sprite)
	var shape := RectangleShape2D.new()
	shape.size = Vector2(16, 20)
	var cs := CollisionShape2D.new()
	cs.shape = shape
	add_child(cs)
	body_entered.connect(_on_body_entered)
	z_index = -1


## En el nivel del jefe la hoguera permanece oculta hasta que Gélido cae.
func set_active(value: bool) -> void:
	active = value
	visible = value
	set_deferred("monitoring", value)
	if value:
		Global.spawn_burst(get_parent(), global_position, Color(1.0, 0.8, 0.3), 20, 80.0, 0.8, 0.0)


func _on_body_entered(body: Node) -> void:
	if not active or not (body is Player):
		return
	sprite.play("on")
	Global.spawn_burst(get_parent(), global_position + Vector2(0, -6), Color(1.0, 0.75, 0.25), 24, 90.0, 0.9, 40.0)
	level.complete_level()
