"""
Quick Demo of Benchmark Tool
Tests only the first 3 levels for rapid testing.
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from benchmark_calculation import SokobanBenchmark

NUM_OF_LEVEL = 5
def main():
    print("=" * 80)
    print(f"🚀 Sokoban Benchmark - Quick Demo ({NUM_OF_LEVEL} Levels)")
    print("=" * 80)
    
    # Setup
    project_root = Path(__file__).parent.parent
    levels_file = project_root / "assets" / "levels" / "Cosmonotes.slc"
    
    # Create and run benchmark
    benchmark = SokobanBenchmark(output_dir=str(project_root / "benchmark"))
    
    if not benchmark.load_levels(str(levels_file)):
        print("❌ Failed to load levels")
        return
    
    # Run on first 3 levels only
    benchmark.run_benchmark(
        algorithms=['bfs', 'astar'],
        max_levels=NUM_OF_LEVEL,  # Only 5 levels for quick test
        time_limit=600.0,  # 120 seconds per level
        max_iterations=100000  # 100k iterations
    )
    
    # Show results
    print("\n" + "=" * 80)
    print("📊 SUMMARY")
    print("=" * 80)
    print(benchmark.generate_summary_table())
    
    # Export
    benchmark.export_results()
    
    print("\n✅ Quick demo completed!")

if __name__ == "__main__":
    main()
