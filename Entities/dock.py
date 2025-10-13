from base.Base import StaticEntity, Position, EntityType


class Dock(StaticEntity):
    """Dock entity - target location for boxes"""
    
    def __init__(self, position: Position):
        super().__init__(position, EntityType.DOCK)
        self.has_box = False
        self.has_player = False
    
    def render(self) -> str:
        """Render dock with glowing target indicator"""
        if self.has_box:
            # Dock with box - success state with pulsing effect
            return "[bold white on bright_green blink]◉[/bold white on bright_green blink]"
        else:
            # Empty dock - glowing target
            return "[bold bright_green on green]○[/bold bright_green on green]"
    
    def is_solid(self) -> bool:
        return False
    
    def place_box(self):
        """Mark that a box is placed on this dock"""
        self.has_box = True
    
    def remove_box(self):
        """Mark that the box is removed from this dock"""
        self.has_box = False
    
    def place_player(self):
        """Mark that the player is on this dock"""
        self.has_player = True
    
    def remove_player(self):
        """Mark that the player left this dock"""
        self.has_player = False