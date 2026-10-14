extends Area2D
class_name Checkpoint
## Checkpoint.gd -- Brasero: al tocarlo se enciende y guarda el punto de reaparición.

var level: Level
var lit := false
var sprite: AnimatedSprite2D


func _ready() -> void:
	collision_layer = 0
	collision_mask = 2
	sprite = AnimatedSprite2D.new()
	sprite.sprite_frames = Global.make_frames("checkpoint.png", 16, 24, {
		"off": {"frames": [0], "fps": 1.0},
		"on": {"frames": [1], "fps": 1.0},
	})
	sprite.play("off")
	add_child(sprite)
	var shape := RectangleShape2D.new()
	shape.size = Vector2(14, 22)
	var cs := CollisionShape2D.new()
	cs.shape = shape
	add_child(cs)
	body_entered.connect(_on_body_entered)
	z_index = -1


func _on_body_entered(body: Node) -> void:
	if lit or not (body is Player):
		return
	lit = true
	sprite.play("on")
	level.checkpoint_pos = global_position + Vector2(0, 4)
	Global.play_sfx("checkpoint")
	level.hud.show_message("¡Punto de control!", 1.5)
	Global.spawn_burst(get_parent(), global_position + Vector2(0, -8), Color(1.0, 0.7, 0.25), 12, 50.0, 0.6, -40.0)
