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

def main():
    print("Running full experiment pipeline on levels:", FULL_LEVELS)
    
    for level in FULL_LEVELS:
        for params in FULL_HYPERS:
            cmd = (
                f'"{PYTHON}" -m pipeline.train_sb3'
                f' --alg ppo'
                f' --env_path "{level}"'
                f' --seed 0'
                f' --timesteps {TIMESTEPS_FULL}'
                f' --learning_rate {params["learning_rate"]}'
                f' --ent_coef {params["ent_coef"]}'
                f' --n_steps {params["n_steps"]}'
                f' --n_parallel 2'
            )
            print(">> RUN:", cmd)
            subprocess.run(cmd, shell=True)

if __name__ == "__main__":
    main()