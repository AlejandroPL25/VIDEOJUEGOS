extends Area2D
class_name Spike
## Spike.gd -- Púas: lastiman a Embra al tocarlas.

var theme := 0


func _ready() -> void:
	collision_layer = 0
	collision_mask = 2
	var spr := Sprite2D.new()
	var at := AtlasTexture.new()
	at.atlas = Global.tex("spikes.png")
	at.region = Rect2(theme * 16, 0, 16, 16)
	spr.texture = at
	add_child(spr)
	var shape := RectangleShape2D.new()
	shape.size = Vector2(12, 7)
	var cs := CollisionShape2D.new()
	cs.shape = shape
	cs.position = Vector2(0, 4)
	add_child(cs)


func _physics_process(_delta: float) -> void:
	for b in get_overlapping_bodies():
		if b is Player:
			b.hurt()
