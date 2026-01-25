extends AIController2D

# Since we define the Enum as type it becomes a dropdown!
enum Alg { PPO, DQN }
@export var alg: Alg = Alg.PPO

# Simple bool checks if it is either ppo or dqn
func is_ppo() -> bool:
	return alg == Alg.PPO

func is_dqn() -> bool:
	return alg == Alg.DQN

# Agent state
var move: float = 0.0
var jump: float = 0.0
@onready var player = $".."
@onready var goal: Node2D  = $"../../LevelFinishDoor"

# Observation for RL
func get_obs() -> Dictionary:
	var obs := [
		player.position.x,
		player.position.y,
		goal.position.x,
		goal.position.y
	]
	return {"obs": obs}

# Reward
func get_reward() -> float:	
	return reward

func get_action_space() -> Dictionary:
	if is_ppo():
		print("using ppo")
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
	else:
		print("using dqn")
		# 6 discrete actions: stay, left, right, jump, left+jump, right+jump
		return {
			"action": 6
		}

func set_action(action) -> void:
	if is_ppo():
		move = action["move"][0]
		jump = action["jump"][0]
	elif is_dqn():
		# DQN gives a single integer 0..5
		move = 0.0
		jump = 0.0
		match action["action"]:
			0: pass
			1: move = -1.0
			2: move = 1.0
			3: jump = 1.0
			4: move = -1.0; jump = 1.0
			5: move = 1.0; jump = 1.0
