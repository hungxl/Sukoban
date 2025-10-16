#!/usr/bin/env python3
"""
Test script for Sokoban pathfinding algorithms.
Demonstrates all three algorithms on a simple puzzle.
"""

from src.game_manager import GameMap
from src.algorithms import SokobanBot


def test_simple_puzzle():
    """Test all algorithms on a simple Sokoban puzzle."""
    
    # Simple test level - should be solvable quickly
    simple_level = [
        "#####",
        "#   #",
        "# $ #",
        "# .@#",
        "#####"
    ]
    
    print("🎮 Testing Sokoban Pathfinding Algorithms")
    print("=" * 50)
    print("Simple Test Level:")
    for row in simple_level:
        print(f"  {row}")
    print()
    
    # Create game map and bot
    game_map = GameMap(simple_level)
    bot = SokobanBot()
    
    # Test each algorithm
    algorithms = ['bfs', 'astar', 'sa']
    results = {}
    
    for algo in algorithms:
        print(f"\n{'='*20} {algo.upper()} {'='*20}")
        try:
            result = bot.solve(game_map, algo, max_iterations=1000)
            results[algo] = result
        except Exception as e:
            print(f"❌ Error testing {algo}: {e}")
            results[algo] = {'success': False, 'error': str(e)}
    
    # Summary
    print("\n" + "="*50)
    print("📊 RESULTS SUMMARY")
    print("="*50)
    
    for algo, result in results.items():
        if result.get('success'):
            print(f"✅ {algo.upper():3}: {result['move_count']:2} moves in {result['solve_time']:.3f}s")
            print(f"   Solution: {' '.join(result['moves'])}")
        else:
            print(f"❌ {algo.upper():3}: Failed - {result.get('error', 'No solution found')}")
    
    return results


def test_complex_puzzle():
    """Test algorithms on a more complex puzzle."""
    
    complex_level = [
        "########",
        "#      #",
        "# $$   #",
        "# $  $ #",
        "#   .. #",
        "#   .@ #",
        "#   .  #",
        "########"
    ]
    
    print("\n\n🎯 Testing on More Complex Puzzle")
    print("=" * 50)
    print("Complex Test Level:")
    for row in complex_level:
        print(f"  {row}")
    print()
    
    # Create game map and bot
    game_map = GameMap(complex_level)
    bot = SokobanBot()
    
    # Use auto-solve feature
    print("🤖 Using auto-solve feature...")
    result = bot.auto_solve(game_map)
    
    if result['success']:
        print(f"\n🎉 Auto-solve successful!")
        print(f"Algorithm: {result['algorithm']}")
        print(f"Moves: {result['move_count']}")
        print(f"Time: {result['solve_time']:.3f}s")
        print(f"Solution: {' '.join(result['moves'])}")
    else:
        print("\n❌ Auto-solve failed")
    
    return result


def compare_all_algorithms():
    """Compare all algorithms on the same puzzle."""
    
    print("\n\n🏁 Algorithm Comparison")
    print("=" * 50)
    
    # Medium complexity level
    test_level = [
        "######",
        "#    #",
        "# $$ #",
        "# .. #",
        "#  @ #",
        "######"
    ]
    
    print("Test Level:")
    for row in test_level:
        print(f"  {row}")
    print()
    
    game_map = GameMap(test_level)
    bot = SokobanBot()
    
    # Compare all algorithms
    results = bot.compare_algorithms(game_map)
    
    return results


def main():
    """Main test function."""
    print("🤖 Sokoban Algorithm Testing Suite")
    print("="*60)
    
    try:
        # Test 1: Simple puzzle
        simple_results = test_simple_puzzle()
        
        # Test 2: Complex puzzle with auto-solve
        complex_result = test_complex_puzzle()
        
        # Test 3: Algorithm comparison
        comparison_results = compare_all_algorithms()
        
        print("\n🎯 All tests completed successfully!")
        
    except Exception as e:
        print(f"\n💥 Test suite failed: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()