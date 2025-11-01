"""
Test A* on Level 2 from AKK_Informatika
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.game_manager import GameMap
from src.algorithms.astar_search import AStarSearch
from src.algorithms.breadth_first_search import BreadthFirstSearch

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
print("TESTING LEVEL 2 FROM AKK_INFORMATIKA")
print("=" * 70)
print("\nLevel Layout:")
for line in level_2:
    print(line)

print("\n" + "=" * 70)
print("ANALYSIS")
print("=" * 70)

game_map = GameMap(level_2)
print(f"Boxes: {len(game_map.boxes)}")
print(f"Docks: {len(game_map.docks)}")
print(f"Box positions: {[box.position.to_tuple() for box in game_map.boxes]}")
print(f"Dock positions: {[dock.position.to_tuple() for dock in game_map.docks]}")

print("\n" + "=" * 70)
print("TESTING WITH BFS (10000 iterations)")
print("=" * 70)

game_map = GameMap(level_2)
solver = BreadthFirstSearch(game_map, max_iterations=10000, time_limit=30.0)
solution = solver.solve()

if solution:
    print(f"✅ BFS found solution!")
    print(f"   Length: {len(solution)} moves")
    print(f"   Solution: {' '.join(solution[:100])}")
else:
    print(f"❌ BFS could not solve (might be too complex)")

print("\n" + "=" * 70)
print("TESTING WITH A* (3000 iterations)")
print("=" * 70)

game_map = GameMap(level_2)
solver = AStarSearch(game_map, max_iterations=3000, time_limit=30.0)
solution = solver.solve()

if solution:
    print(f"✅ A* found solution!")
    print(f"   Length: {len(solution)} moves")
    print(f"   Solution: {' '.join(solution[:100])}")
else:
    print(f"❌ A* could not solve in 3000 iterations")
    print(f"   This level might require more iterations")

print("\n" + "=" * 70)
print("TESTING WITH A* (20000 iterations)")
print("=" * 70)

game_map = GameMap(level_2)
solver = AStarSearch(game_map, max_iterations=20000, time_limit=60.0)
solution = solver.solve()

if solution:
    print(f"✅ A* found solution with more iterations!")
    print(f"   Length: {len(solution)} moves")
    print(f"   Solution: {' '.join(solution[:100])}")
else:
    print(f"❌ A* still could not solve")
    print(f"   Possible issues:")
    print(f"   1. Level is too complex (needs >20000 states)")
    print(f"   2. Heuristic is not guiding search effectively")
    print(f"   3. Deadlock detection is too aggressive")

print("\n" + "=" * 70)
