# 2D Platformer Starter Kit

A Godot-based 2D platformer starter kit to help you quickly prototype and build platformer games.

---

## Installation

1. **Clone the repository**
```bash
git clone https://github.com/yourusername/2d-platformer---starter-kit.git
```

2. **Open in Godot**
- Launch Godot Engine (version 4.x recommended)
- Open the cloned project folder

3. **Install Python dependencies**
```bash
pip install -r requirements.txt
```
- This will include `rl-godot-agents` and any other Python packages needed.

4. **Optional: Set up Git ignore**
- Make sure `.gitignore` is configured to ignore:
  - `logs/`
  - `*.tmp`
  - `.import/`

---

## Usage

- Open the `Scenes/Levels/Level_01.tscn` scene to start prototyping your first level.
- Player controls are preconfigured:
  - Move: **Arrow Keys / A,D**
  - Jump: **Space**
- To add test cases or different player behaviors, see the `Testcases` folder and `TestcaseManager.gd`.
- Run the scene by pressing **F5** in Godot.

### AI Integration
- Ensure `rl_godot_agents` is installed via `requirements.txt`
- You can run training scripts in Python that connect to the Godot project for reinforcement learning experiments.
- See the `ai` folder for example Python scripts using `rl_godot_agents`.

---

## Credits

- **Original Project:** [Your Name or Source]
- **Assets & Audio:** [Sources or "All assets are free for commercial use"]
- **Godot Engine:** [https://godotengine.org](https://godotengine.org)
- **RL Godot Agents:** [https://github.com/Calimucho/rl_godot_agents](https://github.com/Calimucho/rl_godot_agents)

