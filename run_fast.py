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

def main():
    print("Running fast test pipeline on levels:", FAST_LEVELS)
    
    for level in FAST_LEVELS:
        for params in FAST_HYPERS:
            cmd = (
                f'"{PYTHON}" -m pipeline.train_sb3'
                f' --alg ppo'
                f' --env_path "{level}"'
                f' --seed 0'
                f' --timesteps {TIMESTEPS_FAST}'
                f' --learning_rate {params["learning_rate"]}'
                f' --ent_coef {params["ent_coef"]}'
                f' --n_steps {params["n_steps"]}'
                f' --n_parallel 2'
            )
            print(">> RUN:", cmd)
            subprocess.run(cmd, shell=True)

if __name__ == "__main__":
    main()