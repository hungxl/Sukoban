"""
Quick test to verify iteration tracking works
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.game_manager import GameMap
from src.algorithms.sokoban_bot import SokobanBot

# Simple test level
test_level = [
    "######",
    "#    #",
    "# $  #",
    "# .@ #",
    "#    #",
    "######"
]

print("=" * 60)
print("Testing Iteration Tracking")
print("=" * 60)

game_map = GameMap(test_level)
bot = SokobanBot()

print("\n🎮 Test Level:")
for row in test_level:
    print(row)

print("\n🤖 Testing BFS...")
bfs_result = bot.solve(game_map, 'bfs', max_iterations=10000, time_limit=30.0)
print(f"Success: {bfs_result['success']}")
print(f"Moves: {bfs_result.get('move_count', 0)}")
print(f"Iterations: {bfs_result.get('iterations_used', 'NOT FOUND')}")

print("\n🤖 Testing A*...")
game_map2 = GameMap(test_level)
astar_result = bot.solve(game_map2, 'astar', max_iterations=10000, time_limit=30.0)
print(f"Success: {astar_result['success']}")
print(f"Moves: {astar_result.get('move_count', 0)}")
print(f"Iterations: {astar_result.get('iterations_used', 'NOT FOUND')}")

print("\n" + "=" * 60)
if (bfs_result.get('iterations_used', 0) > 0 or 
    astar_result.get('iterations_used', 0) > 0):
    print("✅ Iteration tracking WORKING!")
else:
    print("❌ Iteration tracking NOT working")
print("=" * 60)
