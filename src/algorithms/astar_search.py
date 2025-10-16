"""
A* Algorithm for Sokoban
Optimized for memory usage and performance with time limits.
"""

import heapq
from typing import List, Tuple, Optional, Set, Dict
import copy
import time
from dataclasses import dataclass, field
from ..game_manager import GameMap
from ..log.logger import get_logger

log = get_logger(__name__)

@dataclass
class AStarState:
    """Optimized game state for A* pathfinding"""
    player_pos: Tuple[int, int]
    box_positions: Tuple[Tuple[int, int], ...]
    moves: List[str]
    g_cost: int = 0  # Cost from start
    h_cost: int = 0  # Heuristic cost to goal
    f_cost: int = field(init=False)  # Total cost
    
    def __post_init__(self):
        self.f_cost = self.g_cost + self.h_cost
    
    def __lt__(self, other):
        """For priority queue comparison"""
        if self.f_cost == other.f_cost:
            return self.g_cost > other.g_cost  # Prefer higher g_cost for tie-breaking
        return self.f_cost < other.f_cost
    
    def __hash__(self):
        """Hash for state comparison"""
        return hash((self.player_pos, self.box_positions))
    
    def __eq__(self, other):
        """Equality comparison for states"""
        if not isinstance(other, AStarState):
            return False
        return (self.player_pos == other.player_pos and 
                self.box_positions == other.box_positions)


