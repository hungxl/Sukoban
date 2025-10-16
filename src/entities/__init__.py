"""
Entities package for Sokoban game.

This package contains all game entity classes:
- Wall: Static wall entities that block movement
- Floor: Static floor entities that allow movement
- Dock: Target locations for boxes
- Box: Movable box entities that can be pushed
- Player: The player character
"""

from .wall import Wall
from .floor import Floor
from .dock import Dock
from .box import Box
from .character import Player

__all__ = ['Wall', 'Floor', 'Dock', 'Box', 'Player']