"""Test enhanced deadlock detection"""
from src.game_manager import GameMap
from src.algorithms.breadth_first_search import BreadthFirstSearch
from src.algorithms.astar_search import AStarSearch

# Simple solvable level
test_level_simple = [
    '#######',
    '#     #',
    '#  .$ #',
    '#  @  #',
    '#     #',
    '#######'
]

# Test BFS
print("=" * 50)
print("Testing BFS with simple solvable level...")
game_map = GameMap(test_level_simple)
solver = BreadthFirstSearch(game_map, max_iterations=10000, time_limit=15)
solution = solver.solve()
print(f"✓ Solution found: {solution is not None}")
print(f"✓ Moves: {len(solution) if solution else 0}")
if solution and len(solution) <= 20:
    print(f"✓ Path: {solution}")

# Test A*
print("\n" + "=" * 50)
print("Testing A* with simple solvable level...")
game_map = GameMap(test_level_simple)
solver = AStarSearch(game_map, max_iterations=10000, time_limit=15)
solution = solver.solve()
print(f"✓ Solution found: {solution is not None}")
print(f"✓ Moves: {len(solution) if solution else 0}")
if solution and len(solution) <= 20:
    print(f"✓ Path: {solution}")

# Level with corner deadlock (unsolvable)
test_level_corner = [
    '#######',
    '#  .  #',
    '# $ $ #',
    '#  @  #',
    '#######'
]

print("\n" + "=" * 50)
print("Testing BFS with corner deadlock (should fail)...")
game_map = GameMap(test_level_corner)
solver = BreadthFirstSearch(game_map, max_iterations=5000, time_limit=10)
solution = solver.solve()
print(f"✓ Solution found: {solution is not None}")
print(f"✓ Expected: False (corner deadlock)")

print("\n" + "=" * 50)
print("All tests complete!")
