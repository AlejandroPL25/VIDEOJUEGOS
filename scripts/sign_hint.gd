extends Area2D
class_name SignHint
## SignHint.gd -- Letrero: muestra un consejo cuando Embra se acerca.

var text := ""
var label: Label


func _ready() -> void:
	collision_layer = 0
	collision_mask = 2
	var spr := Sprite2D.new()
	spr.texture = Global.tex("sign.png")
	add_child(spr)
	var shape := RectangleShape2D.new()
	shape.size = Vector2(36, 20)
	var cs := CollisionShape2D.new()
	cs.shape = shape
	add_child(cs)

	label = Label.new()
	label.text = text
	label.add_theme_font_size_override("font_size", 8)
	label.add_theme_color_override("font_color", Color(1, 0.95, 0.8))
	label.add_theme_color_override("font_outline_color", Color(0.1, 0.05, 0.12))
	label.add_theme_constant_override("outline_size", 3)
	label.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	label.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	label.custom_minimum_size = Vector2(150, 0)
	label.size = Vector2(150, 30)
	label.position = Vector2(-75, -48)
	label.visible = false
	label.z_index = 30
	add_child(label)
	body_entered.connect(func(b: Node) -> void:
		if b is Player:
			label.visible = true)
	body_exited.connect(func(b: Node) -> void:
		if b is Player:
			label.visible = false)
	z_index = -1
