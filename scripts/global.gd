extends Node
## Global.gd (Autoload)
## Estado compartido del juego (vidas, chispas, puntos, nivel actual), registro de controles,
## reproductor de audio y utilidades que usan todas las escenas.

signal lives_changed(lives: int)
signal sparks_changed(total: int)

const MAX_LIVES := 5
const START_LIVES := 3
const SPRITES := "res://assets/sprites/"
const AUDIO := "res://assets/audio/"

# ---- Estado de la partida ----
var lives := START_LIVES
var sparks := 0          # chispas recogidas en toda la partida
var score := 0
var kills := 0
var deaths := 0
var play_time := 0.0
var current_level := 0

# ---- Modo de pruebas automáticas (bot). Se activa con:  godot -- --autotest ----
var autotest := false
var autotest_no_enemies := false

var _tex_cache := {}
var _sfx_cache := {}
var _sfx_players: Array[AudioStreamPlayer] = []
var _music: AudioStreamPlayer
var music_name := ""


func _ready() -> void:
	process_mode = Node.PROCESS_MODE_ALWAYS
	_register_inputs()
	for i in 8:
		var p := AudioStreamPlayer.new()
		p.bus = "Master"
		add_child(p)
		_sfx_players.append(p)
	_music = AudioStreamPlayer.new()
	_music.volume_db = -9.0
	add_child(_music)
	var args := OS.get_cmdline_user_args()
	autotest = "--autotest" in args
	autotest_no_enemies = "--no-enemies" in args
	for a in args:
		if a.begins_with("--level="):
			current_level = int(a.substr(8))


# ----------------------------------------------------------------- Controles
## Registra las acciones del juego por código (teclado y control de consola).
func _register_inputs() -> void:
	var keys := {
		"move_left": [KEY_A, KEY_LEFT],
		"move_right": [KEY_D, KEY_RIGHT],
		"jump": [KEY_SPACE, KEY_W, KEY_UP, KEY_Z],
		"fire": [KEY_X, KEY_J, KEY_SHIFT],
		"pause": [KEY_ESCAPE, KEY_P],
		"confirm": [KEY_ENTER, KEY_KP_ENTER],
		"menu": [KEY_M],
	}
	for action in keys:
		if not InputMap.has_action(action):
			InputMap.add_action(action, 0.5)
		for k in keys[action]:
			var ev := InputEventKey.new()
			ev.physical_keycode = k
			InputMap.action_add_event(action, ev)
	var pad := {
		"jump": JOY_BUTTON_A,
		"fire": JOY_BUTTON_X,
		"pause": JOY_BUTTON_START,
		"confirm": JOY_BUTTON_A,
		"move_left": JOY_BUTTON_DPAD_LEFT,
		"move_right": JOY_BUTTON_DPAD_RIGHT,
	}
	for action in pad:
		var jb := InputEventJoypadButton.new()
		jb.button_index = pad[action]
		InputMap.action_add_event(action, jb)
	var axes := {"move_left": -1.0, "move_right": 1.0}
	for action in axes:
		var jm := InputEventJoypadMotion.new()
		jm.axis = JOY_AXIS_LEFT_X
		jm.axis_value = axes[action]
		InputMap.action_add_event(action, jm)


# ----------------------------------------------------------------- Partida
func start_new_game() -> void:
	lives = START_LIVES
	sparks = 0
	score = 0
	kills = 0
	deaths = 0
	play_time = 0.0
	current_level = 0
	lives_changed.emit(lives)
	sparks_changed.emit(sparks)


func add_spark() -> void:
	sparks += 1
	score += 10
	sparks_changed.emit(sparks)


func add_score(points: int) -> void:
	score += points


func gain_life() -> void:
	lives = min(lives + 1, MAX_LIVES)
	lives_changed.emit(lives)


## Resta una vida. Devuelve true si ya no quedan (fin del juego).
func lose_life() -> bool:
	lives -= 1
	lives_changed.emit(max(lives, 0))
	return lives <= 0


# ----------------------------------------------------------------- Recursos
func tex(file: String) -> Texture2D:
	if not _tex_cache.has(file):
		_tex_cache[file] = load(SPRITES + file)
	return _tex_cache[file]


## Crea SpriteFrames a partir de una hoja horizontal.
## anims = { "idle": {"frames": [0, 1], "fps": 3.0, "loop": true}, ... }
func make_frames(file: String, fw: int, fh: int, anims: Dictionary) -> SpriteFrames:
	var sf := SpriteFrames.new()
	if sf.has_animation("default"):
		sf.remove_animation("default")
	var t := tex(file)
	for anim_name in anims:
		var cfg: Dictionary = anims[anim_name]
		sf.add_animation(anim_name)
		sf.set_animation_speed(anim_name, cfg.get("fps", 6.0))
		sf.set_animation_loop(anim_name, cfg.get("loop", true))
		for idx in cfg["frames"]:
			var at := AtlasTexture.new()
			at.atlas = t
			at.region = Rect2(idx * fw, 0, fw, fh)
			sf.add_frame(anim_name, at)
	return sf


# ----------------------------------------------------------------- Audio
func play_sfx(sfx_name: String, volume_db: float = 0.0) -> void:
	if autotest:
		return
	if not _sfx_cache.has(sfx_name):
		_sfx_cache[sfx_name] = load(AUDIO + sfx_name + ".wav")
	for p in _sfx_players:
		if not p.playing:
			p.stream = _sfx_cache[sfx_name]
			p.volume_db = volume_db - 4.0
			p.play()
			return


func play_music(track: String) -> void:
	if autotest or track == music_name:
		return
	music_name = track
	var s: AudioStreamWAV = load(AUDIO + track + ".wav")
	s.loop_mode = AudioStreamWAV.LOOP_FORWARD
	s.loop_begin = 0
	s.loop_end = s.data.size() / 2   # 16 bits, mono -> 2 bytes por muestra
	_music.stream = s
	_music.play()


func stop_music() -> void:
	music_name = ""
	_music.stop()


# ----------------------------------------------------------------- Efectos
## Explosión de partículas de una sola vez (chispas, humo, impactos).
func spawn_burst(parent: Node, pos: Vector2, color: Color, amount: int = 14,
		speed: float = 70.0, life: float = 0.6, grav: float = 120.0) -> void:
	var p := CPUParticles2D.new()
	p.texture = tex("particle.png")
	p.one_shot = true
	p.emitting = true
	p.amount = amount
	p.lifetime = life
	p.explosiveness = 1.0
	p.direction = Vector2(0, -1)
	p.spread = 180.0
	p.initial_velocity_min = speed * 0.5
	p.initial_velocity_max = speed
	p.gravity = Vector2(0, grav)
	p.scale_amount_min = 0.8
	p.scale_amount_max = 1.5
	p.color = color
	var g := Gradient.new()
	g.set_color(0, Color(1, 1, 1, 1))
	g.set_color(1, Color(1, 1, 1, 0))
	p.color_ramp = g
	p.z_index = 20
	parent.add_child(p)
	p.global_position = pos
	get_tree().create_timer(life + 0.4).timeout.connect(p.queue_free)
