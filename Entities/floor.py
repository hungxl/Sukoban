from base import StaticEntity, Position, EntityType


class Floor(StaticEntity):
    """Floor entity that allows movement"""
    
    def __init__(self, position: Position):
        super().__init__(position, EntityType.FLOOR)
    
    def render(self) -> str:
        """Render floor with subtle tile pattern"""
        return "[dim grey50 on grey30]·[/dim grey50 on grey30]"
    
    def is_solid(self) -> bool:
        return False
