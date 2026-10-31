extends CharacterBody2D
class_name Player
## Player.gd -- Embra, elemental de brasa (boceto del GDD).
## Mecánicas del GDD: moverse a izquierda/derecha y saltar entre plataformas.
## Se agregaron "coyote time" y buffer de salto para que los controles se sientan justos, y una
## estela de fuego y humo hecha con partículas. Chocar con un Rondín o con fuego activo, o caer
## al vacío, cuesta una vida (la penalización de puntos la maneja Level/Global).
## Mejoras tras la prueba con usuarios: Embra puede pisar enemigos (rebota) y EVOLUCIONA con las
## chispas: Brasa (pisotón) -> Llama (lanza bolas de fuego con X) -> Fuego ardiente (fuego perforante).

const SPEED := 100.0
const ACCEL := 1100.0
const AIR_ACCEL := 800.0
const FRICTION := 1300.0
const GRAVITY := 980.0
const JUMP_VELOCITY := -340.0
const JUMP_CUT := -120.0       # al soltar el botón se recorta el salto (salto variable)
const MAX_FALL := 420.0
const COYOTE_TIME := 0.10      # margen para saltar justo después de dejar un borde
const JUMP_BUFFER := 0.12      # margen si se presiona saltar un poco antes de aterrizar
const INVULN_TIME := 1.6       # parpadeo e invulnerabilidad tras reaparecer
const HALF_HEIGHT := 12.0      # el sprite mide 24 px de alto
const FIRE_COOLDOWN := [0.0, 0.5, 0.28]   # por etapa (la etapa 1 no dispara)
const MAX_FIREBALLS := [0, 3, 4]

var level: Level
var sprite: AnimatedSprite2D
var camera: Camera2D
var fire_trail: CPUParticles2D
var smoke_trail: CPUParticles2D

var facing := 1
var coyote := 0.0
var jump_buffer := 0.0
var invuln := 0.0
var stage := 1
var prev_feet_y := 0.0      # posición de los pies antes de moverse en este fotograma (para detectar pisotones)
var fire_timer := 0.0
var shoot_anim := 0.0
var _hint_cd := 0.0
var _stage_frames: Array = []
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
	shape.radius = 4.5
	shape.height = 16.0
	var cs := CollisionShape2D.new()
	cs.shape = shape
	cs.position = Vector2(0, 4)
	add_child(cs)

	# Una hoja de sprites por etapa de evolución
	for file in ["embra_sheet.png", "embra2_sheet.png", "embra3_sheet.png"]:
		_stage_frames.append(Global.make_frames(file, 16, 24, {
			"idle": {"frames": [0, 1], "fps": 3.0},
			"run": {"frames": [2, 3, 4, 5], "fps": 11.0},
			"jump": {"frames": [6], "fps": 1.0},
			"fall": {"frames": [7], "fps": 1.0},
			"hurt": {"frames": [8], "fps": 1.0},
			"shoot": {"frames": [9], "fps": 1.0},
		}))
	sprite = AnimatedSprite2D.new()
	sprite.sprite_frames = _stage_frames[0]
	sprite.play("idle")
	add_child(sprite)

	_setup_particles()

	camera = Camera2D.new()
	camera.position_smoothing_enabled = true
	camera.position_smoothing_speed = 7.0
	add_child(camera)
	camera.make_current()


## Estela de fuego y humo que acompaña a Embra (sistema de partículas del GDD).
func _setup_particles() -> void:
	fire_trail = CPUParticles2D.new()
	fire_trail.texture = Global.tex("particle.png")
	fire_trail.position = Vector2(0, -10)
	fire_trail.amount = 12
	fire_trail.lifetime = 0.5
	fire_trail.local_coords = false
	fire_trail.direction = Vector2(0, -1)
	fire_trail.spread = 22.0
	fire_trail.gravity = Vector2(0, -35)
	fire_trail.initial_velocity_min = 12.0
	fire_trail.initial_velocity_max = 26.0
	fire_trail.scale_amount_min = 0.5
	fire_trail.scale_amount_max = 1.0
	var g := Gradient.new()
	g.offsets = PackedFloat32Array([0.0, 0.45, 1.0])
	g.colors = PackedColorArray([Color("FFF3C4", 0.95), Color("F4A62A", 0.75), Color("E8542A", 0.0)])
	fire_trail.color_ramp = g
	fire_trail.z_index = 5
	add_child(fire_trail)

	smoke_trail = CPUParticles2D.new()
	smoke_trail.texture = Global.tex("particle.png")
	smoke_trail.position = Vector2(0, -14)
	smoke_trail.amount = 6
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
	gs.colors = PackedColorArray([Color(0.7, 0.72, 0.85, 0.0), Color(0.6, 0.62, 0.78, 0.4), Color(0.4, 0.42, 0.6, 0.0)])
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

	prev_feet_y = global_position.y + HALF_HEIGHT
	_read_input()
	fire_timer = max(fire_timer - delta, 0.0)
	shoot_anim = max(shoot_anim - delta, 0.0)
	_hint_cd = max(_hint_cd - delta, 0.0)
	if in_fire:
		_try_shoot()

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
	_update_animation()

	# Caída al vacío: pierde una vida pero conserva el puntaje (GDD)
	if level != null and global_position.y > level.height_tiles * Level.TILE + 48:
		die("void")


