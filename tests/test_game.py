#!/usr/bin/env python3
"""Simple test to verify the Sokoban game can be imported and basic functionality works"""

try:
    from main import SukobanApp
    print("✓ Successfully imported SukobanApp")
    
    # Test level loading
    app = SukobanApp()
    print("✓ Successfully created SukobanApp instance")
    
    # Test that the game map loads properly
    print(f"✓ Game map has {len(app.level_data)} rows")
    print("✓ Level data sample:", app.level_data[0] if app.level_data else "No data")
    
    print("\n🎮 Sokoban game is ready to run!")
    print("Run: uv run python main.py")
    
except ImportError as e:
    print(f"❌ Import error: {e}")
except Exception as e:
    print(f"❌ Error: {e}")