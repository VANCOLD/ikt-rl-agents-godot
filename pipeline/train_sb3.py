import argparse
import os
import pathlib
from typing import Callable

from stable_baselines3 import PPO, DQN 
from stable_baselines3.common.callbacks import CheckpointCallback
from stable_baselines3.common.vec_env.vec_monitor import VecMonitor

from godot_rl.core.utils import can_import
from godot_rl.wrappers.onnx.stable_baselines_export import export_model_as_onnx
from pipeline.godot_env_wrapper import SeededGodotEnv

import numpy as np
import csv

if can_import("ray"):
    print("WARNING, stable baselines and ray[rllib] are not compatible")

parser = argparse.ArgumentParser(allow_abbrev=False)
parser.add_argument(
    "--env_path",
    default=None,
    type=str,
    help="The Godot binary to use, do not include for in-editor training",
)
parser.add_argument(
    "--experiment_dir",
    default="logs/sb3",
    type=str,
    help="Directory to store tensorboard logs and checkpoints.",
)
parser.add_argument(
    "--experiment_name",
    default="experiment",
    type=str,
    help="Name of the experiment, used for logging, checkpoints, and tensorboard.",
)
parser.add_argument("--seed", type=int, default=0, help="Random seed for the experiment")
parser.add_argument(
    "--resume_model_path",
    default=None,
    type=str,
    help="Path to a previously saved model or checkpoint to resume training or perform inference.",
)
parser.add_argument(
    "--save_model_path",
    default=None,
    type=str,
    help="Path to save the trained model after training completes (extension .zip).",
)
parser.add_argument(
    "--save_checkpoint_frequency",
    default=None,
    type=int,
    help="If set, saves checkpoints every 'frequency' environment steps.",
)
parser.add_argument(
    "--onnx_export_path",
    default=None,
    type=str,
    help="Path to export ONNX model after training.",
)
parser.add_argument(
    "--timesteps",
    default=1_000_000,
    type=int,
    help="Number of environment steps to train for.",
)
parser.add_argument(
    "--inference",
    default=False,
    action="store_true",
    help="Run inference for --timesteps steps instead of training. Requires --resume_model_path.",
)
parser.add_argument(
    "--linear_lr_schedule",
    default=False,
    action="store_true",
    help="If set, learning rate decreases linearly from initial value to 0 during training.",
)
parser.add_argument(
    "--viz",
    action="store_true",
    help="Show simulation window during training.",
    default=False,
)
parser.add_argument("--speedup", default=1, type=int, help="Physics speedup multiplier for the env")
parser.add_argument(
    "--n_parallel",
    default=1,
    type=int,
    help="Number of parallel Godot env instances (requires --env_path if >1).",
)
parser.add_argument(
    "--alg",
    default="ppo",
    choices=["ppo", "dqn"],
    type=str,
    help="RL algorithm to use: ppo or dqn",
)

# PPO hyperparameters
parser.add_argument("--learning_rate", type=float, default=3e-4, help="Learning rate for PPO/DQN")
parser.add_argument("--ent_coef", type=float, default=1e-4, help="Entropy coefficient for PPO")
parser.add_argument("--n_steps", type=int, default=32, help="Number of steps per PPO rollout")

# DQN hyperparameters
parser.add_argument("--buffer_size", type=int, default=100000, help="Replay buffer size for DQN")
parser.add_argument("--batch_size", type=int, default=64, help="Batch size for DQN")

# Evaluation
parser.add_argument("--eval_episodes", type=int, default=50, help="Number of episodes to evaluate")
parser.add_argument("--eval_only", action="store_true", help="Only perform evaluation, no training")
parser.add_argument("--results_path", type=str, default=None, help="CSV file path to save evaluation results")

args, extras = parser.parse_known_args()


# === Utility functions ===
def handle_onnx_export():
    if args.onnx_export_path is not None:
        path_onnx = pathlib.Path(args.onnx_export_path).with_suffix(".onnx")
        print("Exporting ONNX to: " + os.path.abspath(path_onnx))
        export_model_as_onnx(model, str(path_onnx))


def handle_model_save():
    if args.save_model_path is not None:
        zip_save_path = pathlib.Path(args.save_model_path).with_suffix(".zip")
        print("Saving model to: " + os.path.abspath(zip_save_path))
        model.save(zip_save_path)


