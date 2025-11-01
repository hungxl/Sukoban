# 🎯 Sokoban Benchmark Tool - Quick Reference

## ✅ Setup Verified
All dependencies and files are installed and ready!

## 🚀 Quick Start (3 Commands)

```bash
# 1. Check setup (optional)
uv run python benchmark\check_setup.py

# 2. See example output (runs instantly)
uv run python benchmark\sample_output.py

# 3. Run actual benchmark (takes time)
uv run python benchmark\quick_demo.py      # 3 levels (~10 min)
# OR
uv run python benchmark\benchmark_calculation.py  # 10 levels (~60 min)
```

## 📁 Files in This Directory

| File | Purpose | Run Time |
|------|---------|----------|
| `check_setup.py` | Verify setup ✅ | Instant |
| `sample_output.py` | Show example reports | Instant |
| `quick_demo.py` | Test 3 levels | ~10 min |
| `benchmark_calculation.py` | Full benchmark (10 levels) | ~60 min |
| `requirements.txt` | Python packages | - |
| `README.md` | Full documentation | - |
| `USAGE.md` | Usage guide | - |
| `IMPLEMENTATION_SUMMARY.md` | Technical details | - |

## 📊 What You Get

After running benchmark, you get 5 files:

1. **`benchmark_results_*.txt`** - Summary tables (human-readable)
2. **`benchmark_data_*.json`** - Raw data (for analysis)
3. **`benchmark_graphs_*.png`** - Main comparison charts
4. **`benchmark_detailed_*.png`** - Detailed analysis charts
5. **`benchmark_report_*.pdf`** - Complete PDF report

## 🎨 What's Benchmarked

✅ **Algorithms:** BFS (Breadth-First Search) and A* Search
✅ **Levels:** Cosmonotes.slc (20 levels total)
✅ **Metrics:**
- Execution time (seconds)
- Peak memory usage (MB)
- Search iterations
- Solution length (moves)
- Success/failure rate

## ⚙️ Configuration

Edit `benchmark_calculation.py` line ~701:

```python
benchmark.run_benchmark(
    algorithms=['bfs', 'astar'],  # Which algorithms
    max_levels=10,                # How many levels (None = all 20)
    time_limit=300.0,             # Max seconds per level
    max_iterations=200000         # Max iterations per level
)
```

## 🎓 Understanding Results

### Summary Table Example
```
+----------------------+--------------+-----------+
|      Algorithm       | Success Rate | Avg Moves |
+----------------------+--------------+-----------+
| Breadth-First Search |    45.0%     |   38.2    |
|      A* Search       |    65.0%     |   42.7    |
+----------------------+--------------+-----------+
```

**Key Points:**
- **Success Rate**: Higher is better (A* usually wins)
- **Avg Moves**: Lower is better (BFS is optimal)
- **BFS**: Finds shortest path but slower
- **A***: Faster but may find longer paths

### Expected Performance
- **Easy levels (1-5)**: 60-80% success rate
- **Medium levels (6-15)**: 40-60% success rate
- **Hard levels (16-20)**: 20-40% success rate

## 🐛 Troubleshooting

### "No solution found" for all levels
➡️ **Increase time/iteration limits** in the code

### Takes too long
➡️ **Reduce `max_levels`** (try 3 instead of 10)

### Import errors
➡️ **Run:** `uv add pandas matplotlib seaborn prettytable numpy`

## 📚 Documentation

- **README.md** - Complete feature documentation
- **USAGE.md** - Step-by-step usage guide
- **IMPLEMENTATION_SUMMARY.md** - Technical implementation details

## 💡 Tips

1. **Start with sample output** to see what results look like
2. **Test with quick_demo** (3 levels) before full benchmark
3. **Increase limits** if levels timeout
4. **Check generated graphs** - they're very informative!
5. **Compare with reference PDF** (`refs/Statistics/Statistic_bfs_astart.pdf`)

## 🎯 Typical Workflow

```bash
# Step 1: Verify setup
uv run python benchmark\check_setup.py

# Step 2: See what output looks like (no solving, instant)
uv run python benchmark\sample_output.py
# Check: benchmark_graphs_*.png

# Step 3: Test with 3 levels
uv run python benchmark\quick_demo.py
# Takes ~5-10 minutes
# Check: benchmark_results_*.txt

# Step 4: If results look good, run full benchmark
uv run python benchmark\benchmark_calculation.py
# Takes ~30-60 minutes
# Check: benchmark_report_*.pdf for complete analysis
```

## ✨ Features Implemented

✅ Automatic metric collection (decorator pattern)
✅ Multiple export formats (TXT, JSON, PNG, PDF)
✅ 8 different graph types (box plots, violin plots, heatmaps, etc.)
✅ Configurable parameters (time limits, iterations, level selection)
✅ Comprehensive statistics (success rate, averages, distributions)
✅ Professional visualizations (Seaborn + Matplotlib)
✅ Formatted tables (PrettyTable)
✅ Complete documentation

## 🎉 Ready to Use!

Everything is installed and configured. Just run:

```bash
uv run python benchmark\sample_output.py    # See example output
uv run python benchmark\quick_demo.py       # Test 3 levels
```

Enjoy benchmarking! 🚀
