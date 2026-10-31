extends Node
## Global.gd (Autoload)
## Estado compartido del juego según el GDD: vidas, chispas, puntaje del nivel, penalizaciones,
## tabla de mejor puntaje por nivel (se guarda en disco), registro de controles y audio
## (música de dos capas que se intensifica cerca de enemigos y fuego).

signal lives_changed(lives: int)
signal stage_changed(stage: int)

const START_LIVES := 3
const PENALTY_RATIO := 0.2         # al chocar con un Rondín o con fuego se pierde el 20 % del puntaje del nivel
const SPARK_POINTS := 10
const LEVEL_BONUS := 100
const SAVE_PATH := "user://embra_scores.cfg"
# Evolución de Embra (mejora posterior a la prueba con usuarios): se evoluciona con las chispas recogidas
const STAGE_NAMES := ["Brasa", "Llama", "Fuego ardiente"]
const STAGE_SPARKS := [0, 20, 70]
const SPRITES := "res://assets/sprites/"
const AUDIO := "res://assets/audio/"

# ---- Estado de la partida ----
var lives := START_LIVES
var sparks := 0              # chispas recogidas en toda la partida
var level_score := 0         # puntaje acumulado en el nivel actual
var total_score := 0         # suma de los niveles ya completados
var deaths := 0
var kills := 0
var sparks_at_level_start := 0
var play_time := 0.0
var current_level := 0
var best_scores: Array = [0, 0, 0, 0]    # mejor puntaje por nivel

# ---- Modo de pruebas automáticas (bot):  godot -- --autotest ----
var autotest := false
var freeze_enemies := false      # solo para pruebas del pisotón: los Rondines no se mueven

# ---- Modo de capturas (desarrollo):  godot -- --shot=ruta.png --shot-frames=90 ----
var shot_path := ""
var shot_frames := 90
var _frame_count := 0

var _tex_cache := {}
var _sfx_cache := {}
var _sfx_players: Array[AudioStreamPlayer] = []
var _music: AudioStreamPlayer
var _danger: AudioStreamPlayer
var music_name := ""
var _danger_target := 0.0
var _danger_value := 0.0


func _ready() -> void:
	process_mode = Node.PROCESS_MODE_ALWAYS
	_register_inputs()
	for i in 8:
		var p := AudioStreamPlayer.new()
		add_child(p)
		_sfx_players.append(p)
	_music = AudioStreamPlayer.new()
	_music.volume_db = -9.0
	add_child(_music)
	_danger = AudioStreamPlayer.new()
	_danger.volume_db = -80.0
	add_child(_danger)
	_load_scores()
	var args := OS.get_cmdline_user_args()
	autotest = "--autotest" in args
	for a in args:
		if a.begins_with("--level="):
			current_level = int(a.substr(8))
		elif a == "--freeze-enemies":
			freeze_enemies = true
		elif a.begins_with("--sparks="):
			sparks = int(a.substr(9))       # solo para pruebas: empezar con N chispas (define la etapa de Embra)
		elif a.begins_with("--shot="):
			shot_path = a.substr(7)
		elif a.begins_with("--shot-frames="):
			shot_frames = int(a.substr(14))