def close_env():
    try:
        print("Closing environment")
        env.close()
    except Exception as e:
        print("Exception while closing env: ", e)


def cleanup():
    handle_onnx_export()
    handle_model_save()
    close_env()


def linear_schedule(initial_value: float) -> Callable[[float], float]:
    def func(progress_remaining: float) -> float:
        return progress_remaining * initial_value
    return func


def evaluate(model, env, n_episodes=50, results_path=None):
    episode_rewards = []
    episode_lengths = []

    for ep in range(n_episodes):
        obs = env.reset()
        done = False

        while not done:
            action, _ = model.predict(obs, deterministic=True)
            obs, reward, done, info = env.step(action)

            if "episode" in info[0]:
                episode_rewards.append(info[0]["episode"]["r"])
                episode_lengths.append(info[0]["episode"]["l"])

    mean_r = np.mean(episode_rewards)
    std_r = np.std(episode_rewards)
    mean_l = np.mean(episode_lengths)

    print("=== Evaluation Results ===")
    print("Mean Reward:", mean_r)
    print("Std Reward:", std_r)
    print("Mean Episode Length:", mean_l)

    if results_path:
        with open(results_path, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["reward", "length"])
            for r, l in zip(episode_rewards, episode_lengths):
                writer.writerow([r, l])

    return mean_r, std_r, mean_l


# === Environment setup ===
env = SeededGodotEnv(
    env_path=args.env_path,
    show_window=args.viz,
    seed=args.seed,
    n_parallel=args.n_parallel,
    speedup=args.speedup,
)
env = VecMonitor(env)

# === Model setup ===
if args.resume_model_path is None:
    if args.alg == "ppo":
        learning_rate = 0.0003 if not args.linear_lr_schedule else linear_schedule(0.0003)
        model: PPO = PPO(
            "MultiInputPolicy",
            env,
            ent_coef=args.ent_coef,
            verbose=2,
            n_steps=args.n_steps,
            batch_size=args.n_steps * args.n_parallel,  # ensure divisible
            tensorboard_log=args.experiment_dir,
            learning_rate=learning_rate,
        )
    else:  # DQN
        model = DQN(
            "MultiInputPolicy",
            env,
            learning_rate=args.learning_rate,
            buffer_size=args.buffer_size,
            batch_size=args.batch_size,
            verbose=2,
            tensorboard_log=args.experiment_dir,
            seed=args.seed,
        )
else:
    path_zip = pathlib.Path(args.resume_model_path)
    print("Loading model: " + os.path.abspath(path_zip))
    if args.alg == "ppo":
        model = PPO.load(path_zip, env=env, tensorboard_log=args.experiment_dir)
    else:
        model = DQN.load(path_zip, env=env, tensorboard_log=args.experiment_dir)

path_checkpoint = os.path.join(args.experiment_dir, args.experiment_name + "_checkpoints")
abs_path_checkpoint = os.path.abspath(path_checkpoint)

if args.save_checkpoint_frequency is not None and os.path.isdir(path_checkpoint):
    raise RuntimeError(
        abs_path_checkpoint + " folder already exists. Use a different --experiment_dir or --experiment_name, "
        "or remove the folder containing previous checkpoints."
    )

if args.inference and args.resume_model_path is None:
    raise parser.error("Using --inference requires --resume_model_path to be set.")

if args.env_path is None and args.viz:
    print("Info: Using --viz without --env_path set has no effect, in-editor training will always render.")

# === Execution ===
if args.inference or args.eval_only:
    evaluate(model, env, n_episodes=args.eval_episodes, results_path=args.results_path)
    cleanup()
else:
    print(f"Starting training for {args.timesteps} steps...")
    learn_kwargs = dict(total_timesteps=args.timesteps, tb_log_name=args.experiment_name)

    if args.save_checkpoint_frequency:
        checkpoint_callback = CheckpointCallback(
            save_freq=(args.save_checkpoint_frequency // env.num_envs),
            save_path=path_checkpoint,
            name_prefix=args.experiment_name,
        )
        learn_kwargs["callback"] = checkpoint_callback

    try:
        model.learn(**learn_kwargs)
    except (KeyboardInterrupt, ConnectionError, ConnectionResetError):
        print("Training interrupted, cleaning up...")
    finally:
        cleanup()