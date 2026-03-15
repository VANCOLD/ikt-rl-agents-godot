import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.abspath(__file__))
PYTHON = sys.executable

FAST_LEVELS = [
    os.path.join(ROOT, "bin", "level1.exe"),
]

FAST_HYPERS = [
    {"learning_rate": 0.0003, "ent_coef": 0.0001, "n_steps": 32},
    {"learning_rate": 0.0001, "ent_coef": 0.001, "n_steps": 32},
]

TIMESTEPS_FAST = 50_000
RUNNER_SCRIPT = os.path.join(ROOT, "runner.py")  # general pipeline runner


def main():
    print("Running fast test pipeline via runner.py on levels:", FAST_LEVELS)

    for level in FAST_LEVELS:
        for params in FAST_HYPERS:
            cmd = [
                PYTHON,
                RUNNER_SCRIPT,
                "--fast_test",
                "--fast_levels", level,
                "--timesteps", str(TIMESTEPS_FAST),
                "--learning_rate", str(params["learning_rate"]),
                "--ent_coef", str(params["ent_coef"]),
                "--n_steps", str(params["n_steps"]),
                "--n_parallel", "2",
            ]

            print(">> RUN:", " ".join(cmd))
            subprocess.run(cmd, check=True)


if __name__ == "__main__":
    main()