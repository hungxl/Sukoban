"""
Quick test to see if the 2-box level is solvable
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.game_manager import GameMap
from src.algorithms.breadth_first_search import BreadthFirstSearch

test_level_2_boxes = [
    '########',
    '#      #',
    '# .    #',
    '# $@   #',
    '#   $  #',
    '#    . #',
    '########'
]

print("Testing if level is solvable with BFS...")
game_map = GameMap(test_level_2_boxes)
solver = BreadthFirstSearch(game_map, max_iterations=10000, time_limit=30.0)
solution = solver.solve()

if solution:
    print(f"✅ Level IS solvable!")
    print(f"   Solution length: {len(solution)} moves")
    print(f"   Solution: {' '.join(solution[:50])}")
else:
    print(f"❌ Level NOT solvable (or too hard for BFS)")
