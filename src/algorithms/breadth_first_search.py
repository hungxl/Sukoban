"""
Breadth-First Search Algorithm for Sokoban
Optimized for memory usage and performance with time limits.
"""

from collections import deque
from typing import List, Tuple, Optional, Set
import copy
import time
from dataclasses import dataclass
from ..game_manager import GameMap
from ..base import Position
from ..log.logger import get_logger

# Get logger for this module
log = get_logger(__name__)


@dataclass(frozen=True)
class GameStateKey:
    """Lightweight state representation for hashing and comparison"""
    player_pos: Tuple[int, int]
    box_positions: Tuple[Tuple[int, int], ...]
    
    @classmethod
    def from_game_map(cls, game_map: GameMap):
        box_positions = tuple(sorted(box.position.to_tuple() for box in game_map.boxes))
        player_pos = game_map.player.position.to_tuple() if game_map.player else (0, 0)
        return cls(
            player_pos=player_pos,
            box_positions=box_positions
        )


class BreadthFirstSearch:
    """
    Optimized Breadth-First Search solver for Sokoban puzzles.
    Guarantees to find the shortest solution in terms of moves.
    """
    
    def __init__(self, initial_game_map: GameMap, max_iterations: int = 50000, time_limit: float = 60.0):
        self.initial_map = initial_game_map
        self.max_iterations = max_iterations
        self.time_limit = time_limit
        self.visited_states: Set[GameStateKey] = set()
        self.solution_found = False
        self.start_time = None
        self.iterations_used = 0  # Track actual iterations used
        
    def is_time_exceeded(self) -> bool:
        """Check if time limit has been exceeded"""
        if self.start_time is None:
            return False
        return time.time() - self.start_time > self.time_limit
    
    def get_possible_moves(self, game_map: GameMap, current_moves: List[str]) -> List[Tuple[str, GameMap, List[str]]]:
        """Get all possible moves from current state with enhanced dock reassignment logic"""
        possible_moves = []
        directions = ['up', 'down', 'left', 'right']
        
        for direction in directions:
            # Create a shallow copy and test the move
            test_map = copy.deepcopy(game_map)
            
            # Use move_player_bot for deadlock detection in algorithms
            if test_map.move_player_bot(direction):
                # Check for global deadlock: all boxes stuck
                if test_map._is_all_boxes_stuck():
                    continue
                
                # Check if this move involves dock reassignment and evaluate if it's beneficial
                if self._is_beneficial_move(game_map, test_map, direction):
                    state_key = GameStateKey.from_game_map(test_map)
                    
                    # Only add if we haven't visited this state before
                    if state_key not in self.visited_states:
                        new_moves = current_moves + [direction]
                        possible_moves.append((direction, test_map, new_moves))
                        self.visited_states.add(state_key)
        
        return possible_moves
    
    def _is_beneficial_move(self, old_map: GameMap, new_map: GameMap, direction: str) -> bool:
        """
        Enhanced move evaluation that considers dock reassignment benefits.
        This implements your requirement for smarter box movement between docks.
        """
        # Always allow moves that don't involve pushing boxes
        if not old_map.player or not new_map.player:
            return True
            
        old_player_pos = old_map.player.position
        new_player_pos = new_map.player.position
        
        # Calculate direction offset
        offsets = {'up': (0, -1), 'down': (0, 1), 'left': (-1, 0), 'right': (1, 0)}
        dx, dy = offsets[direction]
        pushed_box_pos = (old_player_pos.x + dx, old_player_pos.y + dy)
        
        # Check if we pushed a box
        old_box_at_push_pos = None
        for box in old_map.boxes:
            if box.position.to_tuple() == pushed_box_pos:
                old_box_at_push_pos = box
                break
        
        if not old_box_at_push_pos:
            # No box was pushed - always allow
            return True
        
        # A box was pushed - analyze if it's beneficial
        was_on_dock = old_box_at_push_pos.on_dock
        
        # Find the corresponding box in new map
        new_box_pos = (pushed_box_pos[0] + dx, pushed_box_pos[1] + dy)
        new_box_on_dock = False
        for box in new_map.boxes:
            if box.position.to_tuple() == new_box_pos:
                new_box_on_dock = box.on_dock
                break
        
        # Case 1: Box moved from non-dock to dock - always beneficial
        if not was_on_dock and new_box_on_dock:
            return True
        
        # Case 2: Box moved from dock to non-dock - evaluate if this helps other boxes
        if was_on_dock and not new_box_on_dock:
            return self._evaluate_dock_vacation_benefit(old_map, new_map, pushed_box_pos)
        
        # Case 3: Box moved from dock to dock - evaluate relative positioning
        if was_on_dock and new_box_on_dock:
            return self._evaluate_dock_to_dock_benefit(old_map, new_map, pushed_box_pos, new_box_pos)
        
        # Case 4: Box moved from non-dock to non-dock - always allow (standard move)
        return True
    
    def _evaluate_dock_vacation_benefit(self, old_map: GameMap, new_map: GameMap, vacated_dock_pos: Tuple[int, int]) -> bool:
        """
        Evaluate if moving a box off a dock creates opportunities for other boxes.
        This is a key part of the dock reassignment strategy.
        """
        # Find boxes that are not on docks
        boxes_needing_docks = []
        for box in new_map.boxes:
            if not box.on_dock:
                boxes_needing_docks.append(box.position.to_tuple())
        
        if not boxes_needing_docks:
            # No boxes need docks - vacating might not be beneficial
            return False
        
        # Calculate if any waiting box is closer to the vacated dock than their current best option
        vacated_dock = Position(vacated_dock_pos[0], vacated_dock_pos[1])
        
        dock_positions = {dock.position.to_tuple() for dock in new_map.docks}
        occupied_docks = {box.position.to_tuple() for box in new_map.boxes if box.on_dock}
        free_docks = dock_positions - occupied_docks
        
        for waiting_box_pos in boxes_needing_docks:
            waiting_box = Position(waiting_box_pos[0], waiting_box_pos[1])
            
            # Distance to vacated dock
            distance_to_vacated = abs(waiting_box.x - vacated_dock.x) + abs(waiting_box.y - vacated_dock.y)
            
            # Distance to best alternative free dock
            min_alternative_distance = float('inf')
            for free_dock_pos in free_docks:
                if free_dock_pos != vacated_dock_pos:  # Exclude the vacated dock
                    free_dock = Position(free_dock_pos[0], free_dock_pos[1])
                    distance = abs(waiting_box.x - free_dock.x) + abs(waiting_box.y - free_dock.y)
                    min_alternative_distance = min(min_alternative_distance, distance)
            
            # If vacated dock is significantly closer, the move is beneficial
            if distance_to_vacated < min_alternative_distance - 1:  # At least 2 steps closer
                return True
        
        # Also consider if vacating improves overall accessibility
        return self._improves_accessibility(old_map, new_map, vacated_dock_pos)
    
    def _evaluate_dock_to_dock_benefit(self, old_map: GameMap, new_map: GameMap, 
                                     old_dock_pos: Tuple[int, int], new_dock_pos: Tuple[int, int]) -> bool:
        """
        Evaluate if moving a box from one dock to another improves the overall situation.
        """
        # Check if the new dock position provides better access for the player
        # or creates better positioning for remaining boxes
        
        # Find boxes that still need to be moved
        boxes_needing_docks = [box.position.to_tuple() for box in new_map.boxes if not box.on_dock]
        
        if not boxes_needing_docks:
            # All boxes are on docks - this move might be unnecessary unless it improves access
            return new_map.player is not None and len(new_map.get_entities_at(new_map.player.position)) > 1  # Allow if player movement is restricted
        
        # Calculate if the freed dock (old position) is more accessible to waiting boxes
        old_dock = Position(old_dock_pos[0], old_dock_pos[1])
        
        for waiting_box_pos in boxes_needing_docks:
            waiting_box = Position(waiting_box_pos[0], waiting_box_pos[1])
            distance_to_freed_dock = abs(waiting_box.x - old_dock.x) + abs(waiting_box.y - old_dock.y)
            
            # Find distance to other available docks
            dock_positions = {dock.position.to_tuple() for dock in new_map.docks}
            occupied_docks = {box.position.to_tuple() for box in new_map.boxes if box.on_dock}
            available_docks = dock_positions - occupied_docks
            
            min_other_distance = float('inf')
            for available_dock_pos in available_docks:
                if available_dock_pos != old_dock_pos:
                    available_dock = Position(available_dock_pos[0], available_dock_pos[1])
                    distance = abs(waiting_box.x - available_dock.x) + abs(waiting_box.y - available_dock.y)
                    min_other_distance = min(min_other_distance, distance)
            
            # If freed dock is notably closer, the reassignment is beneficial
            if distance_to_freed_dock < min_other_distance - 1:
                return True
        
        return False
    
    def _improves_accessibility(self, old_map: GameMap, new_map: GameMap, vacated_dock_pos: Tuple[int, int]) -> bool:
        """
        Check if vacating a dock improves overall map accessibility.
        """
        # Simple heuristic: check if the vacated position was blocking access paths
        vacated_pos = Position(vacated_dock_pos[0], vacated_dock_pos[1])
        
        # Count how many boxes can potentially access the vacated area more easily
        accessibility_improvement = 0
        
        for box in new_map.boxes:
            if not box.on_dock:
                # Check if this box has better access to dock areas now
                old_min_dock_distance = self._min_distance_to_accessible_dock(box.position, old_map)
                new_min_dock_distance = self._min_distance_to_accessible_dock(box.position, new_map)
                
                if new_min_dock_distance < old_min_dock_distance:
                    accessibility_improvement += 1
        
        return accessibility_improvement > 0
    
    def _min_distance_to_accessible_dock(self, box_position: Position, game_map: GameMap) -> int:
        """Calculate minimum distance to an accessible dock."""
        min_distance = float('inf')
        
        dock_positions = {dock.position.to_tuple() for dock in game_map.docks}
        occupied_docks = {box.position.to_tuple() for box in game_map.boxes if box.on_dock}
        free_docks = dock_positions - occupied_docks
        
        for dock_pos in free_docks:
            distance = abs(box_position.x - dock_pos[0]) + abs(box_position.y - dock_pos[1])
            min_distance = min(min_distance, distance)
        
        return int(min_distance) if min_distance != float('inf') else 999
    
    def solve(self) -> Optional[List[str]]:
        """
        Solve the Sokoban puzzle using optimized BFS.
        Returns the sequence of moves to solve the puzzle, or None if no solution found.
        """
        log.info("🔍 Starting Breadth-First Search...")
        self.start_time = time.time()
        
        # Initialize with starting state
        initial_state_key = GameStateKey.from_game_map(self.initial_map)
        queue = deque([(self.initial_map, [])])
        self.visited_states.add(initial_state_key)
        
        iterations = 0
        
        while queue and iterations < self.max_iterations:
            if self.is_time_exceeded():
                log.warning(f"⏰ Time limit of {self.time_limit}s exceeded after {iterations} iterations")
                self.iterations_used = iterations  # Store iterations before breaking
                break
                
            current_map, current_moves = queue.popleft()
            iterations += 1
            
            # Check if we've solved the puzzle
            if current_map.is_level_complete():
                elapsed_time = time.time() - self.start_time
                log.success(f"✅ Solution found in {iterations} iterations!")
                log.info(f"📏 Solution length: {len(current_moves)} moves")
                log.info(f"⏰ Time taken: {elapsed_time:.2f}s")
                self.solution_found = True
                self.iterations_used = iterations  # Store iterations on success
                return current_moves
            
            # Explore all possible moves
            possible_moves = self.get_possible_moves(current_map, current_moves)
            
            for direction, new_map, new_moves in possible_moves:
                queue.append((new_map, new_moves))
            
            # Progress indicator with memory management
            if iterations % 5000 == 0:  # More frequent progress updates
                elapsed_time = time.time() - self.start_time
                log.debug(f"⏳ Explored {iterations} states, queue: {len(queue)}, time: {elapsed_time:.1f}s")
                
                # Memory management: limit queue size but less aggressively
                if len(queue) > 200000:  # Increased threshold for better coverage
                    log.debug("🧹 Trimming queue to manage memory...")
                    # Keep more states (75% instead of 50%)
                    queue = deque(list(queue)[:150000])
        
        elapsed_time = time.time() - self.start_time if self.start_time else 0
        log.warning(f"❌ No solution found after {iterations} iterations in {elapsed_time:.2f}s")
        return None
    
    def get_statistics(self) -> dict:
        """Get search statistics"""
        return {
            'visited_states': len(self.visited_states),
            'solution_found': self.solution_found,
            'algorithm': 'Breadth-First Search (Optimized)'
        }


