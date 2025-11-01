"""
Test Level 2 with the actual bot using new iteration limits
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.game_manager import GameMap
from src.algorithms.sokoban_bot import SokobanBot

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
print("TESTING LEVEL 2 WITH SOKOBAN BOT (NEW LIMITS)")
print("=" * 70)
print("\nLevel Layout:")
for line in level_2:
    print(line)

print("\n" + "=" * 70)
print("BOT SOLVING WITH A* (100K iterations)")
print("=" * 70)

game_map = GameMap(level_2)
bot = SokobanBot()
result = bot.solve(game_map, 'astar')

print("\n" + "=" * 70)
print("RESULTS")
print("=" * 70)
if result['success']:
    print(f"✅ A* SOLVED IT!")
    print(f"   Moves: {result['move_count']}")
    print(f"   Time: {result['solve_time']:.2f}s")
    print(f"   Iterations used: {result['iterations_used']}")
    print(f"   Solution: {' '.join(result['moves'][:50])}")
else:
    print(f"❌ A* could not solve")
    print(f"   Time: {result['solve_time']:.2f}s")
    print(f"   Max iterations: {result['max_iterations']}")
