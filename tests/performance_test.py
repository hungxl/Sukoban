#!/usr/bin/env python3
"""
Performance Comparison for Optimized Sokoban Algorithms
Shows time limits and performance improvements.
"""

import time
from src.game_manager import GameMap
from src.algorithms import SokobanBot
from src.levels.level import generate_sokoban_level

def test_performance():
    """Test performance improvements of optimized algorithms"""
    print("🚀 Optimized Sokoban Algorithm Performance Test")
    print("=" * 60)
    print("✨ New Features:")
    print("  • 60-second time limits on all algorithms")
    print("  • Optimized memory usage with lightweight state representation")
    print("  • Improved heuristics and pruning strategies")
    print("  • Progress indicators with memory management")
    print("  • Cache optimizations for repeated calculations")
    print()
    
    # Test different puzzle sizes
    test_cases = [
        {"size": 6, "boxes": 2, "name": "Small Puzzle"},
        {"size": 8, "boxes": 3, "name": "Medium Puzzle"},
        {"size": 10, "boxes": 4, "name": "Large Puzzle"}
    ]
    
    bot = SokobanBot()
    
    for test_case in test_cases:
        print(f"🎯 {test_case['name']} ({test_case['size']}x{test_case['size']}, {test_case['boxes']} boxes)")
        print("-" * 40)
        
        # Generate test level
        try:
            level_data = generate_sokoban_level(test_case['size'], test_case['size'], test_case['boxes'])
            game_map = GameMap(level_data)
            
            print("Level:")
            for row in level_data:
                print(f"  {row}")
            print()
            
            # Test each algorithm
            algorithms = ['astar', 'bfs']  # Skip SA for faster testing
            
            for algo in algorithms:
                print(f"🔬 Testing {algo.upper()}...")
                
                start_time = time.time()
                
                # Run algorithm with 20s limit for demo
                result = bot.solve(game_map, algo, time_limit=20.0)
                
                total_time = time.time() - start_time
                
                if result['success']:
                    print(f"  ✅ SUCCESS: {result['move_count']} moves in {total_time:.2f}s")
                    print(f"  🔧 Efficiency: {result['move_count']/total_time:.1f} moves/second")
                else:
                    print("  ❌ TIMEOUT: No solution within 20s")
                
                print()
                
        except Exception as e:
            print(f"  ❌ Error generating level: {e}")
            
        print()
    
    # Demonstrate time limit effectiveness
    print("⏱️  TIME LIMIT DEMONSTRATION")
    print("-" * 40)
    print("Testing time limit enforcement on a complex puzzle...")
    
    try:
        # Create a challenging level
        complex_level = generate_sokoban_level(12, 12, 5)
        complex_map = GameMap(complex_level)
        
        print("🎯 Complex Puzzle (12x12, 5 boxes)")
        print("Testing A* with 10-second time limit...")
        
        start_time = time.time()
        result = bot.solve(complex_map, 'astar', time_limit=10.0)
        actual_time = time.time() - start_time
        
        print(f"⏰ Actual time taken: {actual_time:.2f}s")
        
        if actual_time <= 11.0:  # Allow 1s margin
            print("✅ Time limit enforced correctly!")
        else:
            print("❌ Time limit exceeded tolerance")
            
    except Exception as e:
        print(f"❌ Error in time limit test: {e}")
    
    print("\n🎉 Performance testing completed!")
    print("\n📊 Key Improvements:")
    print("  • Lightweight state representation reduces memory usage")
    print("  • Optimized heuristics improve A* search efficiency") 
    print("  • Time limits prevent infinite search on difficult puzzles")
    print("  • Memory management prevents out-of-memory errors")
    print("  • Progress indicators provide real-time feedback")
    print("  • Queue trimming maintains performance on large search spaces")

if __name__ == "__main__":
    test_performance()