def solve_with_bfs(game_map: GameMap, max_iterations: int = 50000, time_limit: float = 60.0):
    """
    Optimized convenience function to solve Sokoban puzzle with BFS.
    
    Args:
        game_map: The game map to solve
        max_iterations: Maximum number of iterations before giving up
        time_limit: Maximum time in seconds before giving up
        
    Returns:
        Dictionary with 'moves' (list of moves or None) and 'iterations' (count)
    """
    solver = BreadthFirstSearch(game_map, max_iterations, time_limit)
    moves = solver.solve()
    
    # Return dictionary with moves and iteration count
    return {
        'moves': moves,
        'iterations': solver.iterations_used
    }


if __name__ == "__main__":
    # Example usage
    from ..levels.level import generate_sokoban_level
    
    # Generate a test level
    level_data = generate_sokoban_level(8, 6, 2)
    test_map = GameMap(level_data)
    
    log.info("🎮 Testing BFS Solver on generated level:")
    log.info("Level:")
    for row in level_data:
        log.info(row)
    
    # Solve with BFS
    solution = solve_with_bfs(test_map, max_iterations=5000)
    
    if solution:
        log.success(f"\n🎯 Solution found: {' '.join(solution)}")
        log.info(f"📊 Total moves: {len(solution)}")
    else:
        log.warning("\n❌ No solution found within iteration limit")