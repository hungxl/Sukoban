"""
Sokoban Level Loader
Loads levels from .slc XML files and provides level selection functionality.
"""

import xml.etree.ElementTree as ET
from pathlib import Path
from typing import List, Optional

# Add logging
from ..log.logger import get_logger, log_function_call, log_performance

# Get logger for this module
log = get_logger(__name__)


class SokobanLevel:
    """Represents a single Sokoban level"""
    
    def __init__(self, level_id: str, width: int, height: int, lines: List[str]):
        self.id = level_id
        self.width = width
        self.height = height
        self.lines = lines
        self.number: Optional[int] = None  # Will be set when loaded into collection
        
    def get_level_data(self) -> List[str]:
        """Get the level data as a list of strings"""
        return self.lines
        
    def __str__(self) -> str:
        return f"Level {self.number}: {self.id} ({self.width}x{self.height})"


class LevelCollection:
    """Manages a collection of Sokoban levels from .slc files"""
    
    def __init__(self):
        self.levels: List[SokobanLevel] = []
        self.title = ""
        self.description = ""
        self.loaded_file = None
        
    @log_function_call("INFO")
    def load_from_slc(self, file_path: str) -> bool:
        """Load levels from an .slc XML file"""
        try:
            path = Path(file_path)
            if not path.exists():
                log.error(f"❌ Level file not found: {file_path}")
                return False
                
            log.info(f"📁 Loading levels from: {path.name}")
            
            # Read the file and handle potential header lines
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Find the XML declaration and remove any content before it
            xml_start = content.find('<?xml')
            if xml_start > 0:
                content = content[xml_start:]
                log.info("🔧 Removed non-XML header from file")
            elif xml_start == -1:
                # Look for the root element if no XML declaration
                root_start = content.find('<SokobanLevels')
                if root_start > 0:
                    content = content[root_start:]
                    log.info("🔧 Removed header, no XML declaration found")
            
            # Parse XML from cleaned content
            root = ET.fromstring(content)
            
            # Extract metadata
            title_elem = root.find("Title")
            self.title = title_elem.text if title_elem is not None else "Unknown Collection"
            
            desc_elem = root.find("Description")
            self.description = desc_elem.text if desc_elem is not None else ""
            
            # Find level collection
            level_collection = root.find("LevelCollection")
            if level_collection is None:
                log.error("❌ No LevelCollection found in file")
                return False
                
            # Load all levels
            levels = level_collection.findall("Level")
            self.levels = []
            
            for i, level_elem in enumerate(levels, 1):
                level = self._parse_level(level_elem, i)
                if level:
                    self.levels.append(level)
                    
            log.info(f"✅ Loaded {len(self.levels)} levels from {self.title}")
            self.loaded_file = file_path
            return True
            
        except ET.ParseError as e:
            log.error(f"❌ XML parsing error: {e}")
            return False
        except Exception as e:
            log.error(f"❌ Error loading levels: {e}")
            return False
            
    def _parse_level(self, level_elem: ET.Element, number: int) -> Optional[SokobanLevel]:
        """Parse a single level from XML element"""
        try:
            level_id = level_elem.get("Id", f"Level_{number}")
            width = int(level_elem.get("Width", 0))
            height = int(level_elem.get("Height", 0))
            
            # Extract level lines
            lines = []
            for line_elem in level_elem.findall("L"):
                if line_elem.text:
                    lines.append(line_elem.text)
                    
            if not lines:
                log.warning(f"⚠️ Empty level: {level_id}")
                return None
                
            # Normalize level data
            lines = self._normalize_level(lines)
            
            level = SokobanLevel(level_id, width, height, lines)
            level.number = number
            
            log.debug(f"📋 Parsed level {number}: {level_id}")
            return level
            
        except Exception as e:
            log.error(f"❌ Error parsing level {number}: {e}")
            return None
            
    def _normalize_level(self, lines: List[str]) -> List[str]:
        """Normalize level data for consistent format"""
        if not lines:
            return lines
            
        # Convert HTML entities
        normalized = []
        for line in lines:
            # Replace HTML entities
            line = line.replace("&amp;", "&")
            line = line.replace("&lt;", "<")
            line = line.replace("&gt;", ">")
            normalized.append(line)
            
        return normalized
        
    def get_level(self, level_number: int) -> Optional[SokobanLevel]:
        """Get a level by its number (1-based)"""
        if 1 <= level_number <= len(self.levels):
            return self.levels[level_number - 1]
        return None
        
    def get_level_count(self) -> int:
        """Get the total number of levels"""
        return len(self.levels)
        
    def list_levels(self, page: int = 1, per_page: int = 10) -> List[SokobanLevel]:
        """Get a page of levels for display"""
        start = (page - 1) * per_page
        end = start + per_page
        return self.levels[start:end]
        
    def get_level_info(self, level_number: int) -> str:
        """Get formatted information about a level"""
        level = self.get_level(level_number)
        if level:
            return f"Level {level.number}: {level.id} ({level.width}x{level.height})"
        return f"Level {level_number}: Not found"


