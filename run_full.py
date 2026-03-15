import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.abspath(__file__))
PYTHON = sys.executable

FULL_LEVELS = [
    os.path.join(ROOT, "bin", "level1.exe"),
    os.path.join(ROOT, "bin", "level2.exe"),
    os.path.join(ROOT, "bin", "level3.exe"),
]

FULL_HYPERS = [
    {"learning_rate": 0.0003, "ent_coef": 0.0001, "n_steps": 32},
    {"learning_rate": 0.0001, "ent_coef": 0.001, "n_steps": 64},
]

TIMESTEPS_FULL = 1_000_000
RUNNER_SCRIPT = os.path.join(ROOT, "runner.py")  # general pipeline runner


def main():
    print("Running full experiment pipeline via runner.py on levels:", FULL_LEVELS)

    for level in FULL_LEVELS:
        for params in FULL_HYPERS:
            cmd = [
                PYTHON,
                RUNNER_SCRIPT,
                "--full_test",
                "--full_levels", level,
                "--timesteps", str(TIMESTEPS_FULL),
                "--learning_rate", str(params["learning_rate"]),
                "--ent_coef", str(params["ent_coef"]),
                "--n_steps", str(params["n_steps"]),
                "--n_parallel", "2",
            ]

            print(">> RUN:", " ".join(cmd))
            subprocess.run(cmd, check=True)


if __name__ == "__main__":
    main()