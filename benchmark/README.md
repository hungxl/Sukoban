# Sokoban Algorithm Benchmark Tool

Comprehensive performance analysis tool for Sokoban solving algorithms (BFS and A*).

## Features

- **Performance Metrics Collection**:
  - Execution time
  - Peak memory usage
  - Iterations count
  - Solution quality (number of moves)
  - Success rate

- **Multiple Output Formats**:
  - Text reports with formatted tables
  - JSON data export for further analysis
  - PNG graphs and visualizations
  - Comprehensive PDF reports

- **Visualizations**:
  - Success rate comparison
  - Solve time distribution
  - Memory usage analysis
  - Solution length comparison
  - Algorithm performance across levels
  - Correlation heatmaps

## Installation

Install required dependencies:

```bash
pip install -r requirements.txt
```

Or with uv:

```bash
uv add seaborn pandas matplotlib prettytable
```

## Usage

### Full Benchmark (All 30 Levels)

```bash
python benchmark_calculation.py
```

Edit line 524 in `benchmark_calculation.py` to change:
- `max_levels=10` → `max_levels=None` for all levels
- Adjust `time_limit` and `max_iterations` in the `run_benchmark` method

### Quick Demo (First 3 Levels)

```bash
python quick_demo.py
```

## Configuration

You can customize the benchmark by modifying:

```python
# In benchmark_calculation.py, line ~172
result, metrics = benchmark_algorithm(
    game_map, algo, bot, 
    time_limit=30.0,      # Maximum time per level (seconds)
    max_iterations=10000  # Maximum iterations per level
)
```

### Recommended Settings

| Scenario | Time Limit | Max Iterations |
|----------|------------|----------------|
| Quick test | 30s | 10,000 |
| Standard benchmark | 120s | 100,000 |
| Thorough analysis | 300s | 200,000 |
| Complete solutions | 600s | 500,000 |

**Note**: Cosmonotes levels are moderately challenging. Expect some levels to timeout even with higher limits.

## Output Files

All outputs are saved in the `benchmark/` directory with timestamps:

- `benchmark_results_YYYYMMDD_HHMMSS.txt` - Text report with tables
- `benchmark_data_YYYYMMDD_HHMMSS.json` - Raw data in JSON format
- `benchmark_graphs_YYYYMMDD_HHMMSS.png` - Main comparison graphs
- `benchmark_detailed_YYYYMMDD_HHMMSS.png` - Detailed analysis graphs
- `benchmark_report_YYYYMMDD_HHMMSS.pdf` - Complete PDF report

## Benchmark Metrics

### Time Performance
- Measures actual wall-clock time to solve each level
- Includes algorithm initialization and solution validation

### Memory Usage
- Tracks peak memory consumption during solving
- Useful for understanding space complexity

### Iterations
- Counts search iterations/expansions
- Indicates algorithm efficiency

### Solution Quality
- Number of moves in the solution
- BFS guarantees optimal solutions
- A* provides good but not always optimal solutions

### Success Rate
- Percentage of levels solved within time/iteration limits
- Indicates algorithm robustness

## Interpreting Results

### Summary Table

```
+------------+--------------+-----------+-------------+-----------------+--------------+
| Algorithm  | Success Rate | Avg Moves | Avg Time (s)| Avg Memory (MB) | Total Solved |
+------------+--------------+-----------+-------------+-----------------+--------------+
| BFS        |    85.0%     |   42.3    |    5.234    |      12.45      |    17/20     |
| ASTAR      |    95.0%     |   45.1    |    2.156    |       8.23      |    19/20     |
+------------+--------------+-----------+-------------+-----------------+--------------+
```

**Analysis**:
- A* has higher success rate (95% vs 85%)
- A* is faster on average (2.1s vs 5.2s)
- BFS finds shorter solutions (42.3 vs 45.1 moves) - optimal!
- A* uses less memory (8.2MB vs 12.5MB)

### Graphs

1. **Success Rate Bar Chart**: Shows which algorithm solves more levels
2. **Time Distribution Box Plot**: Shows solve time variability
3. **Memory Usage Box Plot**: Compares memory efficiency
4. **Solution Length Violin Plot**: Shows solution quality distribution
5. **Time by Level Scatter**: Identifies difficult levels
6. **Iterations Comparison**: Shows search efficiency

## Example Results

Based on the Anomaly.slc level set (30 small levels):

**Expected Performance** (approximate):
- BFS: 60-80% success rate, optimal solutions, moderate time
- A*: 80-95% success rate, near-optimal solutions, faster time

**Typical patterns**:
- Simple levels (1-10): Both algorithms succeed quickly
- Medium levels (11-20): A* shows speed advantage
- Complex levels (21-30): Some may timeout for BFS

## Extending the Benchmark

### Add More Algorithms

Edit `benchmark_calculation.py`:

```python
# In run_benchmark method
algorithms = ['bfs', 'astar', 'your_new_algorithm']
```

Make sure the algorithm is registered in `SokobanBot`:

```python
# In sokoban_bot.py
self.algorithms = {
    'your_algo': {
        'name': 'Your Algorithm Name',
        'solver': your_solver_function,
        'max_iterations': 50000,
        'time_limit': 60.0
    }
}
```

### Test Different Level Sets

```python
# Load different level file
benchmark.load_levels("path/to/your/levels.slc")
```

### Export to Different Formats

The JSON export can be imported into:
- Excel/Google Sheets for further analysis
- Python notebooks (Jupyter) for custom visualizations
- R for statistical analysis
- Any data analysis tool

## Troubleshooting

### "No solution found" errors
- Increase `time_limit` and `max_iterations`
- Some levels may be unsolvable or extremely difficult

### Memory errors
- Reduce `max_levels` to process fewer levels at once
- Increase system RAM or close other applications

### Slow execution
- Reduce `time_limit` for faster (but less complete) results
- Use `quick_demo.py` for testing
- Reduce `max_levels` to benchmark fewer levels

### Missing dependencies
```bash
pip install prettytable matplotlib seaborn pandas numpy
```

## Technical Details

### Decorator Pattern
The `@benchmark_decorator` automatically tracks:
- Execution time using `time.time()`
- Memory usage using `tracemalloc`
- Exception handling and error reporting

### Memory Tracking
- Uses Python's `tracemalloc` module
- Tracks peak memory (highest point during execution)
- Tracks current memory (at end of execution)
- Converts to MB for readability

### Visualization
- **Seaborn**: Statistical data visualization
- **Matplotlib**: Base plotting library
- **PrettyTable**: ASCII table formatting
- **Pandas**: Data manipulation and analysis

## License

Part of the Sokoban solver project. See main project LICENSE.

## References

- Algorithm implementations: `src/algorithms/`
- Level loader: `src/levels/level.py`
- Game engine: `src/game_manager.py`
- Statistics reference: `refs/Statistics/Statistic_bfs_astart.pdf`
