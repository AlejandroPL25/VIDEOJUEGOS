extends Area2D
class_name Flyer
## Flyer.gd -- Humoro: fantasma de humo que vuela en ondas alrededor de su punto de origen.
## Se vence pisándolo o con una bola de fuego.

var origin := Vector2.ZERO
var dead := false
var _t := 0.0
var sprite: AnimatedSprite2D


func _ready() -> void:
	add_to_group("enemy")
	collision_layer = 4          # para que las bolas de fuego lo detecten
	collision_mask = 2           # y detecta al jugador
	origin = position
	_t = randf() * TAU
	var shape := CircleShape2D.new()
	shape.radius = 6.0
	var cs := CollisionShape2D.new()
	cs.shape = shape
	add_child(cs)
	sprite = AnimatedSprite2D.new()
	sprite.sprite_frames = Global.make_frames("humoro_sheet.png", 16, 16, {"fly": {"frames": [0, 1], "fps": 6.0}})
	sprite.play("fly")
	add_child(sprite)
	body_entered.connect(_on_body_entered)


func _physics_process(delta: float) -> void:
	if dead:
		return
	_t += delta
	var new_pos := origin + Vector2(sin(_t * 0.9) * 42.0, sin(_t * 1.8) * 10.0)
	sprite.flip_h = cos(_t * 0.9) < 0.0
	position = new_pos


func _on_body_entered(body: Node) -> void:
	if body is Player and not dead and not body.dead:
		if body.velocity.y > 20.0 and body.global_position.y < global_position.y - 2.0:
			body.bounce()
			_die(true)
		else:
			body.hurt()


func hit(_dmg: int) -> void:
	_die(false)


func _die(stomp: bool) -> void:
	if dead:
		return
	dead = true
	Global.kills += 1
	Global.add_score(75)
	set_deferred("monitoring", false)
	set_deferred("monitorable", false)
	Global.play_sfx("stomp" if stomp else "hit")
	Global.spawn_burst(get_parent(), global_position, Color(0.75, 0.78, 0.82), 12, 50.0, 0.7, -10.0)
	if not stomp:
		Global.spawn_burst(get_parent(), global_position, Color(1.0, 0.6, 0.25), 8, 55.0, 0.4, 80.0)
	queue_free()