func _update_animation() -> void:
	sprite.flip_h = facing < 0
	var anim := "idle"
	if shoot_anim > 0.0:
		anim = "shoot"
	elif not is_on_floor():
		anim = "jump" if velocity.y < 0.0 else "fall"
	elif absf(velocity.x) > 10.0:
		anim = "run"
	if sprite.animation != anim:
		sprite.play(anim)
	fire_trail.speed_scale = 1.0 if absf(velocity.x) > 10.0 or not is_on_floor() else 0.7


## Rebote al pisar un enemigo (mantener saltar da más impulso).
func bounce() -> void:
	velocity.y = -290.0 if in_jump_held else -230.0
	coyote = 0.0


## Dispara una bola de fuego (desde la etapa 2). Si aún no se ha evolucionado, avisa cómo lograrlo.
func _try_shoot() -> void:
	if stage < 2:
		if _hint_cd <= 0.0 and level != null:
			_hint_cd = 3.0
			level.hud.show_message("¡Junta %d chispas más para evolucionar y lanzar fuego!" % Global.sparks_to_next(), 2.0)
		return
	if fire_timer > 0.0 or get_tree().get_nodes_in_group("fireball").size() >= MAX_FIREBALLS[stage - 1]:
		return
	fire_timer = FIRE_COOLDOWN[stage - 1]
	shoot_anim = 0.18
	var fb := Fireball.new()
	fb.direction = facing
	fb.damage = 2 if stage >= 3 else 1
	fb.pierce = stage >= 3
	level.add_child(fb)
	fb.global_position = global_position + Vector2(facing * 11.0, 2.0)
	Global.play_sfx("shoot")


## Cambia la apariencia y las habilidades según la etapa de evolución.
func set_stage(new_stage: int, celebrate: bool = false) -> void:
	stage = clampi(new_stage, 1, 3)
	sprite.sprite_frames = _stage_frames[stage - 1]
	sprite.play("idle")
	if celebrate:
		Global.play_sfx("evolve")
		Global.spawn_burst(level, global_position, Color("FFF3C4"), 26, 120.0, 0.8, 0.0)
		Global.spawn_burst(level, global_position, Color("F4A62A"), 20, 90.0, 0.9, -30.0)
		var tw := create_tween()
		tw.tween_property(sprite, "modulate", Color(3, 3, 3), 0.1)
		tw.tween_property(sprite, "modulate", Color.WHITE, 0.4)


## Contacto con un Rondín o con una zona de fuego y humo activa.
func hurt() -> void:
	if invuln > 0.0 or dead or frozen:
		return
	if Global.autotest:
		return   # en pruebas automáticas Embra es invulnerable a enemigos y fuego
	die("hit")


## kind = "hit" (enemigo o fuego: pierde vida y parte del puntaje) o "void" (vacío: solo pierde vida)
func die(kind: String) -> void:
	if dead:
		return
	dead = true
	sprite.visible = false
	fire_trail.emitting = false
	smoke_trail.emitting = false
	velocity = Vector2.ZERO
	Global.play_sfx("hurt" if kind == "hit" else "lifelost")
	Global.spawn_burst(level, global_position, Color("F4A62A"), 24, 110.0, 0.8, 200.0)
	Global.spawn_burst(level, global_position, Color("E8542A"), 12, 80.0, 0.7, 150.0)
	level.on_player_died(kind)


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
