# 🏰 Wumpus World - Dungeon Adventure

A visually stunning dungeon-crawler implementation of the classic Wumpus World AI problem, built with Pygame. Features a cave-themed parallax background, humanoid adventurer character, menacing demon monsters, and atmospheric visual effects.

![Python](https://img.shields.io/badge/python-3.8+-blue.svg)
![Pygame](https://img.shields.io/badge/pygame-2.0+-green.svg)
![License](https://img.shields.io/badge/license-MIT-blue.svg)

## ✨ Features

### 🎮 Gameplay
- **Classic Wumpus World mechanics** with modern visual presentation
- **Dynamic world size** - Adjustable grid from 4×4 to 8×8
- **Smart AI elements** - Percepts (Stench, Breeze, Glitter) warn of nearby dangers
- **Strategic combat** - Collect arrows to defeat the Wumpus
- **Score tracking** - Earn points for gold, kills, and efficient exploration

### 🎨 Visual Enhancements
- **Fullscreen support** - Press F11 to toggle fullscreen mode
- **Resizable window** - Dynamic layout that scales with window size
- **Cave-themed parallax background** - Stalactites, stalagmites, and atmospheric vignette
- **Particle system** - Floating dust motes for immersive atmosphere
- **Humanoid player character** - Adventurer with torch, walking animation, and directional facing
- **Menacing Wumpus** - Demon/beast with glowing eyes, breathing animation, and red aura
- **Dead Wumpus visual** - Collapsed body with arrow and blood splatter when killed
- **Enhanced tiles** - Rich stone textures with cracks, deep swirling fog
- **Visual effects** - Torch glow, dramatic gold sparkle, abyssal pits, percept halos

### 🎯 Controls
- **WASD / Arrow Keys** - Move your character
- **Enter / Space** - Shoot arrow in facing direction
- **R** - Restart game
- **H** - Toggle help overlay
- **F11** - Toggle fullscreen
- **ESC** - Exit game (or close help)

## 🚀 Installation

### Prerequisites
- Python 3.8 or higher
- pip (Python package installer)

### Setup

1. **Clone the repository**
```bash
git clone https://github.com/yourusername/wumpus-world-main-gui.git
cd wumpus-world-main-gui
```

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

3. **Run the game**
```bash
python wumpus_gui.py
```

## 🌐 Play in Browser (GitHub Pages)

**Want to play without installing anything?** Deploy to GitHub Pages!

### Quick Deploy Steps:

1. **Create a GitHub repository** named `wumpus-world-main-gui`

2. **Push your code:**
```bash
git init
git add .
git commit -m "Deploy Wumpus World to GitHub Pages"
git remote add origin https://github.com/YOUR_USERNAME/wumpus-world-main-gui.git
git push -u origin main
```

3. **Enable GitHub Pages:**
   - Go to repository Settings → Pages
   - Source: `main` branch, `/ (root)` folder
   - Click Save

4. **Play at:** `https://YOUR_USERNAME.github.io/wumpus-world-main-gui/`

The game runs entirely in your browser using **Pygbag** - no installation needed!

📖 **Detailed instructions:** See [DEPLOYMENT.md](DEPLOYMENT.md)

## 🎲 How to Play

### Objective
Find the gold treasure hidden in the dungeon and return to the starting position (bottom-left corner) without dying!

### Game Elements

| Element | Description |
|---------|-------------|
| 👤 **Player** | You! An adventurer exploring the dungeon |
| 👹 **Wumpus** | Deadly monster - kill with arrow or avoid |
| ✨ **Gold** | The treasure you seek |
| 🕳️ **Pit** | Bottomless pit - instant death |
| 🏹 **Arrow** | Weapon pickup - shoot or auto-defend |

### Percepts (Warnings)

| Percept | Icon | Meaning |
|---------|------|---------|
| **Stench** | 💨 | Wumpus is in an adjacent cell |
| **Breeze** | 🌀 | Pit is in an adjacent cell |
| **Glitter** | ✨ | Gold is in your current cell |

### Strategy Tips
1. **Use percepts wisely** - They tell you what's nearby
2. **Collect the arrow** - You'll need it to defeat the Wumpus
3. **Map the dungeon** - Remember where dangers are
4. **Plan your route** - Find the gold and a safe path back
5. **Auto-defense** - If you have an arrow and walk into the Wumpus, you'll automatically kill it!

## 📁 Project Structure

```
wumpus-world-main-gui/
├── wumpus_gui.py          # Main GUI with Pygame rendering
├── wumpus_game.py         # Game engine and logic
├── requirements.txt       # Python dependencies
├── README.md             # This file
└── .gitignore            # Git ignore rules
```

## 🛠️ Technical Details

### Architecture
- **Game Engine** (`wumpus_game.py`) - Pure Python logic, no GUI dependencies
- **GUI Layer** (`wumpus_gui.py`) - Pygame-based visual interface
- **Separation of Concerns** - Engine can be used independently for AI experiments

### Key Technologies
- **Pygame** - Graphics, input handling, and game loop
- **Python 3.8+** - Modern Python features
- **Object-oriented design** - Clean, maintainable code structure

## 🎨 Customization

### Adjusting Colors
Edit the color constants at the top of `wumpus_gui.py`:
```python
COL_PLAYER_TUNIC = (80, 60, 140)  # Player's outfit color
COL_WUMPUS = (140, 30, 30)        # Wumpus body color
COL_CAVE_DEEP = (25, 20, 15)      # Cave background
```

### Changing World Size
Use the in-game slider or modify the default in `wumpus_gui.py`:
```python
self.world_size = 4  # Default grid size (4-8)
```

## 🐛 Troubleshooting

### Game won't start
- Ensure Python 3.8+ is installed: `python --version`
- Install dependencies: `pip install -r requirements.txt`
- Try: `python3 wumpus_gui.py` if `python` doesn't work

### Performance issues
- Reduce world size using the in-game slider
- Close other applications
- Update your graphics drivers

### Display issues
- Try toggling fullscreen with F11
- Resize the window manually
- Check your display scaling settings

## 📝 License

This project is licensed under the MIT License - see below for details:

```
MIT License

Copyright (c) 2026 Wumpus World Contributors

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

## 🤝 Contributing

Contributions are welcome! Feel free to:
- Report bugs
- Suggest new features
- Submit pull requests
- Improve documentation

## 🙏 Acknowledgments

- Based on the classic **Wumpus World** problem from AI textbooks
- Built with **Pygame** - the excellent Python game development library
- Inspired by classic dungeon-crawler games

## 📧 Contact

For questions or feedback, please open an issue on GitHub.

---

**Enjoy exploring the dungeon! 🏰✨**
