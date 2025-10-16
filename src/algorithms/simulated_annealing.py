"""
Simulated Annealing Algorithm for Sokoban
Optimized for memory usage and performance with time limits.
"""

import random
import math
import time
from typing import List, Tuple, Optional, Set
import copy
from dataclasses import dataclass
from ..game_manager import GameMap
from ..log.logger import get_logger

# Get logger for this module
log = get_logger(__name__)


@dataclass
class SAState:
    """Lightweight game state for Simulated Annealing"""
    moves: List[str]
    fitness: float = 0.0  # Higher is better
    
    def copy_with_move(self, move: str, new_fitness: float) -> 'SAState':
        """Create a new state with an additional move"""
        return SAState(
            moves=self.moves + [move],
            fitness=new_fitness
        )


class SimulatedAnnealing:
    """
    Optimized Simulated Annealing solver for Sokoban puzzles.
    Uses probabilistic search with temperature cooling to escape local optima.
    """
    
    def __init__(self, initial_game_map: GameMap, max_iterations: int = 100000, time_limit: float = 60.0):
        self.initial_map = copy.deepcopy(initial_game_map)
        self.max_iterations = max_iterations
        self.time_limit = time_limit
        self.solution_found = False
        self.dock_positions = self.get_dock_positions(initial_game_map)
        self.best_fitness = float('-inf')
        self.best_state = None
        self.start_time = None
        
        # Optimized SA parameters for better performance
        self.initial_temperature = 100.0  # Higher initial temperature for better exploration
        self.final_temperature = 0.001    # Lower final temperature for precision
        self.cooling_rate = 0.995         # Slower cooling for better convergence
        
        # Cache for fitness calculations
        self._fitness_cache = {}
        
    def is_time_exceeded(self) -> bool:
        """Check if time limit has been exceeded"""
        if self.start_time is None:
            return False
        return time.time() - self.start_time > self.time_limit
        
    def get_dock_positions(self, game_map: GameMap) -> Set[Tuple[int, int]]:
        """Extract dock positions from game map"""
        return {dock.position.to_tuple() for dock in game_map.docks}
    
    def get_box_positions(self, game_map: GameMap) -> Tuple[Tuple[int, int], ...]:
        """Extract box positions from game map as sorted tuple"""
        return tuple(sorted(box.position.to_tuple() for box in game_map.boxes))
    
    def manhattan_distance(self, pos1: Tuple[int, int], pos2: Tuple[int, int]) -> int:
        """Calculate Manhattan distance between two positions"""
        return abs(pos1[0] - pos2[0]) + abs(pos1[1] - pos2[1])
    
    def calculate_fitness(self, game_map: GameMap) -> float:
        """
        Enhanced fitness calculation with dock reassignment considerations.
        Higher values are better.
        """
        # Check for solved state first
        if game_map.is_level_complete():
            return 10000.0  # Maximum fitness for solved state
        
        box_positions = self.get_box_positions(game_map)
        
        # Use cache to avoid recalculation
        cache_key = box_positions
        if cache_key in self._fitness_cache:
            return self._fitness_cache[cache_key]
        
        if not box_positions or not self.dock_positions:
            fitness = 0.0
        else:
            # Enhanced fitness calculation with dock reassignment consideration
            fitness = self._calculate_enhanced_fitness(game_map, box_positions)
        
        # Cache the result
        self._fitness_cache[cache_key] = fitness
        return fitness
    
    def _calculate_enhanced_fitness(self, game_map: GameMap, box_positions: Tuple[Tuple[int, int], ...]) -> float:
        """
        Enhanced fitness calculation that considers optimal dock assignments.
        This implements your requirement for intelligent dock reassignment.
        """
        # Separate boxes on docks vs not on docks
        boxes_on_docks = [pos for pos in box_positions if pos in self.dock_positions]
        boxes_not_on_docks = [pos for pos in box_positions if pos not in self.dock_positions]
        
        # Base fitness components
        dock_bonus = len(boxes_on_docks) * 100  # Bonus for each box on a dock
        
        # Calculate movement cost for boxes not on docks
        if boxes_not_on_docks:
            movement_cost = self._calculate_optimal_movement_cost(boxes_on_docks, boxes_not_on_docks)
        else:
            movement_cost = 0
        
        # Calculate dock reassignment benefit
        reassignment_benefit = self._calculate_reassignment_benefit(boxes_on_docks, boxes_not_on_docks)
        
        # Penalty components
        corner_penalty = self.calculate_corner_penalty_fast(game_map, box_positions)
        
        # Accessibility bonus - reward configurations that keep paths open
        accessibility_bonus = self._calculate_accessibility_bonus(game_map, box_positions)
        
        # Combine all components
        fitness = (
            1000 +                    # Base score
            dock_bonus +              # Boxes on docks
            reassignment_benefit +    # Smart dock usage
            accessibility_bonus -     # Open paths
            movement_cost * 2 -       # Distance to move remaining boxes
            corner_penalty            # Deadlock penalties
        )
        
        return max(0.0, fitness)  # Ensure non-negative
    
    def _calculate_optimal_movement_cost(self, boxes_on_docks: List[Tuple[int, int]], 
                                       boxes_not_on_docks: List[Tuple[int, int]]) -> float:
        """Calculate the cost to optimally place remaining boxes."""
        if not boxes_not_on_docks:
            return 0.0
        
        occupied_docks = set(boxes_on_docks)
        available_docks = [dock for dock in self.dock_positions if dock not in occupied_docks]
        
        if len(available_docks) < len(boxes_not_on_docks):
            # Not enough docks - very high cost
            return 500.0
        
        # Calculate minimum cost assignment
        total_cost = 0.0
        available_docks_list = list(available_docks)
        
        for box_pos in boxes_not_on_docks:
            min_distance = min(
                self.manhattan_distance(box_pos, dock_pos) 
                for dock_pos in available_docks_list
            )
            total_cost += min_distance
        
        return total_cost
    
    def _calculate_reassignment_benefit(self, boxes_on_docks: List[Tuple[int, int]], 
                                      boxes_not_on_docks: List[Tuple[int, int]]) -> float:
        """
        Calculate benefit of reassigning boxes between docks.
        This is the core of the dock reassignment feature you requested.
        """
        if not boxes_on_docks or not boxes_not_on_docks:
            return 0.0
        
        max_benefit = 0.0
        
        # For each box currently on a dock, consider if moving it would help
        for current_dock_pos in boxes_on_docks:
            # Calculate cost to move this box to other docks
            reassignment_costs = []
            
            for target_dock in self.dock_positions:
                if target_dock != current_dock_pos:
                    move_cost = self.manhattan_distance(current_dock_pos, target_dock)
                    
                    # Calculate benefit: how much closer can waiting boxes get to the freed dock?
                    freed_dock = current_dock_pos
                    total_benefit = 0.0
                    
                    for waiting_box in boxes_not_on_docks:
                        # Distance to freed dock
                        distance_to_freed = self.manhattan_distance(waiting_box, freed_dock)
                        
                        # Distance to best alternative dock (excluding current arrangements)
                        other_available_docks = [
                            dock for dock in self.dock_positions 
                            if dock not in boxes_on_docks or dock == current_dock_pos
                        ]
                        other_available_docks = [dock for dock in other_available_docks if dock != freed_dock]
                        
                        if other_available_docks:
                            distance_to_alternative = min(
                                self.manhattan_distance(waiting_box, dock) 
                                for dock in other_available_docks
                            )
                            
                            # Benefit is the distance saved
                            benefit = max(0, distance_to_alternative - distance_to_freed)
                            total_benefit += benefit
                    
                    # Net benefit of this reassignment
                    net_benefit = total_benefit - move_cost
                    reassignment_costs.append(net_benefit)
            
            if reassignment_costs:
                max_benefit = max(max_benefit, max(reassignment_costs))
        
        return max_benefit * 10  # Scale the benefit
    
    def _calculate_accessibility_bonus(self, game_map: GameMap, box_positions: Tuple[Tuple[int, int], ...]) -> float:
        """Calculate bonus for maintaining accessible paths."""
        accessibility_bonus = 0.0
        
        # Bonus for boxes that don't block corridors
        for box_pos in box_positions:
            if box_pos in self.dock_positions:
                # Boxes on docks get a small bonus
                accessibility_bonus += 5
            else:
                # Check if box is in a position that maintains accessibility
                x, y = box_pos
                neighbors = [(x+1, y), (x-1, y), (x, y+1), (x, y-1)]
                
                free_neighbors = 0
                for nx, ny in neighbors:
                    if (0 <= nx < game_map.width and 0 <= ny < game_map.height):
                        try:
                            from ..base import Position
                            neighbor_pos = Position(nx, ny)
                            entities = game_map.get_entities_at(neighbor_pos)
                            
                            # Count as free if no solid entities
                            is_free = True
                            for entity in entities:
                                if hasattr(entity, 'is_solid') and entity.is_solid():
                                    is_free = False
                                    break
                            
                            if is_free:
                                free_neighbors += 1
                        except Exception:
                            pass  # Assume blocked if error
                
                # Bonus for boxes that maintain open paths
                accessibility_bonus += free_neighbors * 2
        
        return accessibility_bonus
    
    def calculate_corner_penalty_fast(self, game_map: GameMap, box_positions: Tuple[Tuple[int, int], ...]) -> float:
        """Fast corner penalty calculation"""
        penalty = 0.0
        
        for box_pos in box_positions:
            if box_pos in self.dock_positions:
                continue  # No penalty if box is on a dock
                
            x, y = box_pos
            walls_around = 0
            
            # Check cardinal directions for walls
            for dx, dy in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
                check_x, check_y = x + dx, y + dy
                
                # Boundary check
                if (check_x < 0 or check_x >= game_map.width or 
                    check_y < 0 or check_y >= game_map.height):
                    walls_around += 1
                    continue
                
                # Check for wall entity (simplified check)
                try:
                    from ..base import Position
                    check_pos = Position(check_x, check_y)
                    entities = game_map.get_entities_at(check_pos)
                    for entity in entities:
                        if hasattr(entity, 'entity_type') and entity.entity_type.name == 'WALL':
                            walls_around += 1
                            break
                except Exception:
                    # If there's an error, assume it's a wall
                    walls_around += 1
            
            # Penalty increases with number of walls
            if walls_around >= 2:
                penalty += walls_around * 5  # Reduced penalty for performance
        
        return penalty
    
    def apply_moves_to_map(self, moves: List[str]) -> GameMap:
        """Apply a sequence of moves to get the current game state"""
        current_map = copy.deepcopy(self.initial_map)
        for move in moves:
            # Use move_player_bot for deadlock detection in algorithms
            if not current_map.move_player_bot(move):
                break  # Invalid move sequence
        return current_map
    
    def get_random_neighbor(self, state: SAState) -> Optional[SAState]:
        """Get a random neighboring state with optimized move selection"""
        # Apply current moves to get current map state
        current_map = self.apply_moves_to_map(state.moves)
        
        directions = ['up', 'down', 'left', 'right']
        random.shuffle(directions)
        
        # Try up to 3 random directions for efficiency
        for direction in directions[:3]:
            test_map = copy.deepcopy(current_map)
            
            # Use move_player_bot for deadlock detection in algorithms
            if test_map.move_player_bot(direction):
                new_fitness = self.calculate_fitness(test_map)
                return state.copy_with_move(direction, new_fitness)
        
        return None  # No valid moves available
    
    def acceptance_probability(self, current_fitness: float, new_fitness: float, temperature: float) -> float:
        """Calculate probability of accepting a worse solution"""
        if new_fitness > current_fitness:
            return 1.0  # Always accept better solutions
        
        if temperature <= 0:
            return 0.0
        
        # Probability decreases with worse fitness and lower temperature
        try:
            return math.exp((new_fitness - current_fitness) / temperature)
        except OverflowError:
            return 0.0
    
    def solve(self) -> Optional[List[str]]:
        """
        Solve the Sokoban puzzle using optimized Simulated Annealing.
        """
        log.info("🔥 Starting Simulated Annealing Search...")
        self.start_time = time.time()
        
        # Initialize with starting state
        initial_fitness = self.calculate_fitness(self.initial_map)
        current_state = SAState(moves=[], fitness=initial_fitness)
        self.best_state = current_state
        self.best_fitness = initial_fitness
        
        temperature = self.initial_temperature
        iterations = 0
        iterations_without_improvement = 0
        max_without_improvement = 5000  # Reduced for efficiency
        
        # Temperature cooling schedule
        temperature_updates = max(1, self.max_iterations // 100)
        
        while (iterations < self.max_iterations and 
               temperature > self.final_temperature and
               iterations_without_improvement < max_without_improvement):
            
            if self.is_time_exceeded():
                elapsed_time = time.time() - self.start_time
                log.warning(f"⏰ Time limit of {self.time_limit}s exceeded after {iterations} iterations")
                break
            
            iterations += 1
            
            # Check if current state is solved
            if current_state.fitness >= 10000.0:
                elapsed_time = time.time() - self.start_time
                log.success(f"✅ Solution found in {iterations} iterations!")
                log.info(f"📏 Solution length: {len(current_state.moves)} moves")
                log.info(f"🔥 Final fitness: {current_state.fitness}")
                log.info(f"⏰ Time taken: {elapsed_time:.2f}s")
                self.solution_found = True
                return current_state.moves
            
            # Get a random neighbor
            neighbor = self.get_random_neighbor(current_state)
            if neighbor is None:
                # No valid moves, restart from a random point in best path
                if len(self.best_state.moves) > 5:
                    restart_point = random.randint(0, len(self.best_state.moves) // 2)
                    restart_moves = self.best_state.moves[:restart_point]
                    restart_map = self.apply_moves_to_map(restart_moves)
                    restart_fitness = self.calculate_fitness(restart_map)
                    current_state = SAState(moves=restart_moves, fitness=restart_fitness)
                iterations_without_improvement += 1
                continue
            
            # Decide whether to accept the neighbor
            accept_prob = self.acceptance_probability(
                current_state.fitness, neighbor.fitness, temperature
            )
            
            if random.random() < accept_prob:
                current_state = neighbor
                
                # Update best state if necessary
                if neighbor.fitness > self.best_fitness:
                    self.best_state = neighbor
                    self.best_fitness = neighbor.fitness
                    iterations_without_improvement = 0
                    if iterations % 1000 == 0:
                        log.info(f"🌟 New best fitness: {self.best_fitness:.2f} at iteration {iterations}")
                else:
                    iterations_without_improvement += 1
            else:
                iterations_without_improvement += 1
            
            # Cool down temperature periodically
            if iterations % temperature_updates == 0:
                temperature *= self.cooling_rate
                if iterations % 5000 == 0:
                    elapsed_time = time.time() - self.start_time
                    log.debug(f"🌡️  Iteration {iterations}, Temp: {temperature:.3f}, Best: {self.best_fitness:.2f}, Time: {elapsed_time:.1f}s")
        
        elapsed_time = time.time() - self.start_time if self.start_time else 0
        log.warning(f"❌ No solution found after {iterations} iterations in {elapsed_time:.2f}s")
        log.info(f"🏆 Best fitness achieved: {self.best_fitness:.2f}")
        
        # Return best solution found, even if not complete
        if self.best_state and len(self.best_state.moves) > 0:
            log.info("🎯 Returning best partial solution found")
            return self.best_state.moves
        
        return None
    
    def get_statistics(self) -> dict:
        """Get search statistics"""
        return {
            'best_fitness': self.best_fitness,
            'solution_found': self.solution_found,
            'algorithm': 'Simulated Annealing (Optimized)',
            'cache_size': len(self._fitness_cache)
        }


def solve_with_simulated_annealing(game_map: GameMap, max_iterations: int = 100000, time_limit: float = 60.0) -> Optional[List[str]]:
    """
    Optimized convenience function to solve Sokoban puzzle with Simulated Annealing.
    
    Args:
        game_map: The game map to solve
        max_iterations: Maximum number of iterations before giving up
        time_limit: Maximum time in seconds before giving up
        
    Returns:
        List of moves to solve the puzzle, or None if no solution found
    """
    solver = SimulatedAnnealing(game_map, max_iterations, time_limit)
    return solver.solve()


if __name__ == "__main__":
    # Example usage
    from ..levels.level import generate_sokoban_level
    
    # Generate a test level
    level_data = generate_sokoban_level(6, 5, 2)
    test_map = GameMap(level_data)
    
    log.info("🎮 Testing Simulated Annealing Solver on generated level:")
    log.info("Level:")
    for row in level_data:
        log.info(row)
    
    # Solve with Simulated Annealing
    solution = solve_with_simulated_annealing(test_map, max_iterations=10000)
    
    if solution:
        log.success(f"\n🔥 Solution found: {' '.join(solution)}")
        log.info(f"📊 Total moves: {len(solution)}")
    else:
        log.warning("\n❌ No solution found within iteration limit")


