extends CharacterBody2D
class_name Player
## Player.gd -- Embra, la brasa protagonista.
## Movimiento con aceleración, salto variable, "coyote time" y buffer de salto,
## bola de fuego (X), rebote al pisar enemigos y estela de fuego/humo con partículas.

const SPEED := 100.0
const ACCEL := 1100.0
const AIR_ACCEL := 800.0
const FRICTION := 1300.0
const GRAVITY := 980.0
const JUMP_VELOCITY := -340.0
const JUMP_CUT := -120.0       # al soltar el botón se recorta el salto
const MAX_FALL := 420.0
const COYOTE_TIME := 0.10      # margen para saltar justo después de dejar el borde
const JUMP_BUFFER := 0.12      # margen si se presiona saltar un poco antes de aterrizar
const STOMP_BOUNCE := -230.0
const FIRE_COOLDOWN := 0.40
const MAX_FIREBALLS := 3
const INVULN_TIME := 1.6

var level: Level
var sprite: AnimatedSprite2D
var camera: Camera2D
var fire_trail: CPUParticles2D
var smoke_trail: CPUParticles2D

var facing := 1
var coyote := 0.0
var jump_buffer := 0.0
var fire_timer := 0.0
var invuln := 0.0
var dead := false
var frozen := false

# Entrada: la llena el teclado/control o el bot de pruebas
var bot: Bot = null
var in_dir := 0.0
var in_jump_pressed := false
var in_jump_held := false
var in_fire := false


func _ready() -> void:
	collision_layer = 2
	collision_mask = 1
	floor_snap_length = 4.0
	var shape := CapsuleShape2D.new()
	shape.radius = 5.0
	shape.height = 14.0
	var cs := CollisionShape2D.new()
	cs.shape = shape
	cs.position = Vector2(0, 1)
	add_child(cs)

	sprite = AnimatedSprite2D.new()
	sprite.sprite_frames = Global.make_frames("embra_sheet.png", 16, 16, {
		"idle": {"frames": [0, 1], "fps": 3.0},
		"run": {"frames": [2, 3, 4, 5], "fps": 11.0},
		"jump": {"frames": [6], "fps": 1.0},
		"fall": {"frames": [7], "fps": 1.0},
		"hurt": {"frames": [8], "fps": 1.0},
	})
	sprite.play("idle")
	add_child(sprite)

	_setup_particles()

	camera = Camera2D.new()
	camera.position_smoothing_enabled = true
	camera.position_smoothing_speed = 7.0
	camera.drag_horizontal_enabled = false
	add_child(camera)
	camera.make_current()


## Estela de fuego y humo que acompaña a Embra (sistema de partículas).
func _setup_particles() -> void:
	fire_trail = CPUParticles2D.new()
	fire_trail.texture = Global.tex("particle.png")
	fire_trail.position = Vector2(0, -5)
	fire_trail.amount = 14
	fire_trail.lifetime = 0.55
	fire_trail.local_coords = false
	fire_trail.direction = Vector2(0, -1)
	fire_trail.spread = 22.0
	fire_trail.gravity = Vector2(0, -35)
	fire_trail.initial_velocity_min = 12.0
	fire_trail.initial_velocity_max = 28.0
	fire_trail.scale_amount_min = 0.6
	fire_trail.scale_amount_max = 1.1
	var g := Gradient.new()
	g.offsets = PackedFloat32Array([0.0, 0.45, 1.0])
	g.colors = PackedColorArray([Color(1.0, 0.92, 0.45, 0.95), Color(1.0, 0.45, 0.15, 0.75), Color(0.7, 0.15, 0.2, 0.0)])
	fire_trail.color_ramp = g
	fire_trail.z_index = 5
	add_child(fire_trail)

	smoke_trail = CPUParticles2D.new()
	smoke_trail.texture = Global.tex("particle.png")
	smoke_trail.position = Vector2(0, -8)
	smoke_trail.amount = 7
	smoke_trail.lifetime = 1.1
	smoke_trail.local_coords = false
	smoke_trail.direction = Vector2(0, -1)
	smoke_trail.spread = 30.0
	smoke_trail.gravity = Vector2(0, -18)
	smoke_trail.initial_velocity_min = 8.0
	smoke_trail.initial_velocity_max = 16.0
	smoke_trail.scale_amount_min = 0.8
	smoke_trail.scale_amount_max = 1.4
	var gs := Gradient.new()
	gs.offsets = PackedFloat32Array([0.0, 0.3, 1.0])
	gs.colors = PackedColorArray([Color(0.75, 0.75, 0.78, 0.0), Color(0.6, 0.6, 0.65, 0.45), Color(0.4, 0.4, 0.45, 0.0)])
	smoke_trail.color_ramp = gs
	smoke_trail.z_index = 4
	add_child(smoke_trail)


