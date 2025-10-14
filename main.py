from textual.app import App, ComposeResult
from textual.widgets import Header, Footer, Static
from textual.containers import Container
from rich.text import Text
from game_manager import GameMap
from base import Position
from log import get_logger
from random import randint
from pathlib import Path

LOG_DIR = Path(__file__).resolve().parent.parent / "logs"
LOG_DIR.mkdir(exist_ok=True)
for file in LOG_DIR.glob("*.log"):
    file.unlink()
    
# Get logger for this module
log = get_logger(__name__)


class GameMapWidget(Static):
    """Widget to display the Sokoban game map using entity system"""
    
    def __init__(self, level_data: list[str]):
        super().__init__()
        log.info(f"Initializing GameMapWidget with level size {len(level_data)}x{len(level_data[0]) if level_data else 0}")
        self.game_map = GameMap(level_data)
        log.info("GameMapWidget initialization complete")
        
    def render(self) -> Text:
        """Render the game map with entities"""
        lines = []
        
        for y in range(self.game_map.height):
            line = ""
            for x in range(self.game_map.width):
                position = Position(x, y)
                cell_render = self.game_map.render_cell(position)
                line += cell_render
            lines.append(line)
        
        return Text.from_markup("\n".join(lines))
    
    def move_player(self, direction: str) -> bool:
        """Move player in the given direction"""
        log.debug(f"Moving player in direction: {direction}")
        success = self.game_map.move_player(direction)
        if success:
            log.info(f"Player moved {direction} successfully")
        else:
            log.warning(f"Player could not move {direction}")
        return success
    
    def is_level_complete(self) -> bool:
        """Check if all boxes are on docks"""
        complete = self.game_map.is_level_complete()
        if complete:
            log.success("🎉 Level completed! All boxes are on docks!")
        return complete
    
    def reset_level(self):
        """Reset the level to its original state"""
        self.game_map.reset_level()
    
    def get_moves(self) -> int:
        """Get player's move count"""
        return self.game_map.get_moves()
    
    def get_pushes(self) -> int:
        """Get player's push count"""
        return self.game_map.get_pushes()


class ScoreBar(Static):
    """Widget to display game statistics"""
    
    def __init__(self, game_map_widget: GameMapWidget):
        super().__init__()
        self.game_map_widget = game_map_widget
        
    def render(self) -> Text:
        moves = self.game_map_widget.get_moves()
        pushes = self.game_map_widget.get_pushes()
        return Text.from_markup(
            f"[bold cyan]Moves: {moves}[/bold cyan]  "
            f"[bold magenta]Pushes: {pushes}[/bold magenta]"
        )


class PauseMenu(Static):
    """Pause menu overlay"""
    
    def __init__(self):
        super().__init__()
        self.visible = False
        
    def render(self) -> Text:
        if not self.visible:
            return Text("")
            
        return Text.from_markup(
            "\n[bold white on blue]        PAUSED        [/bold white on blue]\n"
            "[bold white on blue]                      [/bold white on blue]\n"
            "[bold white on blue]  R - Resume Game     [/bold white on blue]\n"
            "[bold white on blue]  N - New Level       [/bold white on blue]\n"
            "[bold white on blue]  R - Reset Level     [/bold white on blue]\n"
            "[bold white on blue]  Q - Quit Game       [/bold white on blue]\n"
            "[bold white on blue]                      [/bold white on blue]\n"
        )
    
    def toggle(self):
        self.visible = not self.visible


