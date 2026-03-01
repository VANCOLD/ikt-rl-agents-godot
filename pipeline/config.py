import os

SCENARIOS = [
    os.path.abspath(os.path.join(os.path.dirname(__file__), "../bin/level1.exe"))
]

SEEDS = [0, 1, 2]

PPO_GRID = {
    "learning_rate": [3e-4, 1e-4],
    "ent_coef": [1e-4, 1e-3],
    "n_steps": [32, 64],
}

DQN_GRID = {
    "learning_rate": [1e-3, 5e-4],
    "buffer_size": [100000, 200000],
    "batch_size": [64],
}

TIMESTEPS = 1_000_000 # default value in the system
EVAL_EPISODES = 50