import itertools
import subprocess
import os
import sys
import time
import atexit
import argparse
from pipeline.config import *
import webbrowser

ROOT = os.path.dirname(os.path.abspath(__file__))
TRAIN_SCRIPT = os.path.join(ROOT, "pipeline", "train_sb3.py")
PYTHON = sys.executable
TB_DIR = os.path.join(ROOT, "logs", "tensorboard")
MODELS_DIR = os.path.join(ROOT, "logs", "models")
RESULTS_DIR = os.path.join(ROOT, "logs", "results")

os.makedirs(TB_DIR, exist_ok=True)
os.makedirs(MODELS_DIR, exist_ok=True)
os.makedirs(RESULTS_DIR, exist_ok=True)

def run_cmd(cmd):
    print("\n>> RUN:", " ".join(cmd))
    env = os.environ.copy()
    env["PYTHONPATH"] = ROOT  # Add root so `pipeline` is found
    subprocess.run(cmd, check=True, env=env)

def grid_search(grid):
    keys = list(grid.keys())
    values = list(grid.values())
    for combo in itertools.product(*values):
        yield dict(zip(keys, combo))

def start_tensorboard(logdir):
    print("\nStarting TensorBoard...")
    tb_process = subprocess.Popen(
        [sys.executable, "-m", "tensorboard.main", "--logdir", logdir, "--port", "6006"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )

    url = "http://localhost:6006"
    print(f"TensorBoard running at {url}")

    try:
        webbrowser.open(url)
    except Exception as e:
        print(f"Failed to open browser automatically: {e}")

    def stop():
        print("Stopping TensorBoard...")
        tb_process.terminate()

    atexit.register(stop)
    time.sleep(2)
    return tb_process

def run_pipeline(levels, timesteps, hyperparams, algs, n_parallel=1):
    for level in levels:
        for seed in SEEDS:
            for alg in algs:
                grid = PPO_GRID if alg == "ppo" else DQN_GRID
                for params in grid_search(grid):
                    for k, v in hyperparams.items():
                        params[k] = v

                    if alg == "ppo":
                        exp_name = f"ppo_lr{params['learning_rate']}_ent{params['ent_coef']}_steps{params['n_steps']}_s{seed}"
                    else:
                        exp_name = f"dqn_lr{params['learning_rate']}_buf{params['buffer_size']}_batch{params['batch_size']}_s{seed}"

                    model_path = os.path.join(MODELS_DIR, exp_name + ".zip")
                    results_csv = os.path.join(RESULTS_DIR, exp_name + ".csv")

                    train_cmd = [
                        PYTHON, TRAIN_SCRIPT,
                        "--alg", alg,
                        "--env_path", level,
                        "--seed", str(seed),
                        "--timesteps", str(timesteps),
                        "--experiment_dir", os.path.join(TB_DIR, alg),
                        "--experiment_name", exp_name,
                        "--save_model_path", model_path,
                        "--n_parallel", str(n_parallel),
                    ]

                    if alg == "ppo":
                        train_cmd += [
                            "--learning_rate", str(params["learning_rate"]),
                            "--ent_coef", str(params["ent_coef"]),
                            "--n_steps", str(params["n_steps"]),
                        ]
                    else:
                        train_cmd += [
                            "--learning_rate", str(params["learning_rate"]),
                            "--buffer_size", str(params["buffer_size"]),
                            "--batch_size", str(params["batch_size"]),
                        ]

                    run_cmd(train_cmd)

                    eval_cmd = [
                        PYTHON, TRAIN_SCRIPT,
                        "--alg", alg,
                        "--env_path", level,
                        "--resume_model_path", model_path,
                        "--eval_only",
                        "--eval_episodes", str(EVAL_EPISODES),
                        "--results_path", results_csv,
                        "--n_parallel", str(n_parallel),
                    ]
                    run_cmd(eval_cmd)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--fast_test", action="store_true", help="Run fast test pipeline")
    parser.add_argument("--fast_levels", nargs="+", default=None)
    parser.add_argument("--full_test", action="store_true", help="Run full experiment pipeline")
    parser.add_argument("--full_levels", nargs="+", default=None)
    parser.add_argument("--timesteps", type=int, default=TIMESTEPS)
    parser.add_argument("--learning_rate", type=float, default=None)
    parser.add_argument("--ent_coef", type=float, default=None)
    parser.add_argument("--n_steps", type=int, default=None)
    parser.add_argument("--n_parallel", type=int, default=1)
    args = parser.parse_args()

    # Start TensorBoard once for all experiments
    start_tensorboard(TB_DIR)

    if args.fast_test:
        levels = args.fast_levels if args.fast_levels else SCENARIOS
        hyperparams = {}
        if args.learning_rate: hyperparams["learning_rate"] = args.learning_rate
        if args.ent_coef: hyperparams["ent_coef"] = args.ent_coef
        if args.n_steps: hyperparams["n_steps"] = args.n_steps
        run_pipeline(levels, timesteps=args.timesteps, hyperparams=hyperparams, algs=["ppo"], n_parallel=args.n_parallel)

    if args.full_test:
        levels = args.full_levels if args.full_levels else SCENARIOS
        hyperparams = {}
        if args.learning_rate: hyperparams["learning_rate"] = args.learning_rate
        if args.ent_coef: hyperparams["ent_coef"] = args.ent_coef
        if args.n_steps: hyperparams["n_steps"] = args.n_steps
        run_pipeline(levels, timesteps=args.timesteps, hyperparams=hyperparams, algs=["ppo","dqn"], n_parallel=args.n_parallel)