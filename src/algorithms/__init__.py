"""
Sokoban Pathfinding Algorithms Package

This package contains implementations of various algorithms for automatically
solving Sokoban puzzles:

- Breadth-First Search (BFS): Guarantees optimal solution
- A* Search: Fast heuristic-based search  
- Simulated Annealing: Probabilistic optimization

Usage:
    from algorithms import SokobanBot
    
    bot = SokobanBot()
    result = bot.solve(game_map, algorithm='astar')
"""

from .sokoban_bot import SokobanBot, TIME_LIMIT_DEFAULT
from .breadth_first_search import solve_with_bfs
from .astar_search import solve_with_astar  

__all__ = [
    'SokobanBot',
    'TIME_LIMIT_DEFAULT',
    'solve_with_bfs',
    'solve_with_astar', 
]

# Version info
__version__ = '1.0.0'
__author__ = 'Sokoban Bot'