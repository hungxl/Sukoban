"""
Test the fitness calculation with exponential bonuses
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.base import Position
from src.game_manager import GameMap
from src.algorithms.simulated_annealing import SimulatedAnnealing

def create_test_level():
    """Create a simple test level"""
    level_data = [
        "########",
        "#      #",
        "# .    #",
        "# $@   #",
        "#   $  #",
        "#    . #",
        "########"
    ]
    return level_data

def test_fitness_scaling():
    """Test fitness values with 0, 1, and 2 boxes on docks"""
    print("=" * 70)
    print("TESTING FITNESS SCALING WITH EXPONENTIAL BONUS")
    print("=" * 70)
    
    level = create_test_level()
    game_map = GameMap(level)
    sa = SimulatedAnnealing(game_map, max_iterations=1000, time_limit=5.0)
    
    print(f"\nInitial state:")
    print(f"  Box positions: {sa.get_box_positions(game_map)}")
    print(f"  Dock positions: {sa.dock_positions}")
    
    # Calculate initial fitness (0 boxes on docks)
    fitness_0 = sa.calculate_fitness(game_map)
    print(f"\nFitness with 0 boxes on docks: {fitness_0:.2f}")
    
    # Manually place 1 box on a dock to test
    # Box at (2,3) -> move to dock at (2,2)
    boxes_1_on_dock = list(game_map.boxes)
    boxes_1_on_dock[0].position = Position(2, 2)  # Place first box on first dock
    fitness_1 = sa.calculate_fitness(game_map)
    print(f"Fitness with 1 box on dock: {fitness_1:.2f}")
    print(f"  Improvement: +{fitness_1 - fitness_0:.2f}")
    
    # Reset and place 2 boxes on docks
    game_map = GameMap(level)
    boxes_2_on_dock = list(game_map.boxes)
    boxes_2_on_dock[0].position = Position(2, 2)  # First box on first dock
    boxes_2_on_dock[1].position = Position(5, 5)  # Second box on second dock
    fitness_2 = sa.calculate_fitness(game_map)
    print(f"Fitness with 2 boxes on docks: {fitness_2:.2f}")
    print(f"  Improvement from 1 box: +{fitness_2 - fitness_1:.2f}")
    print(f"  Improvement from 0 boxes: +{fitness_2 - fitness_0:.2f}")
    
    print("\n" + "=" * 70)
    print("ANALYSIS")
    print("=" * 70)
    print(f"Expected exponential scaling:")
    print(f"  0 boxes: base fitness only")
    print(f"  1 box: +200 (200 * 4^0)")
    print(f"  2 boxes: +800 (200 * 4^1)")
    print(f"\nActual differences:")
    print(f"  1 box vs 0 boxes: {fitness_1 - fitness_0:.2f} (expected ~200)")
    print(f"  2 boxes vs 1 box: {fitness_2 - fitness_1:.2f} (expected ~600)")
    
    if fitness_2 - fitness_1 > 500:
        print("\n✅ Exponential bonus is working correctly!")
    else:
        print("\n❌ Exponential bonus not providing enough incentive")
        print("   SA will still get stuck at 1 box on dock")

if __name__ == "__main__":
    test_fitness_scaling()
