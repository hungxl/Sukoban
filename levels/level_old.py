"""
Sokoban Level Generator
Based on the ProceduralSokoban algorithm from Dagobah0/ProceduralSokoban
Uses template-based generation with post-processing optimization.
"""

import random
from typing import List, Tuple, Optional
from enum import Enum
from dataclasses import dataclass
import copy

# Add logging
from log.logger import get_logger, log_function_call, log_performance, catch_and_log

# Get logger for this module
log = get_logger(__name__)


class CellType(Enum):
    """Types of cells in the level grid"""
    NULL = "null"
    WALL = "#"
    FLOOR = " "
    FLOOR_FILLED = "filled"  # Temporary for optimization
    CRATE = "$"
    GOAL = "."
    PLAYER = "@"


class Template:
    """Template class for 3x3 level pieces"""
    
    def __init__(self, template_data: List[List[CellType]]):
        """Initialize template with 2D array of CellType"""
        self.template = []
        for row in template_data:
            new_row = []
            for cell in row:
                new_row.append(cell)
            self.template.append(new_row)
    
    def get_cell(self, x: int, y: int) -> CellType:
        """Get cell at coordinates"""
        if 0 <= x < len(self.template) and 0 <= y < len(self.template[0]):
            return self.template[x][y]
        return CellType.NULL
    
    def random_rotation(self):
        """Apply random rotation (0-3 times)"""
        rotations = random.randint(0, 3)
        for _ in range(rotations):
            self._rotate()
    
    def _rotate(self):
        """Rotate template 90 degrees clockwise"""
        if not self.template:
            return
            
        rows = len(self.template)
        cols = len(self.template[0])
        
        # Create new template
        rotated = [[CellType.NULL for _ in range(rows)] for _ in range(cols)]
        
        # Rotate 90 degrees clockwise
        for i in range(rows):
            for j in range(cols):
                rotated[j][rows - 1 - i] = self.template[i][j]
        
        self.template = rotated


