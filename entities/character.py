from base import MovableEntity, Position, EntityType
from log.logger import get_logger, catch_and_log, log_function_call, log_player_action

# Get logger for this module
log = get_logger(__name__)


class Player(MovableEntity):
    """Player character that can move and push boxes"""
    
    @log_function_call("INFO")
    def __init__(self, position: Position):
        log.info(f"👤 Creating player at {position}")
        super().__init__(position, EntityType.PLAYER)
        self.on_dock = False
        self.moves = 0
        self.pushes = 0
    
    def render(self) -> str:
        """Render player with enhanced visual effects - 2x2 block"""
        if self.on_dock:
            # Player on dock - glowing effect with green background
            return "[bold bright_yellow on green]@@[/bold bright_yellow on green]"
        else:
            # Player on floor - bright golden color
            return "[bold gold1]@@[/bold gold1]"
    
    def is_solid(self) -> bool:
        return True
    
    @catch_and_log(level="WARNING", message="Failed to move player")
    def move(self, new_position: Position):
        """Move player to new position and increment move counter"""
        old_pos = self.position
        self.set_position(new_position)
        self.moves += 1
        log_player_action(f"moved from {old_pos} to {new_position}", success=True, 
                         moves=self.moves, pushes=self.pushes)
    
    @log_function_call("INFO")
    def push_box(self):
        """Increment push counter when player pushes a box"""
        self.pushes += 1
        log_player_action(f"pushed box (total pushes: {self.pushes})", success=True)
    
    @catch_and_log(level="WARNING", message="Failed to set dock status")
    def set_on_dock(self, on_dock: bool):
        """Set whether the player is on a dock"""
        old_status = self.on_dock
        self.on_dock = on_dock
        if on_dock:
            self.entity_type = EntityType.PLAYER_ON_DOCK
        else:
            self.entity_type = EntityType.PLAYER
        
        log.debug(f"🎯 Player dock status changed: {old_status} -> {on_dock}")
    
    def reset_stats(self):
        """Reset move and push counters"""
        old_moves, old_pushes = self.moves, self.pushes
        self.moves = 0
        self.pushes = 0
        log.info(f"🔄 Player stats reset: moves {old_moves}->0, pushes {old_pushes}->0")