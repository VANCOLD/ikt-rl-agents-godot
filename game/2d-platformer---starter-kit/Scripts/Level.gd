extends Node2D

var CoinScene = preload("res://Scenes/Prefabs/Coin.tscn")
var AiController = preload("res://Testcases/AiController/ai_controller_2d.tscn")
@onready var spawnPoint : Node2D = $Level/SpawnPoint;
var aiController = null

func _ready() -> void:

	# This is important since we predefine a player prefab with the testcase!
	# The testcase manager then injects that player
	if $TestcaseManager.testcase:
		var player_instance = $TestcaseManager.testcase.instantiate()
		player_instance.spawn_point = $Level/SpawnPoint
		player_instance.global_position = $Level/SpawnPoint.global_position
		
		# Since we inject a prefab we have to do all that manual setup otherwise
		# the whole level will go out of sync and generated nil errors!
		# the coins and door are seperate and need the controller to send rewards
		# the traps are a built in function inside the player!
		var camera = Camera2D.new()
		player_instance.add_child(camera)
		add_child(player_instance)
		aiController = player_instance.aiController
		var door = $LevelFinishDoor
		door.aiController = aiController 
		door.connect("door_opened", Callable(self, "_on_door_opened"))
		spawn_coins(aiController)


func spawn_coins(aiController):
	print("Clearing old coins")
	for child in $Coins.get_children():
		print(child)
		# Only remove actual coins (Node2D instances that are not spawn points)
		if !child.name.begins_with("Coin"):
			print("deleting coin: " + child.name);
			child.queue_free()
	
	print("Spawning coins")
	for spawn_point in $Coins.get_children():
		if spawn_point is Node2D and spawn_point.name.begins_with("Coin"):
			print("Spawning coin at:", spawn_point.global_position)
			var coin = CoinScene.instantiate()
			coin.position = spawn_point.global_position
			coin.aiController = aiController
			$Coins.add_child(coin)
			
func _on_door_opened():
	call_deferred("spawn_coins", aiController)

func getSpawnPoint() -> Node2D:
		return spawnPoint