class AStarSearch:
    """
    Optimized A* Search solver for Sokoban puzzles.
    Uses heuristics to find solutions more efficiently than BFS.
    """
    
    def __init__(self, initial_game_map: GameMap, max_iterations: int = 75000, time_limit: float = 60.0):
        self.initial_map = initial_game_map
        self.max_iterations = max_iterations
        self.time_limit = time_limit
        self.visited_states: Dict[Tuple, int] = {}  # state -> best g_cost
        self.solution_found = False
        self.dock_positions = self.get_dock_positions(initial_game_map)
        self.start_time = None
        
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
    
    def calculate_heuristic(self, box_positions: Tuple[Tuple[int, int], ...]) -> int:
        """
        Enhanced heuristic calculation with dock reassignment optimization.
        Considers moving boxes between docks for better overall positioning.
        """
        if not box_positions or not self.dock_positions:
            return 0
        
        # Quick check for solved state
        if set(box_positions) <= self.dock_positions:
            return 0
        
        # Enhanced assignment that considers dock reassignment
        return self._calculate_optimal_assignment(box_positions)
    
    def _calculate_optimal_assignment(self, box_positions: Tuple[Tuple[int, int], ...]) -> int:
        """
        Calculate optimal box-to-dock assignment considering reassignment benefits.
        Uses Hungarian-like algorithm with box swapping consideration.
        """
        if not box_positions:
            return 0
            
        # Create distance matrix for all boxes to all docks
        distance_matrix = []
        for box_pos in box_positions:
            box_distances = []
            for dock_pos in self.dock_positions:
                distance = self.manhattan_distance(box_pos, dock_pos)
                box_distances.append(distance)
            distance_matrix.append(box_distances)
        
        # Find optimal assignment using greedy approach with reassignment
        dock_list = list(self.dock_positions)
        num_boxes = len(box_positions)
        num_docks = len(dock_list)
        
        if num_boxes > num_docks:
            # More boxes than docks - impossible to solve
            return 999999  # Large number instead of float('inf')
        
        # Try to find the best assignment considering current dock usage
        best_total_cost = self._greedy_assignment(distance_matrix, box_positions, dock_list)
        
        # Consider dock reassignment if it improves accessibility
        reassignment_cost = self._consider_dock_reassignment(box_positions, dock_list)
        
        return min(best_total_cost, reassignment_cost)
    
    def _greedy_assignment(self, distance_matrix: List[List[int]], 
                          box_positions: Tuple[Tuple[int, int], ...], 
                          dock_list: List[Tuple[int, int]]) -> int:
        """Standard greedy assignment algorithm"""
        used_docks = set()
        total_cost = 0
        
        # Sort boxes by their minimum distance to any available dock
        box_indices = list(range(len(box_positions)))
        box_indices.sort(key=lambda i: min(distance_matrix[i]))
        
        for box_idx in box_indices:
            box_pos = box_positions[box_idx]
            
            # Skip boxes already on docks
            if box_pos in self.dock_positions:
                continue
                
            # Find best available dock
            best_cost = 999999  # Large number instead of float('inf')
            best_dock_idx = None
            
            for dock_idx, dock_pos in enumerate(dock_list):
                if dock_pos not in used_docks:
                    cost = distance_matrix[box_idx][dock_idx]
                    if cost < best_cost:
                        best_cost = cost
                        best_dock_idx = dock_idx
            
            if best_dock_idx is not None:
                total_cost += best_cost
                used_docks.add(dock_list[best_dock_idx])
        
        return int(total_cost)
    
    def _consider_dock_reassignment(self, box_positions: Tuple[Tuple[int, int], ...], 
                                   dock_list: List[Tuple[int, int]]) -> int:
        """
        Consider reassigning boxes between docks for better overall solution.
        This is the key enhancement for your requirement!
        """
        # Identify boxes currently on docks
        boxes_on_docks = [pos for pos in box_positions if pos in self.dock_positions]
        boxes_not_on_docks = [pos for pos in box_positions if pos not in self.dock_positions]
        
        if not boxes_on_docks or not boxes_not_on_docks:
            # No reassignment needed if all boxes are on/off docks
            return self._greedy_assignment(
                [[self.manhattan_distance(box, dock) for dock in dock_list] for box in box_positions],
                box_positions, dock_list
            )
        
        # Calculate cost of moving boxes that aren't on docks to free docks
        free_docks = [dock for dock in dock_list if dock not in boxes_on_docks]
        
        if len(free_docks) >= len(boxes_not_on_docks):
            # Enough free docks - no reassignment needed
            return sum(min(self.manhattan_distance(box, dock) for dock in free_docks) 
                      for box in boxes_not_on_docks)
        
        # Need to consider reassignment - try swapping boxes between docks
        min_reassignment_cost = 999999  # Large number instead of float('inf')
        
        # Try reassigning each box currently on a dock
        for current_box_on_dock in boxes_on_docks:
            # Calculate cost to move this box to a different dock
            reassignment_options = []
            
            for target_dock in dock_list:
                if target_dock != current_box_on_dock:  # Different dock
                    move_cost = self.manhattan_distance(current_box_on_dock, target_dock)
                    
                    # Calculate benefit: can a waiting box reach the freed dock easier?
                    freed_dock = current_box_on_dock
                    best_benefit = 0
                    
                    for waiting_box in boxes_not_on_docks:
                        # Cost to move waiting box to freed dock
                        to_freed_cost = self.manhattan_distance(waiting_box, freed_dock)
                        
                        # Compare with cost to move to best alternative dock
                        alternative_docks = [dock for dock in dock_list if dock != freed_dock and dock not in boxes_on_docks]
                        alternative_cost = min(
                            self.manhattan_distance(waiting_box, dock) 
                            for dock in alternative_docks
                        ) if alternative_docks else 999999
                        
                        benefit = max(0, alternative_cost - to_freed_cost)
                        best_benefit = max(best_benefit, benefit)
                    
                    # Net cost of reassignment
                    net_cost = move_cost - best_benefit
                    reassignment_options.append(net_cost)
            
            if reassignment_options:
                min_reassignment_cost = min(min_reassignment_cost, min(reassignment_options))
        
        # Calculate total cost with reassignment
        if min_reassignment_cost < 999999:
            # Cost of reassignment + cost to place remaining boxes
            remaining_cost = sum(
                min(self.manhattan_distance(box, dock) for dock in dock_list)
                for box in boxes_not_on_docks
            )
            return int(min_reassignment_cost + remaining_cost)
        
        # Fallback to greedy assignment
        return self._greedy_assignment(
            [[self.manhattan_distance(box, dock) for dock in dock_list] for box in box_positions],
            box_positions, dock_list
        )
    
    def create_state(self, game_map: GameMap, moves: List[str], g_cost: int) -> AStarState:
        """Create an optimized A* state from current map"""
        player_pos = game_map.player.position.to_tuple() if game_map.player else (0, 0)
        box_positions = self.get_box_positions(game_map)
        h_cost = self.calculate_heuristic(box_positions)
        
        return AStarState(
            player_pos=player_pos,
            box_positions=box_positions,
            moves=moves.copy(),
            g_cost=g_cost,
            h_cost=h_cost
        )
    
    def get_possible_moves(self, state: AStarState, game_map: GameMap) -> List[Tuple[str, AStarState]]:
        """Get all possible moves from current state with pruning"""
        possible_moves = []
        directions = ['up', 'down', 'left', 'right']
        
        for direction in directions:
            # Create a copy of the game map to test the move
            test_map = copy.deepcopy(game_map)
            
            # Use move_player_bot for deadlock detection in algorithms
            if test_map.move_player_bot(direction):
                new_moves = state.moves + [direction]
                new_g_cost = state.g_cost + 1
                new_state = self.create_state(test_map, new_moves, new_g_cost)
                
                # Pruning: only add if we haven't visited or found a better path
                state_key = (new_state.player_pos, new_state.box_positions)
                if (state_key not in self.visited_states or 
                    self.visited_states[state_key] > new_g_cost):
                    self.visited_states[state_key] = new_g_cost
                    possible_moves.append((direction, new_state))
        
        return possible_moves
    
    def solve(self) -> Optional[List[str]]:
        """
        Solve the Sokoban puzzle using optimized A*.
        """
        log.info("🎯 Starting A* Search...")
        self.start_time = time.time()
        
        # Initialize with starting state
        initial_state = self.create_state(self.initial_map, [], 0)
        priority_queue = [initial_state]
        heapq.heapify(priority_queue)
        
        state_key = (initial_state.player_pos, initial_state.box_positions)
        self.visited_states[state_key] = 0
        
        iterations = 0
        
        while priority_queue and iterations < self.max_iterations:
            if self.is_time_exceeded():
                elapsed_time = time.time() - self.start_time
                log.warning(f"⏰ Time limit of {self.time_limit}s exceeded after {iterations} iterations")
                break
                
            current_state = heapq.heappop(priority_queue)
            iterations += 1
            
            # Reconstruct game map from state
            test_map = copy.deepcopy(self.initial_map)
            for move in current_state.moves:
                test_map.move_player_bot(move)
            
            # Check if we've solved the puzzle
            if test_map.is_level_complete():
                elapsed_time = time.time() - self.start_time
                log.success(f"✅ Solution found in {iterations} iterations!")
                log.info(f"📏 Solution length: {len(current_state.moves)} moves")
                log.info(f"🎯 Final cost: {current_state.f_cost}")
                log.info(f"⏰ Time taken: {elapsed_time:.2f}s")
                self.solution_found = True
                return current_state.moves
            
            # Explore all possible moves
            possible_moves = self.get_possible_moves(current_state, test_map)
            
            for direction, new_state in possible_moves:
                heapq.heappush(priority_queue, new_state)
            
            # Progress indicator with memory management
            if iterations % 3000 == 0:
                elapsed_time = time.time() - self.start_time
                best_f = priority_queue[0].f_cost if priority_queue else 0
                log.debug(f"⏳ Explored {iterations} states, queue: {len(priority_queue)}, best f: {best_f}, time: {elapsed_time:.1f}s")
                
                # Memory management: limit queue size
                if len(priority_queue) > 150000:
                    log.info("🧹 Trimming queue to manage memory...")
                    priority_queue.sort()
                    priority_queue = priority_queue[:75000]
                    heapq.heapify(priority_queue)
        
        elapsed_time = time.time() - self.start_time if self.start_time else 0
        log.warning(f"❌ No solution found after {iterations} iterations in {elapsed_time:.2f}s")
        return None
    
    def get_statistics(self) -> dict:
        """Get search statistics"""
        return {
            'visited_states': len(self.visited_states),
            'solution_found': self.solution_found,
            'algorithm': 'A* Search (Optimized)'
        }


def solve_with_astar(game_map: GameMap, max_iterations: int = 75000, time_limit: float = 60.0) -> Optional[List[str]]:
    """
    Optimized convenience function to solve Sokoban puzzle with A*.
    
    Args:
        game_map: The game map to solve
        max_iterations: Maximum number of iterations before giving up
        time_limit: Maximum time in seconds before giving up
        
    Returns:
        List of moves to solve the puzzle, or None if no solution found
    """
    solver = AStarSearch(game_map, max_iterations, time_limit)
    return solver.solve()


if __name__ == "__main__":
    # Example usage
    from ..levels.level import generate_sokoban_level
    
    # Generate a test level
    level_data = generate_sokoban_level(8, 6, 2)
    test_map = GameMap(level_data)
    
    log.info("🎮 Testing A* Solver on generated level:")
    log.info("Level:")
    for row in level_data:
        log.info(row)
    
    # Solve with A*
    solution = solve_with_astar(test_map, max_iterations=5000)
    
    if solution:
        log.success(f"\n🎯 Solution found: {' '.join(solution)}")
        log.info(f"📊 Total moves: {len(solution)}")
    else:
        log.warning("\n❌ No solution found within iteration limit")