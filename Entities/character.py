from base.Base import MovableEntity, Position, EntityType


class Player(MovableEntity):
    """Player character that can move and push boxes"""
    
    def __init__(self, position: Position):
        super().__init__(position, EntityType.PLAYER)
        self.on_dock = False
        self.moves = 0
        self.pushes = 0
    
    def render(self) -> str:
        """Render player with enhanced visual effects"""
        if self.on_dock:
            # Player on dock - glowing effect with green background
            return "[bold bright_yellow on green]@[/bold bright_yellow on green]"
        else:
            # Player on floor - bright golden color
            return "[bold gold1]@[/bold gold1]"
    
    def is_solid(self) -> bool:
        return True
    
    def move(self, new_position: Position):
        """Move player to new position and increment move counter"""
        self.set_position(new_position)
        self.moves += 1
    
    def push_box(self):
        """Increment push counter when player pushes a box"""
        self.pushes += 1
    
    def set_on_dock(self, on_dock: bool):
        """Set whether the player is on a dock"""
        self.on_dock = on_dock
        if on_dock:
            self.entity_type = EntityType.PLAYER_ON_DOCK
        else:
            self.entity_type = EntityType.PLAYER
    
    def reset_stats(self):
        """Reset move and push counters"""
        self.moves = 0
        self.pushes = 0