class SukobanApp(App):
    """Main Sokoban game application using entity-based architecture"""
    
    CSS = """
    Screen {
        background: $background;
    }
    
    .game-container {
        height: 100%;
        width: 100%;
        align: center middle;
    }
    
    .score-bar {
        dock: top;
        height: 3;
        background: $surface;
        text-align: center;
    }
    
    .game-map {
        margin: 1;
        text-align: center;
    }
    
    .pause-menu {
        dock: top;
        height: 8;
        text-align: center;
        layer: overlay;
    }
    """
    
    BINDINGS = [
        ("w,up", "move_up", "Move up"),
        ("s,down", "move_down", "Move down"),
        ("a,left", "move_left", "Move left"),
        ("d,right", "move_right", "Move right"),
        ("p,space", "pause", "Pause"),
        ("r", "reset", "Reset level"),
        ("n", "new_level", "Generate new level"),
        ("q", "quit", "Quit"),
    ]
    
    def __init__(self):
        super().__init__()
        log.info("🎮 Starting Sokoban game application...")
        self.level_data = self.load_level()
        self.game_map_widget = GameMapWidget(self.level_data)
        self.score_bar = ScoreBar(self.game_map_widget)
        self.pause_menu = PauseMenu()
        self.paused = False
        log.success("✅ Sokoban application initialized successfully!")
        
    def load_level(self) -> list[str]:
        """Generate a new level using the procedural level generator"""
        log.info("🎲 Generating new level with procedural generator...")
        try:
            from levels.level import generate_sokoban_level
            
            # Generate a new level with reasonable parameters  
            level_data = generate_sokoban_level(10, 10, 3)
            
            if level_data and len(level_data) > 0:
                log.success(f"✅ Level generated successfully ({len(level_data)} lines)")
                return level_data
            else:
                log.warning("⚠️ Level generation failed, using fallback level")
                return self.get_default_level()
                
        except Exception as e:
            log.error(f"❌ Level generation error: {e}")
            log.info("🔄 Falling back to default level")
            return self.get_default_level()
    
    def get_default_level(self) -> list[str]:
        """Return a default level if file is not found"""
        log.info("🎮 Loading default level...")
        return [
            "####",
            "#  ###",
            "#    #",
            "# $  #",
            "### ###",
            "#   $ #",
            "#. @..#",
            "#  $  #",
            "###  ##",
            "  ####"
        ]
    
    def compose(self) -> ComposeResult:
        """Compose the UI layout"""
        yield Header()
        yield Container(
            self.pause_menu,
            self.score_bar,
            self.game_map_widget,
            classes="game-container"
        )
        yield Footer()
    
    def action_move_up(self):
        if not self.paused:
            self.move_player('up')
    
    def action_move_down(self):
        if not self.paused:
            self.move_player('down')
    
    def action_move_left(self):
        if not self.paused:
            self.move_player('left')
    
    def action_move_right(self):
        if not self.paused:
            self.move_player('right')
    
    def action_pause(self):
        self.paused = not self.paused
        self.pause_menu.toggle()
        self.refresh_widgets()
    
    def action_reset(self):
        self.game_map_widget.reset_level()
        self.refresh_widgets()
    
    def action_new_level(self):
        """Generate and load a new level"""
        try:
            log.info("🎲 Generating new level...")
            from levels.level import generate_sokoban_level
            
            # Generate a new level
            size = randint(8, 12)
            boxes = randint(2, min(5, size // 2))
            new_level_data = generate_sokoban_level(size, size, boxes)
            
            # Get the container
            container = self.query_one(".game-container")
            
            # Remove the old widget if it exists and is mounted
            old_widget = self.game_map_widget
            if old_widget and old_widget.is_mounted:
                old_widget.remove()
            
            # Create new game map widget
            self.game_map_widget = GameMapWidget(new_level_data)
            self.score_bar.game_map_widget = self.game_map_widget
            
            # Mount the new widget in the container
            container.mount(self.game_map_widget)
            
            # Refresh the display
            self.refresh()
            self.notify("🎮 New level generated!", severity="information")
            log.success("✅ New level successfully generated and displayed")
            
        except Exception as e:
            log.error(f"❌ Level generation failed: {e}")
            self.notify(f"❌ Failed to generate level: {e}", severity="error")
    
    def move_player(self, direction: str):
        """Handle player movement and game state updates"""
        if self.game_map_widget.move_player(direction):
            self.refresh_widgets()
            moves = self.game_map_widget.get_moves()
            pushes = self.game_map_widget.get_pushes()
            log.debug(f"Game state updated - Moves: {moves}, Pushes: {pushes}")
            
            if self.game_map_widget.is_level_complete():
                log.success(f"🎉 Level completed in {moves} moves and {pushes} pushes!")
                self.notify("🎉 Level Complete! Congratulations!", severity="information")
    
    def refresh_widgets(self):
        """Refresh all widgets"""
        self.game_map_widget.refresh()
        self.score_bar.refresh()
        self.pause_menu.refresh()


if __name__ == "__main__":
    app = SukobanApp()
    app.run()