func _read_input() -> void:
	if bot != null:
		bot.fill(self)
		return
	in_dir = Input.get_axis("move_left", "move_right")
	in_jump_pressed = Input.is_action_just_pressed("jump")
	in_jump_held = Input.is_action_pressed("jump")
	in_fire = Input.is_action_pressed("fire")


func _physics_process(delta: float) -> void:
	if dead:
		return
	if frozen:
		velocity.x = move_toward(velocity.x, 0.0, FRICTION * delta)
		velocity.y = min(velocity.y + GRAVITY * delta, MAX_FALL)
		move_and_slide()
		_update_animation()
		return

	_read_input()
	fire_timer = max(fire_timer - delta, 0.0)

	# Invulnerabilidad tras reaparecer: parpadeo
	if invuln > 0.0:
		invuln -= delta
		sprite.visible = int(invuln * 14.0) % 2 == 0
		if invuln <= 0.0:
			sprite.visible = true

	# --- Horizontal ---
	if in_dir != 0.0:
		var acc := ACCEL if is_on_floor() else AIR_ACCEL
		velocity.x = move_toward(velocity.x, in_dir * SPEED, acc * delta)
		facing = 1 if in_dir > 0.0 else -1
	else:
		velocity.x = move_toward(velocity.x, 0.0, FRICTION * delta)

	# --- Vertical: gravedad, coyote time, buffer de salto y salto variable ---
	velocity.y = min(velocity.y + GRAVITY * delta, MAX_FALL)
	if is_on_floor():
		coyote = COYOTE_TIME
	else:
		coyote = max(coyote - delta, 0.0)
	if in_jump_pressed:
		jump_buffer = JUMP_BUFFER
	else:
		jump_buffer = max(jump_buffer - delta, 0.0)
	if jump_buffer > 0.0 and coyote > 0.0:
		velocity.y = JUMP_VELOCITY
		coyote = 0.0
		jump_buffer = 0.0
		Global.play_sfx("jump")
	if not in_jump_held and velocity.y < JUMP_CUT:
		velocity.y = JUMP_CUT

	move_and_slide()

	# --- Bola de fuego ---
	if in_fire and fire_timer <= 0.0 and get_tree().get_nodes_in_group("fireball").size() < MAX_FIREBALLS:
		_shoot()

	_update_animation()

	# Caída al vacío
	if level != null and global_position.y > level.height_tiles * Level.TILE + 48:
		die()


func _shoot() -> void:
	fire_timer = FIRE_COOLDOWN
	var fb := Fireball.new()
	fb.direction = facing
	level.add_child(fb)
	fb.global_position = global_position + Vector2(facing * 9.0, 0.0)
	Global.play_sfx("fire")


func _update_animation() -> void:
	sprite.flip_h = facing < 0
	var anim := "idle"
	if not is_on_floor():
		anim = "jump" if velocity.y < 0.0 else "fall"
	elif absf(velocity.x) > 10.0:
		anim = "run"
	if sprite.animation != anim:
		sprite.play(anim)
	# La estela se acelera un poco al moverse
	fire_trail.speed_scale = 1.0 if absf(velocity.x) > 10.0 or not is_on_floor() else 0.7


## Rebote al pisar un enemigo.
func bounce() -> void:
	velocity.y = -290.0 if in_jump_held else STOMP_BOUNCE
	coyote = 0.0


## Daño por enemigo, púas o proyectil.
func hurt() -> void:
	if invuln > 0.0 or dead or frozen:
		return
	if Global.autotest:
		return   # en pruebas automáticas Embra es invulnerable
	die()


func die() -> void:
	if dead:
		return
	dead = true
	sprite.visible = false
	fire_trail.emitting = false
	smoke_trail.emitting = false
	velocity = Vector2.ZERO
	Global.play_sfx("hurt")
	Global.spawn_burst(level, global_position, Color(1.0, 0.55, 0.2), 26, 110.0, 0.8, 200.0)
	Global.spawn_burst(level, global_position, Color(0.55, 0.55, 0.6), 10, 40.0, 1.0, -20.0)
	level.on_player_died()


func respawn(pos: Vector2) -> void:
	global_position = pos
	velocity = Vector2.ZERO
	dead = false
	sprite.visible = true
	fire_trail.emitting = true
	smoke_trail.emitting = true
	invuln = INVULN_TIME
	camera.reset_smoothing()


func freeze() -> void:
	frozen = true
	in_dir = 0.0
