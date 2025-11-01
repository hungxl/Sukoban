"""Test improved Simulated Annealing algorithm"""
from src.game_manager import GameMap
from src.algorithms.simulated_annealing import SimulatedAnnealing
import time

# Test levels of varying difficulty
test_levels = {
    "simple": [
        '#######',
        '#     #',
        '#  .$ #',
        '#  @  #',
        '#     #',
        '#######'
    ],
    "medium": [
        '########',
        '#      #',
        '# .$   #',
        '# $. @ #',
        '#   $. #',
        '########'
    ],
    "complex": [
        '  ####  ',
        '###  ###',
        '#  $ $ #',
        '# .@.  #',
        '#  $ $ #',
        '###  ###',
        '  ####  '
    ]
}

print("=" * 60)
print("TESTING IMPROVED SIMULATED ANNEALING")
print("=" * 60)

for name, level_data in test_levels.items():
    print(f"\n{'='*60}")
    print(f"Testing {name.upper()} level:")
    print(f"{'='*60}")
    
    # Display level
    for row in level_data:
        print(row)
    print()
    
    # Create game map
    game_map = GameMap(level_data)
    
    # Test with improved SA
    print(f"Running Improved SA (max 50000 iterations, 60s limit)...")
    start_time = time.time()
    
    solver = SimulatedAnnealing(game_map, max_iterations=50000, time_limit=60.0)
    solution = solver.solve()
    
    elapsed = time.time() - start_time
    
    if solution:
        print(f"✅ SUCCESS!")
        print(f"   Moves: {len(solution)}")
        print(f"   Time: {elapsed:.2f}s")
        print(f"   Solution: {' '.join(solution[:20])}{'...' if len(solution) > 20 else ''}")
        print(f"   Best fitness: {solver.best_fitness:.2f}")
    else:
        print(f"❌ FAILED")
        print(f"   Time: {elapsed:.2f}s")
        print(f"   Best fitness achieved: {solver.best_fitness:.2f}")
    
    print()

print("=" * 60)
print("SUMMARY")
print("=" * 60)
print("Improvements implemented:")
print("✅ Guided move selection (30% of moves toward goals)")
print("✅ Adaptive temperature with reheating when stuck")
print("✅ Better restart strategy from best paths")
print("✅ Increased iterations to 50,000")
print("✅ Enhanced fitness function with dock reassignment")
print("\nRun the game with: uv run python main.py")
print("Then press 'b' → select 'Simulated Annealing' to test")
