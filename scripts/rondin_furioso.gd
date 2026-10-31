extends Rondin
class_name RondinFurioso
## RondinFurioso.gd -- Rondín furioso: más rápido y, si Embra está a la vista en su misma plataforma,
## carga contra él en línea recta. Hay que esquivar la embestida saltando o vencerlo antes.

var charging := false
var _charge_time := 0.0
var _cooldown := 0.0


func _ready() -> void:
	sheet_file = "furioso_sheet.png"
	speed = 38.0
	points = 100
	super._ready()


func _make_sprite_frames() -> SpriteFrames:
	return Global.make_frames(sheet_file, frame_w, frame_h, {
		"walk": {"frames": [0, 1], "fps": 6.0},
		"charge": {"frames": [2], "fps": 1.0},
	})


func _speed_multiplier() -> float:
	return 2.6 if charging else 1.0


func _behave(delta: float) -> void:
	_cooldown = max(_cooldown - delta, 0.0)
	if charging:
		_charge_time -= delta
		if _charge_time <= 0.0:
			charging = false
			_cooldown = 1.6
			sprite.play("walk")
	elif _cooldown <= 0.0 and level != null and level.player != null and not level.player.dead:
		var dx := level.player.global_position.x - global_position.x
		var dy := absf(level.player.global_position.y - global_position.y)
		if absf(dx) < 120.0 and dy < 26.0 and int(signf(dx)) == dir:
			charging = true
			_charge_time = 0.7
			sprite.play("charge")
	super._behave(delta)
