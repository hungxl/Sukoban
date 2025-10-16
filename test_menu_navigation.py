#!/usr/bin/env python3
"""
Test the menu navigation functionality
"""

def test_menu_navigation():
    """Verify menu navigation classes work correctly"""
    
    # Import the menu classes
    import sys
    sys.path.insert(0, 'src')
    
    # Import main app components
    from main import BotMenu, PauseMenu, LevelMenu
    
    print("🧪 Testing Menu Navigation...")
    
    # Test BotMenu
    print("\n🤖 Testing BotMenu navigation:")
    bot_menu = BotMenu()
    print(f"Initial selection: {bot_menu.selected_option} -> {bot_menu.get_selected_action()}")
    
    bot_menu.move_down()
    print(f"After move_down: {bot_menu.selected_option} -> {bot_menu.get_selected_action()}")
    
    bot_menu.move_up()
    print(f"After move_up: {bot_menu.selected_option} -> {bot_menu.get_selected_action()}")
    
    # Test wraparound
    bot_menu.move_up()  # Should wrap to last option
    print(f"After wrap up: {bot_menu.selected_option} -> {bot_menu.get_selected_action()}")
    
    # Test PauseMenu
    print("\n⏸️ Testing PauseMenu navigation:")
    pause_menu = PauseMenu()
    print(f"Initial selection: {pause_menu.selected_option} -> {pause_menu.get_selected_action()}")
    
    pause_menu.move_down()
    pause_menu.move_down()
    print(f"After 2 moves down: {pause_menu.selected_option} -> {pause_menu.get_selected_action()}")
    
    # Test LevelMenu
    print("\n📋 Testing LevelMenu navigation:")
    level_menu = LevelMenu()
    print(f"Initial selection: {level_menu.selected_level}")
    print(f"Selected level number: {level_menu.get_selected_level_number()}")
    
    level_menu.move_down()
    level_menu.move_down()
    print(f"After 2 moves down: level {level_menu.get_selected_level_number()}")
    
    print("\n✅ Menu navigation tests completed!")
    
    # Test toggle behavior
    print("\n🔄 Testing toggle behavior:")
    bot_menu.toggle()
    print(f"Bot menu visible: {bot_menu.visible}")
    print(f"Selection reset to: {bot_menu.selected_option}")
    
    bot_menu.toggle()
    print(f"Bot menu visible after toggle: {bot_menu.visible}")

if __name__ == "__main__":
    test_menu_navigation()