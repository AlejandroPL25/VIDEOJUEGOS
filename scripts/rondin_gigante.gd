extends Rondin
class_name RondinGigante
## RondinGigante.gd -- Rondín gigante: lento pero resistente (2 de vida). Un pisotón lo golpea y rebota,
## y hacen falta dos golpes para vencerlo. Vale más puntos.


func _ready() -> void:
	sheet_file = "gigante_sheet.png"
	frame_w = 24
	frame_h = 24
	hitbox = Vector2(18, 18)
	body_offset = Vector2(0, 3)
	speed = 20.0
	hp = 2
	points = 200
	stomp_line = 8.0
	super._ready()
