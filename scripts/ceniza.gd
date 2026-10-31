extends EnemyBase
class_name Ceniza
## Ceniza.gd -- Ceniza: espíritu de ceniza que vuela en ondas alrededor de su punto de origen.
## Se vence pisándolo desde arriba o con una bola de fuego.

var origin := Vector2.ZERO
var _t := 0.0


func _setup() -> void:
	collision_mask = 0
	origin = position
	_t = randf() * TAU
	points = 75
	var shape := CircleShape2D.new()
	shape.radius = 6.0
	var cs := CollisionShape2D.new()
	cs.shape = shape
	add_child(cs)
	sprite = AnimatedSprite2D.new()
	sprite.sprite_frames = Global.make_frames("ceniza_sheet.png", 16, 16, {"fly": {"frames": [0, 1], "fps": 6.0}})
	sprite.play("fly")
	add_child(sprite)
	_make_touch(Vector2(12, 12), Vector2.ZERO)


func _behave(delta: float) -> void:
	_t += delta
	sprite.flip_h = cos(_t * 0.9) < 0.0
	position = origin + Vector2(sin(_t * 0.9) * 42.0, sin(_t * 1.8) * 10.0)
