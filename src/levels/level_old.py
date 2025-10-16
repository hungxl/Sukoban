"""
Sokoban Level Generator
Based on the ProceduralSokoban algorithm from Dagobah0/ProceduralSokoban
Uses template-based generation with post-processing optimization.
"""

import random
from enum import Enum

# Add logging
from ..log.logger import get_logger, log_function_call, log_performance

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
    """Template class for 5x5 level pieces"""

    def __init__(self, template_data: list[list[CellType]]):
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
    def get_all_templates() -> list[Template]:
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
        self.map: list[list[CellType]] = []
        self.floor_cell_count = 0
    
    def generate(self) -> list[str]:
        """Generate a complete level and return as string list"""
        log.info("🏗️ Generating level with template placement...")
        
        # Step 1: Initialize empty map
        self._initialize_map()
        
        # Step 2: Place border walls
        self._create_border_walls()
        
        # Step 3: Place templates in 3x3 grid pattern
        self._place_templates()
        
        # Step 4: Post-processing optimization
        if self._post_process():
            return self._to_string_representation()
        else:
            log.warning("⚠️ Post-processing failed, using fallback level")
            return self._generate_fallback_level()
    
    def _initialize_map(self):
        """Initialize the map with NULL cells"""
        self.map = []
        self.floor_cell_count = 0
        for x in range(self.width):
            row = []
            for y in range(self.height):
                row.append(CellType.NULL)
            self.map.append(row)
    
    def _create_border_walls(self):
        """Create wall borders around the level"""
        # Top and bottom borders
        for x in range(self.width):
            self.map[0][x] = CellType.WALL
            self.map[self.height - 1][x] = CellType.WALL
        
        # Left and right borders
        for y in range(1, self.height - 1):
            self.map[y][0] = CellType.WALL
            self.map[y][self.width - 1] = CellType.WALL
    
    def _place_templates(self):
        """Place templates in a 3x3 grid pattern"""
        attempt = 0
        max_attempts = 100
        
        # Place templates every 3 cells
        for x in range(1, self.width - 2, 3):
            for y in range(1, self.height - 2, 3):
                template = TemplateLibrary.get_random_template()
                template.random_rotation()
                
                # Try to place template with compatibility checking
                while not self._placement_allowed(template, x, y) and attempt < max_attempts:
                    template = TemplateLibrary.get_random_template()
                    template.random_rotation()
                    attempt += 1
                
                if attempt >= max_attempts:
                    log.warning("⚠️ Max template placement attempts reached")
                    break
                
                self._place_template(template, x, y)
    
    def _placement_allowed(self, template: Template, x: int, y: int) -> bool:
        """Check if template can be placed at position without conflicts"""
        # Check boundaries around template for compatibility
        for i in range(-1, 4):
            if x + i >= 0 and x + i < self.width:
                # Check upper and lower boundaries
                upper_y, lower_y = y - 1, y + 3
                if 0 <= upper_y < self.height and 0 <= lower_y < self.height:
                    upper_cell_map = self.map[upper_y][x + i]
                    lower_cell_map = self.map[lower_y][x + i]
                    upper_cell_template = template.get_cell(i + 1, 0)
                    lower_cell_template = template.get_cell(i + 1, 4)
                    
                    if (upper_cell_map != CellType.NULL or lower_cell_map != CellType.NULL):
                        if (upper_cell_template != CellType.NULL and lower_cell_template != CellType.NULL):
                            if (upper_cell_template != upper_cell_map or lower_cell_template != lower_cell_map):
                                return False
        
        # Check left and right boundaries
        for j in range(4):
            if y + j < self.height:
                left_x, right_x = x - 1, x + 3
                if 0 <= left_x < self.width and 0 <= right_x < self.width:
                    left_cell_map = self.map[y + j][left_x]
                    right_cell_map = self.map[y + j][right_x]
                    left_cell_template = template.get_cell(0, j + 1)
                    right_cell_template = template.get_cell(4, j + 1)
                    
                    if (left_cell_map != CellType.NULL or right_cell_map != CellType.NULL):
                        if (left_cell_template != CellType.NULL and right_cell_template != CellType.NULL):
                            if (left_cell_template != left_cell_map or right_cell_template != right_cell_map):
                                return False
        
        return True
    
    def _place_template(self, template: Template, x: int, y: int):
        """Place template at specified position"""
        for i in range(-1, 4):
            for j in range(-1, 4):
                map_x, map_y = x + i, y + j
                if 0 < map_x < self.width - 1 and 0 < map_y < self.height - 1:
                    cell = template.get_cell(i + 1, j + 1)
                    if cell != CellType.NULL:
                        if cell == CellType.FLOOR:
                            self.floor_cell_count += 1
                        self.map[map_y][map_x] = cell
    
    def _post_process(self) -> bool:
        """Post-process the level: clean, optimize, and place objects"""
        try:
            # Clean up level structure
            self._clean_dead_cells()
            if not self._clean_useless_rooms():
                return False
            self._clean_alone_walls()
            self._clean_dead_cells()
            
            # Place game objects
            if not self._spawn_crates(self.crates_count):
                return False
            if not self._spawn_goals(self.crates_count):
                return False
            if not self._spawn_player():
                return False
            
            return True
        except Exception as e:
            log.error(f"❌ Post-processing failed: {e}")
            return False
    
    def _clean_dead_cells(self):
        """Replace dead-end cells (surrounded by 3+ walls) with walls"""
        for x in range(1, self.width - 1):
            for y in range(1, self.height - 1):
                if self.map[y][x] == CellType.FLOOR:
                    wall_count = 0
                    wall_count += 1 if self.map[y - 1][x] == CellType.WALL else 0
                    wall_count += 1 if self.map[y + 1][x] == CellType.WALL else 0
                    wall_count += 1 if self.map[y][x - 1] == CellType.WALL else 0
                    wall_count += 1 if self.map[y][x + 1] == CellType.WALL else 0
                    
                    if wall_count >= 3:
                        self.map[y][x] = CellType.WALL
    
    def _clean_useless_rooms(self) -> bool:
        """Keep only the largest connected room, fill others with walls"""
        filled_floor = 0
        attempt = 0
        
        # Find a random starting point
        start_x = self.rand.randint(1, self.width - 2)
        start_y = self.rand.randint(1, self.height - 2)
        
        while filled_floor < int(self.floor_cell_count * 0.5):
            # Convert any previously filled floors back to walls
            self._cell_to_wall(CellType.FLOOR_FILLED)
            
            # Find a floor tile to start flood fill
            while self.map[start_y][start_x] != CellType.FLOOR:
                start_x = self.rand.randint(1, self.width - 2)
                start_y = self.rand.randint(1, self.height - 2)
                attempt += 1
                if attempt > self.width * self.height:
                    return False
            
            # Flood fill to mark the largest room
            filled_floor += self._flood_fill(CellType.FLOOR, CellType.FLOOR_FILLED, start_x, start_y)
        
        # Convert unmarked floors to walls and marked floors back to floors
        for x in range(1, self.width - 1):
            for y in range(1, self.height - 1):
                if self.map[y][x] == CellType.FLOOR:
                    self.map[y][x] = CellType.WALL
                elif self.map[y][x] == CellType.FLOOR_FILLED:
                    self.map[y][x] = CellType.FLOOR
        
        return True
    
    def _flood_fill(self, target: CellType, replace: CellType, x: int, y: int) -> int:
        """Flood fill algorithm to mark connected areas"""
        if target == replace or self.map[y][x] != target:
            return 0
        
        self.map[y][x] = replace
        filled = 1
        
        # Check all 4 directions
        if x + 1 < self.width - 1:
            filled += self._flood_fill(target, replace, x + 1, y)
        if x - 1 > 0:
            filled += self._flood_fill(target, replace, x - 1, y)
        if y + 1 < self.height - 1:
            filled += self._flood_fill(target, replace, x, y + 1)
        if y - 1 > 0:
            filled += self._flood_fill(target, replace, x, y - 1)
        
        return filled
    
    def _cell_to_wall(self, cell_type: CellType):
        """Convert all cells of given type to walls"""
        for x in range(1, self.width - 1):
            for y in range(1, self.height - 1):
                if self.map[y][x] == cell_type:
                    self.map[y][x] = CellType.WALL
    
    def _clean_alone_walls(self):
        """Remove isolated walls (surrounded by 7+ floor cells) with probability"""
        for x in range(1, self.width - 1):
            for y in range(1, self.height - 1):
                if self.map[y][x] == CellType.WALL:
                    floor_count = 0
                    # Check all 8 directions
                    for dx in [-1, 0, 1]:
                        for dy in [-1, 0, 1]:
                            if dx == 0 and dy == 0:
                                continue
                            nx, ny = x + dx, y + dy
                            if 0 <= nx < self.width and 0 <= ny < self.height:
                                if self.map[ny][nx] == CellType.FLOOR:
                                    floor_count += 1
                    
                    # Remove wall with 30% probability if surrounded by many floors
                    if floor_count > 6 and self.rand.randint(0, 99) < 30:
                        self.map[y][x] = CellType.FLOOR
    
    def _spawn_crates(self, n: int) -> bool:
        """Spawn crates on valid floor positions"""
        attempt = 0
        max_attempts = self.floor_cell_count * 2
        
        for i in range(n):
            while attempt < max_attempts:
                x = self.rand.randint(2, self.width - 3)
                y = self.rand.randint(2, self.height - 3)
                
                if self.map[y][x] == CellType.FLOOR:
                    # Check that crate won't be stuck (not surrounded by too many walls)
                    wall_count = 0
                    wall_count += 1 if self.map[y - 1][x] == CellType.WALL else 0
                    wall_count += 1 if self.map[y + 1][x] == CellType.WALL else 0
                    wall_count += 1 if self.map[y][x - 1] == CellType.WALL else 0
                    wall_count += 1 if self.map[y][x + 1] == CellType.WALL else 0
                    
                    if wall_count < 2:  # Ensure crate can be pushed
                        self.map[y][x] = CellType.CRATE
                        break
                
                attempt += 1
            
            if attempt >= max_attempts:
                log.warning(f"⚠️ Could not place all crates, placed {i}")
                return i > 0  # Return true if at least one crate was placed
        
        return True
    
    def _spawn_goals(self, n: int) -> bool:
        """Spawn goal positions with valid push space"""
        attempt = 0
        max_attempts = self.floor_cell_count * 2
        
        for i in range(n):
            while attempt < max_attempts:
                x = self.rand.randint(1, self.width - 2)
                y = self.rand.randint(1, self.height - 2)
                
                if self.map[y][x] == CellType.FLOOR:
                    # Check that there's valid push space (2 consecutive floor cells in at least one direction)
                    valid_goal = False
                    
                    # Check all 4 directions for 2 consecutive floors
                    directions = [(0, 1), (0, -1), (1, 0), (-1, 0)]
                    for dx, dy in directions:
                        x1, y1 = x + dx, y + dy
                        x2, y2 = x + 2 * dx, y + 2 * dy
                        if (0 <= x1 < self.width and 0 <= y1 < self.height and
                            0 <= x2 < self.width and 0 <= y2 < self.height):
                            if self.map[y1][x1] == CellType.FLOOR and self.map[y2][x2] == CellType.FLOOR:
                                valid_goal = True
                                break
                    
                    if valid_goal:
                        self.map[y][x] = CellType.GOAL
                        break
                
                attempt += 1
            
            if attempt >= max_attempts:
                log.warning(f"⚠️ Could not place all goals, placed {i}")
                return i > 0
        
        return True
    
    def _spawn_player(self) -> bool:
        """Spawn player on a random floor position"""
        attempt = 0
        max_attempts = self.floor_cell_count
        
        while attempt < max_attempts:
            x = self.rand.randint(1, self.width - 2)
            y = self.rand.randint(1, self.height - 2)
            
            if self.map[y][x] == CellType.FLOOR:
                self.map[y][x] = CellType.PLAYER
                return True
            
            attempt += 1
        
        log.error("❌ Could not place player")
        return False
    
    def _to_string_representation(self) -> list[str]:
        """Convert the map to string representation for the game"""
        result = []
        
        for y in range(self.height):
            row = ""
            for x in range(self.width):
                cell = self.map[y][x]
                
                if cell == CellType.WALL:
                    row += "#"
                elif cell == CellType.FLOOR:
                    row += " "
                elif cell == CellType.CRATE:
                    row += "$"
                elif cell == CellType.GOAL:
                    row += "."
                elif cell == CellType.PLAYER:
                    row += "@"
                else:  # NULL or other
                    row += "#"  # Default to wall
            
            result.append(row)
        
        return result
    
    def _generate_fallback_level(self) -> list[str]:
        """Generate a simple fallback level if main generation fails"""
        log.info("🔄 Generating fallback level...")
        return generate_simple_level(self.width, self.height, self.crates_count)


