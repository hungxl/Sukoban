# Benchmark Tool Usage Guide

## Quick Start

### 1. Install Dependencies
```bash
cd d:\Filelab\Sukoban
uv add pandas matplotlib seaborn prettytable numpy
```

### 2. Run Sample Demo (No Solver - Just Shows Output Format)
```bash
cd d:\Filelab\Sukoban
uv run python benchmark\sample_output.py
```

This creates sample reports to show you what the output looks like without running actual solvers.

### 3. Run Quick Test (3 Levels)
```bash
cd d:\Filelab\Sukoban
uv run python benchmark\quick_demo.py
```

Tests first 3 levels from Cosmonotes.slc. Takes ~5-10 minutes.

### 4. Run Full Benchmark (10 Levels)
```bash
cd d:\Filelab\Sukoban
uv run python benchmark\benchmark_calculation.py
```

Tests first 10 levels from Cosmonotes.slc. Takes ~30-60 minutes depending on level difficulty.

## Configuration

Edit `benchmark_calculation.py` at line ~701:

```python
benchmark.run_benchmark(
    algorithms=['bfs', 'astar'],
    max_levels=10,        # Change to None for all 20 levels
    time_limit=300.0,     # Seconds per level (300 = 5 minutes)
    max_iterations=200000 # Max iterations per level
)
```

## Understanding Results

### Summary Table
```
+----------------------+--------------+-----------+--------------+-----------------+----------------+--------------+
|      Algorithm       | Success Rate | Avg Moves | Avg Time (s) | Avg Memory (MB) | Avg Iterations | Total Solved |
+----------------------+--------------+-----------+--------------+-----------------+----------------+--------------+
| Breadth-First Search |    45.0%     |   38.2    |    45.123    |      8.45       |     12450      |     9/20     |
|      A* Search       |    65.0%     |   42.7    |    28.456    |      5.23       |     8320       |    13/20     |
+----------------------+--------------+-----------+--------------+-----------------+----------------+--------------+
```

**Interpretation:**
- **Success Rate**: % of levels solved (higher is better)
- **Avg Moves**: Solution length - BFS is optimal (shorter is better)
- **Avg Time**: Solve time - A* is usually faster
- **Avg Memory**: Peak memory usage - Lower is more efficient
- **Avg Iterations**: Search iterations - Lower is more efficient

### What's "Good" Performance?

| Metric | BFS (Expected) | A* (Expected) |
|--------|---------------|---------------|
| Success Rate | 40-60% | 60-80% |
| Avg Time | 30-60s | 15-40s |
| Avg Memory | 5-15 MB | 3-10 MB |
| Solution Quality | Optimal (shortest) | Near-optimal |

**Note**: Cosmonotes levels are moderately challenging. Many levels may timeout with default settings.

## Output Files

All files saved to `benchmark/` directory with timestamps:

1. **`benchmark_results_YYYYMMDD_HHMMSS.txt`**
   - Human-readable text report
   - Summary and detailed tables
   - Open with any text editor

2. **`benchmark_data_YYYYMMDD_HHMMSS.json`**
   - Machine-readable data
   - Import into Excel, Python, R
   - Contains all raw metrics

3. **`benchmark_graphs_YYYYMMDD_HHMMSS.png`**
   - Main comparison graphs
   - Success rate, time, memory, solution length
   - 4 charts in 2×2 grid

4. **`benchmark_detailed_YYYYMMDD_HHMMSS.png`**
   - Detailed analysis graphs
   - Time by level, iterations, correlations
   - 4 charts in 2×2 grid

5. **`benchmark_report_YYYYMMDD_HHMMSS.pdf`**
   - Complete PDF report
   - All tables and graphs
   - Multi-page comprehensive report

## Troubleshooting

### "No solution found" for all levels
- **Cause**: Time limit or iteration limit too low
- **Fix**: Increase `time_limit` and `max_iterations` in code
- **Recommended**: `time_limit=300.0, max_iterations=200000`

### Benchmark takes too long
- **Cause**: Too many levels or too generous limits
- **Fix**: Reduce `max_levels` (e.g., 3-5 levels for testing)
- **Quick test**: Use `quick_demo.py` instead

### Memory errors
- **Cause**: Testing too many levels at once or complex levels
- **Fix**: Reduce `max_levels` or close other applications
- **Note**: Each level runs independently (memory is freed between levels)

### Import errors
```
ModuleNotFoundError: No module named 'pandas'
```
- **Fix**: Run `uv add pandas matplotlib seaborn prettytable numpy`

## Comparing Algorithms

### BFS (Breadth-First Search)
✅ **Strengths:**
- Guarantees optimal (shortest) solution
- Complete (finds solution if it exists)
- Good for small/medium levels

❌ **Weaknesses:**
- Slower on complex levels
- Higher memory usage
- May timeout on difficult puzzles

### A* Search
✅ **Strengths:**
- Faster than BFS (uses heuristics)
- Lower memory usage
- Better success rate on complex levels

❌ **Weaknesses:**
- Solutions may be longer than optimal
- Heuristic quality affects performance
- Can still timeout on very hard levels

## Customizing the Benchmark

### Test Different Level Files
```python
# In main() function, change:
levels_file = project_root / "assets" / "levels" / "YourLevels.slc"
```

### Test Only BFS or A*
```python
benchmark.run_benchmark(
    algorithms=['bfs'],  # Only test BFS
    # or
    algorithms=['astar'],  # Only test A*
)
```

### Export Only Specific Formats
Edit `export_results()` method to comment out unwanted exports.

## Performance Tips

1. **Start Small**: Test 3-5 levels first
2. **Adjust Limits**: Tune time_limit based on results
3. **Monitor Progress**: Watch console output
4. **Check Logs**: Look at `logs/` directory for detailed solver logs
5. **Parallel Testing**: Run multiple benchmarks in separate terminals

## Example Workflow

```bash
# 1. Install dependencies (one time)
uv add pandas matplotlib seaborn prettytable numpy

# 2. Test sample output (1 second)
uv run python benchmark\sample_output.py

# 3. Quick test on 3 levels (5-10 minutes)
uv run python benchmark\quick_demo.py

# 4. Review results
# Check benchmark/*.txt and *.png files

# 5. Adjust settings if needed
# Edit benchmark_calculation.py line ~701

# 6. Run full benchmark (30-60 minutes)
uv run python benchmark\benchmark_calculation.py

# 7. Analyze results
# Open *.pdf report for complete analysis
```

## Advanced Usage

### Batch Processing Multiple Level Sets
```python
level_files = [
    "Cosmonotes.slc",
    "Anomaly.slc",
    "YourLevels.slc"
]

for level_file in level_files:
    benchmark = SokobanBenchmark()
    benchmark.load_levels(level_file)
    benchmark.run_benchmark(...)
    benchmark.export_results()
```

### Custom Metrics
Add your own metrics by modifying the `BenchmarkMetrics` class:

```python
class BenchmarkMetrics:
    def __init__(self):
        # ... existing metrics ...
        self.custom_metric: float = 0.0
```

### Integration with CI/CD
```bash
# Run benchmark in CI
uv run python benchmark\benchmark_calculation.py > results.log
# Check if success rate meets threshold
python check_threshold.py --min-success-rate 50
```

## Getting Help

- Check `README.md` for overview
- Run `sample_output.py` to see expected output
- Review generated files in `benchmark/` directory
- Check `logs/` directory for solver logs
- Look at `refs/Statistics/Statistic_bfs_astart.pdf` for reference results
