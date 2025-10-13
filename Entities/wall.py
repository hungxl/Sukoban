from base.Base import StaticEntity, Position, EntityType


class Wall(StaticEntity):
    """Wall entity that blocks movement"""
    
    def __init__(self, position: Position):
        super().__init__(position, EntityType.WALL)
    
    def render(self) -> str:
        """Render wall with stone brick texture effect"""
        return "[bold steel_blue1 on blue]█[/bold steel_blue1 on blue]"
    
    def is_solid(self) -> bool:
        return True
