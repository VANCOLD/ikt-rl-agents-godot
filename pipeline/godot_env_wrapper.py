from godot_rl.wrappers.stable_baselines_wrapper import StableBaselinesGodotEnv

class SeededGodotEnv(StableBaselinesGodotEnv):
    def seed(self, seed=None):
        self.env_seed = seed  # store internally for reference
        return [seed]