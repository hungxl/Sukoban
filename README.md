# Sokoban Game

A simple Sokoban puzzle game implemented with the Textual library in Python.

## Features

- **Text-based UI** using the Textual library
- **Level loading** from `levels.txt` file
- **Score tracking** showing moves and pushes
- **Pause menu** with game controls
- **Colorful display** with different symbols for game elements
- **Game completion detection**

## Game Elements

The game uses the following symbols:

- ` ` (space) = Floor
- `#` = Wall  
- `@` = Worker on floor
- `.` = Dock (target location)
- `*` = Box on dock
- `$` = Box
- `+` = Worker on dock

## Visual Representation

In the game, these symbols are displayed with colors:

- `█` (blue) = Wall
- `·` (white) = Floor
- `@` (yellow) = Player
- `·` (green) = Dock
- `▓` (red on green) = Box on dock  
- `▓` (red) = Box
- `@` (yellow on green) = Player on dock

## Controls

- **W/↑** - Move up
- **S/↓** - Move down  
- **A/←** - Move left
- **D/→** - Move right
- **P/Space** - Pause game
- **R** - Reset current level
- **Q** - Quit game

## Goal

Push all boxes (`$`) onto the dock positions (`.`) to complete the level.
When all boxes are on docks, they become `*` symbols.

## How to Run

1. Make sure you have Python 3.12+ and uv installed
2. Install dependencies:
   ```
   uv sync
   ```
3. Run the game:
   ```
   uv run python main.py
   ```

## Alternative Demo

For a simpler text-based demo without the full TUI:
```
uv run python demo.py
```

## Project Structure

- `main.py` - Main game application with Textual UI
- `levels.txt` - Level definitions
- `demo.py` - Simple text-based demo
- `test_game.py` - Test script to verify functionality

## Level Format

Levels are stored in `levels.txt` with the format:
```
Level 1
####
#  ###
#    #
# $  #
### ###
# $ $ #
#..@..#
#  $  #
###  ##
  ####

Level 2
...
```

Each level starts with "Level N" followed by the level layout using the symbols described above.