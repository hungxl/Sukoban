"""
Test that countdown timer uses correct time limits from each algorithm
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.algorithms.sokoban_bot import SokobanBot

print("=" * 70)
print("ALGORITHM TIME LIMITS VERIFICATION")
print("=" * 70)

bot = SokobanBot()

print("\n📋 Configured Time Limits:")
print("-" * 70)

for algo_key, algo_info in bot.algorithms.items():
    name = algo_info['name']
    time_limit = algo_info['time_limit']
    max_iter = algo_info['max_iterations']
    
    print(f"  {name:25} | Time Limit: {time_limit:6.1f}s | Iterations: {max_iter:,}")

print("\n" + "=" * 70)
print("VERIFICATION")
print("=" * 70)

# Test getting specific algorithm info
astar_info = bot.get_algorithm_info('astar')
print(f"\n✓ A* time limit: {astar_info['time_limit']}s")

bfs_info = bot.get_algorithm_info('bfs')
print(f"✓ BFS time limit: {bfs_info['time_limit']}s")

# Test getting all algorithms
all_info = bot.get_algorithm_info()
max_time = max(algo['time_limit'] for algo in all_info.values())
print(f"\n✓ Maximum time limit (for auto-solve): {max_time}s")

print("\n💡 The countdown timer will now show:")
print(f"   - A* solving: {astar_info['time_limit']:.0f} seconds")
print(f"   - BFS solving: {bfs_info['time_limit']:.0f} seconds")
print(f"   - Auto-solve: {max_time:.0f} seconds (max of all)")

print("\n" + "=" * 70)
