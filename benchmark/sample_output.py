"""
Simple Benchmark Test - Creates sample output to demonstrate functionality
"""

import sys
from pathlib import Path
import json
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    from prettytable import PrettyTable
    import matplotlib.pyplot as plt
    import seaborn as sns
    import pandas as pd
    from matplotlib.backends.backend_pdf import PdfPages
except ImportError as e:
    print(f"Missing library: {e}")
    sys.exit(1)

# Sample benchmark data (realistic values)
sample_results = [
    {'level_id': 1, 'algorithm': 'bfs', 'success': True, 'solve_time': 0.234, 'memory_peak_mb': 2.45, 'iterations': 1250, 'moves': 15, 'error': None},
    {'level_id': 1, 'algorithm': 'astar', 'success': True, 'solve_time': 0.156, 'memory_peak_mb': 1.87, 'iterations': 850, 'moves': 16, 'error': None},
    {'level_id': 2, 'algorithm': 'bfs', 'success': True, 'solve_time': 1.234, 'memory_peak_mb': 5.23, 'iterations': 3450, 'moves': 28, 'error': None},
    {'level_id': 2, 'algorithm': 'astar', 'success': True, 'solve_time': 0.678, 'memory_peak_mb': 3.12, 'iterations': 1890, 'moves': 29, 'error': None},
    {'level_id': 3, 'algorithm': 'bfs', 'success': True, 'solve_time': 2.567, 'memory_peak_mb': 8.45, 'iterations': 5670, 'moves': 35, 'error': None},
    {'level_id': 3, 'algorithm': 'astar', 'success': True, 'solve_time': 1.234, 'memory_peak_mb': 4.56, 'iterations': 2340, 'moves': 37, 'error': None},
    {'level_id': 4, 'algorithm': 'bfs', 'success': False, 'solve_time': 30.0, 'memory_peak_mb': 15.67, 'iterations': 10000, 'moves': 0, 'error': 'Timeout'},
    {'level_id': 4, 'algorithm': 'astar', 'success': True, 'solve_time': 5.234, 'memory_peak_mb': 7.89, 'iterations': 4560, 'moves': 42, 'error': None},
    {'level_id': 5, 'algorithm': 'bfs', 'success': True, 'solve_time': 3.456, 'memory_peak_mb': 9.12, 'iterations': 6780, 'moves': 38, 'error': None},
    {'level_id': 5, 'algorithm': 'astar', 'success': True, 'solve_time': 1.890, 'memory_peak_mb': 5.34, 'iterations': 2890, 'moves': 40, 'error': None},
]

