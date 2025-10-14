from base import MovableEntity, Position, EntityType
from log.logger import get_logger, catch_and_log, log_function_call

# Get logger for this module
log = get_logger(__name__)


class Box(MovableEntity):
    """Box entity that can be pushed by the player"""
    
    @log_function_call("INFO")
    def __init__(self, position: Position):
        log.info(f"📦 Creating box at {position}")
        super().__init__(position, EntityType.BOX)
        self.on_dock = False
    
    def render(self) -> str:
        """Render box with enhanced 3D visual effects - 2x2 block"""
        if self.on_dock:
            # Box correctly placed - success indicator
            return "[bold white on bright_green]◉◉[/bold white on bright_green]"
        else:
            # Box not in place - wooden crate appearance
            return "[bold orange_red1]▓▓[/bold orange_red1]"
    
    def is_solid(self) -> bool:
        return True
    
    @catch_and_log(level="WARNING", message="Failed to check box push position")
    def can_be_pushed_to(self, position: Position, game_map) -> bool:
        """Check if box can be pushed to the given position"""
        log.debug(f"📦 Checking if box can be pushed from {self.position} to {position}")
        
        # Box can be pushed to empty floor or dock
        entity_at_pos = game_map.get_entity_at(position)
        if entity_at_pos is None:
            log.debug(f"✅ Box can move to empty position {position}")
            return True
        
        # Can move to dock if it's empty
        if entity_at_pos.entity_type == EntityType.DOCK:
            can_move = not entity_at_pos.has_box
            log.debug(f"🎯 Box dock check at {position}: can_move={can_move}")
            return can_move
        
        # Can move to floor
        if entity_at_pos.entity_type == EntityType.FLOOR:
            log.debug(f"✅ Box can move to floor at {position}")
            return True
        
        log.debug(f"❌ Box cannot move to {position} (blocked by {entity_at_pos.entity_type})")
        return False
    
    def set_on_dock(self, on_dock: bool):
        """Set whether the box is on a dock"""
        self.on_dock = on_dock
        if on_dock:
            self.entity_type = EntityType.BOX_ON_DOCK
        else:
            self.entity_type = EntityType.BOX