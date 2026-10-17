extends Area2D
class_name Goal
## Goal.gd -- Altar: la meta de cada nivel (GDD). Al llegar a él, Embra lo enciende y el nivel termina.
## En "El Altar" (último nivel) enciende la fogata ancestral y termina la historia.

var level: Level
var active := true
var sprite: AnimatedSprite2D


func _ready() -> void:
	collision_layer = 0
	collision_mask = 2
	sprite = AnimatedSprite2D.new()
	sprite.sprite_frames = Global.make_frames("altar.png", 24, 28, {
		"off": {"frames": [0], "fps": 1.0},
		"on": {"frames": [1], "fps": 1.0},
	})
	sprite.play("off")
	add_child(sprite)
	var shape := RectangleShape2D.new()
	shape.size = Vector2(18, 24)
	var cs := CollisionShape2D.new()
	cs.shape = shape
	add_child(cs)
	body_entered.connect(_on_body_entered)
	z_index = -1


func _on_body_entered(body: Node) -> void:
	if not active or not (body is Player):
		return
	active = false
	sprite.play("on")
	Global.spawn_burst(get_parent(), global_position + Vector2(0, -8), Color("F4A62A"), 28, 100.0, 0.9, 40.0)
	Global.spawn_burst(get_parent(), global_position + Vector2(0, -8), Color("FFF3C4"), 16, 70.0, 0.7, 30.0)
	level.complete_level()
