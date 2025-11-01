"""
Test if Level 2 is actually solvable - try with very high limits
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.game_manager import GameMap
from src.algorithms.breadth_first_search import BreadthFirstSearch
from src.algorithms.astar_search import AStarSearch

# Level 2 from AKK_Informatika.slc
level_2 = [
    '########',
    '#  #   #',
    '#   $  #',
    '#  #$$ #',
    '## #   #',
    '#.. $# #',
    '#..   @#',
    '########'
]

print("=" * 70)
print("TESTING IF LEVEL 2 IS SOLVABLE")
print("=" * 70)

print("\n1. Testing with BFS (100K iterations, 120s timeout)")
game_map = GameMap(level_2)
solver = BreadthFirstSearch(game_map, max_iterations=100000, time_limit=120.0)
solution = solver.solve()

if solution:
    print(f"   ✅ BFS SOLVED IT!")
    print(f"   Solution length: {len(solution)} moves")
    print(f"   First 50 moves: {' '.join(solution[:50])}")
else:
    print(f"   ❌ BFS could not solve")
    
    # Try to understand why
    print("\n2. Checking for obvious deadlocks...")
    game_map = GameMap(level_2)
    print(f"   Boxes: {len(game_map.boxes)}")
    print(f"   Docks: {len(game_map.docks)}")
    print(f"   Initial box positions: {[box.position.to_tuple() for box in game_map.boxes]}")
    print(f"   Dock positions: {[dock.position.to_tuple() for dock in game_map.docks]}")
    
    # Check if any box is immediately deadlocked
    print("\n3. Checking initial state for deadlocks...")
    for box in game_map.boxes:
        if game_map._is_box_in_corner(box.position):
            if box.position.to_tuple() not in [dock.position.to_tuple() for dock in game_map.docks]:
                print(f"   ⚠️  Box at {box.position.to_tuple()} is in a corner!")
    
    print("\n💡 This level might be:")
    print("   - Extremely complex (requires >100K states)")
    print("   - Has a very long optimal solution")
    print("   - Contains a subtle deadlock that makes it unsolvable")