# Global level collection instance
_level_collection = LevelCollection()


@log_function_call("INFO")
def load_level_collection(file_path: Optional[str] = None) -> bool:
    """Load the global level collection from file"""
    if file_path is None:
        # Default to the Cosmonotes.slc file
        file_path = str(Path(__file__).parent.parent.parent / "assets" / "levels" / "Cosmonotes.slc")
        
    return _level_collection.load_from_slc(file_path)


def get_level_collection() -> LevelCollection:
    """Get the global level collection"""
    return _level_collection


def get_level(level_number: int) -> Optional[List[str]]:
    """Get level data by number (1-based)"""
    level = _level_collection.get_level(level_number)
    if level:
        return level.get_level_data()
    return None


def get_level_count() -> int:
    """Get total number of available levels"""
    return _level_collection.get_level_count()


def get_level_info(level_number: int) -> str:
    """Get information about a specific level"""
    return _level_collection.get_level_info(level_number)


def list_available_levels(page: int = 1, per_page: int = 10) -> List[str]:
    """List available levels with their information"""
    levels = _level_collection.list_levels(page, per_page)
    return [str(level) for level in levels]


class Level:
    """Legacy Level class for compatibility with existing code"""
    
    def __init__(self, level_number: int = 1):
        """Initialize with a specific level number"""
        self.level_number = level_number
        
        # Ensure collection is loaded
        if _level_collection.get_level_count() == 0:
            if not load_level_collection():
                log.error("❌ Failed to load level collection")
                
    def generate_level(self) -> List[str]:
        """Get the specified level (renamed for compatibility)"""
        level_data = get_level(self.level_number)
        if level_data:
            log.info(f"🎮 Loading level {self.level_number}")
            return level_data
        else:
            log.warning(f"⚠️ Level {self.level_number} not found, using fallback")
            return self._get_fallback_level()
            
    def _get_fallback_level(self) -> List[str]:
        """Provide a simple fallback level if requested level is not found"""
        return [
            "########",
            "#      #",
            "#  $   #",
            "#   . @#",
            "#      #",
            "########"
        ]


@log_performance
def generate_sokoban_level(width: int = 10, height: int = 10, 
                          num_boxes: int = 3, level_number: int = 1) -> List[str]:
    """
    Generate/Load a Sokoban level
    
    Args:
        width: Ignored (levels come from file)
        height: Ignored (levels come from file) 
        num_boxes: Ignored (levels come from file)
        level_number: Which level to load (1-based)
        
    Returns:
        List of strings representing the level
    """
    log.info(f"🎮 Requesting level {level_number}")
    
    # Ensure collection is loaded
    if _level_collection.get_level_count() == 0:
        if not load_level_collection():
            log.error("❌ Failed to load level collection, using fallback")
            return Level()._get_fallback_level()
    
    # Get the requested level
    level_data = get_level(level_number)
    if level_data:
        log.info(f"✅ Loaded level {level_number}: {get_level_info(level_number)}")
        return level_data
    else:
        log.warning(f"⚠️ Level {level_number} not found, using level 1")
        level_data = get_level(1)
        if level_data:
            return level_data
        else:
            log.error("❌ No levels available, using fallback")
            return Level()._get_fallback_level()


# Initialize the level collection on module import
def _initialize_collection():
    """Initialize the level collection when module is imported"""
    try:
        load_level_collection()
        if _level_collection.get_level_count() > 0:
            log.info(f"🎮 Initialized with {_level_collection.get_level_count()} levels from {_level_collection.title}")
    except Exception as e:
        log.warning(f"⚠️ Could not initialize level collection: {e}")


# Auto-initialize when module is imported
_initialize_collection()
