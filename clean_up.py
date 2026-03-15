import os
import shutil

ROOT = os.path.dirname(os.path.abspath(__file__))

LOG_DIRS = [
    os.path.join(ROOT, "logs", "tensorboard"),
    os.path.join(ROOT, "logs", "models"),
    os.path.join(ROOT, "logs", "results"),
]

def clear_dir(path):
    if os.path.exists(path):
        print(f"Removing {path} ...")
        shutil.rmtree(path)
        print(f"Removed {path}")
    else:
        print(f"{path} does not exist, skipping.")

def main():
    print("Cleaning up logs, models, and results...")
    for path in LOG_DIRS:
        clear_dir(path)
    for path in LOG_DIRS:
        os.makedirs(path, exist_ok=True)
    print("Cleanup complete. You now have a fresh start.")

if __name__ == "__main__":
    main()