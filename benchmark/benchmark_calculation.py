"""
Sokoban Algorithm Benchmark Tool
Comprehensive performance analysis for BFS and A* algorithms on Sokoban puzzles.

Features:
- Loads levels from Cosmonotes.slc
- Measures time, memory, iterations for each algorithm
- Generates tables, graphs, and PDF reports
- Exports results in multiple formats
"""

import time
import tracemalloc
import json
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime
from functools import wraps
import sys

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

# Data analysis and visualization
try:
    import pandas as pd
    import matplotlib.pyplot as plt
    import seaborn as sns
    from prettytable import PrettyTable
    from matplotlib.backends.backend_pdf import PdfPages
    import numpy as np
except ImportError as e:
    print(f"❌ Missing required package: {e}")
    print("Install with: uv add pandas matplotlib seaborn prettytable numpy")
    sys.exit(1)

# Import Sokoban modules
from src.levels.level import LevelCollection, SokobanLevel
from src.game_manager import GameMap
from src.algorithms.sokoban_bot import SokobanBot
from src.log.logger import get_logger

# Setup logger
log = get_logger(__name__)

TIME_LIMIT = 600.0
MAX_ITERATIONS = 100000

# Set matplotlib style
sns.set_style("whitegrid")
plt.rcParams['figure.figsize'] = (12, 8)
plt.rcParams['font.size'] = 10


class BenchmarkMetrics:
    """Container for benchmark metrics"""
    
    def __init__(self):
        self.execution_time: float = 0.0
        self.peak_memory_mb: float = 0.0
        self.current_memory_mb: float = 0.0
        self.iterations: int = 0
        self.moves_count: int = 0
        self.success: bool = False
        self.error: Optional[str] = None
        self.algorithm_name: str = ""
        self.level_id: str = ""
        self.level_number: int = 0
        
    def to_dict(self) -> Dict:
        """Convert metrics to dictionary"""
        return {
            'execution_time': self.execution_time,
            'peak_memory_mb': self.peak_memory_mb,
            'current_memory_mb': self.current_memory_mb,
            'iterations': self.iterations,
            'moves_count': self.moves_count,
            'success': self.success,
            'error': self.error,
            'algorithm_name': self.algorithm_name,
            'level_id': self.level_id,
            'level_number': self.level_number
        }