class TemplateLibrary:
    """Library of predefined templates based on Ian Parberry's research"""
    
    @staticmethod
    def get_all_templates() -> List[Template]:
        """Get all available templates"""
        templates = []
        
        # Template 1: Simple 3x3 floor area
        t1 = [
            [CellType.NULL, CellType.NULL, CellType.NULL, CellType.NULL, CellType.NULL],
            [CellType.NULL, CellType.FLOOR, CellType.FLOOR, CellType.FLOOR, CellType.NULL],
            [CellType.NULL, CellType.FLOOR, CellType.FLOOR, CellType.FLOOR, CellType.NULL],
            [CellType.NULL, CellType.FLOOR, CellType.FLOOR, CellType.FLOOR, CellType.NULL],
            [CellType.NULL, CellType.NULL, CellType.NULL, CellType.NULL, CellType.NULL],
        ]
        templates.append(Template(t1))
        
        # Template 2: Corner wall
        t2 = [
            [CellType.NULL, CellType.NULL, CellType.NULL, CellType.NULL, CellType.NULL],
            [CellType.NULL, CellType.WALL, CellType.FLOOR, CellType.FLOOR, CellType.NULL],
            [CellType.NULL, CellType.FLOOR, CellType.FLOOR, CellType.FLOOR, CellType.NULL],
            [CellType.NULL, CellType.FLOOR, CellType.FLOOR, CellType.FLOOR, CellType.NULL],
            [CellType.NULL, CellType.NULL, CellType.NULL, CellType.NULL, CellType.NULL],
        ]
        templates.append(Template(t2))
        
        # Template 3: L-shaped corridor
        t3 = [
            [CellType.NULL, CellType.NULL, CellType.NULL, CellType.FLOOR, CellType.FLOOR],
            [CellType.NULL, CellType.WALL, CellType.WALL, CellType.FLOOR, CellType.FLOOR],
            [CellType.NULL, CellType.FLOOR, CellType.FLOOR, CellType.FLOOR, CellType.NULL],
            [CellType.NULL, CellType.FLOOR, CellType.FLOOR, CellType.FLOOR, CellType.NULL],
            [CellType.NULL, CellType.NULL, CellType.NULL, CellType.NULL, CellType.NULL],
        ]
        templates.append(Template(t3))
        
        # Template 4: U-shaped room
        t4 = [
            [CellType.NULL, CellType.NULL, CellType.NULL, CellType.NULL, CellType.NULL],
            [CellType.NULL, CellType.WALL, CellType.WALL, CellType.WALL, CellType.NULL],
            [CellType.NULL, CellType.FLOOR, CellType.FLOOR, CellType.FLOOR, CellType.NULL],
            [CellType.NULL, CellType.FLOOR, CellType.FLOOR, CellType.FLOOR, CellType.NULL],
            [CellType.NULL, CellType.NULL, CellType.NULL, CellType.NULL, CellType.NULL],
        ]
        templates.append(Template(t4))
        
        # Template 5: Corner room
        t5 = [
            [CellType.NULL, CellType.NULL, CellType.NULL, CellType.NULL, CellType.NULL],
            [CellType.NULL, CellType.WALL, CellType.WALL, CellType.WALL, CellType.NULL],
            [CellType.NULL, CellType.WALL, CellType.FLOOR, CellType.FLOOR, CellType.NULL],
            [CellType.NULL, CellType.WALL, CellType.FLOOR, CellType.FLOOR, CellType.NULL],
            [CellType.NULL, CellType.NULL, CellType.NULL, CellType.NULL, CellType.NULL],
        ]
        templates.append(Template(t5))
        
        # Template 6: Cross pattern
        t6 = [
            [CellType.NULL, CellType.NULL, CellType.FLOOR, CellType.NULL, CellType.NULL],
            [CellType.NULL, CellType.WALL, CellType.FLOOR, CellType.FLOOR, CellType.NULL],
            [CellType.FLOOR, CellType.FLOOR, CellType.FLOOR, CellType.FLOOR, CellType.NULL],
            [CellType.NULL, CellType.WALL, CellType.FLOOR, CellType.WALL, CellType.NULL],
            [CellType.NULL, CellType.NULL, CellType.NULL, CellType.NULL, CellType.NULL],
        ]
        templates.append(Template(t6))
        
        # Template 7: Side corridor
        t7 = [
            [CellType.NULL, CellType.NULL, CellType.NULL, CellType.NULL, CellType.NULL],
            [CellType.NULL, CellType.WALL, CellType.FLOOR, CellType.FLOOR, CellType.NULL],
            [CellType.FLOOR, CellType.FLOOR, CellType.FLOOR, CellType.FLOOR, CellType.NULL],
            [CellType.NULL, CellType.WALL, CellType.FLOOR, CellType.FLOOR, CellType.NULL],
            [CellType.NULL, CellType.NULL, CellType.NULL, CellType.NULL, CellType.NULL],
        ]
        templates.append(Template(t7))
        
        # Template 8: Plus pattern  
        t8 = [
            [CellType.NULL, CellType.NULL, CellType.FLOOR, CellType.NULL, CellType.NULL],
            [CellType.NULL, CellType.WALL, CellType.FLOOR, CellType.WALL, CellType.NULL],
            [CellType.FLOOR, CellType.FLOOR, CellType.FLOOR, CellType.FLOOR, CellType.FLOOR],
            [CellType.NULL, CellType.WALL, CellType.FLOOR, CellType.WALL, CellType.NULL],
            [CellType.NULL, CellType.NULL, CellType.FLOOR, CellType.NULL, CellType.NULL],
        ]
        templates.append(Template(t8))
        
        return templates
    
    @staticmethod
    def get_random_template() -> Template:
        """Get a random template from the library"""
        templates = TemplateLibrary.get_all_templates()
        return random.choice(templates)


