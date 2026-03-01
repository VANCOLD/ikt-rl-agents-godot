import itertools
import subprocess
import os
import sys
import argparse
from pipeline.config import *

# root directory of project
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TRAIN_SCRIPT = os.path.join(ROOT, "pipeline" ,"train_sb3.py")
PYTHON = sys.executable  # ensures same python environment
    
# === CLI arguments ===
parser = argparse.ArgumentParser()
parser.add_argument("--fast_test", action="store_true", help="Enable fast test mode")
parser.add_argument(
    "--fast_levels",
    nargs="+",
    default=None,
    help="List of level executables to test in fast mode, e.g. ../bin/level1.exe ../bin/level2.exe",
)
args, _ = parser.parse_known_args()

FAST_TRAIN_ARGS = {
    "n_parallel": 2,              # number of Godot envs in parallel
    "fast_levels": ["../bin/level1.exe"],  # default fast test level(s)
    "fast_timesteps": 50_000,     # smaller timesteps for quick testing
    "fast_eval_episodes": 5,      # fewer evaluation episodes for fast test
}


def run_cmd(cmd):
    print(">> RUN:", cmd)
    result = subprocess.run(cmd, shell=True)
    if result.returncode != 0:
        print("!! Command failed with code", result.returncode)
    print()


def grid_search(grid):
    keys = list(grid.keys())
    values = list(grid.values())
    for combo in itertools.product(*values):
        yield dict(zip(keys, combo))


def run_pipeline():
    # ensure results folder exists
    os.makedirs(os.path.join(ROOT, "results"), exist_ok=True)

    # determine which scenarios to use
    if args.fast_test:
        scenarios_to_use = args.fast_levels if args.fast_levels else FAST_TRAIN_ARGS["fast_levels"]
        timesteps = FAST_TRAIN_ARGS["fast_timesteps"]
        eval_episodes = FAST_TRAIN_ARGS["fast_eval_episodes"]
        n_parallel = FAST_TRAIN_ARGS["n_parallel"]
    else:
        scenarios_to_use = SCENARIOS
        timesteps = TIMESTEPS
        eval_episodes = EVAL_EPISODES
        n_parallel = 1

    for scenario in scenarios_to_use:
        scenario_path = os.path.abspath(scenario)

        for seed in SEEDS:

            # PPO experiments
            for params in grid_search(PPO_GRID):

                exp_name = f"ppo_s{seed}_lr{params['learning_rate']}_ent{params['ent_coef']}_steps{params['n_steps']}"
                model_path = os.path.join(ROOT, "results", exp_name + ".zip")
                results_csv = os.path.join(ROOT, "results", exp_name + ".csv")

                # TRAIN
                train_cmd = (
                    f"{PYTHON} {TRAIN_SCRIPT}"
                    f" --alg ppo"
                    f" --env_path \"{scenario_path}\""
                    f" --seed {seed}"
                    f" --timesteps {timesteps}"
                    f" --learning_rate {params['learning_rate']}"
                    f" --ent_coef {params['ent_coef']}"
                    f" --n_steps {params['n_steps']}"
                    f" --experiment_name {exp_name}"
                    f" --save_model_path \"{model_path}\""
                    f" --viz"
                    f" --n_parallel {n_parallel}"
                )
                run_cmd(train_cmd)

                # EVALUATE
                eval_cmd = (
                    f"{PYTHON} {TRAIN_SCRIPT}"
                    f" --alg ppo"
                    f" --env_path \"{scenario_path}\""
                    f" --seed {seed}"
                    f" --resume_model_path \"{model_path}\""
                    f" --eval_only"
                    f" --eval_episodes {eval_episodes}"
                    f" --results_path \"{results_csv}\""
                    f" --viz"
                    f" --n_parallel {n_parallel}"
                )
                run_cmd(eval_cmd)

            # DQN experiments
            for params in grid_search(DQN_GRID):

                exp_name = f"dqn_s{seed}_lr{params['learning_rate']}_buf{params['buffer_size']}_batch{params['batch_size']}"
                model_path = os.path.join(ROOT, "results", exp_name + ".zip")
                results_csv = os.path.join(ROOT, "results", exp_name + ".csv")

                train_cmd = (
                    f"{PYTHON} {TRAIN_SCRIPT}"
                    f" --alg dqn"
                    f" --env_path \"{scenario_path}\""
                    f" --seed {seed}"
                    f" --timesteps {timesteps}"
                    f" --learning_rate {params['learning_rate']}"
                    f" --buffer_size {params['buffer_size']}"
                    f" --batch_size {params['batch_size']}"
                    f" --experiment_name {exp_name}"
                    f" --save_model_path \"{model_path}\""
                    f" --viz"
                    f" --n_parallel {n_parallel}"
                )
                run_cmd(train_cmd)

                eval_cmd = (
                    f"{PYTHON} {TRAIN_SCRIPT}"
                    f" --alg dqn"
                    f" --env_path \"{scenario_path}\""
                    f" --seed {seed}"
                    f" --resume_model_path \"{model_path}\""
                    f" --eval_only"
                    f" --eval_episodes {eval_episodes}"
                    f" --results_path \"{results_csv}\""
                    f" --viz"
                    f" --n_parallel {n_parallel}"
                )
                run_cmd(eval_cmd)


if __name__ == "__main__":
    run_pipeline()