def benchmark_decorator(func):
    """
    Decorator to automatically track execution time and memory usage.
    
    Usage:
        @benchmark_decorator
        def solve_puzzle(game_map, algorithm):
            return solver.solve(game_map, algorithm)
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        metrics = BenchmarkMetrics()
        
        # Start memory tracking
        tracemalloc.start()
        start_time = time.time()
        
        try:
            # Execute the function
            result = func(*args, **kwargs)
            
            # Record success
            metrics.success = True
            
        except Exception as e:
            # Record error
            metrics.error = str(e)
            metrics.success = False
            result = None
            log.error(f"Benchmark error: {e}")
            
        finally:
            # Stop timing
            metrics.execution_time = time.time() - start_time
            
            # Get memory stats
            current, peak = tracemalloc.get_traced_memory()
            metrics.current_memory_mb = current / 1024 / 1024
            metrics.peak_memory_mb = peak / 1024 / 1024
            tracemalloc.stop()
        
        return result, metrics
    
    return wrapper


@benchmark_decorator
def benchmark_algorithm(game_map: GameMap, algorithm: str, bot: SokobanBot, 
                       time_limit: float = TIME_LIMIT, max_iterations: int = MAX_ITERATIONS) -> Dict:
    """
    Benchmark a single algorithm on a single level.
    
    Args:
        game_map: The game map to solve
        algorithm: Algorithm key ('bfs' or 'astar')
        bot: SokobanBot instance
        time_limit: Maximum time in seconds
        max_iterations: Maximum iterations
        
    Returns:
        Result dictionary from the solver
    """
    result = bot.solve(game_map, algorithm, max_iterations, time_limit)
    return result


class SokobanBenchmark:
    """Main benchmark orchestrator"""
    
    def __init__(self, output_dir: str = "benchmark"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        
        self.levels: List[SokobanLevel] = []
        self.results: List[Dict] = []
        self.bot = SokobanBot()
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
    def load_levels(self, slc_file: str) -> bool:
        """Load levels from SLC file"""
        log.info(f"📁 Loading levels from: {slc_file}")
        
        collection = LevelCollection()
        if collection.load_from_slc(slc_file):
            self.levels = collection.levels
            log.info(f"✅ Loaded {len(self.levels)} levels from {collection.title}")
            return True
        else:
            log.error(f"❌ Failed to load levels from {slc_file}")
            return False
    
    def run_benchmark(self, algorithms: Optional[List[str]] = None, 
                     max_levels: Optional[int] = None,
                     time_limit: float = TIME_LIMIT,
                     max_iterations: int = MAX_ITERATIONS) -> List[Dict]:
        """
        Run benchmark on all levels with specified algorithms.
        
        Args:
            algorithms: List of algorithm keys (default: ['bfs', 'astar'])
            max_levels: Maximum number of levels to test (None = all)
            time_limit: Time limit per level in seconds
            max_iterations: Iteration limit per level
            
        Returns:
            List of result dictionaries
        """
        if algorithms is None:
            algorithms = ['bfs', 'astar']
        
        levels_to_test = self.levels[:max_levels] if max_levels else self.levels
        total_tests = len(levels_to_test) * len(algorithms)
        
        log.info("=" * 80)
        log.info(f"🚀 Starting Sokoban Algorithm Benchmark")
        log.info(f"📊 Levels: {len(levels_to_test)}, Algorithms: {len(algorithms)}")
        log.info(f"⏱️  Time limit: {time_limit}s, Max iterations: {max_iterations}")
        log.info("=" * 80)
        
        self.results = []
        test_num = 0
        
        for level in levels_to_test:
            log.info(f"\n{'='*80}")
            log.info(f"🎮 Level {level.number}: {level.id} ({level.width}x{level.height})")
            log.info(f"{'='*80}")
            
            # Create game map
            try:
                game_map = GameMap(level.get_level_data())
            except Exception as e:
                log.error(f"❌ Failed to create game map: {e}")
                continue
            
            for algo in algorithms:
                test_num += 1
                algo_info = self.bot.get_algorithm_info(algo)
                
                log.info(f"\n[{test_num}/{total_tests}] 🤖 Testing {algo_info['name']}...")
                
                # Run benchmark
                result, metrics = benchmark_algorithm(
                    game_map, algo, self.bot, 
                    time_limit=time_limit,
                    max_iterations=max_iterations
                )
                
                # Populate metrics
                metrics.algorithm_name = algo_info['name']
                metrics.level_id = level.id
                metrics.level_number = level.number
                
                if result and result['success']:
                    metrics.iterations = result.get('iterations_used', 0)
                    metrics.moves_count = result.get('move_count', 0)
                    metrics.success = True
                    
                    log.info(f"✅ Success! Moves: {metrics.moves_count}, "
                           f"Time: {metrics.execution_time:.3f}s, "
                           f"Memory: {metrics.peak_memory_mb:.2f}MB, "
                           f"Iterations: {metrics.iterations}")
                else:
                    metrics.success = False
                    # Still capture iterations even on failure
                    if result:
                        metrics.iterations = result.get('iterations_used', 0)
                        error_msg = result.get('error', 'No solution found')
                    else:
                        error_msg = 'Solver failed'
                    metrics.error = error_msg
                    log.warning(f"❌ Failed: {error_msg} (Iterations: {metrics.iterations})")
                
                # Store result
                result_entry = {
                    'level_number': level.number,
                    'level_id': level.id,
                    'level_size': f"{level.width}x{level.height}",
                    'algorithm': algo,
                    'algorithm_name': algo_info['name'],
                    **metrics.to_dict()
                }
                self.results.append(result_entry)
        
        log.info("\n" + "=" * 80)
        log.info(f"✅ Benchmark completed! Total tests: {test_num}")
        log.info("=" * 80)
        
        return self.results
    
    def generate_summary_table(self) -> PrettyTable:
        """Generate summary statistics table"""
        if not self.results:
            return None
        
        df = pd.DataFrame(self.results)
        
        # Group by algorithm
        summary_table = PrettyTable()
        summary_table.field_names = [
            "Algorithm", "Success Rate", "Avg Moves", "Avg Time (s)", 
            "Avg Memory (MB)", "Avg Iterations", "Total Solved"
        ]
        
        for algo in df['algorithm'].unique():
            algo_df = df[df['algorithm'] == algo]
            successful = algo_df[algo_df['success'] == True]
            
            success_rate = len(successful) / len(algo_df) * 100
            avg_moves = successful['moves_count'].mean() if len(successful) > 0 else 0
            avg_time = successful['execution_time'].mean() if len(successful) > 0 else 0
            avg_memory = successful['peak_memory_mb'].mean() if len(successful) > 0 else 0
            avg_iterations = successful['iterations'].mean() if len(successful) > 0 else 0
            total_solved = f"{len(successful)}/{len(algo_df)}"
            
            summary_table.add_row([
                algo_df.iloc[0]['algorithm_name'],
                f"{success_rate:.1f}%",
                f"{avg_moves:.1f}" if avg_moves > 0 else "N/A",
                f"{avg_time:.3f}" if avg_time > 0 else "N/A",
                f"{avg_memory:.2f}" if avg_memory > 0 else "N/A",
                f"{avg_iterations:.0f}" if avg_iterations > 0 else "N/A",
                total_solved
            ])
        
        return summary_table
    
    def generate_detailed_table(self) -> PrettyTable:
        """Generate detailed results table for each level"""
        if not self.results:
            return None
        
        table = PrettyTable()
        table.field_names = [
            "Level", "Algorithm", "Success", "Moves", "Time (s)", 
            "Memory (MB)", "Iterations"
        ]
        
        for result in self.results:
            table.add_row([
                f"{result['level_number']}: {result['level_id'][:20]}",
                result['algorithm'].upper(),
                "✅" if result['success'] else "❌",
                result['moves_count'] if result['success'] else "-",
                f"{result['execution_time']:.3f}",
                f"{result['peak_memory_mb']:.2f}",
                result['iterations'] if result['success'] else "-"
            ])
        
        return table
    
    def create_visualizations(self) -> Tuple[plt.Figure, plt.Figure]:
        """Create comprehensive visualization graphs"""
        if not self.results:
            return None, None
        
        df = pd.DataFrame(self.results)
        successful_df = df[df['success'] == True]
        
        # Figure 1: Main comparison graphs (2x2 grid)
        fig1, axes = plt.subplots(2, 2, figsize=(16, 12))
        fig1.suptitle('Sokoban Algorithm Benchmark - Main Comparisons', 
                     fontsize=16, fontweight='bold')
        
        # 1. Success Rate by Algorithm
        success_rates = df.groupby('algorithm_name')['success'].apply(
            lambda x: (x.sum() / len(x)) * 100
        )
        axes[0, 0].bar(success_rates.index, success_rates.values, 
                      color=['#3498db', '#e74c3c'])
        axes[0, 0].set_title('Success Rate by Algorithm', fontweight='bold')
        axes[0, 0].set_ylabel('Success Rate (%)')
        axes[0, 0].set_ylim(0, 100)
        for i, v in enumerate(success_rates.values):
            axes[0, 0].text(i, v + 2, f'{v:.1f}%', ha='center', fontweight='bold')
        
        # 2. Execution Time Distribution (Box Plot)
        if len(successful_df) > 0:
            sns.boxplot(data=successful_df, x='algorithm_name', y='execution_time', 
                       ax=axes[0, 1], palette='Set2')
            axes[0, 1].set_title('Execution Time Distribution', fontweight='bold')
            axes[0, 1].set_ylabel('Time (seconds)')
            axes[0, 1].set_xlabel('')
        
        # 3. Memory Usage Comparison (Box Plot)
        if len(successful_df) > 0:
            sns.boxplot(data=successful_df, x='algorithm_name', y='peak_memory_mb', 
                       ax=axes[1, 0], palette='Set3')
            axes[1, 0].set_title('Peak Memory Usage', fontweight='bold')
            axes[1, 0].set_ylabel('Memory (MB)')
            axes[1, 0].set_xlabel('')
        
        # 4. Solution Length Comparison (Violin Plot)
        if len(successful_df) > 0:
            sns.violinplot(data=successful_df, x='algorithm_name', y='moves_count', 
                          ax=axes[1, 1], palette='muted')
            axes[1, 1].set_title('Solution Length Distribution', fontweight='bold')
            axes[1, 1].set_ylabel('Number of Moves')
            axes[1, 1].set_xlabel('')
        
        plt.tight_layout()
        
        # Figure 2: Detailed analysis (2x2 grid)
        fig2, axes2 = plt.subplots(2, 2, figsize=(16, 12))
        fig2.suptitle('Sokoban Algorithm Benchmark - Detailed Analysis', 
                     fontsize=16, fontweight='bold')
        
        # 1. Time by Level (Scatter plot)
        if len(successful_df) > 0:
            for algo in successful_df['algorithm_name'].unique():
                algo_data = successful_df[successful_df['algorithm_name'] == algo]
                axes2[0, 0].scatter(algo_data['level_number'], 
                                   algo_data['execution_time'], 
                                   label=algo, alpha=0.6, s=50)
            axes2[0, 0].set_title('Execution Time by Level', fontweight='bold')
            axes2[0, 0].set_xlabel('Level Number')
            axes2[0, 0].set_ylabel('Time (seconds)')
            axes2[0, 0].legend()
            axes2[0, 0].grid(True, alpha=0.3)
        
        # 2. Iterations Comparison
        if len(successful_df) > 0:
            iteration_data = successful_df.groupby('algorithm_name')['iterations'].mean()
            axes2[0, 1].bar(iteration_data.index, iteration_data.values, 
                           color=['#9b59b6', '#f39c12'])
            axes2[0, 1].set_title('Average Iterations', fontweight='bold')
            axes2[0, 1].set_ylabel('Iterations')
            for i, v in enumerate(iteration_data.values):
                axes2[0, 1].text(i, v + v*0.02, f'{v:.0f}', ha='center')
        
        # 3. Success vs Failure Count
        success_counts = df.groupby(['algorithm_name', 'success']).size().unstack(fill_value=0)
        success_counts.plot(kind='bar', stacked=True, ax=axes2[1, 0], 
                          color=['#e74c3c', '#2ecc71'])
        axes2[1, 0].set_title('Success vs Failure Count', fontweight='bold')
        axes2[1, 0].set_ylabel('Number of Levels')
        axes2[1, 0].set_xlabel('')
        axes2[1, 0].legend(['Failed', 'Success'])
        axes2[1, 0].set_xticklabels(axes2[1, 0].get_xticklabels(), rotation=0)
        
        # 4. Correlation Heatmap (for successful runs)
        if len(successful_df) > 0:
            corr_data = successful_df[['execution_time', 'peak_memory_mb', 
                                       'iterations', 'moves_count']].corr()
            sns.heatmap(corr_data, annot=True, fmt='.2f', cmap='coolwarm', 
                       ax=axes2[1, 1], cbar_kws={'label': 'Correlation'})
            axes2[1, 1].set_title('Metric Correlations', fontweight='bold')
        
        plt.tight_layout()
        
        return fig1, fig2
    
    def export_results(self):
        """Export results in multiple formats"""
        if not self.results:
            log.warning("No results to export")
            return
        
        log.info("\n📊 Exporting results...")
        
        # 1. Export to JSON
        json_file = self.output_dir / f"benchmark_data_{self.timestamp}.json"
        with open(json_file, 'w') as f:
            json.dump(self.results, f, indent=2)
        log.info(f"✅ JSON data: {json_file}")
        
        # 2. Export tables to text file
        txt_file = self.output_dir / f"benchmark_results_{self.timestamp}.txt"
        with open(txt_file, 'w', encoding='utf-8') as f:
            f.write("=" * 80 + "\n")
            f.write("SOKOBAN ALGORITHM BENCHMARK RESULTS\n")
            f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write("=" * 80 + "\n\n")
            
            # Summary table
            f.write("SUMMARY STATISTICS\n")
            f.write("-" * 80 + "\n")
            summary_table = self.generate_summary_table()
            f.write(str(summary_table) + "\n\n")
            
            # Detailed table
            f.write("\nDETAILED RESULTS\n")
            f.write("-" * 80 + "\n")
            detailed_table = self.generate_detailed_table()
            f.write(str(detailed_table) + "\n")
        
        log.info(f"✅ Text report: {txt_file}")
        
        # 3. Export graphs to PNG
        fig1, fig2 = self.create_visualizations()
        if fig1 and fig2:
            png1_file = self.output_dir / f"benchmark_graphs_{self.timestamp}.png"
            fig1.savefig(png1_file, dpi=300, bbox_inches='tight')
            log.info(f"✅ Main graphs: {png1_file}")
            
            png2_file = self.output_dir / f"benchmark_detailed_{self.timestamp}.png"
            fig2.savefig(png2_file, dpi=300, bbox_inches='tight')
            log.info(f"✅ Detailed graphs: {png2_file}")
            
            plt.close(fig1)
            plt.close(fig2)
        
        # 4. Export to PDF (comprehensive report)
        pdf_file = self.output_dir / f"benchmark_report_{self.timestamp}.pdf"
        self._create_pdf_report(pdf_file)
        log.info(f"✅ PDF report: {pdf_file}")
        
        log.info(f"\n🎉 All results exported to: {self.output_dir}")
    
    def _create_pdf_report(self, pdf_file: Path):
        """Create comprehensive PDF report"""
        with PdfPages(pdf_file) as pdf:
            # Page 1: Title and Summary
            fig = plt.figure(figsize=(11, 8.5))
            fig.text(0.5, 0.95, 'Sokoban Algorithm Benchmark Report', 
                    ha='center', fontsize=20, fontweight='bold')
            fig.text(0.5, 0.90, f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", 
                    ha='center', fontsize=12)
            
            # Summary statistics
            summary_table = self.generate_summary_table()
            fig.text(0.1, 0.80, 'Summary Statistics:', fontsize=14, fontweight='bold')
            fig.text(0.1, 0.30, str(summary_table), fontsize=9, family='monospace')
            
            plt.axis('off')
            pdf.savefig(fig, bbox_inches='tight')
            plt.close()
            
            # Page 2: Main visualizations
            fig1, fig2 = self.create_visualizations()
            if fig1:
                pdf.savefig(fig1, bbox_inches='tight')
                plt.close(fig1)
            
            # Page 3: Detailed visualizations
            if fig2:
                pdf.savefig(fig2, bbox_inches='tight')
                plt.close(fig2)
            
            # Page 4: Detailed results table
            fig = plt.figure(figsize=(11, 8.5))
            fig.text(0.5, 0.95, 'Detailed Results by Level', 
                    ha='center', fontsize=16, fontweight='bold')
            
            detailed_table = self.generate_detailed_table()
            # Split table if too long
            table_str = str(detailed_table)
            lines = table_str.split('\n')
            
            if len(lines) > 45:
                # First page of results
                fig.text(0.05, 0.05, '\n'.join(lines[:45]), 
                        fontsize=7, family='monospace', verticalalignment='bottom')
                plt.axis('off')
                pdf.savefig(fig, bbox_inches='tight')
                plt.close()
                
                # Additional pages if needed
                for i in range(45, len(lines), 50):
                    fig = plt.figure(figsize=(11, 8.5))
                    fig.text(0.05, 0.05, '\n'.join(lines[i:i+50]), 
                            fontsize=7, family='monospace', verticalalignment='bottom')
                    plt.axis('off')
                    pdf.savefig(fig, bbox_inches='tight')
                    plt.close()
            else:
                fig.text(0.05, 0.05, table_str, 
                        fontsize=8, family='monospace', verticalalignment='bottom')
                plt.axis('off')
                pdf.savefig(fig, bbox_inches='tight')
                plt.close()


def main():
    """Main execution function"""
    print("=" * 80)
    print("🚀 Sokoban Algorithm Benchmark Tool")
    print("=" * 80)
    
    # Setup paths
    project_root = Path(__file__).parent.parent
    levels_file = project_root / "assets" / "levels" / "Csoko.slc"
    
    if not levels_file.exists():
        log.error(f"❌ Level file not found: {levels_file}")
        return
    
    # Create benchmark instance
    benchmark = SokobanBenchmark(output_dir=str(project_root / "benchmark"))
    
    # Load levels
    if not benchmark.load_levels(str(levels_file)):
        log.error("❌ Failed to load levels")
        return
    
    # Run benchmark
    # Note: Adjust these parameters as needed
    # - max_levels: Number of levels to test (None = all)
    # - time_limit: Maximum time per level (seconds)
    # - max_iterations: Maximum iterations per level
    benchmark.run_benchmark(
        algorithms=['bfs', 'astar'],
        max_levels=5,  # Test first 5 levels (change to None for all 20)
        time_limit=300.0,  # 300 seconds (5 minutes) per level
        max_iterations=100000  # 100k iterations per level
    )
    
    # Generate and export results
    print("\n" + "=" * 80)
    print("📊 SUMMARY STATISTICS")
    print("=" * 80)
    summary = benchmark.generate_summary_table()
    print(summary)
    
    print("\n" + "=" * 80)
    print("📋 DETAILED RESULTS")
    print("=" * 80)
    detailed = benchmark.generate_detailed_table()
    print(detailed)
    
    # Export all results
    benchmark.export_results()
    
    print("\n" + "=" * 80)
    print("✅ Benchmark completed successfully!")
    print("=" * 80)


if __name__ == "__main__":
    main()
