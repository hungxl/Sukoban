"""
Test Simulated Annealing with 2 boxes and 2 docks
Reproduces the issue where SA only pushes 1 box to dock
"""
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.game_manager import GameMap
from src.algorithms.simulated_annealing import SimulatedAnnealing
import time

# Test level with 2 boxes and 2 docks
test_level_2_boxes = [
    '########',
    '#      #',
    '# .    #',
    '# $@   #',
    '#   $  #',
    '#    . #',
    '########'
]

print("=" * 70)
print("TEST: Simulated Annealing with 2 Boxes and 2 Docks")
print("=" * 70)
print("\nLevel Layout:")
for row in test_level_2_boxes:
    print(row)

print("\nKey:")
print("  @ = Player")
print("  $ = Box")
print("  . = Dock (goal)")
print("  # = Wall")

# Create game map
game_map = GameMap(test_level_2_boxes)
print(f"\nInitial state:")
print(f"  Boxes: {len(game_map.boxes)}")
print(f"  Docks: {len(game_map.docks)}")
print(f"  Box positions: {[box.position.to_tuple() for box in game_map.boxes]}")
print(f"  Dock positions: {[dock.position.to_tuple() for dock in game_map.docks]}")

# Test SA solver
print("\n" + "=" * 70)
print("Running Simulated Annealing...")
print("=" * 70)

solver = SimulatedAnnealing(game_map, max_iterations=50000, time_limit=60.0)

# Check initial fitness
initial_fitness = solver.calculate_fitness(game_map)
print(f"\nInitial fitness: {initial_fitness:.2f}")

# Analyze fitness components
print("\nFitness breakdown:")
box_positions = solver.get_box_positions(game_map)
boxes_on_docks = [pos for pos in box_positions if pos in solver.dock_positions]
boxes_not_on_docks = [pos for pos in box_positions if pos not in solver.dock_positions]

print(f"  Boxes on docks: {len(boxes_on_docks)} - {boxes_on_docks}")
print(f"  Boxes not on docks: {len(boxes_not_on_docks)} - {boxes_not_on_docks}")
print(f"  Dock bonus: {len(boxes_on_docks) * 100}")

# Start solving
start_time = time.time()
solution = solver.solve()
elapsed = time.time() - start_time

print("\n" + "=" * 70)
print("RESULTS")
print("=" * 70)

if solution:
    print(f"✅ Solution found!")
    print(f"   Moves: {len(solution)}")
    print(f"   Time: {elapsed:.2f}s")
    print(f"   Best fitness: {solver.best_fitness:.2f}")
    
    # Apply solution and check final state
    print("\nApplying solution to verify...")
    test_map = solver.apply_moves_to_map(solution)
    
    final_boxes_on_docks = sum(1 for box in test_map.boxes if box.on_dock)
    print(f"   Final boxes on docks: {final_boxes_on_docks}/{len(test_map.boxes)}")
    
    if test_map.is_level_complete():
        print("   ✅ Level COMPLETE! All boxes on docks!")
    else:
        print(f"   ⚠️  Level INCOMPLETE - only {final_boxes_on_docks} boxes on docks")
        
        # Show which box positions
        for i, box in enumerate(test_map.boxes):
            pos = box.position.to_tuple()
            on_dock = "✓ ON DOCK" if box.on_dock else "✗ NOT on dock"
            print(f"      Box {i+1} at {pos}: {on_dock}")
    
    # Show first 30 moves
    print(f"\n   First 30 moves: {' '.join(solution[:30])}")
    
else:
    print(f"❌ No solution found")
    print(f"   Time: {elapsed:.2f}s")
    print(f"   Best fitness: {solver.best_fitness:.2f}")

# Analyze why SA might get stuck
print("\n" + "=" * 70)
print("PROBLEM ANALYSIS")
print("=" * 70)

print("\n1. Fitness Function Analysis:")
print("   - Each box on dock gives +100 fitness")
print("   - State with 1 box on dock: ~1100 fitness")
print("   - State with 2 boxes on docks: ~1200 fitness")
print("   - Difference: only 100 points")

print("\n2. Potential Issues:")
print("   a) SA might accept states that move first box OFF dock")
print("      to explore, but rarely finds path to put BOTH on docks")
print("   b) Fitness difference (100 points) might be too small")
print("      compared to movement costs")
print("   c) Guided moves (30%) might not be enough to escape")
print("      from local optimum with 1 box on dock")

print("\n3. Suggested Fixes:")
print("   ✓ Increase dock bonus from 100 → 200 per box")
print("   ✓ Add exponential bonus for multiple boxes on docks")
print("   ✓ Increase guided move probability from 30% → 50%")
print("   ✓ Detect when stuck at local optimum (1 box on dock)")
print("     and force exploration")

print("\n" + "=" * 70)
