from base.Base import MovableEntity, Position, EntityType


class Box(MovableEntity):
    """Box entity that can be pushed by the player"""
    
    def __init__(self, position: Position):
        super().__init__(position, EntityType.BOX)
        self.on_dock = False
    
    def render(self) -> str:
        """Render box with enhanced 3D visual effects"""
        if self.on_dock:
            # Box correctly placed - success indicator
            return "[bold white on bright_green]◉[/bold white on bright_green]"
        else:
            # Box not in place - wooden crate appearance
            return "[bold orange_red1]▓[/bold orange_red1]"
    
    def is_solid(self) -> bool:
        return True
    
    def can_be_pushed_to(self, position: Position, game_map) -> bool:
        """Check if box can be pushed to the given position"""
        # Box can be pushed to empty floor or dock
        entity_at_pos = game_map.get_entity_at(position)
        if entity_at_pos is None:
            return True
        
        # Can move to dock if it's empty
        if entity_at_pos.entity_type == EntityType.DOCK:
            return not entity_at_pos.has_box
        
        # Can move to floor
        if entity_at_pos.entity_type == EntityType.FLOOR:
            return True
            
        return False
    
    def set_on_dock(self, on_dock: bool):
        """Set whether the box is on a dock"""
        self.on_dock = on_dock
        if on_dock:
            self.entity_type = EntityType.BOX_ON_DOCK
        else:
            self.entity_type = EntityType.BOX