class ProceduralSokobanGenerator:
    """Template-based Sokoban level generator based on ProceduralSokoban algorithm"""
    
    @log_function_call("INFO")
    def __init__(self, crates: int = 2):
        """Initialize generator with specified number of crates"""
        log.info(f"🎲 Creating procedural level generator with {crates} crates")
        self.rand = random.Random()
        self.crates_count = crates
        self.width = self.rand.randint(2, 4) * 3 + 2  # 8, 11, or 14
        self.height = self.width
        self.map: List[List[CellType]] = []
        self.floor_cell_count = 0
    
    def _initialize_nodes(self):
        """Initialize the node grid - all walls initially"""
        self.nodes = []
        for x in range(self.width):
            row = []
            for y in range(self.height):
                row.append(Node(x=x, y=y, wall=True))
            self.nodes.append(row)
    
    def _define_allowed_spots(self):
        """Define spots where objects can be placed (inner area only)"""
        self.allowed_spots = []
        for x in range(2, self.width - 2):
            for y in range(2, self.height - 2):
                self.allowed_spots.append(self.nodes[x][y])
    
    def _place_objects(self, num_boxes: int):
        """Place buttons, boxes, and player randomly"""
        # Place buttons first
        for i in range(num_boxes):
            pos = self._get_random_spot()
            if pos:
                button = GeneratedButton(pos[0], pos[1])
                self.buttons.append(button)
        
        # Place boxes
        for i in range(min(num_boxes, len(self.buttons))):
            pos = self._get_random_spot()
            if pos:
                box = GeneratedBox(pos[0], pos[1], pos[0], pos[1])
                box.solve_button = self.buttons[i]
                self.boxes.append(box)
                self.nodes[pos[0]][pos[1]].has_box = True
                self.nodes[pos[0]][pos[1]].occupied = True
        
        # Place player
        pos = self._get_random_spot()
        if pos is None and self.buttons:
            # Fallback to button position
            pos = (self.buttons[0].x, self.buttons[0].y)
        
        if pos:
            self.player_x = pos[0]
            self.player_y = pos[1]
            self.player_start_x = pos[0]
            self.player_start_y = pos[1]
    
    def _get_random_spot(self) -> Optional[Tuple[int, int]]:
        """Get a random unoccupied spot and make it floor"""
        if not self.allowed_spots:
            return None
            
        while self.allowed_spots:
            spot = random.choice(self.allowed_spots)
            self.allowed_spots.remove(spot)
            
            x, y = spot.x, spot.y
            self.nodes[x][y].wall = False
            
            # Check if spot would create blockade
            if not self._is_blockaded(x, y):
                return (x, y)
        
        return None
    
    def _is_blockaded(self, x: int, y: int) -> bool:
        """Check if position would be blockaded by boxes"""
        # Simplified blockade check
        box_neighbors = 0
        for dx, dy in [(1, 0), (-1, 0), (0, 1), (0, -1)]:
            nx, ny = x + dx, y + dy
            if (0 <= nx < self.width and 0 <= ny < self.height and
                self.nodes[nx][ny].has_box):
                box_neighbors += 1
        
        return box_neighbors >= 3
    
    def random_rip(self, amount: int):
        """Randomly remove walls from the level"""
        for _ in range(amount):
            pos = self._get_random_spot()
            if pos is None:
                break
    
    @log_performance
    @catch_and_log(level="ERROR", message="Level generation failed")
    def generate_paths(self):
        """Generate level by solving it and removing walls on the path"""
        log.info(f"🔧 Starting level generation process")
        steps = 0
        max_steps = 4000
        
        # Create ghost boxes for solving
        ghost_boxes = self._copy_boxes()
        log.debug(f"👻 Created {len(ghost_boxes)} ghost boxes for solving")
        
        while self.solve_counter > 0 and steps < max_steps:
            # Calculate paths from all boxes to their buttons
            box_paths = self._calculate_box_paths(ghost_boxes)
            
            # Calculate player paths and choose best one
            player_paths_result = self._calculate_player_paths(ghost_boxes, box_paths)
            player_paths, best_path_idx = player_paths_result
            
            if best_path_idx == -1:
                self.is_trash = True
                break
            
            player_path = player_paths[best_path_idx][0]
            box_path = box_paths[best_path_idx][0]
            
            # Remove walls on player's path
            for node in player_path:
                node.wall = False
                if node.occupied:
                    self.is_trash = True
                    return
            
            # Move box towards solution
            if box_path:
                box = ghost_boxes[best_path_idx]
                current_node = box_path[0]
                diff_x = current_node.x - box.x
                diff_y = current_node.y - box.y
                
                # Find how far to push in straight line
                stop_idx = 0
                if len(box_path) > 1:
                    for i in range(1, len(box_path)):
                        next_node = box_path[i]
                        if (diff_x == next_node.x - current_node.x and
                            diff_y == next_node.y - current_node.y):
                            current_node = next_node
                        else:
                            stop_idx = i - 1
                            break
                
                # Remove walls on box path
                for i in range(stop_idx + 1):
                    box_path[i].wall = False
                
                # Update box position
                self.nodes[box.x][box.y].occupied = False
                box.set_position(box_path[stop_idx].x, box_path[stop_idx].y)
                self.nodes[box.x][box.y].occupied = True
                
                # Update player position
                self.player_x = box.x - diff_x
                self.player_y = box.y - diff_y
                
                # Check if box is now on button
                if (box.solve_button and box.x == box.solve_button.x and 
                    box.y == box.solve_button.y):
                    box.placed = True
                    self.solve_counter -= 1
                    ghost_boxes.remove(box)
            
            steps += 1
        
        # Reset player to start position
        self.player_x = self.player_start_x
        self.player_y = self.player_start_y
        
        if steps >= max_steps:
            self.is_trash = True
    
    def _copy_boxes(self) -> List[GeneratedBox]:
        """Create a copy of boxes for solving simulation"""
        ghost_boxes = []
        for box in self.boxes:
            new_box = GeneratedBox(box.x, box.y, box.x, box.y)
            new_box.solve_button = box.solve_button
            ghost_boxes.append(new_box)
        return ghost_boxes
    
    def _calculate_box_paths(self, ghost_boxes: List[GeneratedBox]) -> List[Tuple[List[Node], int]]:
        """Calculate paths from each box to its target button"""
        box_paths = []
        for box in ghost_boxes:
            if not box.solve_button:
                box_paths.append(([], 999999))
                continue
                
            # Temporarily mark box position as free
            self.nodes[box.x][box.y].occupied = False
            
            pathfinder = Pathfinder(
                self.nodes, box.x, box.y,
                box.solve_button.x, box.solve_button.y
            )
            path_result = pathfinder.find_path(is_box=True)
            box_paths.append(path_result)
            
            # Restore box occupation
            self.nodes[box.x][box.y].occupied = True
        
        return box_paths
    
    def _calculate_player_paths(self, ghost_boxes: List[GeneratedBox], 
                              box_paths: List[Tuple[List[Node], int]]) -> Tuple[List[Tuple[List[Node], int]], int]:
        """Calculate player paths to each box and return best one"""
        player_paths = []
        best_path = -1
        lowest_cost = 999999
        
        for i, box in enumerate(ghost_boxes):
            if not box_paths[i][0]:  # No path found for this box
                continue
                
            # Calculate where player needs to be to push box
            first_box_move = box_paths[i][0][0]
            
            # Determine push direction and required player position
            if first_box_move.x == box.x + 1:
                new_x, new_y = box.x - 1, box.y
            elif first_box_move.x == box.x - 1:
                new_x, new_y = box.x + 1, box.y
            elif first_box_move.y == box.y + 1:
                new_x, new_y = box.x, box.y - 1
            else:
                new_x, new_y = box.x, box.y + 1
            
            # Find path for player
            pathfinder = Pathfinder(
                self.nodes, self.player_x, self.player_y, new_x, new_y
            )
            player_path = pathfinder.find_path(is_box=False)
            player_paths.append(player_path)
            
            if player_path[1] < lowest_cost:
                lowest_cost = player_path[1]
                best_path = i
        
        return player_paths, best_path
    
    def optimize(self, iterations: int = 500):
        """Optimize level by removing unnecessary free spaces"""
        # This is a simplified version of the optimization algorithm
        # The full version would solve the level multiple times and track unused nodes
        
        max_unnecessary = []
        min_destroy_wall = []
        
        for iteration in range(iterations):
            # Reset tracking
            for row in self.nodes:
                for node in row:
                    node.used = False
            
            # Simulate solving and mark used nodes
            self._simulate_solve_and_mark_used()
            
            # Find unnecessary nodes
            unnecessary = []
            for row in self.nodes:
                for node in row:
                    if not node.wall and not node.used:
                        unnecessary.append(node)
            
            # Track best optimization
            if len(unnecessary) > len(max_unnecessary):
                max_unnecessary = unnecessary[:]
        
        # Apply optimization by making unnecessary spaces into walls
        for node in max_unnecessary[:len(max_unnecessary)//2]:  # Only remove half for playability
            node.wall = True
    
    def _simulate_solve_and_mark_used(self):
        """Simulate solving the level and mark used nodes"""
        # Simplified: just mark button positions and a basic path
        for button in self.buttons:
            if (0 <= button.x < self.width and 0 <= button.y < self.height):
                self.nodes[button.x][button.y].used = True
        
        # Mark player start position
        if (0 <= self.player_start_x < self.width and 
            0 <= self.player_start_y < self.height):
            self.nodes[self.player_start_x][self.player_start_y].used = True
    
    def to_string_representation(self) -> List[str]:
        """Convert generated level to string representation for the game"""
        result = []
        
        for y in range(self.height):
            row = ""
            for x in range(self.width):
                node = self.nodes[x][y]
                
                if node.wall:
                    row += "#"
                else:
                    # Check what's on this floor tile
                    is_player = (x == self.player_start_x and y == self.player_start_y)
                    is_button = any(b.x == x and b.y == y for b in self.buttons)
                    is_box = any(b.x == x and b.y == y for b in self.boxes)
                    
                    if is_player and is_button:
                        row += "+"  # Player on dock
                    elif is_player:
                        row += "@"  # Player on floor
                    elif is_box and is_button:
                        row += "*"  # Box on dock
                    elif is_box:
                        row += "$"  # Box on floor
                    elif is_button:
                        row += "."  # Dock
                    else:
                        row += " "  # Floor
            
            result.append(row)
        
        return result


class Level:
    """Main Level class that integrates with the existing game system"""
    
    def __init__(self, size: int = 10, num_boxes: int = 3) -> None:
        self.size = min(max(size, 7), 10)  # Minimum size of 7, maximum of 10
        self.num_boxes = max(num_boxes, 1)  # Minimum 1 box
        self.width = self.size
        self.height = self.size

    def generate_level(self) -> List[str]:
        """Generate a new Sokoban level using the advanced algorithm"""
        return generate_sokoban_level(self.width, self.height, self.num_boxes)
    
    def generate_simple_level(self) -> List[str]:
        """Generate a simple fallback level"""
        return generate_simple_level(self.width, self.height, self.num_boxes)


def generate_sokoban_level(width: int = 10, height: int = 10, 
                          num_boxes: int = 3, optimize: bool = True) -> List[str]:
    """
    Generate a new Sokoban level using the advanced pathfinding algorithm
    
    Args:
        width: Level width
        height: Level height
        num_boxes: Number of boxes/targets
        optimize: Whether to run optimization
        
    Returns:
        List of strings representing the level
    """
    max_attempts = 10
    
    for attempt in range(max_attempts):
        try:
            generator = SokobanLevelGenerator(width, height, num_boxes)
            
            # Add some random walls removal for variety
            generator.random_rip(random.randint(-2, 5))
            
            # Generate the level
            generator.generate_paths()
            
            if not generator.is_trash:
                if optimize and num_boxes < 6:  # Only optimize smaller levels
                    generator.optimize(random.randint(100, 500))
                
                return generator.to_string_representation()
        except Exception as e:
            # Continue to next attempt if generation fails
            print(f"Generation attempt {attempt + 1} failed: {e}")
            continue
    
    # Fallback: return a simple valid level
    return generate_simple_level(width, height, num_boxes)


def generate_simple_level(width: int, height: int, num_boxes: int) -> List[str]:
    """Generate a simple fallback level if generation fails"""
    level = []
    
    # Create border walls
    for y in range(height):
        row = ""
        for x in range(width):
            if x == 0 or x == width - 1 or y == 0 or y == height - 1:
                row += "#"
            else:
                row += " "
        level.append(row)
    
    # Convert to list of lists for easier manipulation
    level_grid = [list(row) for row in level]
    
    # Place player in center-ish area
    player_x = width // 2
    player_y = height // 2
    level_grid[player_y][player_x] = "@"
    
    # Place boxes and targets nearby
    positions = [(player_x + 1, player_y), (player_x - 1, player_y), 
                (player_x, player_y + 1)]
    
    for i in range(min(num_boxes, len(positions))):
        x, y = positions[i]
        if 1 <= x < width - 1 and 1 <= y < height - 1:
            level_grid[y][x] = "$"  # Box
            # Place target nearby
            target_x = x + (1 if x < width - 2 else -1)
            if 1 <= target_x < width - 1:
                level_grid[y][target_x] = "."
    
    # Convert back to strings
    return [''.join(row) for row in level_grid]