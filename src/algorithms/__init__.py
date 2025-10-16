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

from .sokoban_bot import SokobanBot
from .breadth_first_search import solve_with_bfs, BreadthFirstSearch
from .astar_search import solve_with_astar, AStarSearch  

__all__ = [
    'SokobanBot',
    'solve_with_bfs',
    'solve_with_astar', 
    'BreadthFirstSearch',
    'AStarSearch',
]

# Version info
__version__ = '1.0.0'
__author__ = 'Sokoban Bot'