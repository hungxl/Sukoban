# 🎮 Sokoban Game

A feature-rich Sokoban puzzle game implemented with the **Textual** library in Python, featuring procedural level generation and advanced UI.

## ✨ Features

### Core Gameplay
- **Rich Text-based UI** using the Textual library with colorful graphics
- **Procedural Level Generation** using advanced ProceduralSokoban algorithm
- **Dynamic Level Creation** - Generate new levels on-demand during gameplay
- **Score Tracking** with moves, pushes, and completion detection
- **Interactive Pause Menu** with game controls and help
- **Multiple Input Methods** - Keyboard and arrow key support

### Advanced Features
- **Template-based Level Generation** with 8 different room templates
- **Smart Box-Goal Placement** ensuring solvable puzzles
- **Enhanced Visual Rendering** with Unicode symbols and colors
- **Comprehensive Logging** with performance monitoring
- **Error Recovery** and graceful degradation

## 🎯 Game Elements

### Symbols & Visual Representation

| Element | Symbol | Display | Description |
|---------|--------|---------|-------------|
| Floor | ` ` (space) | `·` (white) | Empty walkable space |
| Wall | `#` | `█` (blue) | Impassable barrier |
| Player | `@` | `@` (yellow) | The worker character |
| Dock | `.` | `·` (green) | Target location for boxes |
| Box | `$` | `▓` (red) | Pushable box |
| Box on Dock | `*` | `▓` (red on green) | Box correctly placed |
| Player on Dock | `+` | `@` (yellow on green) | Player standing on target |

## 🎮 Controls

### Movement
- **W** / **↑** - Move up
- **S** / **↓** - Move down  
- **A** / **←** - Move left
- **D** / **→** - Move right

### Game Controls
- **P** - Pause/Resume game
- **R** - Reset current level
- **N** - Generate new level (procedural)
- **Q** - Quit game

## 🚀 Installation & Usage

### Prerequisites
- Python 3.12+
- uv package manager
- Windows/Linux/macOS compatible

### Quick Start
```bash
# Clone the repository
git clone <repository-url>
cd Sukoban

# Install dependencies
uv sync

# Run the game
uv run python main.py
```

### Alternative Demos
```bash
# Simple text-based demo
uv run python demo.py

# Test level generation
uv run python test_level_generator.py
```
## 🏗️ Project Architecture

### Core Components
```
Sukoban/
├── main.py              # Main game application with Textual UI
├── game_manager.py      # Game logic and state management
├── levels/
│   ├── __init__.py
│   └── level.py         # Procedural level generation system
├── Entities/            # Game entity classes
│   ├── __init__.py
│   ├── character.py     # Player character
│   ├── box.py          # Box entities
│   ├── dock.py         # Target dock entities
│   ├── floor.py        # Floor tiles
│   └── wall.py         # Wall entities
├── base/               # Base entity classes
│   ├── __init__.py
│   └── Base.py         # Abstract base entity
├── levels.txt          # Original level definitions
├── demo.py            # Simple text-based demo
└── test_*.py          # Test scripts
```

### Level Generation System

The game features an advanced **ProceduralSokoban** algorithm with:

- **Template-based Generation**: 8 predefined room templates
- **Smart Placement**: Ensures solvable puzzle configurations
- **Post-processing**: Validates accessibility and win conditions
- **Dynamic Sizing**: Customizable level dimensions

### Templates Include:
1. **Empty Room** - Basic open space
2. **Cross Layout** - Plus-shaped room
3. **L-Shape** - Corner configuration
4. **Corridor** - Linear pathway
5. **T-Junction** - Three-way intersection
6. **Corner Room** - Angled layout
7. **Diamond** - Diamond-shaped space
8. **Rectangle** - Rectangular chamber

## 🎲 Procedural Generation

### Algorithm Features
- **Template Rotation**: Templates can be rotated for variety
- **Intelligent Placement**: Ensures connected, solvable layouts
- **Box-Goal Pairing**: Guarantees winnable configurations
- **Accessibility Validation**: Flood-fill ensures all areas are reachable

### Generation Process
1. **Size Selection**: Random dimensions within bounds
2. **Template Placement**: Strategic positioning of room templates
3. **Wall Generation**: Create boundaries and obstacles
4. **Entity Placement**: Add player, boxes, and goals
5. **Validation**: Ensure puzzle is solvable
6. **Post-processing**: Final optimizations

## 🔧 Configuration

### Dependencies
- **textual**: Modern TUI framework
- **loguru**: Advanced logging
- **random**: Procedural generation

### Level Customization
```python
# Generate custom level
generate_sokoban_level(
    width=12,      # Level width
    height=10,     # Level height  
    num_boxes=4    # Number of boxes/goals
)
```

## 🎯 Gameplay Objectives

### Primary Goal
Push all boxes (`▓`) onto the dock positions (`·` green) to complete the level.

### Winning Condition
When all boxes are correctly placed on docks, they become `▓` (red on green) and the level is complete.

### Strategy Tips
- Plan your moves carefully - boxes can only be pushed, not pulled
- Avoid pushing boxes into corners where they can't be retrieved
- Use the reset function (`R`) if you get stuck
- Generate new levels (`N`) for unlimited puzzle variety

## 🚀 Development

### Running Tests
```bash
# Test level generation
uv run python test_level_generator.py

# Test game functionality  
uv run python test_game.py
```

### Logging
The game includes comprehensive logging for debugging and performance monitoring. Logs are stored in the `logs/` directory.

### Contributing
1. Fork the repository
2. Create a feature branch
3. Implement your changes
4. Add tests for new functionality
5. Submit a pull request

## 📄 License

This project is open source and available under the MIT License.

## 🙏 Acknowledgments

- **Textual** library for the excellent TUI framework
- **ProceduralSokoban** algorithm for level generation inspiration
- Classic Sokoban puzzle game for the core gameplay mechanics