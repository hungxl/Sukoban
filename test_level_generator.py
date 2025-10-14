#!/usr/bin/env python3
"""
Test script for the Sokoban level generator
"""

import sys
import os

# Add the Levels directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'Levels'))

try:
    # Import directly from the level.py file
    sys.path.append(os.path.join(os.path.dirname(__file__), 'Levels'))
    from levels.level import Level, generate_sokoban_level, generate_simple_level
    
    print("🎮 Testing Sokoban Level Generator")
    print("=" * 50)
    
    # Test 1: Simple level generation
    print("\n1. Testing simple level generation:")
    simple_level = generate_simple_level(8, 8, 2)
    for i, row in enumerate(simple_level):
        print(f"  {i:2d}: {row}")
    
    # Test 2: Advanced level generation
    print("\n2. Testing advanced level generation:")
    try:
        advanced_level = generate_sokoban_level(10, 10, 3, optimize=False)
        for i, row in enumerate(advanced_level):
            print(f"  {i:2d}: {row}")
    except Exception as e:
        print(f"  Advanced generation failed: {e}")
        print("  Falling back to simple generation...")
    
    # Test 3: Level class usage
    print("\n3. Testing Level class:")
    level_generator = Level(9, 4)
    level_data = level_generator.generate_level()
    for i, row in enumerate(level_data):
        print(f"  {i:2d}: {row}")
    
    print("\n✅ Level generator tests completed!")
    
except ImportError as e:
    print(f"❌ Import error: {e}")
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()