def create_sample_reports():
    """Generate sample benchmark reports"""
    output_dir = Path("benchmark")
    output_dir.mkdir(exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    df = pd.DataFrame(sample_results)
    df_success = df[df['success'] == True]
    
    print("📊 Generating sample benchmark reports...\n")
    
    # 1. Generate text report
    print("1️⃣ Creating text report...")
    text_file = output_dir / f"benchmark_results_{timestamp}.txt"
    
    # Summary table
    summary_table = PrettyTable()
    summary_table.field_names = ["Algorithm", "Success Rate", "Avg Moves", "Avg Time (s)", "Avg Memory (MB)", "Total Solved"]
    
    for algo in ['bfs', 'astar']:
        algo_data = df[df['algorithm'] == algo]
        success_data = algo_data[algo_data['success'] == True]
        success_rate = len(success_data) / len(algo_data) * 100
        
        summary_table.add_row([
            algo.upper(),
            f"{success_rate:.1f}%",
            f"{success_data['moves'].mean():.1f}" if len(success_data) > 0 else "-",
            f"{success_data['solve_time'].mean():.3f}" if len(success_data) > 0 else "-",
            f"{success_data['memory_peak_mb'].mean():.2f}" if len(success_data) > 0 else "-",
            f"{len(success_data)}/{len(algo_data)}"
        ])
    
    # Detailed table
    detail_table = PrettyTable()
    detail_table.field_names = ["Level", "Algorithm", "Status", "Moves", "Time (s)", "Memory (MB)", "Iterations"]
    
    for _, row in df.iterrows():
        status = "✅ Success" if row['success'] else "❌ Failed"
        detail_table.add_row([
            row['level_id'],
            row['algorithm'].upper(),
            status,
            row['moves'] if row['success'] else "-",
            f"{row['solve_time']:.3f}",
            f"{row['memory_peak_mb']:.2f}",
            row['iterations'] if row['success'] else "-"
        ])
    
    with open(text_file, 'w', encoding='utf-8') as f:
        f.write("="*80 + "\n")
        f.write("SOKOBAN ALGORITHM BENCHMARK RESULTS (SAMPLE)\n")
        f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write("="*80 + "\n\n")
        f.write("SUMMARY STATISTICS\n")
        f.write("-"*80 + "\n")
        f.write(str(summary_table) + "\n\n")
        f.write("DETAILED RESULTS\n")
        f.write("-"*80 + "\n")
        f.write(str(detail_table) + "\n")
    
    print(f"   ✅ Saved: {text_file.name}")
    
    # 2. Generate JSON
    print("2️⃣ Creating JSON data...")
    json_file = output_dir / f"benchmark_data_{timestamp}.json"
    
    with open(json_file, 'w', encoding='utf-8') as f:
        json.dump({
            'timestamp': timestamp,
            'total_tests': len(sample_results),
            'results': sample_results
        }, f, indent=2)
    
    print(f"   ✅ Saved: {json_file.name}")
    
    # 3. Generate graphs
    print("3️⃣ Creating visualizations...")
    sns.set_style("whitegrid")
    sns.set_palette("husl")
    
    fig = plt.figure(figsize=(16, 12))
    
    # Success Rate
    ax1 = plt.subplot(2, 3, 1)
    success_summary = df.groupby('algorithm')['success'].apply(lambda x: (x.sum() / len(x)) * 100)
    success_summary.plot(kind='bar', ax=ax1, color=['#2ecc71', '#3498db'])
    ax1.set_title('Success Rate by Algorithm', fontsize=12, fontweight='bold')
    ax1.set_ylabel('Success Rate (%)')
    ax1.set_xlabel('Algorithm')
    ax1.set_xticklabels([x.upper() for x in success_summary.index], rotation=0)
    ax1.set_ylim(0, 100)
    
    # Solve Time
    ax2 = plt.subplot(2, 3, 2)
    sns.boxplot(data=df_success, x='algorithm', y='solve_time', ax=ax2)
    ax2.set_title('Solve Time Distribution', fontsize=12, fontweight='bold')
    ax2.set_ylabel('Time (seconds)')
    ax2.set_xticklabels([x.upper() for x in df_success['algorithm'].unique()])
    
    # Memory Usage
    ax3 = plt.subplot(2, 3, 3)
    sns.boxplot(data=df_success, x='algorithm', y='memory_peak_mb', ax=ax3)
    ax3.set_title('Memory Usage Distribution', fontsize=12, fontweight='bold')
    ax3.set_ylabel('Peak Memory (MB)')
    ax3.set_xticklabels([x.upper() for x in df_success['algorithm'].unique()])
    
    # Moves
    ax4 = plt.subplot(2, 3, 4)
    sns.violinplot(data=df_success, x='algorithm', y='moves', ax=ax4)
    ax4.set_title('Solution Length Distribution', fontsize=12, fontweight='bold')
    ax4.set_ylabel('Number of Moves')
    ax4.set_xticklabels([x.upper() for x in df_success['algorithm'].unique()])
    
    # Time vs Level
    ax5 = plt.subplot(2, 3, 5)
    for algo in df_success['algorithm'].unique():
        algo_data = df_success[df_success['algorithm'] == algo]
        ax5.scatter(algo_data['level_id'], algo_data['solve_time'], 
                   label=algo.upper(), alpha=0.6, s=50)
    ax5.set_title('Solve Time by Level', fontsize=12, fontweight='bold')
    ax5.set_xlabel('Level ID')
    ax5.set_ylabel('Time (seconds)')
    ax5.legend()
    ax5.grid(True, alpha=0.3)
    
    # Iterations
    ax6 = plt.subplot(2, 3, 6)
    df_success.groupby('algorithm')['iterations'].mean().plot(kind='bar', ax=ax6, color=['#e74c3c', '#9b59b6'])
    ax6.set_title('Average Iterations', fontsize=12, fontweight='bold')
    ax6.set_ylabel('Iterations')
    ax6.set_xlabel('Algorithm')
    ax6.set_xticklabels([x.upper() for x in df_success.groupby('algorithm').groups.keys()], rotation=0)
    
    plt.tight_layout()
    
    png_file = output_dir / f"benchmark_graphs_{timestamp}.png"
    plt.savefig(png_file, dpi=300, bbox_inches='tight')
    print(f"   ✅ Saved: {png_file.name}")
    plt.close()
    
    # 4. Generate PDF report
    print("4️⃣ Creating PDF report...")
    pdf_file = output_dir / f"benchmark_report_{timestamp}.pdf"
    
    with PdfPages(pdf_file) as pdf:
        # Title page
        fig = plt.figure(figsize=(11, 8.5))
        fig.text(0.5, 0.9, 'Sokoban Algorithm Benchmark Report', 
                ha='center', fontsize=20, fontweight='bold')
        fig.text(0.5, 0.85, f'Generated: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}',
                ha='center', fontsize=12)
        fig.text(0.5, 0.80, 'Sample Data: 5 Levels × 2 Algorithms',
                ha='center', fontsize=10)
        fig.text(0.1, 0.70, 'Summary Statistics:', fontsize=14, fontweight='bold')
        fig.text(0.1, 0.15, str(summary_table), fontsize=8, family='monospace')
        plt.axis('off')
        pdf.savefig(fig, bbox_inches='tight')
        plt.close()
        
        # Recreate graphs for PDF
        fig = plt.figure(figsize=(16, 12))
        
        ax1 = plt.subplot(2, 3, 1)
        success_summary.plot(kind='bar', ax=ax1, color=['#2ecc71', '#3498db'])
        ax1.set_title('Success Rate by Algorithm', fontsize=12, fontweight='bold')
        ax1.set_ylabel('Success Rate (%)')
        ax1.set_xticklabels([x.upper() for x in success_summary.index], rotation=0)
        ax1.set_ylim(0, 100)
        
        ax2 = plt.subplot(2, 3, 2)
        sns.boxplot(data=df_success, x='algorithm', y='solve_time', ax=ax2)
        ax2.set_title('Solve Time Distribution', fontsize=12, fontweight='bold')
        ax2.set_xticklabels([x.upper() for x in df_success['algorithm'].unique()])
        
        ax3 = plt.subplot(2, 3, 3)
        sns.boxplot(data=df_success, x='algorithm', y='memory_peak_mb', ax=ax3)
        ax3.set_title('Memory Usage Distribution', fontsize=12, fontweight='bold')
        ax3.set_xticklabels([x.upper() for x in df_success['algorithm'].unique()])
        
        ax4 = plt.subplot(2, 3, 4)
        sns.violinplot(data=df_success, x='algorithm', y='moves', ax=ax4)
        ax4.set_title('Solution Length Distribution', fontsize=12, fontweight='bold')
        ax4.set_xticklabels([x.upper() for x in df_success['algorithm'].unique()])
        
        ax5 = plt.subplot(2, 3, 5)
        for algo in df_success['algorithm'].unique():
            algo_data = df_success[df_success['algorithm'] == algo]
            ax5.scatter(algo_data['level_id'], algo_data['solve_time'], 
                       label=algo.upper(), alpha=0.6, s=50)
        ax5.set_title('Solve Time by Level', fontsize=12, fontweight='bold')
        ax5.legend()
        ax5.grid(True, alpha=0.3)
        
        ax6 = plt.subplot(2, 3, 6)
        df_success.groupby('algorithm')['iterations'].mean().plot(kind='bar', ax=ax6, color=['#e74c3c', '#9b59b6'])
        ax6.set_title('Average Iterations', fontsize=12, fontweight='bold')
        ax6.set_xticklabels([x.upper() for x in df_success.groupby('algorithm').groups.keys()], rotation=0)
        
        plt.tight_layout()
        pdf.savefig(fig, bbox_inches='tight')
        plt.close()
        
        d = pdf.infodict()
        d['Title'] = 'Sokoban Benchmark Report (Sample)'
        d['Author'] = 'Sokoban Benchmark Tool'
    
    print(f"   ✅ Saved: {pdf_file.name}")
    
    # Print summary to console
    print("\n" + "="*80)
    print("📋 SUMMARY")
    print("="*80)
    print(summary_table)
    
    print("\n✅ Sample reports generated successfully!")
    print(f"📁 Location: {output_dir.absolute()}\n")
    
    print("Generated files:")
    print(f"  • {text_file.name}")
    print(f"  • {json_file.name}")
    print(f"  • {png_file.name}")
    print(f"  • {pdf_file.name}")
    print("\n💡 Run benchmark_calculation.py for real benchmark on actual levels")

if __name__ == "__main__":
    create_sample_reports()
