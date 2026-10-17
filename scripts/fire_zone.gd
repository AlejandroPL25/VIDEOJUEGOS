extends Area2D
class_name FireZone
## FireZone.gd -- Zona de fuego y humo (GDD): peligro ambiental hecho con partículas.
## Alterna entre fase ACTIVA (llamas: quema a Embra), AVISO (brasas que anuncian que viene el fuego)
## y APAGADA (solo humo: es segura). Así hay que medir el tiempo de los saltos.

enum Phase { IDLE, WARN, ACTIVE }

const IDLE_TIME := 1.5
const WARN_TIME := 0.5
const ACTIVE_TIME := 1.8
const FLAME_HEIGHT := 24.0

var width_px := 32.0
var phase := Phase.ACTIVE
var _t := 0.0
var flames: CPUParticles2D
var embers: CPUParticles2D
var smoke: CPUParticles2D
var shape: RectangleShape2D


func _ready() -> void:
	add_to_group("hazard")
	collision_layer = 0
	collision_mask = 2
	# Base de piedra con grieta de brasa
	var vents := int(round(width_px / 16.0))
	for i in vents:
		var v := Sprite2D.new()
		v.texture = Global.tex("fire_vent.png")
		v.position = Vector2(-width_px / 2.0 + 8.0 + i * 16.0, -4.0)
		add_child(v)

	shape = RectangleShape2D.new()
	shape.size = Vector2(width_px - 4.0, FLAME_HEIGHT)
	var cs := CollisionShape2D.new()
	cs.shape = shape
	cs.position = Vector2(0, -8.0 - FLAME_HEIGHT / 2.0)
	add_child(cs)

	flames = _make_emitter(int(width_px * 0.8), 0.6, 28.0, 46.0, 1.0, 1.8,
		[Color("FFF3C4", 0.95), Color("F4A62A", 0.85), Color("E8542A", 0.0)], Vector2(0, -22))
	embers = _make_emitter(int(width_px / 5.0), 0.9, 16.0, 30.0, 0.4, 0.7,
		[Color("FFF3C4", 0.9), Color("F4A62A", 0.7), Color("E8542A", 0.0)], Vector2(0, -12))
	smoke = _make_emitter(int(width_px / 4.0), 1.6, 8.0, 16.0, 1.2, 2.0,
		[Color(0.55, 0.58, 0.75, 0.0), Color(0.5, 0.52, 0.7, 0.38), Color(0.35, 0.38, 0.55, 0.0)], Vector2(0, -10))
	smoke.emitting = true
	z_index = 3
	_t = randf() * (IDLE_TIME + WARN_TIME + ACTIVE_TIME)    # cada zona arranca en un punto distinto del ciclo
	_set_phase_from_time()


func _make_emitter(amount: int, life: float, v_min: float, v_max: float, s_min: float, s_max: float,
		colors: Array, offset: Vector2) -> CPUParticles2D:
	var p := CPUParticles2D.new()
	p.texture = Global.tex("particle.png")
	p.amount = max(amount, 4)
	p.lifetime = life
	p.position = Vector2(0, -8.0)
	p.emission_shape = CPUParticles2D.EMISSION_SHAPE_RECTANGLE
	p.emission_rect_extents = Vector2(width_px / 2.0 - 3.0, 1.0)
	p.direction = Vector2(0, -1)
	p.spread = 14.0
	p.gravity = Vector2(0, -12)
	p.initial_velocity_min = v_min
	p.initial_velocity_max = v_max
	p.scale_amount_min = s_min
	p.scale_amount_max = s_max
	var g := Gradient.new()
	g.offsets = PackedFloat32Array([0.0, 0.5, 1.0])
	g.colors = PackedColorArray(colors)
	p.color_ramp = g
	p.emitting = false
	add_child(p)
	return p


func _set_phase_from_time() -> void:
	var cycle := IDLE_TIME + WARN_TIME + ACTIVE_TIME
	var m := fmod(_t, cycle)
	var new_phase := Phase.IDLE
	if m >= IDLE_TIME + WARN_TIME:
		new_phase = Phase.ACTIVE
	elif m >= IDLE_TIME:
		new_phase = Phase.WARN
	phase = new_phase
	flames.emitting = phase == Phase.ACTIVE
	embers.emitting = phase != Phase.IDLE


func is_active() -> bool:
	return phase == Phase.ACTIVE


func _physics_process(delta: float) -> void:
	_t += delta
	_set_phase_from_time()
	if phase == Phase.ACTIVE:
		for b in get_overlapping_bodies():
			if b is Player:
				b.hurt()
