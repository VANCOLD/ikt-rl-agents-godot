extends AIController2D

var move: float = 0.0;
var jump: float = 0.0;
@onready var player = $".."
@onready var goal: Node2D  = $"../../LevelFinishDoor"

func get_obs() -> Dictionary:
	var obs := [
		player.position.x,
		player.position.y,
		goal.position.x,
		goal.position.y
	]
	return {"obs": obs}

func get_reward() -> float:	
	return reward
	
func get_action_space() -> Dictionary:
	return {
		"move" : {
			"size": 1,
			"action_type": "continuous"
		},
		"jump" : {
			"size": 1,
			"action_type": "continuous"
		}
	}
	
func set_action(action) -> void:	
	move = action["move"][0];
	jump = action["jump"][0];
