"""
Test the countdown timer widget
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.game_manager import GameMap
from src.algorithms.sokoban_bot import SokobanBot

# Simple test level
test_level = [
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
print("TESTING BOT SOLVE WITH TIMING")
print("=" * 70)

game_map = GameMap(test_level)
bot = SokobanBot()

print("\n📊 Bot Configuration:")
algo_info = bot.get_algorithm_info('astar')
print(f"   Algorithm: {algo_info['name']}")
print(f"   Max Iterations: {algo_info['max_iterations']}")
print(f"   Time Limit: {algo_info['time_limit']}s")

print("\n🤖 Starting solve...")
print("   (In the UI, you should see a countdown timer showing time remaining)")

result = bot.solve(game_map, 'astar')

print("\n" + "=" * 70)
print("RESULTS")
print("=" * 70)

if result['success']:
    print(f"✅ Solved!")
    print(f"   Time: {result['solve_time']:.2f}s / {result['time_limit']}s")
    print(f"   Moves: {result['move_count']}")
    print(f"   Iterations: {result['iterations_used']} / {result['max_iterations']}")
else:
    print(f"❌ Failed")
    print(f"   Time: {result['solve_time']:.2f}s")
    
print("\n💡 The countdown timer in the UI should:")
print("   - Show time remaining (MM:SS format)")
print("   - Display a progress bar that fills up")
print("   - Change color: green → yellow → red as time runs out")
print("   - Show the algorithm name being used")
