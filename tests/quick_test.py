#!/usr/bin/env python3
"""
Quick test script to verify bot integration in the game
"""

from src.game_manager import GameMap
from src.algorithms import SokobanBot
from src.log import get_logger

log = get_logger(__name__)

def test_bot_integration():
    """Test that the bot works with the game manager"""
    # Simple test level
    test_level = [
        "#####",
        "#   #",
        "# $ #",
        "# .@#",
        "#####"
    ]
    
    print("🧪 Testing Bot Integration")
    print("=" * 50)
    
    # Create game map
    game_map = GameMap(test_level)
    print(f"✅ Game map created: {game_map.width}x{game_map.height}")
    
    # Create bot
    bot = SokobanBot()
    print("✅ Bot created")
    
    # Test auto-solve
    print("\n🤖 Testing auto-solve...")
    result = bot.auto_solve(game_map)
    
    if result and result.get('success'):
        moves = result.get('moves', [])
        print(f"🎯 Auto-solve SUCCESS: {len(moves)} moves")
        print(f"📝 Moves: {' '.join(moves)}")
    else:
        print("❌ Auto-solve failed")
    
    # Test individual algorithms
    algorithms = ['bfs', 'astar', 'sa']
    
    for alg in algorithms:
        print(f"\n🔄 Testing {alg.upper()}...")
        result = bot.solve(game_map, alg)
        
        if result and result.get('success'):
            moves = result.get('moves', [])
            time_taken = result.get('time', 0)
            print(f"✅ {alg.upper()} SUCCESS: {len(moves)} moves in {time_taken:.3f}s")
        else:
            print(f"❌ {alg.upper()} failed")
    
    print("\n🎉 Integration test completed!")

if __name__ == "__main__":
    test_bot_integration()