# ----------------------------------------------------------------- Controles
## Registra las acciones del juego por código: flechas/AD para mover y ESPACIO para saltar (GDD).
func _register_inputs() -> void:
	var keys := {
		"move_left": [KEY_LEFT, KEY_A],
		"move_right": [KEY_RIGHT, KEY_D],
		"jump": [KEY_SPACE, KEY_UP, KEY_W],
		"fire": [KEY_X, KEY_J],
		"quit_game": [KEY_Q],
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
	var pad := {"jump": JOY_BUTTON_A, "fire": JOY_BUTTON_X, "pause": JOY_BUTTON_START, "confirm": JOY_BUTTON_A,
			"move_left": JOY_BUTTON_DPAD_LEFT, "move_right": JOY_BUTTON_DPAD_RIGHT}
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


# ----------------------------------------------------------------- Partida y puntajes
func start_new_game() -> void:
	lives = START_LIVES
	sparks = 0
	level_score = 0
	total_score = 0
	deaths = 0
	kills = 0
	sparks_at_level_start = 0
	play_time = 0.0
	current_level = 0
	lives_changed.emit(lives)


## Se llama al comenzar (o reintentar) un nivel.
func start_level() -> void:
	level_score = 0
	sparks_at_level_start = sparks


## Al reintentar un nivel tras el fin del juego se recuperan las chispas que se tenían al empezarlo.
func restore_level_start() -> void:
	sparks = sparks_at_level_start


## Etapa de evolución actual (1 = Brasa, 2 = Llama, 3 = Fuego ardiente) según las chispas recogidas.
func stage() -> int:
	var s := 1
	for i in STAGE_SPARKS.size():
		if sparks >= STAGE_SPARKS[i]:
			s = i + 1
	return s


## Progreso (0 a 1) hacia la siguiente etapa; en la última etapa siempre es 1.
func stage_progress() -> float:
	var s := stage()
	if s >= STAGE_SPARKS.size():
		return 1.0
	var a: int = STAGE_SPARKS[s - 1]
	var b: int = STAGE_SPARKS[s]
	return clampf(float(sparks - a) / float(b - a), 0.0, 1.0)


func sparks_to_next() -> int:
	var s := stage()
	if s >= STAGE_SPARKS.size():
		return 0
	return int(STAGE_SPARKS[s]) - sparks


func add_spark() -> void:
	var before := stage()
	sparks += 1
	level_score += SPARK_POINTS
	var after := stage()
	if after > before:
		stage_changed.emit(after)


## Puntos por vencer a un enemigo.
func add_kill(points: int) -> void:
	kills += 1
	level_score += points


func quit_game() -> void:
	get_tree().quit()


## Estilo de botones con la paleta del GDD (menús y pausa).
func style_button(b: Button, font_size: int = 10) -> void:
	var normal := StyleBoxFlat.new()
	normal.bg_color = Color("2E3A59")
	normal.border_color = Color("F4A62A")
	normal.set_border_width_all(1)
	normal.set_corner_radius_all(2)
	normal.content_margin_top = 3
	normal.content_margin_bottom = 3
	var hover: StyleBoxFlat = normal.duplicate()
	hover.bg_color = Color("3d4d73")
	var pressed: StyleBoxFlat = normal.duplicate()
	pressed.bg_color = Color("1B1F3B")
	var focus: StyleBoxFlat = normal.duplicate()
	focus.bg_color = Color("3d4d73")
	focus.border_color = Color("FFF3C4")
	focus.set_border_width_all(2)
	b.add_theme_stylebox_override("normal", normal)
	b.add_theme_stylebox_override("hover", hover)
	b.add_theme_stylebox_override("pressed", pressed)
	b.add_theme_stylebox_override("focus", focus)
	b.add_theme_color_override("font_color", Color("FFF3C4"))
	b.add_theme_color_override("font_hover_color", Color.WHITE)
	b.add_theme_font_size_override("font_size", font_size)


## Penalización por choque con enemigo o fuego: se pierde una parte del puntaje del nivel.
## Devuelve los puntos perdidos. (Caer al vacío NO descuenta puntos, según el GDD.)
func apply_hit_penalty() -> int:
	var lost := int(level_score * PENALTY_RATIO / 10.0) * 10
	level_score -= lost
	return lost


## Resta una vida. Devuelve true si ya no quedan (fin del juego).
func lose_life() -> bool:
	lives -= 1
	lives_changed.emit(max(lives, 0))
	return lives <= 0


## Cierra el nivel: suma bonus, actualiza el mejor puntaje y lo guarda. Devuelve true si es récord.
func finish_level() -> bool:
	level_score += LEVEL_BONUS
	total_score += level_score
	var record: bool = level_score > int(best_scores[current_level])
	if record:
		best_scores[current_level] = level_score
		_save_scores()
	return record


func _load_scores() -> void:
	var cfg := ConfigFile.new()
	if cfg.load(SAVE_PATH) == OK:
		for i in best_scores.size():
			best_scores[i] = int(cfg.get_value("mejores", "nivel_%d" % i, 0))


func _save_scores() -> void:
	if autotest:
		return
	var cfg := ConfigFile.new()
	for i in best_scores.size():
		cfg.set_value("mejores", "nivel_%d" % i, best_scores[i])
	cfg.save(SAVE_PATH)


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


func _loop_stream(file: String) -> AudioStreamWAV:
	var s: AudioStreamWAV = load(AUDIO + file + ".wav")
	s.loop_mode = AudioStreamWAV.LOOP_FORWARD
	s.loop_begin = 0
	s.loop_end = s.data.size() / 2   # 16 bits, mono -> 2 bytes por muestra
	return s


## Reproduce la pista base y, si existe, su capa de peligro (misma duración, quedan sincronizadas).
func play_music(track: String) -> void:
	if autotest or track == music_name:
		return
	music_name = track
	_music.stream = _loop_stream(track)
	_music.play()
	_danger.stop()
	_danger_value = 0.0
	_danger_target = 0.0
	_danger.volume_db = -80.0
	if ResourceLoader.exists(AUDIO + track + "_danger.wav"):
		_danger.stream = _loop_stream(track + "_danger")
		_danger.play()


func stop_music() -> void:
	music_name = ""
	_music.stop()
	_danger.stop()


## 0 = tranquilo, 1 = Embra está junto a enemigos o fuego activo (la música se intensifica).
func set_danger(level: float) -> void:
	_danger_target = clampf(level, 0.0, 1.0)


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


func _process(delta: float) -> void:
	# Mezcla suave de la capa de peligro
	_danger_value = move_toward(_danger_value, _danger_target, delta * 1.5)
	if _danger.playing:
		_danger.volume_db = linear_to_db(maxf(_danger_value, 0.0001)) - 5.0
	# Captura de pantalla (solo con --shot)
	if shot_path == "":
		return
	_frame_count += 1
	if _frame_count == shot_frames:
		var img := get_viewport().get_texture().get_image()
		img.save_png(shot_path)
		get_tree().quit()