class Level:
    """Main Level class that integrates with the existing game system"""
    
    def __init__(self, size: int = 10, num_boxes: int = 3) -> None:
        self.size = min(max(size, 7), 15)  # Minimum size of 7, maximum of 15
        self.num_boxes = max(num_boxes, 1)  # Minimum 1 box
        self.width = self.size
        self.height = self.size

    def generate_level(self) -> list[str]:
        """Generate a new Sokoban level using the procedural algorithm"""
        return generate_sokoban_level(self.width, self.height, self.num_boxes)
    
    def generate_simple_level(self) -> list[str]:
        """Generate a simple fallback level"""
        return generate_simple_level(self.width, self.height, self.num_boxes)


@log_performance
def generate_sokoban_level(width: int = 10, height: int = 10, 
                          num_boxes: int = 3) -> list[str]:
    """
    Generate a new Sokoban level using the ProceduralSokoban algorithm
    
    Args:
        width: Level width (will be adjusted to fit template grid)
        height: Level height (will be adjusted to fit template grid)
        num_boxes: Number of boxes/targets
        
    Returns:
        list of strings representing the level
    """
    max_attempts = 5
    
    for attempt in range(max_attempts):
        try:
            log.info(f"🎲 Generation attempt {attempt + 1}/{max_attempts}")
            generator = ProceduralSokobanGenerator(num_boxes)
            level_data = generator.generate()
            
            if level_data and len(level_data) > 0:
                log.success(f"✅ Level generated successfully on attempt {attempt + 1}")
                return level_data
                
        except Exception as e:
            log.warning(f"⚠️ Generation attempt {attempt + 1} failed: {e}")
            continue
    
    # Fallback: return a simple valid level
    log.warning("⚠️ All generation attempts failed, using simple fallback")
    return generate_simple_level(width, height, num_boxes)


def generate_simple_level(width: int, height: int, num_boxes: int) -> list[str]:
    """Generate a simple fallback level if generation fails"""
    log.info("🏗️ Generating simple fallback level...")
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
    positions = [(player_x + 2, player_y), (player_x - 2, player_y), 
                (player_x, player_y + 2), (player_x, player_y - 2)]
    
    for i in range(min(num_boxes, len(positions))):
        x, y = positions[i]
        if 1 <= x < width - 1 and 1 <= y < height - 1:
            level_grid[y][x] = "$"  # Box
            # Place target in opposite direction from player
            if x > player_x:
                target_x = max(1, x - 3)
            elif x < player_x:
                target_x = min(width - 2, x + 3)
            else:
                target_x = x
                
            if y > player_y:
                target_y = max(1, y - 3)
            elif y < player_y:
                target_y = min(height - 2, y + 3)
            else:
                target_y = y
                
            if 1 <= target_x < width - 1 and 1 <= target_y < height - 1:
                if level_grid[target_y][target_x] == " ":
                    level_grid[target_y][target_x] = "."
    
    # Convert back to strings
    return [''.join(row) for row in level_grid]