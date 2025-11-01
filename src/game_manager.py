from typing import List, Optional, Dict, Tuple
from .base import Entity, Position, EntityType
from .entities import Wall, Floor, Player, Box, Dock
from .log.logger import get_logger, catch_and_log, log_function_call, log_game_event, log_performance

# Get logger for this module
log = get_logger(__name__)


class GameMap:
    """Manages the game map and entities"""
    
    @log_function_call("INFO")
    def __init__(self, level_data: List[str]):
        log.info(f"🗺️  Initializing game map with {len(level_data)} rows")
        self.width = max(len(line) for line in level_data) if level_data else 0
        self.height = len(level_data)
        self.original_level_data = level_data.copy()
        
        # Entity storage
        self.entities: Dict[Tuple[int, int], List[Entity]] = {}
        self.player: Optional[Player] = None
        self.boxes: List[Box] = []
        self.docks: List[Dock] = []
        
        # Initialize map from level data
        self._parse_level_data(level_data)
        log_game_event(log, f"Game map initialized: {self.width}x{self.height}, entities: {len(self.entities)}")
    
    def _parse_level_data(self, level_data: List[str]):
        """Parse level data and create entities"""
        self.entities.clear()
        self.boxes.clear()
        self.docks.clear()
        self.player = None
        
        for y, row in enumerate(level_data):
            for x, char in enumerate(row):
                position = Position(x, y)
                
                if char == '#':  # Wall
                    self._add_entity(Wall(position))
                elif char == ' ':  # Floor
                    self._add_entity(Floor(position))
                elif char == '.':  # Dock
                    dock = Dock(position)
                    self._add_entity(dock)
                    self.docks.append(dock)
                elif char == '@':  # Player on floor
                    self._add_entity(Floor(position))
                    self.player = Player(position)
                    self._add_entity(self.player)
                elif char == '+':  # Player on dock
                    dock = Dock(position)
                    self._add_entity(dock)
                    self.docks.append(dock)
                    self.player = Player(position)
                    self.player.set_on_dock(True)
                    dock.place_player()
                    self._add_entity(self.player)
                elif char == '$':  # Box on floor
                    self._add_entity(Floor(position))
                    box = Box(position)
                    self._add_entity(box)
                    self.boxes.append(box)
                elif char == '*':  # Box on dock
                    dock = Dock(position)
                    self._add_entity(dock)
                    self.docks.append(dock)
                    box = Box(position)
                    box.set_on_dock(True)
                    dock.place_box()
                    self._add_entity(box)
                    self.boxes.append(box)
                else:  # Unknown character, treat as floor
                    self._add_entity(Floor(position))
    
    def _add_entity(self, entity: Entity):
        """Add entity to the map"""
        pos_tuple = entity.position.to_tuple()
        if pos_tuple not in self.entities:
            self.entities[pos_tuple] = []
        self.entities[pos_tuple].append(entity)
    
    def _remove_entity(self, entity: Entity):
        """Remove entity from the map"""
        pos_tuple = entity.position.to_tuple()
        if pos_tuple in self.entities:
            if entity in self.entities[pos_tuple]:
                self.entities[pos_tuple].remove(entity)
            if not self.entities[pos_tuple]:
                del self.entities[pos_tuple]
    
    def get_entities_at(self, position: Position) -> List[Entity]:
        """Get all entities at the given position"""
        pos_tuple = position.to_tuple()
        return self.entities.get(pos_tuple, [])
    
    def get_top_entity_at(self, position: Position) -> Optional[Entity]:
        """Get the topmost (last added) entity at the given position"""
        entities = self.get_entities_at(position)
        return entities[-1] if entities else None
    
    def get_entity_of_type_at(self, position: Position, entity_type: EntityType) -> Optional[Entity]:
        """Get entity of specific type at the given position"""
        entities = self.get_entities_at(position)
        for entity in entities:
            if entity.entity_type == entity_type:
                return entity
        return None
    
    def is_position_valid(self, position: Position) -> bool:
        """Check if position is within map bounds"""
        return 0 <= position.x < self.width and 0 <= position.y < self.height
    
    def can_move_to(self, position: Position) -> bool:
        """Check if position can be moved to (not blocked by solid entities)"""
        if not self.is_position_valid(position):
            return False
        
        entities = self.get_entities_at(position)
        for entity in entities:
            if entity.is_solid():
                return False
        return True
    
    @log_performance
    @catch_and_log(level="WARNING", message="Player movement failed")
    def move_player(self, direction: str) -> bool:
        """Move player in the given direction (human player - no deadlock detection)"""
        log.debug(f"🎮 Attempting to move player {direction}")
        
        if not self.player:
            log.error("❌ No player found to move")
            return False
        
        # Calculate movement offset
        offsets = {
            'up': (0, -1),
            'down': (0, 1),
            'left': (-1, 0),
            'right': (1, 0)
        }
        
        if direction not in offsets:
            log.warning(f"⚠️ Invalid movement direction: {direction}")
            return False
        
        dx, dy = offsets[direction]
        new_position = Position(self.player.x + dx, self.player.y + dy)
        
        if not self.is_position_valid(new_position):
            return False
        
        # Check what's at the target position
        target_entities = self.get_entities_at(new_position)
        
        # Check for walls
        for entity in target_entities:
            if entity.entity_type == EntityType.WALL:
                return False
        
        # Check for boxes
        box_at_target = None
        for entity in target_entities:
            if isinstance(entity, Box):
                box_at_target = entity
                break
        
        if box_at_target:
            # Try to push the box (no deadlock detection for human player)
            box_new_position = Position(new_position.x + dx, new_position.y + dy)
            if not self._can_push_box(box_at_target, box_new_position):
                return False
            
            # Move the box
            self._move_box(box_at_target, box_new_position)
            self.player.push_box(log_action=True)  # Log for human player
        
        # Move the player (with logging for human player)
        self._move_player_to(new_position, log_action=True)
        return True
    
    @catch_and_log(level="WARNING", message="Bot movement failed")
    def move_player_bot(self, direction: str) -> bool:
        """Move player in the given direction (bot algorithms - with deadlock detection)"""
        # Removed excessive debug logging for bot moves to reduce log volume
        
        if not self.player:
            log.error("❌ No player found to move")
            return False
        
        # Calculate movement offset
        offsets = {
            'up': (0, -1),
            'down': (0, 1),
            'left': (-1, 0),
            'right': (1, 0)
        }
        
        if direction not in offsets:
            log.warning(f"⚠️ Invalid movement direction: {direction}")
            return False
        
        dx, dy = offsets[direction]
        new_position = Position(self.player.x + dx, self.player.y + dy)
        
        if not self.is_position_valid(new_position):
            return False
        
        # Check what's at the target position
        target_entities = self.get_entities_at(new_position)
        
        # Check for walls
        for entity in target_entities:
            if entity.entity_type == EntityType.WALL:
                return False
        
        # Check for boxes
        box_at_target = None
        for entity in target_entities:
            if isinstance(entity, Box):
                box_at_target = entity
                break
        
        if box_at_target:
            # Try to push the box (WITH deadlock detection for bot)
            box_new_position = Position(new_position.x + dx, new_position.y + dy)
            if not self._can_push_box_with_deadlock_detection(box_at_target, box_new_position):
                return False
            
            # Move the box
            self._move_box(box_at_target, box_new_position)
            self.player.push_box(log_action=False)  # No logging for bot
        
        # Move the player (no logging for bot to reduce log volume)
        self._move_player_to(new_position, log_action=False)
        return True
    
    def _can_push_box(self, box: Box, new_position: Position) -> bool:
        """Check if box can be pushed to the new position (no deadlock detection for human player)"""
        if not self.is_position_valid(new_position):
            return False
        
        # Check for solid entities at target position
        entities = self.get_entities_at(new_position)
        for entity in entities:
            if entity.is_solid():
                return False
        
        return True
    
    def _is_box_in_corner(self, position: Position) -> bool:
        """Check if position is in a corner with walls (based on reference check_in_corner)"""
        x, y = position.x, position.y
        
        # Check all 4 diagonal corners
        # Top-left corner (x-1, y-1)
        if self.get_entity_of_type_at(Position(x - 1, y - 1), EntityType.WALL):
            if (self.get_entity_of_type_at(Position(x - 1, y), EntityType.WALL) and 
                self.get_entity_of_type_at(Position(x, y - 1), EntityType.WALL)):
                return True
        
        # Bottom-left corner (x-1, y+1)
        if self.get_entity_of_type_at(Position(x - 1, y + 1), EntityType.WALL):
            if (self.get_entity_of_type_at(Position(x - 1, y), EntityType.WALL) and 
                self.get_entity_of_type_at(Position(x, y + 1), EntityType.WALL)):
                return True
        
        # Top-right corner (x+1, y-1)
        if self.get_entity_of_type_at(Position(x + 1, y - 1), EntityType.WALL):
            if (self.get_entity_of_type_at(Position(x + 1, y), EntityType.WALL) and 
                self.get_entity_of_type_at(Position(x, y - 1), EntityType.WALL)):
                return True
        
        # Bottom-right corner (x+1, y+1)
        if self.get_entity_of_type_at(Position(x + 1, y + 1), EntityType.WALL):
            if (self.get_entity_of_type_at(Position(x + 1, y), EntityType.WALL) and 
                self.get_entity_of_type_at(Position(x, y + 1), EntityType.WALL)):
                return True
        
        return False
    
    def _is_box_can_be_moved(self, position: Position) -> bool:
        """Check if a box at position can be moved in at least one direction (based on reference is_box_can_be_moved)"""
        x, y = position.x, position.y
        
        # Helper to check if position is walkable or has player
        def is_walkable(pos: Position) -> bool:
            if not self.is_position_valid(pos):
                return False
            entities = self.get_entities_at(pos)
            for entity in entities:
                if entity.entity_type == EntityType.WALL or entity.entity_type == EntityType.BOX:
                    return False
            return True
        
        # Check left-right movement
        left = Position(x - 1, y)
        right = Position(x + 1, y)
        if (is_walkable(left) or self.player and self.player.position == left) and is_walkable(right):
            return True
        if (is_walkable(right) or self.player and self.player.position == right) and is_walkable(left):
            return True
        
        # Check up-down movement
        up = Position(x, y - 1)
        down = Position(x, y + 1)
        if (is_walkable(up) or self.player and self.player.position == up) and is_walkable(down):
            return True
        if (is_walkable(down) or self.player and self.player.position == down) and is_walkable(up):
            return True
        
        return False
    
    def _is_all_boxes_stuck(self) -> bool:
        """Check if all boxes are stuck (based on reference is_all_boxes_stuck)"""
        for box in self.boxes:
            # If box is on dock, not all stuck
            if box.on_dock:
                return False
            # If box can be moved, not all stuck
            if self._is_box_can_be_moved(box.position):
                return False
        return True
    
    def _can_push_box_with_deadlock_detection(self, box: Box, new_position: Position) -> bool:
        """Check if box can be pushed to the new position with deadlock detection (for bot algorithms)"""
        if not self.is_position_valid(new_position):
            return False
        
        # Check for solid entities at target position
        entities = self.get_entities_at(new_position)
        for entity in entities:
            if entity.is_solid():
                return False
        
        # CRITICAL: Enhanced deadlock detection based on reference implementation
        dock_at_new_pos = self.get_entity_of_type_at(new_position, EntityType.DOCK)
        if not dock_at_new_pos:  # Only check deadlock if not on goal
            # Check if box would be stuck in corner
            if self._is_box_in_corner(new_position):
                log.debug(f"🚫 Corner deadlock detected: box at {new_position}")
                return False
        
        return True
    
    def _move_box(self, box: Box, new_position: Position):
        """Move box to new position and update dock states"""
        old_position = box.position
        
        # Remove box from old position
        self._remove_entity(box)
        
        # Update dock state at old position
        old_dock = self.get_entity_of_type_at(old_position, EntityType.DOCK)
        if old_dock and isinstance(old_dock, Dock):
            old_dock.remove_box()
            box.set_on_dock(False)
        
        # Move box
        box.set_position(new_position)
        self._add_entity(box)
        
        # Update dock state at new position
        new_dock = self.get_entity_of_type_at(new_position, EntityType.DOCK)
        if new_dock and isinstance(new_dock, Dock):
            new_dock.place_box()
            box.set_on_dock(True)
    
    def _move_player_to(self, new_position: Position, log_action: bool = True):
        """Move player to new position and update dock states"""
        if not self.player:
            return
            
        old_position = self.player.position
        
        # Remove player from old position
        self._remove_entity(self.player)
        
        # Update dock state at old position
        old_dock = self.get_entity_of_type_at(old_position, EntityType.DOCK)
        if old_dock and isinstance(old_dock, Dock):
            old_dock.remove_player()
            self.player.set_on_dock(False)
        
        # Move player (with logging control)
        self.player.move(new_position, log_action=log_action)
        self._add_entity(self.player)
        
        # Update dock state at new position
        new_dock = self.get_entity_of_type_at(new_position, EntityType.DOCK)
        if new_dock and isinstance(new_dock, Dock):
            new_dock.place_player()
            self.player.set_on_dock(True)
    
    def is_level_complete(self) -> bool:
        """Check if all boxes are on docks"""
        for box in self.boxes:
            if not box.on_dock:
                return False
        return True
    
    def reset_level(self):
        """Reset the level to its original state"""
        self._parse_level_data(self.original_level_data)
        if self.player:
            self.player.reset_stats()
    
    def render_cell(self, position: Position) -> str:
        """Render the visual representation of a cell"""
        entities = self.get_entities_at(position)
        if not entities:
            return " "
        
        # Return the topmost entity's representation
        return entities[-1].render()
    
    def get_moves(self) -> int:
        """Get player's move count"""
        return self.player.moves if self.player else 0
    
    def get_pushes(self) -> int:
        """Get player's push count"""
        return self.player.pushes if self.player else 0