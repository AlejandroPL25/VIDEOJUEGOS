extends Area2D
class_name Pickup
## Pickup.gd -- Objetos coleccionables: chispa (puntos) y corazón (vida extra).

enum Kind { SPARK, HEART }

var kind: Kind = Kind.SPARK
var level: Level
var _base_y := 0.0
var _t := 0.0


func _ready() -> void:
	collision_layer = 0
	collision_mask = 2
	var shape := CircleShape2D.new()
	shape.radius = 5.0 if kind == Kind.SPARK else 6.0
	var cs := CollisionShape2D.new()
	cs.shape = shape
	add_child(cs)
	if kind == Kind.SPARK:
		var spr := AnimatedSprite2D.new()
		spr.sprite_frames = Global.make_frames("spark.png", 8, 8, {"glow": {"frames": [0, 1], "fps": 4.0}})
		spr.play("glow")
		add_child(spr)
	else:
		var spr2 := Sprite2D.new()
		spr2.texture = Global.tex("heart.png")
		add_child(spr2)
	_base_y = position.y
	_t = randf() * TAU
	body_entered.connect(_on_body_entered)


func _physics_process(delta: float) -> void:
	_t += delta * 3.0
	position.y = _base_y + sin(_t) * 1.5     # flota suavemente


func _on_body_entered(body: Node) -> void:
	if not (body is Player) or body.dead:
		return
	set_deferred("monitoring", false)
	if kind == Kind.SPARK:
		Global.add_spark()
		level.sparks_collected += 1
		level.hud.set_sparks(level.sparks_collected, level.sparks_in_level)
		Global.play_sfx("spark")
		Global.spawn_burst(get_parent(), global_position, Color(1.0, 0.85, 0.3), 6, 40.0, 0.35, 0.0)
	else:
		Global.gain_life()
		Global.play_sfx("oneup")
		level.hud.show_message("¡Vida extra!", 1.5)
		Global.spawn_burst(get_parent(), global_position, Color(1.0, 0.4, 0.5), 10, 50.0, 0.5, 0.0)
	queue_free()
