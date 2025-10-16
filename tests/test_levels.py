#!/usr/bin/env python3
"""
Test the level loading functionality
"""

import sys
from pathlib import Path

# Add src to path if needed
sys.path.insert(0, 'src')

def test_level_loading():
    """Test the level loading functionality"""
    try:
        print("🧪 Testing level loading...")
        
        # Test imports
        from src.levels.level import (
            get_level_count, 
            get_level_info, 
            get_level, 
            load_level_collection,
            generate_sokoban_level
        )
        print("✅ Imports successful")
        
        # Test loading collection
        if load_level_collection():
            print("✅ Level collection loaded")
        else:
            print("❌ Failed to load level collection")
            return False
            
        # Test level count
        count = get_level_count()
        print(f"📊 Total levels available: {count}")
        
        if count == 0:
            print("❌ No levels found")
            return False
            
        # Test getting level info
        for i in range(1, min(6, count + 1)):
            info = get_level_info(i)
            print(f"📋 {info}")
            
        # Test getting actual level data
        level_1 = get_level(1)
        if level_1:
            print(f"🎮 Level 1 data ({len(level_1)} lines):")
            for line in level_1[:5]:  # Show first 5 lines
                print(f"   {line}")
            if len(level_1) > 5:
                print(f"   ... ({len(level_1) - 5} more lines)")
        else:
            print("❌ Could not get level 1 data")
            return False
            
        # Test the generate_sokoban_level function
        print("\n🔄 Testing generate_sokoban_level function...")
        level_data = generate_sokoban_level(10, 10, 3, 5)  # Load level 5
        if level_data:
            print(f"✅ generate_sokoban_level returned level 5 ({len(level_data)} lines)")
        else:
            print("❌ generate_sokoban_level failed")
            return False
            
        print("\n✅ All tests passed!")
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_level_loading()