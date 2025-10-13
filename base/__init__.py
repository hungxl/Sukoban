"""
Base package for Sokoban game.

Contains the core abstract classes and data structures:
- Entity: Base abstract class for all game entities
- MovableEntity: Base class for entities that can move
- StaticEntity: Base class for entities that cannot move
- Position: 2D position representation
- EntityType: Enum for different entity types
"""

from .Base import Entity, MovableEntity, StaticEntity, Position, EntityType

__all__ = ['Entity', 'MovableEntity', 'StaticEntity', 'Position', 'EntityType']