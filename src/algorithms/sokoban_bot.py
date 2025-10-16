"""
Sokoban Bot - Automatic Solver Interface
Provides a unified interface to use different pathfinding algorithms for solving Sokoban puzzles.
"""

from typing import Optional, Dict
import time
from ..game_manager import GameMap
from .breadth_first_search import solve_with_bfs
from .astar_search import solve_with_astar
from .simulated_annealing import solve_with_simulated_annealing
from ..log.logger import get_logger

# Get logger for this module
log = get_logger(__name__)

TIME_LIMIT_DEFAULT = 60.0  # seconds

class SokobanBot:
    """
    Sokoban Bot that can automatically solve puzzles using different algorithms.
    """
    
    def __init__(self):
        self.algorithms = {
            'bfs': {
                'name': 'Breadth-First Search',
                'solver': solve_with_bfs,
                'description': 'Guarantees shortest solution but may be slow for complex puzzles',
                'optimal': True,
                'max_iterations': 4000,  # Increased from 50K for better coverage
                'time_limit': TIME_LIMIT_DEFAULT
            },
            'astar': {
                'name': 'A* Search',
                'solver': solve_with_astar,
                'description': 'Fast and often finds good solutions using heuristics',
                'optimal': False,
                'max_iterations': 3000,  # Increased from 75K for complex puzzles
                'time_limit': TIME_LIMIT_DEFAULT
            },
            'sa': {
                'name': 'Simulated Annealing',
                'solver': solve_with_simulated_annealing,
                'description': 'Probabilistic search that can escape local optima',
                'optimal': False,
                'max_iterations': 6000,  # High iterations for probabilistic search
                'time_limit': TIME_LIMIT_DEFAULT
            },
        }
    
    def solve(self, game_map: GameMap, algorithm: str = 'astar', max_iterations: Optional[int] = None, time_limit: Optional[float] = None) -> Dict:
        """
        Solve a Sokoban puzzle using the specified algorithm.
        
        Args:
            game_map: The game map to solve
            algorithm: Algorithm to use ('bfs', 'astar', 'sa')
            max_iterations: Maximum iterations (uses default if None)
            time_limit: Maximum time in seconds (uses default if None)
            
        Returns:
            Dictionary with solution results
        """
        if algorithm not in self.algorithms:
            raise ValueError(f"Unknown algorithm: {algorithm}. Available: {list(self.algorithms.keys())}")
        
        algo_info = self.algorithms[algorithm]
        iterations = max_iterations or algo_info['max_iterations']
        time_limit_val = time_limit or algo_info['time_limit']
        
        log.info(f"🤖 Starting Sokoban Bot with {algo_info['name']}")
        log.info(f"📝 {algo_info['description']}")
        log.info(f"⚙️  Max iterations: {iterations}, Time limit: {time_limit_val}s")
        log.info("-" * 50)
        
        start_time = time.time()
        
        try:
            # Call solver with both iterations and time limit
            solution = algo_info['solver'](game_map, iterations, time_limit_val)
            solve_time = time.time() - start_time
            
            result = {
                'success': solution is not None,
                'algorithm': algo_info['name'],
                'moves': solution,
                'move_count': len(solution) if solution else 0,
                'solve_time': solve_time,
                'optimal': algo_info['optimal'],
                'iterations_used': iterations,
                'time_limit': time_limit_val
            }
            
            if solution:
                log.success("✅ Puzzle solved successfully!")
                log.info(f"📏 Solution: {len(solution)} moves")
                log.info(f"⏱️  Time taken: {solve_time:.2f} seconds")
                log.info(f"🎯 Moves: {' '.join(solution)}")
            else:
                log.warning(f"❌ No solution found within {iterations} iterations or {time_limit_val}s")
                log.info(f"⏱️  Time taken: {solve_time:.2f} seconds")
            
            return result
            
        except Exception as e:
            solve_time = time.time() - start_time
            log.error(f"💥 Error during solving: {e}")
            
            return {
                'success': False,
                'algorithm': algo_info['name'],
                'moves': None,
                'move_count': 0,
                'solve_time': solve_time,
                'optimal': algo_info['optimal'],
                'error': str(e)
            }

    def compare_algorithms(self, game_map: GameMap, algorithms: list[str] | None = None) -> dict:
        """
        Compare multiple algorithms on the same puzzle.
        
        Args:
            game_map: The game map to solve
            algorithms: List of algorithms to compare (uses all if None)
            
        Returns:
            Dictionary with comparison results
        """
        if algorithms is None:
            algorithms = list(self.algorithms.keys())
        
        log.info("🏁 Starting algorithm comparison...")
        log.info("=" * 60)
        
        results = {}
        
        for algo in algorithms:
            if algo in self.algorithms:
                log.info(f"\n🔄 Testing {self.algorithms[algo]['name']}...")
                result = self.solve(game_map, algo)
                results[algo] = result
        
        # Summary
        log.info("\n" + "=" * 60)
        log.info("📊 COMPARISON SUMMARY")
        log.info("=" * 60)
        
        successful_solutions = []
        for algo, result in results.items():
            status = "✅ SUCCESS" if result['success'] else "❌ FAILED"
            moves = result['move_count'] if result['success'] else "N/A"
            time_taken = result['solve_time']
            
            log.info(f"{self.algorithms[algo]['name']:20} | {status:9} | {str(moves):8} moves | {time_taken:6.2f}s")
            
            if result['success']:
                successful_solutions.append((algo, result))
        
        # Find best solution
        if successful_solutions:
            best_algo = min(successful_solutions, key=lambda x: x[1]['move_count'])
            log.success(f"\n🏆 Best solution: {self.algorithms[best_algo[0]]['name']} ({best_algo[1]['move_count']} moves)")
        
        return results
    
    def get_algorithm_info(self, algorithm: Optional[str] = None) -> Dict:
        """Get information about available algorithms."""
        if algorithm:
            if algorithm in self.algorithms:
                return self.algorithms[algorithm]
            else:
                raise ValueError(f"Unknown algorithm: {algorithm}")
        else:
            return self.algorithms
    
    def auto_solve(self, game_map: GameMap) -> Dict:
        """
        Automatically choose the best algorithm for the given puzzle.
        
        Args:
            game_map: The game map to solve
            
        Returns:
            Dictionary with solution results
        """
        # Simple heuristic: try A* first, then BFS for small puzzles, SA for large ones
        puzzle_size = game_map.width * game_map.height
        num_boxes = len(game_map.boxes)
        
        log.info(f"🧠 Auto-selecting algorithm for puzzle (size: {puzzle_size}, boxes: {num_boxes})")
        
        # Try A* first (good balance of speed and optimality)
        result = self.solve(game_map, 'astar')
        if result['success']:
            return result
        
        # If A* fails and puzzle is small, try BFS for optimal solution
        log.info("🔄 Trying BFS for optimal solution on small puzzle...")
        result = self.solve(game_map, 'bfs')
        if result['success']:
            return result
        
        # If both fail, try SA as last resort
        log.info("🔥 Trying Simulated Annealing as last resort...")
        result = self.solve(game_map, 'sa')
        return result
        

def demo_solver():
    """Demonstration of the Sokoban bot solver."""
    log.info("🤖 Sokoban Bot Demonstration")
    log.info("=" * 40)
    
    # Create a simple test level
    test_level = [
        "######",
        "#    #",
        "# $  #",
        "# .@ #",
        "#    #",
        "######"
    ]
    
    print("🎮 Test Level:")
    for row in test_level:
        print(row)
    
    game_map = GameMap(test_level)
    bot = SokobanBot()
    
    # Test auto-solve
    result = bot.auto_solve(game_map)
    
    if result['success']:
        print(f"\n🎯 Solution found: {' '.join(result['moves'])}")
    else:
        print("\n❌ No solution found")


if __name__ == "__main__":
    demo_solver()