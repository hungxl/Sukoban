from abc import ABC, abstractmethod
from typing import Tuple
from enum import Enum

from log.logger import get_logger

# Get logger for this module
log = get_logger(__name__)


class EntityType(Enum):
    """Enum for different entity types"""
    WALL = "wall"
    FLOOR = "floor"
    PLAYER = "player"
    BOX = "box"
    DOCK = "dock"
    PLAYER_ON_DOCK = "player_on_dock"
    BOX_ON_DOCK = "box_on_dock"


class Position:
    """Represents a position in 2D space"""
    
    def __init__(self, x: int, y: int):
        self.x = x
        self.y = y
    
    def __eq__(self, other) -> bool:
        if not isinstance(other, Position):
            return False
        return self.x == other.x and self.y == other.y
    
    def __add__(self, other) -> 'Position':
        if isinstance(other, Position):
            return Position(self.x + other.x, self.y + other.y)
        return NotImplemented
        return NotImplemented
    
    def __repr__(self) -> str:
        return f"Position({self.x}, {self.y})"
    
    def to_tuple(self) -> Tuple[int, int]:
        return (self.x, self.y)


class Entity(ABC):
    """Base class for all game entities"""
    
    def __init__(self, position: Position, entity_type: EntityType):
        self.position = position
        self.entity_type = entity_type
        self._visible = True
    
    @property
    def x(self) -> int:
        return self.position.x
    
    @property
    def y(self) -> int:
        return self.position.y
    
    @property
    def visible(self) -> bool:
        return self._visible
    
    def set_position(self, position: Position):
        """Set the entity's position"""
        self.position = position
    
    def move_to(self, x: int, y: int):
        """Move entity to specific coordinates"""
        self.position = Position(x, y)
    
    def is_at(self, position: Position) -> bool:
        """Check if entity is at the given position"""
        return self.position == position
    
    @abstractmethod
    def render(self) -> str:
        """Return the visual representation of the entity"""
        pass
    
    @abstractmethod
    def can_move_to(self, position: Position) -> bool:
        """Check if this entity can move to the given position"""
        pass
    
    @abstractmethod
    def is_solid(self) -> bool:
        """Check if this entity blocks movement"""
        pass
    
    def update(self):
        """Update entity state - default implementation does nothing"""
        pass
    
    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(position={self.position}, type={self.entity_type})"


class MovableEntity(Entity):
    """Base class for entities that can move"""
    
    def __init__(self, position: Position, entity_type: EntityType):
        super().__init__(position, entity_type)
    
    def move_by(self, dx: int, dy: int) -> Position:
        """Calculate new position after moving by offset"""
        return Position(self.x + dx, self.y + dy)
    
    def can_move_to(self, position: Position) -> bool:
        """Movable entities can generally move unless blocked"""
        return True


class StaticEntity(Entity):
    """Base class for entities that cannot move"""
    
    def __init__(self, position: Position, entity_type: EntityType):
        super().__init__(position, entity_type)
    
    def can_move_to(self, position: Position) -> bool:
        """Static entities cannot move"""
        return False
