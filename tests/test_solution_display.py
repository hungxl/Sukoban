"""Test solution display functionality"""
from src.game_manager import GameMap
from src.algorithms import SokobanBot

# Simple solvable level
test_level = [
    '#######',
    '#     #',
    '#  .$ #',
    '#  @  #',
    '#     #',
    '#######'
]

print("Testing Bot Solution with Result Display")
print("=" * 50)

game_map = GameMap(test_level)
bot = SokobanBot()

# Test with BFS
print("\n1. Testing BFS:")
result = bot.solve(game_map, 'bfs')
print(f"   Success: {result.get('success')}")
print(f"   Algorithm: {result.get('algorithm')}")
print(f"   Moves: {result.get('move_count')}")
print(f"   Time: {result.get('solve_time', 0):.3f}s")
print(f"   Iterations: {result.get('iterations_used')}")
print(f"   Solution: {result.get('moves')}")

# Test with A*
print("\n2. Testing A*:")
game_map = GameMap(test_level)  # Reset map
result = bot.solve(game_map, 'astar')
print(f"   Success: {result.get('success')}")
print(f"   Algorithm: {result.get('algorithm')}")
print(f"   Moves: {result.get('move_count')}")
print(f"   Time: {result.get('solve_time', 0):.3f}s")
print(f"   Iterations: {result.get('iterations_used')}")
print(f"   Solution: {result.get('moves')}")

# Test auto-solve
print("\n3. Testing Auto-Solve:")
game_map = GameMap(test_level)  # Reset map
result = bot.auto_solve(game_map)
print(f"   Success: {result.get('success')}")
print(f"   Algorithm: {result.get('algorithm')}")
print(f"   Moves: {result.get('move_count')}")
print(f"   Time: {result.get('solve_time', 0):.3f}s")
print(f"   Iterations: {result.get('iterations_used')}")
print(f"   Optimal: {result.get('optimal')}")

print("\n" + "=" * 50)
print("✅ All tests complete!")
print("\nTo test in the app:")
print("1. Run: uv run python main.py")
print("2. Press 'b' to open bot menu")
print("3. Select an algorithm")
print("4. Watch for solution display with:")
print("   - Algorithm name, moves, time, iterations")
print("   - Press SPACE to autoplay")
print("   - Press ENTER to skip")
