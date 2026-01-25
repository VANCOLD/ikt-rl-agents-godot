extends Area2D

signal door_opened

# Define the next scene to load in the inspector
var next_scene = "res://Scenes/Levels/" + self.name + ".tscn"
var aiController = null

# Load next level scene when player collide with level finish door.
func _on_body_entered(body):
	if body.is_in_group("Player"):
		aiController.reward += 150;
		get_tree().call_group("Player", "death_tween") # death_tween is called here just to give the feeling of player entering the door.
		AudioManager.level_complete_sfx.play()
		
		emit_signal("door_opened")
